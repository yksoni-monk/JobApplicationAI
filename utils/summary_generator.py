"""
Summary Generator for Resume and Job Description Analysis
Creates targeted summaries that highlight relevant experience and value propositions
"""

import logging
from typing import Dict, List, Any, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)

class SummaryGenerator:
    """Generates targeted summaries for resume and job description matching"""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
    
    def generate_resume_summary(self, resume_content: Dict[str, Any], job_requirements: str) -> str:
        """
        Generate a targeted resume summary that highlights relevant experience
        
        Args:
            resume_content: Parsed resume content
            job_requirements: Job requirements text
            
        Returns:
            Targeted summary highlighting relevant experience
        """
        try:
            # Extract key information from resume
            raw_text = resume_content.get("raw_text", "")
            analysis = resume_content.get("analysis", "")
            
            # Create a focused summary prompt
            summary_prompt = f"""
            Based on the following resume content and job requirements, create a targeted summary that:
            1. Highlights the 3-4 most relevant experiences for this specific role
            2. Emphasizes skills that directly match the job requirements
            3. Shows quantifiable achievements that demonstrate value
            4. Focuses on experience that would be most valuable to this position
            
            Resume Content:
            {raw_text[:1500]}...
            
            Resume Analysis:
            {analysis[:1000]}...
            
            Job Requirements:
            {job_requirements[:1000]}...
            
            Please provide a concise summary (150-200 words) that connects the candidate's experience to this specific role.
            Focus on concrete achievements and relevant skills.
            """
            
            # Generate summary using LLM
            response = self.llm.invoke(summary_prompt)
            summary = response.content if hasattr(response, 'content') else str(response)
            
            logger.info("Resume summary generated successfully")
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error generating resume summary: {e}")
            return self._fallback_resume_summary(resume_content)
    
    def generate_job_summary(self, job_description: str) -> str:
        """
        Generate a focused summary of job requirements and key responsibilities
        
        Args:
            job_description: Raw job description text
            
        Returns:
            Focused summary of key requirements and responsibilities
        """
        try:
            summary_prompt = f"""
            Based on the following job description, create a focused summary that highlights:
            1. The 3-4 most critical technical skills required
            2. Key responsibilities that define the role
            3. Experience level and qualifications needed
            4. What success looks like in this position
            
            Job Description:
            {job_description[:1500]}...
            
            Please provide a concise summary (150-200 words) focusing on the most important requirements and expectations.
            """
            
            # Generate summary using LLM
            response = self.llm.invoke(summary_prompt)
            summary = response.content if hasattr(response, 'content') else str(response)
            
            logger.info("Job description summary generated successfully")
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error generating job summary: {e}")
            return self._fallback_job_summary(job_description)
    
    def generate_value_proposition(self, resume_summary: str, job_summary: str) -> str:
        """
        Generate a specific value proposition showing how the candidate adds value
        
        Args:
            resume_summary: Targeted resume summary
            job_summary: Focused job requirements summary
            
        Returns:
            Specific value proposition (2-3 sentences)
        """
        try:
            value_prompt = f"""
            Based on the candidate's experience and the job requirements, write 2-3 specific sentences that:
            1. Show exactly how the candidate's experience addresses the job's key needs
            2. Provide concrete examples of value they can bring
            3. Connect their achievements to the role's success metrics
            
            Candidate's Relevant Experience:
            {resume_summary}
            
            Job Requirements:
            {job_summary}
            
            Write 2-3 sentences that specifically show how this candidate's experience translates to value in this role.
            Be specific and concrete, not generic.
            """
            
            # Generate value proposition using LLM
            response = self.llm.invoke(value_prompt)
            value_prop = response.content if hasattr(response, 'content') else str(response)
            
            logger.info("Value proposition generated successfully")
            return value_prop.strip()
            
        except Exception as e:
            logger.error(f"Error generating value proposition: {e}")
            return self._fallback_value_proposition()
    
    def _fallback_resume_summary(self, resume_content: Dict[str, Any]) -> str:
        """Fallback resume summary when LLM generation fails"""
        try:
            raw_text = resume_content.get("raw_text", "")
            lines = raw_text.split('\n')[:10]  # First 10 lines
            return f"Experienced professional with background in technology and business. Key areas include: {', '.join(lines[:3])}"
        except Exception:
            return "Experienced professional with relevant background in technology and business."
    
    def _fallback_job_summary(self, job_description: str) -> str:
        """Fallback job summary when LLM generation fails"""
        try:
            lines = job_description.split('\n')[:5]  # First 5 lines
            return f"Role requiring technical expertise and business acumen. Key focus areas: {', '.join(lines[:2])}"
        except Exception:
            return "Technical role requiring relevant experience and skills."
    
    def _fallback_value_proposition(self) -> str:
        """Fallback value proposition when LLM generation fails"""
        return "My experience in technology and business leadership directly aligns with your needs. I can bring proven results and strategic thinking to help achieve your goals."
