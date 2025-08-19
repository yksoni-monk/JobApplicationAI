"""
Job Analyzer Agent
Uses LangChain to analyze job descriptions and extract key requirements
"""

import logging
import re
from typing import Dict, List, Any, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool
from langchain_core.messages import AIMessage

logger = logging.getLogger(__name__)

class JobDescriptionTool(BaseTool):
    """Tool for analyzing job description text"""
    
    name = "analyze_job_description"
    description = "Analyze job description text and extract key requirements, responsibilities, and company information"
    
    def _run(self, job_description: str) -> Dict[str, Any]:
        """Analyze the job description text"""
        try:
            if not job_description or len(job_description.strip()) < 50:
                return {"error": "Job description is too short or empty"}
            
            # Basic text analysis
            analysis = self._basic_analysis(job_description)
            
            return {
                "success": True,
                "analysis": analysis,
                "message": "Successfully analyzed job description"
            }
        except Exception as e:
            logger.error(f"Error analyzing job description: {e}")
            return {"error": f"Failed to analyze job description: {str(e)}"}
    
    def _basic_analysis(self, text: str) -> Dict[str, Any]:
        """Perform basic text analysis on job description"""
        text_lower = text.lower()
        
        # Extract company information
        company_info = self._extract_company_info(text)
        
        # Extract job requirements
        requirements = self._extract_requirements(text)
        
        # Extract responsibilities
        responsibilities = self._extract_responsibilities(text)
        
        # Determine company size and stage
        company_size = self._determine_company_size(text)
        company_stage = self._determine_company_stage(text)
        
        # Extract industry focus
        industry_focus = self._extract_industry_focus(text)
        
        return {
            "company_info": company_info,
            "requirements": requirements,
            "responsibilities": responsibilities,
            "company_size": company_size,
            "company_stage": company_stage,
            "industry_focus": industry_focus,
            "text_length": len(text),
            "key_phrases": self._extract_key_phrases(text)
        }
    
    def _extract_company_info(self, text: str) -> Dict[str, str]:
        """Extract company name and basic information"""
        company_info = {}
        
        # Look for company name patterns
        company_patterns = [
            r'at\s+([A-Z][a-zA-Z\s&]+(?:Inc|Corp|LLC|Ltd|Company|Technologies|Systems))',
            r'([A-Z][a-zA-Z\s&]+(?:Inc|Corp|LLC|Ltd|Company|Technologies|Systems))',
            r'company:\s*([A-Z][a-zA-Z\s&]+)',
            r'organization:\s*([A-Z][a-zA-Z\s&]+)'
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                company_info['name'] = match.group(1).strip()
                break
        
        # Look for location
        location_patterns = [
            r'location:\s*([A-Z][a-zA-Z\s,]+)',
            r'in\s+([A-Z][a-zA-Z\s,]+(?:CA|NY|TX|WA|MA|CA))',
            r'based\s+in\s+([A-Z][a-zA-Z\s,]+)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                company_info['location'] = match.group(1).strip()
                break
        
        return company_info
    
    def _extract_requirements(self, text: str) -> Dict[str, List[str]]:
        """Extract job requirements and qualifications"""
        requirements = {
            'technical_skills': [],
            'experience_level': [],
            'education': [],
            'soft_skills': []
        }
        
        text_lower = text.lower()
        
        # Technical skills
        tech_skills = [
            'python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust', 'scala',
            'machine learning', 'ai', 'artificial intelligence', 'deep learning',
            'data science', 'analytics', 'sql', 'nosql', 'mongodb', 'postgresql',
            'aws', 'azure', 'gcp', 'cloud', 'docker', 'kubernetes', 'microservices',
            'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy'
        ]
        
        for skill in tech_skills:
            if skill in text_lower:
                requirements['technical_skills'].append(skill)
        
        # Experience level
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*of\s*experience',
            r'(\d+)\+?\s*years?\s*in\s*[a-zA-Z\s]+',
            r'senior\s+level',
            r'entry\s+level',
            r'junior',
            r'mid\s+level',
            r'lead',
            r'principal'
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text_lower)
            requirements['experience_level'].extend(matches)
        
        # Education
        education_patterns = [
            r'bs\s+in\s+[a-zA-Z\s]+',
            r'ms\s+in\s+[a-zA-Z\s]+',
            r'phd\s+in\s+[a-zA-Z\s]+',
            r'bachelor[^s]*s?\s+degree',
            r'master[^s]*s?\s+degree',
            r'doctorate'
        ]
        
        for pattern in education_patterns:
            matches = re.findall(pattern, text_lower)
            requirements['education'].extend(matches)
        
        # Soft skills
        soft_skills = [
            'leadership', 'communication', 'teamwork', 'problem solving',
            'analytical thinking', 'creativity', 'adaptability', 'time management',
            'project management', 'collaboration', 'mentoring', 'strategic thinking'
        ]
        
        for skill in soft_skills:
            if skill in text_lower:
                requirements['soft_skills'].append(skill)
        
        return requirements
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract job responsibilities and duties"""
        responsibilities = []
        
        # Look for responsibility indicators
        responsibility_patterns = [
            r'responsible\s+for\s+([^.]*)',
            r'will\s+([^.]*)',
            r'must\s+([^.]*)',
            r'expected\s+to\s+([^.]*)',
            r'primary\s+duties\s+include\s+([^.]*)'
        ]
        
        for pattern in responsibility_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            responsibilities.extend([match.strip() for match in matches])
        
        return responsibilities
    
    def _determine_company_size(self, text: str) -> str:
        """Determine company size based on job description"""
        text_lower = text.lower()
        
        if any(phrase in text_lower for phrase in ['startup', 'early stage', 'seed', 'series a']):
            return 'startup'
        elif any(phrase in text_lower for phrase in ['fortune 500', 'enterprise', 'large corporation']):
            return 'enterprise'
        elif any(phrase in text_lower for phrase in ['mid-size', 'medium-sized', 'growing company']):
            return 'mid-size'
        else:
            return 'unknown'
    
    def _determine_company_stage(self, text: str) -> str:
        """Determine company growth stage"""
        text_lower = text.lower()
        
        if any(phrase in text_lower for phrase in ['startup', 'early stage', 'seed funding']):
            return 'early-stage'
        elif any(phrase in text_lower for phrase in ['growth stage', 'scaling', 'series b', 'series c']):
            return 'growth-stage'
        elif any(phrase in text_lower for phrase in ['established', 'mature', 'stable']):
            return 'mature'
        else:
            return 'unknown'
    
    def _extract_industry_focus(self, text: str) -> List[str]:
        """Extract industry focus areas"""
        industries = [
            'healthcare', 'finance', 'e-commerce', 'education', 'automotive',
            'aerospace', 'defense', 'energy', 'telecommunications', 'media',
            'entertainment', 'real estate', 'transportation', 'logistics',
            'manufacturing', 'retail', 'consulting', 'non-profit'
        ]
        
        found_industries = []
        text_lower = text.lower()
        
        for industry in industries:
            if industry in text_lower:
                found_industries.append(industry)
        
        return found_industries
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases and buzzwords"""
        key_phrases = []
        
        # Common job description buzzwords
        buzzwords = [
            'fast-paced environment', 'dynamic team', 'innovative solutions',
            'cutting-edge technology', 'collaborative culture', 'growth mindset',
            'results-driven', 'customer-focused', 'data-driven', 'agile',
            'scalable', 'high-performance', 'mission-critical', 'end-to-end'
        ]
        
        text_lower = text.lower()
        for phrase in buzzwords:
            if phrase in text_lower:
                key_phrases.append(phrase)
        
        return key_phrases

class JobAnalyzerAgent:
    """LangChain-based agent for analyzing job descriptions"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.tools = [JobDescriptionTool()]
        self.agent = self._create_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def _create_agent(self):
        """Create the LangChain agent"""
        system_prompt = """You are a Job Description Analyzer Agent specialized in understanding job requirements and company information.

Your responsibilities:
1. Analyze job descriptions to extract key requirements
2. Identify technical skills, experience levels, and qualifications
3. Determine company size, stage, and industry focus
4. Extract job responsibilities and expectations
5. Provide insights about the role and company culture

Always be thorough and accurate in your analysis. Focus on actionable insights that can help with job applications."""

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
    
    def analyze_job(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze a job description and return structured information
        
        Args:
            job_description: Text content of the job description
            
        Returns:
            Dictionary containing analyzed job information
        """
        try:
            # Use the tool to get basic analysis
            tool_result = self.tools[0]._run(job_description)
            
            if not tool_result.get("success", False):
                return tool_result
            
            # Use the agent for deeper analysis
            analysis_prompt = f"""
            Analyze the following job description and provide comprehensive insights:
            
            Job Description:
            {job_description[:3000]}...
            
            Based on the basic analysis, please provide:
            1. Key technical requirements and skills needed
            2. Experience level and qualifications
            3. Company culture and work environment insights
            4. Growth opportunities and challenges
            5. How this role fits into the company's mission
            6. Recommendations for highlighting relevant experience
            """
            
            result = self.agent_executor.invoke({
                "input": analysis_prompt,
                "chat_history": []
            })
            
            return {
                "success": True,
                "basic_analysis": tool_result.get("analysis", {}),
                "detailed_analysis": result.get("output", ""),
                "job_description_length": len(job_description)
            }
            
        except Exception as e:
            logger.error(f"Error in job analysis agent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_requirements_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract a summary of key requirements from the analysis"""
        try:
            basic_analysis = analysis.get("basic_analysis", {})
            requirements = basic_analysis.get("requirements", {})
            
            return {
                "technical_skills": requirements.get("technical_skills", []),
                "experience_level": requirements.get("experience_level", []),
                "education": requirements.get("education", []),
                "soft_skills": requirements.get("soft_skills", []),
                "company_size": basic_analysis.get("company_size", "unknown"),
                "company_stage": basic_analysis.get("company_stage", "unknown"),
                "industry_focus": basic_analysis.get("industry_focus", [])
            }
        except Exception as e:
            logger.error(f"Error extracting requirements summary: {e}")
            return {}
