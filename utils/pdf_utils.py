"""
PDF Utility Functions for Resume Parsing
Handles PDF text extraction and basic structure detection
"""

import pdfplumber
import PyPDF2
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class PDFParser:
    """Handles PDF parsing with fallback methods"""
    
    def __init__(self):
        self.text_content = ""
        self.structured_content = {}
    
    def parse_pdf(self, file_path: str) -> Dict[str, any]:
        """
        Parse PDF file and extract text content
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing parsed content and metadata
        """
        try:
            # Try pdfplumber first (better for structured documents)
            content = self._parse_with_pdfplumber(file_path)
            if content and len(content.strip()) > 100:
                self.text_content = content
                return self._structure_content(content)
            
            # Fallback to PyPDF2
            content = self._parse_with_pypdf2(file_path)
            if content and len(content.strip()) > 100:
                self.text_content = content
                return self._structure_content(content)
            
            raise ValueError("Could not extract meaningful text from PDF")
            
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {e}")
            raise
    
    def _parse_with_pdfplumber(self, file_path: str) -> Optional[str]:
        """Parse PDF using pdfplumber"""
        try:
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text.strip()
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}")
            return None
    
    def _parse_with_pypdf2(self, file_path: str) -> Optional[str]:
        """Parse PDF using PyPDF2 as fallback"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            logger.warning(f"PyPDF2 failed: {e}")
            return None
    
    def _structure_content(self, text: str) -> Dict[str, any]:
        """
        Basic structure detection for resume content
        
        Args:
            text: Raw text content from PDF
            
        Returns:
            Structured dictionary with detected sections
        """
        lines = text.split('\n')
        structured = {
            'raw_text': text,
            'sections': {},
            'skills': [],
            'experience': [],
            'education': [],
            'contact_info': {}
        }
        
        current_section = None
        section_content = []
        
        # Common resume section headers
        section_headers = [
            'experience', 'work experience', 'employment history',
            'education', 'academic background', 'qualifications',
            'skills', 'technical skills', 'competencies',
            'projects', 'achievements', 'summary', 'objective'
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line is a section header
            line_lower = line.lower()
            is_header = any(header in line_lower for header in section_headers)
            
            if is_header:
                # Save previous section
                if current_section and section_content:
                    structured['sections'][current_section] = '\n'.join(section_content)
                
                # Start new section
                current_section = line
                section_content = []
            else:
                if current_section:
                    section_content.append(line)
                else:
                    # Content before first section (likely contact info)
                    if '@' in line or 'phone' in line_lower or 'linkedin' in line_lower:
                        structured['contact_info'][line] = line
        
        # Save last section
        if current_section and section_content:
            structured['sections'][current_section] = '\n'.join(section_content)
        
        return structured
    
    def get_contact_info(self) -> Dict[str, str]:
        """Extract contact information from parsed content"""
        # Basic contact info extraction
        contact_info = {}
        if not self.text_content:
            return contact_info
        
        lines = self.text_content.split('\n')
        for line in lines:
            line = line.strip()
            if '@' in line:  # Email
                contact_info['email'] = line
            elif any(phone_indicator in line.lower() for phone_indicator in ['phone', 'mobile', 'cell']):
                contact_info['phone'] = line
            elif 'linkedin.com' in line.lower():
                contact_info['linkedin'] = line
        
        return contact_info
    
    def get_skills(self) -> List[str]:
        """Extract skills from parsed content"""
        skills = []
        if not self.text_content:
            return skills
        
        # Look for skills section
        for section_name, content in self.structured_content.get('sections', {}).items():
            if 'skill' in section_name.lower():
                # Split by common delimiters
                skill_lines = content.split('\n')
                for line in skill_lines:
                    if line.strip():
                        skills.extend([skill.strip() for skill in line.split(',')])
        
        return [skill for skill in skills if skill and len(skill) > 2]
