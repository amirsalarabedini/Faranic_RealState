#!/usr/bin/env python3
"""
RISA Setup Script
Helps configure the Real Estate Intelligence System
"""

import os
import sys
import shutil
from pathlib import Path


def create_env_file():
    """Create .env file from template"""
    env_template = """
# RISA Configuration
# Copy this file to .env and fill in your API keys

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini Configuration  
GOOGLE_API_KEY=your_google_api_key_here

# Default LLM Provider (openai or gemini)
DEFAULT_LLM_PROVIDER=openai

# Default Model
DEFAULT_OPENAI_MODEL=gpt-4
DEFAULT_GEMINI_MODEL=gemini-pro

# LangSmith (Optional - for tracing)
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=your_langsmith_api_key_here

# Logging Level
LOG_LEVEL=INFO

# Data Processing
MAX_FILE_SIZE_MB=100
SUPPORTED_FILE_TYPES=pdf,txt,csv,json
"""
    
    env_file = Path(".env.example")
    
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_template.strip())
        print(f"✅ Created {env_file}")
    else:
        print(f"ℹ️  {env_file} already exists")
    
    # Check if .env exists
    actual_env = Path(".env")
    if not actual_env.exists():
        print(f"⚠️  Please copy {env_file} to .env and add your API keys")


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'langchain',
        'langgraph', 
        'langsmith',
        'openai',
        'google-generativeai',
        'python-dotenv',
        'pandas',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        print("✅ All required packages are installed")
        return True


def create_directories():
    """Create necessary directories"""
    directories = [
        "data/raw",
        "data/processed", 
        "data/external",
        "output/reports",
        "output/visualizations",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")


def test_configuration():
    """Test the configuration"""
    print("\n🧪 Testing configuration...")
    
    try:
        # Add src to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        
        from src.config.llm_config import get_current_config
        
        config = get_current_config()
        print(f"✅ Configuration loaded: {config['provider']} - {config['model']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def main():
    """Main setup function"""
    print("🏠 RISA Setup Script")
    print("=" * 30)
    
    # Change to project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    print(f"📁 Working in: {project_root.absolute()}")
    
    # Setup steps
    print("\n1️⃣ Creating environment configuration...")
    create_env_file()
    
    print("\n2️⃣ Checking dependencies...")
    deps_ok = check_dependencies()
    
    print("\n3️⃣ Creating directories...")
    create_directories()
    
    print("\n4️⃣ Testing configuration...")
    config_ok = test_configuration()
    
    # Summary
    print("\n" + "=" * 30)
    print("📋 Setup Summary")
    print("=" * 30)
    
    if deps_ok and config_ok:
        print("✅ Setup completed successfully!")
        print("\n🚀 You can now run RISA with:")
        print("   python main.py")
        print("   python main.py --example")
        print("   python examples/basic_usage.py")
    else:
        print("⚠️  Setup completed with issues")
        print("Please resolve the issues above before running RISA")
    
    print("\n📚 For more information, see README.md")


if __name__ == "__main__":
    main() 