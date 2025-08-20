"""
Resume Parser Agent
Uses LangChain to parse and analyze resume content
Powered by Gemini Pro 2.5
"""

import os
import logging
from typing import Dict, List, Any
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.tools import BaseTool
from langchain_core.messages import AIMessage

from utils.pdf_utils import PDFParser

logger = logging.getLogger(__name__)

class ResumeParserTool(BaseTool):
    """Tool for parsing PDF resumes"""
    
    name: str = "parse_resume_pdf"
    description: str = "Parse a PDF resume file and extract structured information"
    
    def __init__(self, pdf_parser: PDFParser):
        super().__init__()
        self._pdf_parser = pdf_parser
    
    def _run(self, file_path: str) -> Dict[str, Any]:
        """Parse the PDF resume"""
        try:
            if not os.path.exists(file_path):
                return {"error": f"File not found: {file_path}"}
            
            parsed_content = self._pdf_parser.parse_pdf(file_path)
            return {
                "success": True,
                "content": parsed_content,
                "message": f"Successfully parsed resume from {file_path}"
            }
        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            return {"error": f"Failed to parse resume: {str(e)}"}

class ResumeParserAgent:
    """LangChain-based agent for parsing and analyzing resumes"""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.pdf_parser = PDFParser()
        self.tools = [ResumeParserTool(self.pdf_parser)]
        self.agent = self._create_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def _create_agent(self):
        """Create the LangChain agent"""
        system_prompt = """You are a Resume Parser Agent specialized in extracting and analyzing resume information, powered by Gemini Pro 2.5.

Your responsibilities:
1. Parse PDF resumes and extract structured information
2. Identify key sections: experience, skills, education, contact info
3. Analyze the relevance of experience to job requirements
4. Provide insights about the candidate's background

Always be thorough and accurate in your analysis. If you encounter any issues, report them clearly."""

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
    
    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a resume and return structured information
        
        Args:
            file_path: Path to the PDF resume file
            
        Returns:
            Dictionary containing parsed resume information and analysis
        """
        try:
            # First, parse the PDF to get raw content
            raw_content = self.pdf_parser.parse_pdf(file_path)
            
            # Use the agent to analyze the content
            analysis_prompt = f"""
            Analyze the following resume content and provide insights:
            
            Resume Content:
            {raw_content.get('raw_text', '')[:2000]}...
            
            Please provide:
            1. Key skills and technologies
            2. Relevant work experience
            3. Education and certifications
            4. Contact information
            5. Overall assessment of the candidate's background
            """
            
            result = self.agent_executor.invoke({
                "input": analysis_prompt,
                "chat_history": []
            })
            
            return {
                "success": True,
                "raw_content": raw_content,
                "analysis": result.get("output", ""),
                "file_path": file_path
            }
            
        except Exception as e:
            logger.error(f"Error in resume parsing agent: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    def extract_key_skills(self, parsed_content: Dict[str, Any]) -> List[str]:
        """Extract key skills from parsed resume content"""
        try:
            # Get skills from structured content
            skills = parsed_content.get('raw_content', {}).get('skills', [])
            
            # Also try to extract from analysis text
            analysis_text = parsed_content.get('analysis', '')
            if analysis_text:
                # Look for skills mentioned in the analysis
                skill_indicators = ['skills:', 'technologies:', 'expertise:', 'proficient in']
                for indicator in skill_indicators:
                    if indicator in analysis_text.lower():
                        # Extract skills after the indicator
                        start_idx = analysis_text.lower().find(indicator)
                        if start_idx != -1:
                            skills_text = analysis_text[start_idx:start_idx + 500]
                            # Simple extraction - look for capitalized words that might be skills
                            import re
                            potential_skills = re.findall(r'\b[A-Z][a-zA-Z0-9\s&+]*\b', skills_text)
                            skills.extend([skill.strip() for skill in potential_skills if len(skill.strip()) > 2])
            
            return list(set(skills))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error extracting skills: {e}")
            return []
    
    def extract_experience(self, parsed_content: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract work experience from parsed resume content"""
        try:
            experience = []
            raw_content = parsed_content.get('raw_content', {})
            
            # Look for experience sections
            for section_name, content in raw_content.get('sections', {}).items():
                if any(keyword in section_name.lower() for keyword in ['experience', 'work', 'employment']):
                    # Parse experience content
                    lines = content.split('\n')
                    current_role = {}
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Look for company names (usually in caps or followed by dates)
                        if any(indicator in line for indicator in ['Inc', 'Corp', 'LLC', 'Ltd', 'Company']):
                            if current_role:
                                experience.append(current_role)
                            current_role = {'company': line}
                        elif line and current_role and 'company' in current_role:
                            if not 'role' in current_role:
                                current_role['role'] = line
                            elif not 'duration' in current_role:
                                current_role['duration'] = line
            
            if current_role:
                experience.append(current_role)
            
            return experience
            
        except Exception as e:
            logger.error(f"Error extracting experience: {e}")
            return []
    
    def get_contact_info(self, parsed_content: Dict[str, Any]) -> Dict[str, str]:
        """Extract contact information from parsed resume"""
        try:
            raw_content = parsed_content.get('raw_content', {})
            return raw_content.get('contact_info', {})
        except Exception as e:
            logger.error(f"Error extracting contact info: {e}")
            return {}
