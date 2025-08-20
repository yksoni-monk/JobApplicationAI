"""
Email Writer Agent
Uses LangChain to generate executive-style introduction emails
"""

import logging
import os
from typing import Dict, List, Any, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool
from langchain_core.messages import AIMessage

from utils.email_templates import EmailTemplateManager, EmailFormatter

logger = logging.getLogger(__name__)

class EmailGenerationTool(BaseTool):
    """Tool for generating email content"""
    
    name: str = "generate_email_content"
    description: str = "Generate executive-style email content based on resume and job analysis"
    email_template_manager: EmailTemplateManager
    
    def __init__(self, email_template_manager: EmailTemplateManager):
        super().__init__()
        self.template_manager = email_template_manager
    
    def _run(self, resume_data: Dict[str, Any], job_analysis: Dict[str, Any], email_style: str = "executive_formal") -> Dict[str, Any]:
        """Generate email content based on provided data"""
        try:
            # Extract key information
            candidate_name = self._extract_candidate_name(resume_data)
            key_skills = self._extract_key_skills(resume_data)
            relevant_experience = self._extract_relevant_experience(resume_data, job_analysis)
            
            # Get company information
            company_info = job_analysis.get("basic_analysis", {}).get("company_info", {})
            company_name = company_info.get("name", "the company")
            
            # Determine email style based on company characteristics
            if email_style == "auto":
                email_style = self._determine_auto_style(job_analysis)
            
            # Generate email content
            email_content = self._generate_email_content(
                candidate_name=candidate_name,
                company_name=company_name,
                key_skills=key_skills,
                relevant_experience=relevant_experience,
                job_analysis=job_analysis,
                style=email_style
            )
            
            return {
                "success": True,
                "email_content": email_content,
                "style_used": email_style,
                "message": "Successfully generated email content"
            }
            
        except Exception as e:
            logger.error(f"Error generating email content: {e}")
            return {"error": f"Failed to generate email content: {str(e)}"}
    
    def _extract_candidate_name(self, resume_data: Dict[str, Any]) -> str:
        """Extract candidate name from resume data"""
        try:
            # Look for name in contact info or first few lines
            raw_text = resume_data.get("raw_content", {}).get("raw_text", "")
            lines = raw_text.split('\n')
            
            # First non-empty line is usually the name
            for line in lines:
                line = line.strip()
                if line and len(line) > 2 and not any(keyword in line.lower() for keyword in ['email', 'phone', 'linkedin', 'github']):
                    return line
            
            return "Your Name"  # Fallback
        except Exception:
            return "Your Name"
    
    def _extract_key_skills(self, resume_data: Dict[str, Any]) -> List[str]:
        """Extract key skills from resume data"""
        try:
            skills = resume_data.get("raw_content", {}).get("skills", [])
            if not skills:
                # Try to extract from analysis
                analysis = resume_data.get("analysis", "")
                if analysis:
                    # Simple skill extraction from text
                    import re
                    skill_patterns = [
                        r'proficient\s+in\s+([^,]+)',
                        r'expertise\s+in\s+([^,]+)',
                        r'skills:\s*([^,]+)',
                        r'technologies:\s*([^,]+)'
                    ]
                    
                    for pattern in skill_patterns:
                        matches = re.findall(pattern, analysis, re.IGNORECASE)
                        if matches:
                            skills.extend([skill.strip() for skill in matches[0].split(',')])
            
            return skills[:10]  # Limit to top 10 skills
        except Exception:
            return []
    
    def _extract_relevant_experience(self, resume_data: Dict[str, Any], job_analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract experience relevant to the job requirements"""
        try:
            experience = resume_data.get("raw_content", {}).get("sections", {})
            relevant_experience = []
            
            # Get job requirements
            job_requirements = job_analysis.get("basic_analysis", {}).get("requirements", {})
            required_skills = job_requirements.get("technical_skills", [])
            
            # Look for experience sections
            for section_name, content in experience.items():
                if any(keyword in section_name.lower() for keyword in ['experience', 'work', 'employment']):
                    # Check if content mentions required skills
                    content_lower = content.lower()
                    relevance_score = sum(1 for skill in required_skills if skill.lower() in content_lower)
                    
                    if relevance_score > 0:
                        relevant_experience.append({
                            "section": section_name,
                            "content": content[:200] + "..." if len(content) > 200 else content,
                            "relevance_score": relevance_score
                        })
            
            # Sort by relevance
            relevant_experience.sort(key=lambda x: x["relevance_score"], reverse=True)
            return relevant_experience[:3]  # Top 3 most relevant
            
        except Exception:
            return []
    
    def _determine_auto_style(self, job_analysis: Dict[str, Any]) -> str:
        """Automatically determine email style based on company characteristics"""
        try:
            company_size = job_analysis.get("basic_analysis", {}).get("company_size", "unknown")
            company_stage = job_analysis.get("basic_analysis", {}).get("company_stage", "unknown")
            
            if company_size == "startup" or company_stage == "early-stage":
                return "startup_casual"
            elif company_size == "enterprise":
                return "executive_formal"
            elif "leadership" in str(job_analysis).lower():
                return "leadership_focused"
            else:
                return "executive_formal"
                
        except Exception:
            return "executive_formal"
    
    def _generate_email_content(self, candidate_name: str, company_name: str, key_skills: List[str], 
                               relevant_experience: List[Dict[str, str]], job_analysis: Dict[str, Any], 
                               style: str) -> Dict[str, str]:
        """Generate the actual email content"""
        try:
            # Create context for template
            context = {
                "name": candidate_name,
                "company": company_name,
                "role": "the position",  # Will be filled by LLM
                "years_experience": "5+",  # Will be filled by LLM
                "key_areas": ", ".join(key_skills[:3]) if key_skills else "technology and innovation",
                "industry_focus": "technology and innovation",
                "specific_skills": ", ".join(key_skills[:5]) if key_skills else "technical expertise",
                "specific_innovation": "innovative solutions",
                "key_technology": key_skills[0] if key_skills else "technology",
                "specific_technical_area": "technical development",
                "related_technologies": ", ".join(key_skills[:3]) if key_skills else "various technologies",
                "company_mission": "innovation and growth",
                "leadership_areas": "team leadership and technical direction"
            }
            
            # Generate content paragraphs
            relevant_experience_paragraph = self._generate_experience_paragraph(relevant_experience)
            technical_achievements_paragraph = self._generate_technical_paragraph(key_skills)
            leadership_impact_paragraph = self._generate_leadership_paragraph(job_analysis)
            
            # Add generated paragraphs to context
            context.update({
                "relevant_experience_paragraph": relevant_experience_paragraph,
                "technical_achievements_paragraph": technical_achievements_paragraph,
                "leadership_impact_paragraph": leadership_impact_paragraph,
                "startup_experience_paragraph": self._generate_startup_paragraph(job_analysis),
                "project_achievements_paragraph": self._generate_project_paragraph(relevant_experience),
                "innovation_contributions_paragraph": self._generate_innovation_paragraph(key_skills),
                "team_building_achievements_paragraph": self._generate_team_paragraph(job_analysis),
                "strategic_impact_paragraph": self._generate_strategic_paragraph(job_analysis),
                "call_to_action": "I would welcome the opportunity to discuss how my experience can contribute to your team's success."
            })
            
            # Get template and format
            template = self.template_manager.get_template(style)
            email_content = self.template_manager.format_template(template, context)
            
            return {
                "subject": template.subject.format(**context),
                "greeting": template.greeting,
                "body": template.body.format(**context),
                "closing": template.closing,
                "signature": template.signature.format(**context),
                "full_email": email_content
            }
            
        except Exception as e:
            logger.error(f"Error generating email content: {e}")
            raise
    
    def _generate_experience_paragraph(self, relevant_experience: List[Dict[str, str]]) -> str:
        """Generate paragraph about relevant experience"""
        if not relevant_experience:
            return "I have extensive experience in technology and innovation, with a proven track record of delivering impactful solutions."
        
        experience_text = "My relevant experience includes "
        for i, exp in enumerate(relevant_experience[:2]):
            if i > 0:
                experience_text += ", as well as "
            experience_text += f"work in {exp['section'].lower()}"
        
        experience_text += ". I have consistently demonstrated the ability to deliver high-quality solutions and drive innovation in fast-paced environments."
        return experience_text
    
    def _generate_technical_paragraph(self, key_skills: List[str]) -> str:
        """Generate paragraph about technical achievements"""
        if not key_skills:
            return "I have a strong technical background with expertise in developing scalable solutions and implementing cutting-edge technologies."
        
        skills_text = ", ".join(key_skills[:5])
        return f"I bring deep technical expertise in {skills_text}, with a proven track record of architecting and implementing solutions that drive business value and technical excellence."
    
    def _generate_leadership_paragraph(self, job_analysis: Dict[str, Any]) -> str:
        """Generate paragraph about leadership impact"""
        return "Throughout my career, I have demonstrated strong leadership skills, successfully leading cross-functional teams and mentoring junior developers to deliver high-impact projects."
    
    def _generate_startup_paragraph(self, job_analysis: Dict[str, Any]) -> str:
        """Generate paragraph about startup experience"""
        return "I have experience working in dynamic, fast-paced environments where adaptability and quick decision-making are crucial for success."
    
    def _generate_project_paragraph(self, relevant_experience: List[Dict[str, str]]) -> str:
        """Generate paragraph about project achievements"""
        if not relevant_experience:
            return "I have successfully delivered numerous high-impact projects, consistently meeting deadlines and exceeding expectations."
        
        return f"I have successfully delivered projects in {relevant_experience[0]['section'].lower()}, demonstrating strong project management skills and technical execution."
    
    def _generate_innovation_paragraph(self, key_skills: List[str]) -> str:
        """Generate paragraph about innovation contributions"""
        if not key_skills:
            return "I have consistently contributed to innovation initiatives, bringing creative solutions to complex technical challenges."
        
        return f"I have been at the forefront of innovation in {key_skills[0] if key_skills else 'technology'}, developing novel approaches that have significantly improved system performance and user experience."
    
    def _generate_team_paragraph(self, job_analysis: Dict[str, Any]) -> str:
        """Generate paragraph about team building achievements"""
        return "I have successfully built and led high-performing teams, creating collaborative environments that foster innovation and professional growth."
    
    def _generate_strategic_paragraph(self, job_analysis: Dict[str, Any]) -> str:
        """Generate paragraph about strategic impact"""
        return "I have contributed to strategic initiatives that have driven significant business outcomes, demonstrating the ability to align technical solutions with organizational goals."

class EmailWriterAgent:
    """LangChain-based agent for writing executive-style emails"""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.email_template_manager = EmailTemplateManager()
        self.tools = [EmailGenerationTool(self.email_template_manager)]
        self.agent = self._create_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def _create_agent(self):
        """Create the LangChain agent"""
        system_prompt = """You are an Email Writer Agent specialized in creating executive-style job application emails.

Your responsibilities:
1. Generate compelling, professional email content
2. Tailor emails to specific job requirements and company culture
3. Highlight relevant experience and skills effectively
4. Maintain appropriate tone and style for the target audience
5. Create emails that stand out and drive action

Always focus on creating emails that are personalized, relevant, and compelling. Use the provided tools to generate content based on resume and job analysis data."""

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
    
    def write_email(self, resume_data: Dict[str, Any], job_analysis: Dict[str, Any], 
                    email_style: str = "auto") -> Dict[str, Any]:
        """
        Write an executive-style email based on resume and job analysis
        
        Args:
            resume_data: Parsed resume information
            job_analysis: Analyzed job description
            email_style: Desired email style (auto, executive_formal, startup_casual, etc.)
            
        Returns:
            Dictionary containing the generated email content
        """
        try:
            # Use the tool to generate email content
            tool_result = self.tools[0]._run(resume_data, job_analysis, email_style)
            
            if not tool_result.get("success", False):
                return tool_result
            
            # Use the agent for refinement and optimization
            refinement_prompt = f"""
            Review and optimize the following email content for maximum impact:
            
            Email Content:
            {tool_result.get('email_content', {}).get('full_email', '')}
            
            Please provide:
            1. Suggestions for improving the opening hook
            2. Ways to make the experience highlights more compelling
            3. Recommendations for strengthening the call-to-action
            4. Overall tone and style assessment
            5. Any specific improvements for better engagement
            """
            
            result = self.agent_executor.invoke({
                "input": refinement_prompt,
                "chat_history": []
            })
            
            return {
                "success": True,
                "email_content": tool_result.get("email_content", {}),
                "style_used": tool_result.get("style_used", email_style),
                "refinement_suggestions": result.get("output", ""),
                "message": "Successfully generated and refined email content"
            }
            
        except Exception as e:
            logger.error(f"Error in email writing agent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_email_to_markdown(self, email_data: Dict[str, Any], output_path: str = "output/email.md") -> bool:
        """Save the generated email to a markdown file"""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Create markdown content
            email_content = email_data.get("email_content", {})
            markdown_content = EmailFormatter.create_markdown_email(
                subject=email_content.get("subject", "Job Application"),
                greeting=email_content.get("greeting", "Dear Hiring Manager,"),
                body=email_content.get("body", ""),
                closing=email_content.get("closing", ""),
                signature=email_content.get("signature", ""),
                metadata={
                    "Style": email_data.get("style_used", "unknown"),
                    "Generated": "by AI Job Application Agent"
                }
            )
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Email saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving email to markdown: {e}")
            return False
