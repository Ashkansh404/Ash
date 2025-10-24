#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration validation script for Advanced Military Aircraft Tracker Bot
Version 2.0 - Enhanced with Gemini AI Integration
"""

import os
import sys
import requests
import asyncio
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path(".env")
    if env_file.exists():
        print("📄 Loading configuration from .env file")
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()
    else:
        print("⚠️  No .env file found, using environment variables")

def validate_telegram_config():
    """Validate Telegram configuration"""
    print("\n📱 Validating Telegram configuration...")
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    channel_id = os.getenv("TELEGRAM_CHANNEL_ID")
    admin_id = os.getenv("TELEGRAM_ADMIN_ID")
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return False
    
    if not channel_id:
        print("❌ TELEGRAM_CHANNEL_ID not set")
        return False
    
    # Test bot token
    try:
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get("ok"):
                print(f"✅ Bot token valid: @{bot_info['result']['username']}")
            else:
                print("❌ Bot token invalid")
                return False
        else:
            print(f"❌ Bot API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing bot token: {e}")
        return False
    
    print(f"✅ Channel ID: {channel_id}")
    print(f"✅ Admin ID: {admin_id or 'Not set'}")
    return True

def validate_gemini_config():
    """Validate Gemini AI configuration"""
    print("\n🤖 Validating Gemini AI configuration...")
    
    api_keys = []
    for i in range(1, 4):
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key:
            api_keys.append(key)
    
    # Check primary key
    primary_key = os.getenv("GEMINI_API_KEY")
    if primary_key:
        api_keys.insert(0, primary_key)
    
    if not api_keys:
        print("❌ No Gemini API keys found")
        print("Please set GEMINI_API_KEY or GEMINI_API_KEY_1")
        return False
    
    print(f"✅ Found {len(api_keys)} Gemini API key(s)")
    
    # Test API keys
    for i, key in enumerate(api_keys, 1):
        try:
            import google.generativeai as genai
            genai.configure(api_key=key)
            
            # Test with a simple request
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            response = model.generate_content("Test")
            
            if response.text:
                print(f"✅ API key {i} is working")
            else:
                print(f"⚠️  API key {i} returned empty response")
        except Exception as e:
            print(f"❌ API key {i} error: {e}")
            return False
    
    return True

def validate_database_config():
    """Validate database configuration"""
    print("\n🗄️ Validating database configuration...")
    
    try:
        from database import AdvancedDatabaseManager
        
        # Test database creation
        db = AdvancedDatabaseManager("test_validation.db")
        
        # Test basic operations
        success = db.add_spotted_aircraft("test123", "TEST01", "C130", "United States")
        if success:
            print("✅ Database operations working")
            
            # Cleanup test database
            os.remove("test_validation.db")
            return True
        else:
            print("❌ Database operations failed")
            return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def validate_flight_apis():
    """Validate flight tracking APIs"""
    print("\n✈️ Validating flight tracking APIs...")
    
    apis = [
        ("ADSB.lol", "https://api.adsb.lol/v2/mil"),
        ("OpenSky Network", "https://opensky-network.org/api/states/all"),
    ]
    
    working_apis = 0
    for name, url in apis:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name} API is accessible")
                working_apis += 1
            else:
                print(f"⚠️  {name} API returned status {response.status_code}")
        except Exception as e:
            print(f"❌ {name} API error: {e}")
    
    if working_apis == 0:
        print("❌ No flight tracking APIs are accessible")
        return False
    elif working_apis < len(apis):
        print(f"⚠️  Only {working_apis}/{len(apis)} APIs are working")
    else:
        print("✅ All flight tracking APIs are accessible")
    
    return True

def validate_optional_config():
    """Validate optional configuration"""
    print("\n⚙️ Validating optional configuration...")
    
    # Check polling interval
    poll_interval = os.getenv("POLL_INTERVAL", "30")
    try:
        interval = int(poll_interval)
        if interval < 10:
            print("⚠️  Polling interval is very low (< 10 seconds)")
        elif interval > 300:
            print("⚠️  Polling interval is very high (> 5 minutes)")
        else:
            print(f"✅ Polling interval: {interval} seconds")
    except ValueError:
        print("❌ Invalid polling interval format")
        return False
    
    # Check log level
    log_level = os.getenv("LOG_LEVEL", "INFO")
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level.upper() in valid_levels:
        print(f"✅ Log level: {log_level}")
    else:
        print(f"⚠️  Invalid log level: {log_level}")
    
    # Check database file
    db_file = os.getenv("DATABASE_FILE", "military_aircraft.db")
    db_path = Path(db_file)
    if db_path.exists():
        print(f"✅ Database file exists: {db_file}")
    else:
        print(f"ℹ️  Database file will be created: {db_file}")
    
    return True

def main():
    """Main validation function"""
    print("🔍 Advanced Military Aircraft Tracker Bot - Configuration Validation")
    print("=" * 70)
    
    # Load environment
    load_env_file()
    
    # Run validations
    validations = [
        ("Telegram Configuration", validate_telegram_config),
        ("Gemini AI Configuration", validate_gemini_config),
        ("Database Configuration", validate_database_config),
        ("Flight Tracking APIs", validate_flight_apis),
        ("Optional Configuration", validate_optional_config),
    ]
    
    results = []
    for name, validator in validations:
        try:
            result = validator()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} validation failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Validation Summary:")
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} validations passed")
    
    if passed == len(results):
        print("🎉 All validations passed! Bot is ready to run.")
        return True
    else:
        print("⚠️  Some validations failed. Please fix the issues before running the bot.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)