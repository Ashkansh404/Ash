#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for Advanced Military Aircraft Tracker Bot
Version 2.0 - Enhanced with Gemini AI Integration
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def create_env_file():
    """Create .env file template"""
    env_content = """# Advanced Military Aircraft Tracker Bot Configuration
# Copy this file to .env and fill in your values

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=your_channel_id_here
TELEGRAM_ADMIN_ID=7717672777

# Gemini AI Configuration (Multiple keys for redundancy)
GEMINI_API_KEY=your_primary_gemini_api_key_here
GEMINI_API_KEY_2=your_secondary_gemini_api_key_here
GEMINI_API_KEY_3=your_tertiary_gemini_api_key_here

# Optional Configuration
POLL_INTERVAL=30
LOG_LEVEL=INFO
DATABASE_FILE=military_aircraft.db
ENVIRONMENT=production
"""
    
    env_file = Path(".env.template")
    if not env_file.exists():
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(env_content)
        print("✅ Created .env.template file")
        print("📝 Please copy .env.template to .env and fill in your values")
    else:
        print("✅ .env.template already exists")

def create_directories():
    """Create necessary directories"""
    directories = ["logs", "backups", "data"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Created necessary directories")

def check_dependencies():
    """Check if all dependencies are available"""
    required_packages = [
        "telegram",
        "requests",
        "aiohttp",
        "pandas",
        "google.generativeai"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        return False
    
    print("✅ All dependencies are available")
    return True

def test_database():
    """Test database functionality"""
    print("🗄️ Testing database functionality...")
    try:
        from database import AdvancedDatabaseManager
        db = AdvancedDatabaseManager("test.db")
        
        # Test basic operations
        success = db.add_spotted_aircraft("test123", "TEST01", "C130", "United States")
        if success:
            print("✅ Database test successful")
            # Cleanup test database
            os.remove("test.db")
            return True
        else:
            print("❌ Database test failed")
            return False
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return False

def main():
    """Main setup function"""
    print("🚁 Advanced Military Aircraft Tracker Bot Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Some dependencies are missing. Please install them manually.")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create env file template
    create_env_file()
    
    # Test database
    if not test_database():
        print("❌ Database test failed. Please check your system.")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Copy .env.template to .env")
    print("2. Fill in your API keys and configuration")
    print("3. Run: python military_tracker.py")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()