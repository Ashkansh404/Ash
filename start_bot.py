#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Military Flight Tracker Bot - Startup Script
Version: 2.0 - Advanced Intelligence System
"""

import sys
import os
import logging
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_requirements():
    """Check if all required packages are installed"""
    required_packages = [
        'telegram',
        'requests',
        'pandas',
        'aiohttp',
        'google.generativeai'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_configuration():
    """Check if configuration is properly set up"""
    try:
        from config import Config
        
        errors = Config.validate_config()
        if errors:
            print("❌ Configuration errors found:")
            for error in errors:
                print(f"   - {error}")
            print("\n🔧 Please fix these errors in config.py")
            return False
        
        print("✅ Configuration is valid")
        return True
        
    except ImportError as e:
        print(f"❌ Error importing configuration: {e}")
        return False

def check_database():
    """Check database setup"""
    try:
        from database import init_database
        init_database()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def main():
    """Main startup function"""
    print("🚀 Military Flight Tracker Bot v2.0 - Advanced Intelligence System")
    print("=" * 70)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Check requirements
    print("\n📦 Checking requirements...")
    if not check_requirements():
        sys.exit(1)
    
    # Check configuration
    print("\n🔧 Checking configuration...")
    if not check_configuration():
        sys.exit(1)
    
    # Check database
    print("\n🗄️ Checking database...")
    if not check_database():
        sys.exit(1)
    
    # All checks passed
    print("\n✅ All checks passed! Starting bot...")
    print("=" * 70)
    
    # Import and run the main bot
    try:
        from military_tracker_bot import main as bot_main
        bot_main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logging.error(f"Fatal error in startup: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()