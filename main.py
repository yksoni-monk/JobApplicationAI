#!/usr/bin/env python3
"""
Main Application for Job Application Multi-Agent System
Orchestrates the entire workflow from resume parsing to email generation
Uses Gemini Pro 2.5 via OpenAI-compatible API
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from typing import Dict, Any

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_google_genai import ChatGoogleGenerativeAI
from agents.orchestrator import OrchestratorAgent
from utils.cache_utils import DocumentCache

# Initialize logger without file handler initially
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def setup_file_logging():
    """Setup file logging after output directory is created"""
    try:
        file_handler = logging.FileHandler('output/app.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.info("File logging initialized")
    except Exception as e:
        logger.warning(f"Could not setup file logging: {e}")

def load_environment():
    """Load environment variables"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check for required environment variables
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            logger.info("Please create a .env file with your Gemini API key")
            return False
        
        logger.info("Environment variables loaded successfully")
        return True
        
    except ImportError:
        logger.warning("python-dotenv not installed, using system environment variables")
        return True
    except Exception as e:
        logger.error(f"Error loading environment: {e}")
        return False

def initialize_llm() -> ChatGoogleGenerativeAI:
    """Initialize the Gemini LLM"""
    try:
        model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-pro')
        temperature = float(os.getenv('GEMINI_TEMPERATURE', '0.7'))
        max_tokens = int(os.getenv('GEMINI_MAX_TOKENS', '4000'))
        
        # Use OpenAI-compatible client for Gemini
        import openai
        
        # Configure OpenAI client to use Gemini
        openai.api_key = os.getenv('GEMINI_API_KEY')
        openai.base_url = os.getenv('GEMINI_BASE_URL', 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent')
        
        # Create LangChain wrapper for Gemini
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            max_output_tokens=max_tokens,
            google_api_key=os.getenv('GEMINI_API_KEY')
        )
        
        logger.info(f"Gemini LLM initialized with model: {model_name}")
        return llm
        
    except Exception as e:
        logger.error(f"Error initializing Gemini LLM: {e}")
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
        logger.info("Initializing Gemini LLM...")
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
        description="Job Application Multi-Agent System (Powered by Gemini Pro 2.5)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py -r YogeshResume.pdf -j JobDescription.txt
  python main.py -r resume.pdf -j job.txt --style startup_casual
  python main.py -r resume.pdf -j job.txt --debug
  python main.py --cache-info
  python main.py --clear-cache
        """
    )
    
    parser.add_argument(
        "-r", "--resume",
        required=False,
        help="Path to the resume PDF file"
    )
    
    parser.add_argument(
        "-j", "--job-description",
        required=False,
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
    
    parser.add_argument(
        "--cache-info",
        action="store_true",
        help="Show information about cached documents"
    )
    
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear all cached documents"
    )
    
    args = parser.parse_args()
    
    try:
        # Print banner
        print("🚀 Job Application Multi-Agent System")
        print("🤖 Powered by Gemini Pro 2.5")
        print("=" * 50)
        
        # Load environment
        if not load_environment():
            print("❌ Failed to load environment variables")
            sys.exit(1)
        
        # Handle cache operations
        if args.cache_info:
            cache = DocumentCache()
            cache_info = cache.get_cache_info()
            print("\n📁 CACHE INFORMATION")
            print("=" * 30)
            print(f"Cache directory: {cache_info['cache_directory']}")
            print(f"Total cached files: {len(cache_info['cached_files'])}")
            print(f"Total cache size: {cache_info['total_size']} bytes")
            
            if cache_info['cached_files']:
                print("\nCached files:")
                for cached_file in cache_info['cached_files']:
                    print(f"  • {cached_file['file']}")
                    print(f"    Original: {cached_file['original_file']}")
                    print(f"    Cached at: {cached_file['cached_at']}")
                    print(f"    Size: {cached_file['size']} bytes")
            else:
                print("\nNo cached files found.")
            sys.exit(0)
        
        if args.clear_cache:
            cache = DocumentCache()
            cache.clear_cache()
            print("\n🗑️  Cache cleared successfully!")
            sys.exit(0)
        
        # Check if resume and job description are provided for workflow execution
        if not args.resume or not args.job_description:
            print("❌ Resume (-r) and job description (-j) are required for workflow execution")
            print("Use --cache-info or --clear-cache for cache operations")
            sys.exit(1)
        
        # Validate input files
        if not validate_input_files(args.resume, args.job_description):
            print("❌ Input file validation failed")
            sys.exit(1)
        
        # Create output directory
        if not create_output_directory():
            print("❌ Failed to create output directory")
            sys.exit(1)
        
        # Setup file logging after output directory is created
        setup_file_logging()
        
        # Run workflow
        print(f"\n📄 Resume: {args.resume}")
        print(f"📋 Job Description: {args.job_description}")
        print(f"🎨 Email Style: {args.style}")
        print(f"🔍 Debug Mode: {'Enabled' if args.debug else 'Disabled'}")
        print("\nStarting workflow with Gemini Pro 2.5...")
        
        result = run_workflow(
            resume_path=args.resume,
            job_description_path=args.job_description,
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
