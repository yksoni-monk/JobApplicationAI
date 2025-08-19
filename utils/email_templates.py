"""
Email Template Utilities for Executive-Style Job Application Emails
Provides templates and formatting functions for professional communication
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class EmailTemplate:
    """Email template structure"""
    subject: str
    greeting: str
    body: str
    closing: str
    signature: str

class EmailTemplateManager:
    """Manages different email templates and styles"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, EmailTemplate]:
        """Initialize different email template styles"""
        return {
            'executive_formal': EmailTemplate(
                subject="Experienced {role} Professional - {company} Opportunity",
                greeting="Dear VP, Edge AI,",
                body="""
I am writing to express my strong interest in the {role} position at {company}. With {years_experience} years of experience in {key_areas}, I believe I can make significant contributions to your team and help drive {company}'s continued success.

{relevant_experience_paragraph}

{technical_achievements_paragraph}

{leadership_impact_paragraph}

I am particularly drawn to {company}'s mission in {industry_focus} and believe my background in {specific_skills} aligns perfectly with your current needs. I would welcome the opportunity to discuss how my experience can contribute to {company}'s growth and innovation.

{call_to_action}
                """,
                closing="I look forward to the possibility of contributing to {company}'s success.",
                signature="Best regards,\n{name}"
            ),
            
            'startup_casual': EmailTemplate(
                subject="Hey {company} team - {role} role looks perfect!",
                greeting="Hi VP, Edge AI,",
                body="""
I came across your {role} opening and got really excited about the opportunity to join {company}! Your work in {industry_focus} is exactly what I've been looking for.

{relevant_experience_paragraph}

{startup_experience_paragraph}

{technical_achievements_paragraph}

What really caught my attention is {company}'s approach to {specific_innovation}. I've been working on similar challenges and would love to bring my experience to help scale your solutions.

{call_to_action}
                """,
                closing="Looking forward to potentially joining the {company} team!",
                signature="Cheers,\n{name}"
            ),
            
            'technical_detailed': EmailTemplate(
                subject="Senior {role} - {key_technology} Expert for {company}",
                greeting="Dear VP, Edge AI,",
                body="""
I am excited to apply for the {role} position at {company}. With deep expertise in {key_technology} and {years_experience} years of experience building scalable systems, I am confident I can contribute significantly to your technical initiatives.

{technical_experience_paragraph}

{project_achievements_paragraph}

{innovation_contributions_paragraph}

{company}'s focus on {specific_technical_area} particularly interests me, as I have extensive experience in {related_technologies}. I would welcome the opportunity to discuss how my technical background can accelerate {company}'s development efforts.

{call_to_action}
                """,
                closing="I look forward to discussing how my technical expertise can benefit {company}.",
                signature="Best regards,\n{name}"
            ),
            
            'leadership_focused': EmailTemplate(
                subject="Strategic {role} Leader - Driving {company} Growth",
                greeting="Dear VP, Edge AI,",
                body="""
I am writing to express my interest in the {role} position at {company}. As a proven leader with {years_experience} years of experience building and scaling teams, I am excited about the opportunity to contribute to {company}'s strategic growth.

{leadership_experience_paragraph}

{team_building_achievements_paragraph}

{strategic_impact_paragraph}

{company}'s mission to {company_mission} resonates strongly with my own values and experience. I believe my background in {leadership_areas} can help {company} achieve its ambitious goals while building a world-class team.

{call_to_action}
                """,
                closing="I look forward to discussing how my leadership experience can contribute to {company}'s success.",
                signature="Best regards,\n{name}"
            )
        }
    
    def get_template(self, style: str) -> EmailTemplate:
        """Get email template by style"""
        return self.templates.get(style, self.templates['executive_formal'])
    
    def format_template(self, template: EmailTemplate, context: Dict[str, str]) -> str:
        """Format template with provided context variables"""
        formatted_email = f"""
Subject: {template.subject.format(**context)}

{template.greeting}

{template.body.format(**context)}

{template.closing}

{template.signature.format(**context)}
        """.strip()
        
        return formatted_email
    
    def generate_subject_line(self, role: str, company: str, style: str = 'executive_formal') -> str:
        """Generate appropriate subject line based on style and context"""
        if style == 'startup_casual':
            return f"Hey {company} team - {role} role looks perfect!"
        elif style == 'technical_detailed':
            return f"Senior {role} - Technical Expert for {company}"
        elif style == 'leadership_focused':
            return f"Strategic {role} Leader - Driving {company} Growth"
        else:
            return f"Experienced {role} Professional - {company} Opportunity"
    
    def get_greeting(self, recipient: str, style: str = 'executive_formal') -> str:
        """Get appropriate greeting based on style"""
        if style == 'startup_casual':
            return f"Hi {recipient},"
        else:
            return f"Dear {recipient},"
    
    def get_closing(self, style: str = 'executive_formal') -> str:
        """Get appropriate closing based on style"""
        if style == 'startup_casual':
            return "Looking forward to potentially joining the team!"
        else:
            return "I look forward to discussing this opportunity further."
    
    def get_signature(self, name: str, style: str = 'executive_formal') -> str:
        """Get appropriate signature based on style"""
        if style == 'startup_casual':
            return f"Cheers,\n{name}"
        else:
            return f"Best regards,\n{name}"

class EmailFormatter:
    """Handles email formatting and structure"""
    
    @staticmethod
    def create_markdown_email(
        subject: str,
        greeting: str,
        body: str,
        closing: str,
        signature: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Create a markdown-formatted email"""
        markdown_email = f"""# {subject}

---

**From:** [Your Email]  
**To:** VP, Edge AI  
**Subject:** {subject}

---

{greeting}

{body}

{closing}

{signature}

---

"""
        
        if metadata:
            markdown_email += "## Email Metadata\n\n"
            for key, value in metadata.items():
                markdown_email += f"**{key}:** {value}\n"
        
        return markdown_email
    
    @staticmethod
    def format_paragraphs(text: str, max_width: int = 80) -> str:
        """Format text into properly sized paragraphs"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= max_width:
                current_line += (" " + word) if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return "\n".join(lines)
