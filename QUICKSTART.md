# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Set Up Environment
```bash
# Navigate to the project directory
cd AnalogDevicesApp

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure OpenAI API
```bash
# Copy environment template
cp env_template.txt .env

# Edit .env file with your OpenAI API key
# OPENAI_API_KEY=your_actual_api_key_here
```

### 3. Test the System
```bash
# Run component tests (no API calls)
python test_system.py

# You should see: "🎉 All tests passed! System is ready for use."
```

### 4. Run the Full Workflow
```bash
# Execute the complete job application workflow
python main.py YogeshResume.pdf JobDescription.txt

# Or with custom email style
python main.py YogeshResume.pdf JobDescription.txt --style startup_casual

# Enable debug mode for detailed logging
python main.py YogeshResume.pdf JobDescription.txt --debug
```

## 📁 What You'll Get

After running the workflow, you'll find:

- **`output/email.md`** - Your generated executive-style email
- **`output/workflow_results.json`** - Complete analysis and results
- **`output/app.log`** - Detailed execution log

## 🎯 Available Email Styles

- **`auto`** - Automatically determined based on company analysis
- **`executive_formal`** - Professional, corporate style
- **`startup_casual`** - Friendly, startup-focused style
- **`technical_detailed`** - Technical expertise emphasis
- **`leadership_focused`** - Leadership and management focus

## 🔧 Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY not found"**
   - Create a `.env` file with your API key
   - Ensure the file is in the project root

2. **"Module not found" errors**
   - Install dependencies: `pip install -r requirements.txt`
   - Activate virtual environment if using one

3. **PDF parsing issues**
   - Ensure your resume is text-based (not image-based)
   - Check file permissions

4. **API rate limits**
   - Check your OpenAI usage and billing
   - Consider using a different model in `.env`

### Debug Mode
```bash
# Enable detailed logging
python main.py resume.pdf job.txt --debug

# Check logs
tail -f output/app.log
```

## 📊 Understanding the Output

### Strategic Analysis
- **Skill Match Score**: How well your skills align with job requirements
- **Relevant Experience**: Number of experience sections matching job needs
- **Company Characteristics**: Size, stage, and industry focus

### Email Assessment
- **Overall Assessment**: Application strength evaluation
- **Key Highlights**: Strategic recommendations for your application
- **Next Steps**: Actionable advice for improvement

## 🚀 Advanced Usage

### Custom Email Styles
```python
# In your own scripts
from agents.email_writer import EmailWriterAgent
from agents.orchestrator import OrchestratorAgent

# Create custom orchestrator
orchestrator = OrchestratorAgent(llm)
result = orchestrator.execute_workflow(
    resume_path="path/to/resume.pdf",
    job_description_path="path/to/job.txt",
    email_style="custom_style"
)
```

### Batch Processing
```bash
# Process multiple job applications
for job_file in jobs/*.txt; do
    python main.py resume.pdf "$job_file" --style auto
done
```

## 📞 Need Help?

1. **Check the logs**: `output/app.log`
2. **Run tests**: `python test_system.py`
3. **Review README.md** for detailed architecture
4. **Check requirements.txt** for dependency versions

---

**Happy Job Hunting! 🎯**
