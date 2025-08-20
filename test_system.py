#!/usr/bin/env python3
"""
Test Script for Job Application Multi-Agent System
Tests individual components without requiring OpenAI API or external packages
"""

import os
import sys
import logging

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_file_structure():
    """Test that all required files and directories exist"""
    print("🧪 Testing File Structure...")
    
    required_files = [
        "main.py",
        "requirements.txt",
        "README.md",
        "QUICKSTART.md",
        "agents/__init__.py",
        "agents/orchestrator.py",
        "agents/resume_parser.py",
        "agents/job_analyzer.py",
        "agents/email_writer.py",
        "utils/__init__.py",
        "utils/pdf_utils.py",
        "utils/email_templates.py"
    ]
    
    required_dirs = [
        "agents",
        "utils",
        "output"
    ]
    
    all_good = True
    
    # Check directories
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ Directory exists: {directory}")
        else:
            print(f"❌ Directory missing: {directory}")
            all_good = False
    
    # Check files
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ File exists: {file_path}")
        else:
            print(f"❌ File missing: {file_path}")
            all_good = False
    
    return all_good

def test_python_syntax():
    """Test that Python files have valid syntax"""
    print("\n🧪 Testing Python Syntax...")
    
    python_files = [
        "main.py",
        "agents/orchestrator.py",
        "agents/resume_parser.py",
        "agents/job_analyzer.py",
        "agents/email_writer.py",
        "utils/pdf_utils.py",
        "utils/email_templates.py"
    ]
    
    all_good = True
    
    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic syntax check - try to compile
                compile(content, file_path, 'exec')
                print(f"✅ Syntax OK: {file_path}")
                
            except SyntaxError as e:
                print(f"❌ Syntax error in {file_path}: {e}")
                all_good = False
            except Exception as e:
                print(f"⚠️  Warning reading {file_path}: {e}")
        else:
            print(f"⚠️  File not found: {file_path}")
    
    return all_good

def test_import_structure():
    """Test that import statements are properly structured"""
    print("\n🧪 Testing Import Structure...")
    
    try:
        # Test basic imports without external dependencies
        import importlib.util
        
        # Test agents package
        agents_init_path = "agents/__init__.py"
        if os.path.exists(agents_init_path):
            spec = importlib.util.spec_from_file_location("agents", agents_init_path)
            if spec and spec.loader:
                print("✅ Agents package structure valid")
            else:
                print("❌ Agents package structure invalid")
                return False
        else:
            print("❌ Agents __init__.py not found")
            return False
        
        # Test utils package
        utils_init_path = "utils/__init__.py"
        if os.path.exists(utils_init_path):
            spec = importlib.util.spec_from_file_location("utils", utils_init_path)
            if spec and spec.loader:
                print("✅ Utils package structure valid")
            else:
                print("❌ Utils package structure invalid")
                return False
        else:
            print("❌ Utils __init__.py not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Import structure test failed: {e}")
        return False

def test_configuration_files():
    """Test configuration and documentation files"""
    print("\n🧪 Testing Configuration Files...")
    
    config_files = [
        ("requirements.txt", "Dependencies list"),
        ("env_template.txt", "Environment template"),
        ("README.md", "Documentation"),
        ("QUICKSTART.md", "Quick start guide")
    ]
    
    all_good = True
    
    for file_path, description in config_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if len(content.strip()) > 0:
                    print(f"✅ {description}: {file_path}")
                else:
                    print(f"⚠️  {description} is empty: {file_path}")
                    
            except Exception as e:
                print(f"❌ Error reading {description}: {e}")
                all_good = False
        else:
            print(f"❌ {description} not found: {file_path}")
            all_good = False
    
    return all_good

def main():
    """Run all tests"""
    print("🚀 Job Application Multi-Agent System - Component Tests")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Python Syntax", test_python_syntax),
        ("Import Structure", test_import_structure),
        ("Configuration Files", test_configuration_files)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System structure is ready.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set your OpenAI API key in a .env file")
        print("3. Run: python main.py -r YogeshResume.pdf -j JobDescription.txt")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
