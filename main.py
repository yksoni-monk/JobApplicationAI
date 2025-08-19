#!/usr/bin/env python3
"""
Main Application for Job Application Multi-Agent System
Orchestrates the entire workflow from resume parsing to email generation
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from typing import Dict, Any

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_openai import ChatOpenAI
from agents.orchestrator import OrchestratorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('output/app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check for required environment variables
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            logger.error("OPENAI_API_KEY not found in environment variables")
            logger.info("Please create a .env file with your OpenAI API key")
            return False
        
        logger.info("Environment variables loaded successfully")
        return True
        
    except ImportError:
        logger.warning("python-dotenv not installed, using system environment variables")
        return True
    except Exception as e:
        logger.error(f"Error loading environment: {e}")
        return False

def initialize_llm() -> ChatOpenAI:
    """Initialize the OpenAI LLM"""
    try:
        model_name = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
        max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '4000'))
        
        llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        logger.info(f"LLM initialized with model: {model_name}")
        return llm
        
    except Exception as e:
        logger.error(f"Error initializing LLM: {e}")
        raise

def validate_input_files(resume_path: str, job_description_path: str) -> bool:
    """Validate that input files exist and are accessible"""
    try:
        # Check resume file
        if not os.path.exists(resume_path):
            logger.error(f"Resume file not found: {resume_path}")
            return False
        
        if not resume_path.lower().endswith('.pdf'):
            logger.warning(f"Resume file is not a PDF: {resume_path}")
        
        # Check job description file
        if not os.path.exists(job_description_path):
            logger.error(f"Job description file not found: {job_description_path}")
            return False
        
        if not job_description_path.lower().endswith('.txt'):
            logger.warning(f"Job description file is not a text file: {job_description_path}")
        
        logger.info("Input files validated successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error validating input files: {e}")
        return False

def create_output_directory():
    """Create output directory if it doesn't exist"""
    try:
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Output directory ready: {output_dir}")
        return True
    except Exception as e:
        logger.error(f"Error creating output directory: {e}")
        return False

def run_workflow(resume_path: str, job_description_path: str, 
                email_style: str = "auto", debug: bool = False) -> Dict[str, Any]:
    """
    Run the complete job application workflow
    
    Args:
        resume_path: Path to the resume PDF file
        job_description_path: Path to the job description text file
        email_style: Desired email style (auto, executive_formal, startup_casual, etc.)
        debug: Enable debug mode for verbose logging
        
    Returns:
        Dictionary containing the workflow results
    """
    try:
        # Set debug logging if requested
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.info("Debug mode enabled")
        
        # Initialize LLM
        logger.info("Initializing LLM...")
        llm = initialize_llm()
        
        # Create orchestrator agent
        logger.info("Creating orchestrator agent...")
        orchestrator = OrchestratorAgent(llm)
        
        # Execute workflow
        logger.info("Starting workflow execution...")
        start_time = datetime.now()
        
        result = orchestrator.execute_workflow(
            resume_path=resume_path,
            job_description_path=job_description_path,
            email_style=email_style
        )
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Log results
        if result.get("success", False):
            logger.info(f"Workflow completed successfully in {execution_time:.2f} seconds")
            
            # Log key metrics
            workflow_steps = result.get("workflow_steps", {})
            if "strategic_analysis" in workflow_steps:
                strategic = workflow_steps["strategic_analysis"]
                skill_match = strategic.get("skill_match_score", 0)
                logger.info(f"Skill match score: {skill_match:.2%}")
            
            if "final_summary" in workflow_steps:
                summary = workflow_steps["final_summary"]
                assessment = summary.get("overall_assessment", "Unknown")
                logger.info(f"Overall assessment: {assessment}")
            
        else:
            logger.error(f"Workflow failed: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in workflow execution: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def print_results(result: Dict[str, Any]):
    """Print workflow results in a user-friendly format"""
    print("\n" + "="*80)
    print("JOB APPLICATION WORKFLOW RESULTS")
    print("="*80)
    
    if not result.get("success", False):
        print(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")
        return
    
    # Print success message
    print(f"✅ {result.get('message', 'Workflow completed successfully')}")
    print(f"📧 Email style used: {result.get('email_style_used', 'Unknown')}")
    
    # Print workflow steps
    workflow_steps = result.get("workflow_steps", {})
    
    if "strategic_analysis" in workflow_steps:
        strategic = workflow_steps["strategic_analysis"]
        print(f"\n📊 STRATEGIC ANALYSIS:")
        print(f"   Skill match score: {strategic.get('skill_match_score', 0):.1%}")
        print(f"   Relevant experience: {strategic.get('relevant_experience_count', 0)} sections")
        
        recommendations = strategic.get("strategic_recommendations", [])
        if recommendations:
            print(f"   Key recommendations:")
            for rec in recommendations:
                print(f"     • {rec}")
    
    if "final_summary" in workflow_steps:
        summary = workflow_steps["final_summary"]
        print(f"\n📋 FINAL SUMMARY:")
        print(f"   Assessment: {summary.get('overall_assessment', 'Unknown')}")
        print(f"   Email effectiveness: {summary.get('email_effectiveness', 'Unknown')}")
        
        next_steps = summary.get("next_steps", [])
        if next_steps:
            print(f"   Next steps:")
            for step in next_steps:
                print(f"     • {step}")
    
    # Print file locations
    print(f"\n📁 OUTPUT FILES:")
    print(f"   Email content: output/email.md")
    print(f"   Workflow results: output/workflow_results.json")
    print(f"   Application log: output/app.log")
    
    print("\n" + "="*80)

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="Job Application Multi-Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py YogeshResume.pdf JobDescription.txt
  python main.py resume.pdf job.txt --style startup_casual
  python main.py resume.pdf job.txt --debug
        """
    )
    
    parser.add_argument(
        "resume_path",
        help="Path to the resume PDF file"
    )
    
    parser.add_argument(
        "job_description_path",
        help="Path to the job description text file"
    )
    
    parser.add_argument(
        "--style", "-s",
        choices=["auto", "executive_formal", "startup_casual", "technical_detailed", "leadership_focused"],
        default="auto",
        help="Email style to use (default: auto)"
    )
    
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    try:
        # Print banner
        print("🚀 Job Application Multi-Agent System")
        print("=" * 50)
        
        # Load environment
        if not load_environment():
            print("❌ Failed to load environment variables")
            sys.exit(1)
        
        # Validate input files
        if not validate_input_files(args.resume_path, args.job_description_path):
            print("❌ Input file validation failed")
            sys.exit(1)
        
        # Create output directory
        if not create_output_directory():
            print("❌ Failed to create output directory")
            sys.exit(1)
        
        # Run workflow
        print(f"\n📄 Resume: {args.resume_path}")
        print(f"📋 Job Description: {args.job_description_path}")
        print(f"🎨 Email Style: {args.style}")
        print(f"🔍 Debug Mode: {'Enabled' if args.debug else 'Disabled'}")
        print("\nStarting workflow...")
        
        result = run_workflow(
            resume_path=args.resume_path,
            job_description_path=args.job_description_path,
            email_style=args.style,
            debug=args.debug
        )
        
        # Print results
        print_results(result)
        
        # Exit with appropriate code
        if result.get("success", False):
            print("\n🎉 Workflow completed successfully!")
            sys.exit(0)
        else:
            print("\n💥 Workflow failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        logger.error(f"Unexpected error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
