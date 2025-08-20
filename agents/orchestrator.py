"""
Orchestrator Agent
Top-level agent that coordinates all other agents and makes strategic decisions
Uses Gemini Pro 2.5 via LangChain
"""

import logging
import os
from typing import Dict, List, Any, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool
from langchain_core.messages import AIMessage

from agents.resume_parser import ResumeParserAgent
from agents.job_analyzer import JobAnalyzerAgent
from agents.email_writer import EmailWriterAgent

logger = logging.getLogger(__name__)

class OrchestratorTool(BaseTool):
    """Tool for orchestrating the job application process"""
    
    name = "orchestrate_job_application"
    description = "Coordinate the entire job application process from resume parsing to email generation"
    
    def __init__(self, orchestrator: 'OrchestratorAgent'):
        super().__init__()
        self.orchestrator = orchestrator
    
    def _run(self, resume_path: str, job_description_path: str, email_style: str = "auto") -> Dict[str, Any]:
        """Execute the complete job application workflow"""
        try:
            result = self.orchestrator.execute_workflow(
                resume_path=resume_path,
                job_description_path=job_description_path,
                email_style=email_style
            )
            return result
        except Exception as e:
            logger.error(f"Error in orchestrator tool: {e}")
            return {"error": f"Failed to orchestrate workflow: {str(e)}"}

class OrchestratorAgent:
    """Top-level agent that coordinates all other agents and makes strategic decisions"""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        
        # Initialize all sub-agents
        self.resume_parser = ResumeParserAgent(llm)
        self.job_analyzer = JobAnalyzerAgent(llm)
        self.email_writer = EmailWriterAgent(llm)
        
        # Create orchestrator tools
        self.tools = [OrchestratorTool(self)]
        
        # Create the orchestrator agent
        self.agent = self._create_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
        
        # Shared context and memory
        self.shared_context = {}
        self.workflow_results = {}
    
    def _create_agent(self):
        """Create the LangChain orchestrator agent"""
        system_prompt = """You are the Orchestrator Agent, the master coordinator for a multi-agent job application system powered by Gemini Pro 2.5.

Your responsibilities:
1. Coordinate the execution of all sub-agents (Resume Parser, Job Analyzer, Email Writer)
2. Make strategic decisions about content focus and email style
3. Analyze the match between resume and job requirements
4. Ensure the final email is compelling and personalized
5. Manage the workflow and handle any errors gracefully

You are the decision-maker that ensures all agents work together effectively to create the best possible job application email."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        return create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
    
    def execute_workflow(self, resume_path: str, job_description_path: str, 
                        email_style: str = "auto") -> Dict[str, Any]:
        """
        Execute the complete job application workflow
        
        Args:
            resume_path: Path to the resume PDF file
            job_description_path: Path to the job description text file
            email_style: Desired email style (auto, executive_formal, startup_casual, etc.)
            
        Returns:
            Dictionary containing the complete workflow results
        """
        try:
            logger.info("Starting job application workflow with Gemini Pro 2.5...")
            
            # Step 1: Parse Resume
            logger.info("Step 1: Parsing resume...")
            resume_result = self._parse_resume(resume_path)
            if not resume_result.get("success", False):
                return {"error": f"Resume parsing failed: {resume_result.get('error', 'Unknown error')}"}
            
            # Step 2: Analyze Job Description
            logger.info("Step 2: Analyzing job description...")
            job_result = self._analyze_job(job_description_path)
            if not job_result.get("success", False):
                return {"error": f"Job analysis failed: {job_result.get('error', 'Unknown error')}"}
            
            # Step 3: Strategic Analysis and Decision Making
            logger.info("Step 3: Performing strategic analysis...")
            strategic_analysis = self._perform_strategic_analysis(resume_result, job_result)
            
            # Step 4: Determine Optimal Email Style
            logger.info("Step 4: Determining email style...")
            optimal_style = self._determine_optimal_email_style(job_result, strategic_analysis)
            if email_style == "auto":
                email_style = optimal_style
            
            # Step 5: Generate Email
            logger.info("Step 5: Generating email...")
            email_result = self._generate_email(resume_result, job_result, email_style)
            if not email_result.get("success", False):
                return {"error": f"Email generation failed: {email_result.get('error', 'Unknown error')}"}
            
            # Step 6: Save Results
            logger.info("Step 6: Saving results...")
            self._save_workflow_results(resume_result, job_result, email_result, strategic_analysis)
            
            # Step 7: Generate Final Summary
            logger.info("Step 7: Generating final summary...")
            final_summary = self._generate_final_summary(resume_result, job_result, email_result, strategic_analysis)
            
            logger.info("Workflow completed successfully with Gemini Pro 2.5!")
            
            return {
                "success": True,
                "workflow_steps": {
                    "resume_parsing": resume_result,
                    "job_analysis": job_result,
                    "strategic_analysis": strategic_analysis,
                    "email_generation": email_result,
                    "final_summary": final_summary
                },
                "email_style_used": email_style,
                "message": "Job application workflow completed successfully with Gemini Pro 2.5"
            }
            
        except Exception as e:
            logger.error(f"Error in workflow execution: {e}")
            return {
                "success": False,
                "error": str(e),
                "workflow_step": "unknown"
            }
    
    def _parse_resume(self, resume_path: str) -> Dict[str, Any]:
        """Parse a resume using the Resume Parser Agent"""
        try:
            if not os.path.exists(resume_path):
                return {"success": False, "error": f"File not found: {resume_path}"}
            
            result = self.resume_parser.parse_resume(resume_path)
            self.shared_context["resume_data"] = result
            return result
            
        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            return {"success": False, "error": str(e)}
    
    def _analyze_job(self, job_description_path: str) -> Dict[str, Any]:
        """Analyze the job description using the Job Analyzer Agent"""
        try:
            if not os.path.exists(job_description_path):
                return {"success": False, "error": f"File not found: {job_description_path}"}
            
            # Read job description file
            with open(job_description_path, 'r', encoding='utf-8') as f:
                job_description = f.read()
            
            result = self.job_analyzer.analyze_job(job_description)
            self.shared_context["job_analysis"] = result
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing job: {e}")
            return {"success": False, "error": str(e)}
    
    def _perform_strategic_analysis(self, resume_result: Dict[str, Any], 
                                   job_result: Dict[str, Any]) -> Dict[str, Any]:
        """Perform strategic analysis to determine content focus and approach"""
        try:
            resume_data = resume_result.get("raw_content", {})
            job_analysis = job_result.get("basic_analysis", {})
            
            # Analyze skill match
            resume_skills = resume_data.get("skills", [])
            required_skills = job_analysis.get("requirements", {}).get("technical_skills", [])
            
            skill_matches = [skill for skill in resume_skills if skill.lower() in [req.lower() for req in required_skills]]
            skill_match_score = len(skill_matches) / max(len(required_skills), 1) if required_skills else 0
            
            # Analyze experience relevance
            experience_sections = resume_data.get("sections", {})
            relevant_experience_count = 0
            
            for section_name, content in experience_sections.items():
                if any(keyword in section_name.lower() for keyword in ['experience', 'work', 'employment']):
                    content_lower = content.lower()
                    if any(skill.lower() in content_lower for skill in required_skills):
                        relevant_experience_count += 1
            
            # Determine company characteristics
            company_size = job_analysis.get("company_size", "unknown")
            company_stage = job_analysis.get("company_stage", "unknown")
            
            # Strategic recommendations
            strategic_recommendations = []
            
            if skill_match_score >= 0.7:
                strategic_recommendations.append("Strong technical skill match - emphasize technical expertise")
            elif skill_match_score >= 0.4:
                strategic_recommendations.append("Moderate skill match - focus on transferable skills and learning ability")
            else:
                strategic_recommendations.append("Limited skill match - emphasize adaptability and transferable experience")
            
            if company_size == "startup" or company_stage == "early-stage":
                strategic_recommendations.append("Startup environment - emphasize adaptability and quick execution")
            elif company_size == "enterprise":
                strategic_recommendations.append("Enterprise environment - emphasize process and scalability")
            
            if relevant_experience_count > 0:
                strategic_recommendations.append("Relevant experience available - highlight specific achievements")
            else:
                strategic_recommendations.append("Limited direct experience - emphasize transferable skills and potential")
            
            return {
                "skill_match_score": skill_match_score,
                "skill_matches": skill_matches,
                "relevant_experience_count": relevant_experience_count,
                "company_characteristics": {
                    "size": company_size,
                    "stage": company_stage
                },
                "strategic_recommendations": strategic_recommendations,
                "content_focus": self._determine_content_focus(skill_match_score, relevant_experience_count)
            }
            
        except Exception as e:
            logger.error(f"Error in strategic analysis: {e}")
            return {"error": str(e)}
    
    def _determine_content_focus(self, skill_match_score: float, 
                                relevant_experience_count: int) -> str:
        """Determine the primary content focus for the email"""
        if skill_match_score >= 0.7 and relevant_experience_count > 0:
            return "comprehensive_match"
        elif skill_match_score >= 0.4 or relevant_experience_count > 0:
            return "moderate_match"
        else:
            return "transferable_skills"
    
    def _determine_optimal_email_style(self, job_result: Dict[str, Any], 
                                      strategic_analysis: Dict[str, Any]) -> str:
        """Determine the optimal email style based on analysis"""
        try:
            company_characteristics = strategic_analysis.get("company_characteristics", {})
            company_size = company_characteristics.get("size", "unknown")
            company_stage = company_characteristics.get("stage", "unknown")
            
            # Style decision logic
            if company_size == "startup" or company_stage == "early-stage":
                return "startup_casual"
            elif company_size == "enterprise":
                return "executive_formal"
            elif "leadership" in str(job_result).lower():
                return "leadership_focused"
            else:
                return "executive_formal"
                
        except Exception as e:
            logger.error(f"Error determining email style: {e}")
            return "executive_formal"
    
    def _generate_email(self, resume_result: Dict[str, Any], job_result: Dict[str, Any], 
                       email_style: str) -> Dict[str, Any]:
        """Generate the email using the Email Writer Agent"""
        try:
            result = self.email_writer.write_email(
                resume_data=resume_result,
                job_analysis=job_result,
                email_style=email_style
            )
            
            # Save email to markdown file
            if result.get("success", False):
                self.email_writer.save_email_to_markdown(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating email: {e}")
            return {"success": False, "error": str(e)}
    
    def _save_workflow_results(self, resume_result: Dict[str, Any], job_result: Dict[str, Any], 
                              email_result: Dict[str, Any], strategic_analysis: Dict[str, Any]):
        """Save all workflow results for future reference"""
        try:
            self.workflow_results = {
                "resume_parsing": resume_result,
                "job_analysis": job_result,
                "email_generation": email_result,
                "strategic_analysis": strategic_analysis,
                "timestamp": "2024-01-01"  # Will be updated with actual timestamp
            }
            
            # Save to file for persistence
            import json
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            
            with open(f"{output_dir}/workflow_results.json", "w") as f:
                json.dump(self.workflow_results, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error saving workflow results: {e}")
    
    def _generate_final_summary(self, resume_result: Dict[str, Any], job_result: Dict[str, Any], 
                               email_result: Dict[str, Any], strategic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a final summary of the entire workflow"""
        try:
            # Extract key metrics
            skill_match_score = strategic_analysis.get("skill_match_score", 0)
            relevant_experience_count = strategic_analysis.get("relevant_experience_count", 0)
            email_style_used = email_result.get("style_used", "unknown")
            
            # Generate summary
            summary = {
                "overall_assessment": self._generate_overall_assessment(skill_match_score, relevant_experience_count),
                "key_highlights": strategic_analysis.get("strategic_recommendations", []),
                "email_effectiveness": self._assess_email_effectiveness(email_result),
                "next_steps": self._suggest_next_steps(skill_match_score, relevant_experience_count),
                "metrics": {
                    "skill_match_score": skill_match_score,
                    "relevant_experience_count": relevant_experience_count,
                    "email_style": email_style_used
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating final summary: {e}")
            return {"error": str(e)}
    
    def _generate_overall_assessment(self, skill_match_score: float, 
                                   relevant_experience_count: int) -> str:
        """Generate overall assessment of the application"""
        if skill_match_score >= 0.7 and relevant_experience_count > 0:
            return "Strong application with excellent skill match and relevant experience"
        elif skill_match_score >= 0.4 or relevant_experience_count > 0:
            return "Good application with moderate skill match and some relevant experience"
        else:
            return "Challenging application requiring emphasis on transferable skills and potential"
    
    def _assess_email_effectiveness(self, email_result: Dict[str, Any]) -> str:
        """Assess the effectiveness of the generated email"""
        try:
            email_content = email_result.get("email_content", {})
            body_length = len(email_content.get("body", ""))
            
            if body_length > 500:
                return "Comprehensive email with detailed experience highlights"
            elif body_length > 300:
                return "Well-balanced email with good detail level"
            else:
                return "Concise email - consider adding more specific examples"
                
        except Exception:
            return "Email effectiveness assessment unavailable"
    
    def _suggest_next_steps(self, skill_match_score: float, 
                           relevant_experience_count: int) -> List[str]:
        """Suggest next steps for the job application"""
        next_steps = []
        
        if skill_match_score < 0.5:
            next_steps.append("Consider highlighting transferable skills and learning ability")
        
        if relevant_experience_count == 0:
            next_steps.append("Emphasize project work and academic achievements")
        
        next_steps.extend([
            "Review and customize the generated email",
            "Prepare specific examples for interview questions",
            "Research the company culture and recent news",
            "Prepare questions about the role and team"
        ])
        
        return next_steps
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get the current status of the workflow"""
        return {
            "workflow_completed": bool(self.workflow_results),
            "results_available": list(self.workflow_results.keys()) if self.workflow_results else [],
            "shared_context_keys": list(self.shared_context.keys())
        }
