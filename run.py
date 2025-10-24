#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run script for Advanced Military Aircraft Tracker Bot
Version 2.0 - Enhanced with Gemini AI Integration
"""

import os
import sys
import signal
import logging
from pathlib import Path

def setup_environment():
    """Setup environment variables and paths"""
    # Add current directory to Python path
    current_dir = Path(__file__).parent.absolute()
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Load environment variables from .env file if it exists
    env_file = current_dir / ".env"
    if env_file.exists():
        print("📄 Loading environment variables from .env file")
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    # Check required modules
    required_modules = [
        "telegram",
        "requests", 
        "aiohttp",
        "pandas",
        "google.generativeai"
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing required modules: {', '.join(missing_modules)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    # Check environment variables
    required_env_vars = [
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHANNEL_ID",
        "GEMINI_API_KEY"
    ]
    
    missing_env_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_env_vars.append(var)
    
    if missing_env_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_env_vars)}")
        print("Please set them in your .env file or environment")
        return False
    
    print("✅ All requirements met")
    return True

def setup_logging():
    """Setup logging configuration"""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE", "military_tracker.log")
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")
    return logger

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\n🛑 Received signal {signum}. Shutting down gracefully...")
    sys.exit(0)

def main():
    """Main function"""
    print("🚁 Advanced Military Aircraft Tracker Bot")
    print("🤖 Version 2.0 - Enhanced with Gemini AI Integration")
    print("=" * 60)
    
    # Setup environment
    setup_environment()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Setup logging
    logger = setup_logging()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Import and run the main bot
        print("🚀 Starting bot...")
        from military_tracker import main as bot_main
        bot_main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()