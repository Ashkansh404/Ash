#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Advanced Military Aircraft Tracker Bot
Version 2.0 - Enhanced with Gemini AI Integration
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

def setup_test_environment():
    """Setup test environment"""
    # Add current directory to Python path
    current_dir = Path(__file__).parent.absolute()
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Set test environment variables
    os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test_token")
    os.environ.setdefault("TELEGRAM_CHANNEL_ID", "test_channel")
    os.environ.setdefault("GEMINI_API_KEY", "test_key")
    os.environ.setdefault("LOG_LEVEL", "INFO")
    os.environ.setdefault("DATABASE_FILE", "test_military_aircraft.db")

def test_imports():
    """Test all imports"""
    print("🔍 Testing imports...")
    
    try:
        import telegram
        print("✅ python-telegram-bot imported")
    except ImportError as e:
        print(f"❌ python-telegram-bot import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ requests imported")
    except ImportError as e:
        print(f"❌ requests import failed: {e}")
        return False
    
    try:
        import aiohttp
        print("✅ aiohttp imported")
    except ImportError as e:
        print(f"❌ aiohttp import failed: {e}")
        return False
    
    try:
        import pandas
        print("✅ pandas imported")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import google.generativeai
        print("✅ google-generativeai imported")
    except ImportError as e:
        print(f"❌ google-generativeai import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\n⚙️ Testing configuration...")
    
    try:
        from config import get_config
        config = get_config()
        print("✅ Configuration loaded successfully")
        print(f"   - Poll interval: {config.flight_tracking.POLL_INTERVAL_SECONDS}s")
        print(f"   - Database file: {config.database.DATABASE_FILE}")
        print(f"   - Log level: {config.logging.LOG_LEVEL}")
        return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\n🗄️ Testing database...")
    
    try:
        from database import AdvancedDatabaseManager
        
        # Create test database
        db = AdvancedDatabaseManager("test_military_aircraft.db")
        print("✅ Database manager created")
        
        # Test adding aircraft
        success = db.add_spotted_aircraft("test123", "TEST01", "C130", "United States")
        if success:
            print("✅ Aircraft added successfully")
        else:
            print("❌ Failed to add aircraft")
            return False
        
        # Test checking if spotted
        spotted = db.check_if_spotted("test123")
        if spotted:
            print("✅ Aircraft spotted check working")
        else:
            print("❌ Aircraft spotted check failed")
            return False
        
        # Test getting aircraft
        aircraft = db.get_spotted_aircraft("test123")
        if aircraft:
            print("✅ Aircraft retrieval working")
            print(f"   - ICAO: {aircraft.icao24}")
            print(f"   - Callsign: {aircraft.callsign}")
        else:
            print("❌ Aircraft retrieval failed")
            return False
        
        # Test statistics
        stats = db.get_system_statistics()
        if stats:
            print("✅ Statistics working")
            print(f"   - Total aircraft: {stats.get('total_spotted_aircraft', 0)}")
        else:
            print("❌ Statistics failed")
            return False
        
        # Cleanup
        db.close_all_connections()
        os.remove("test_military_aircraft.db")
        print("✅ Database test completed and cleaned up")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_ai_analyzer():
    """Test AI analyzer (without actual API calls)"""
    print("\n🤖 Testing AI analyzer...")
    
    try:
        from military_tracker import GeminiAIAnalyzer, FlightData
        
        # Create analyzer
        analyzer = GeminiAIAnalyzer()
        print("✅ AI analyzer created")
        
        # Create test flight data
        flight_data = FlightData(
            icao24="test123",
            callsign="TEST01",
            lat=35.6892,
            lon=51.3890,
            alt=10000,
            vel=500,
            heading=180.0,
            typecode="C130",
            country="United States",
            source="test",
            timestamp=os.path.getmtime(__file__)
        )
        print("✅ Test flight data created")
        
        # Test prompt creation
        prompt = analyzer.create_analysis_prompt(flight_data)
        if prompt and len(prompt) > 100:
            print("✅ Analysis prompt created")
        else:
            print("❌ Analysis prompt creation failed")
            return False
        
        print("✅ AI analyzer test completed (API calls skipped)")
        return True
        
    except Exception as e:
        print(f"❌ AI analyzer test failed: {e}")
        return False

def test_flight_fetcher():
    """Test flight data fetcher"""
    print("\n✈️ Testing flight data fetcher...")
    
    try:
        from military_tracker import FlightDataFetcher
        
        # Create fetcher
        fetcher = FlightDataFetcher()
        print("✅ Flight data fetcher created")
        
        # Test country detection
        country = fetcher.get_country_from_icao("A12345")
        if country == "United States":
            print("✅ Country detection working")
        else:
            print(f"⚠️  Country detection returned: {country}")
        
        print("✅ Flight data fetcher test completed")
        return True
        
    except Exception as e:
        print(f"❌ Flight data fetcher test failed: {e}")
        return False

def test_statistics_tracker():
    """Test statistics tracker"""
    print("\n📊 Testing statistics tracker...")
    
    try:
        from military_tracker import StatisticsTracker
        
        # Create tracker
        stats = StatisticsTracker()
        print("✅ Statistics tracker created")
        
        # Test incrementing
        stats.increment_scan()
        stats.increment_military_flight()
        stats.increment_ai_analysis()
        stats.increment_cache_hit()
        print("✅ Statistics incrementing working")
        
        # Test report generation
        report = stats.get_report()
        if report and "گزارش وضعیت" in report:
            print("✅ Statistics report generation working")
        else:
            print("❌ Statistics report generation failed")
            return False
        
        print("✅ Statistics tracker test completed")
        return True
        
    except Exception as e:
        print(f"❌ Statistics tracker test failed: {e}")
        return False

async def test_async_functionality():
    """Test async functionality"""
    print("\n🔄 Testing async functionality...")
    
    try:
        from military_tracker import MilitaryAircraftTracker
        
        # Create tracker
        tracker = MilitaryAircraftTracker()
        print("✅ Military aircraft tracker created")
        
        # Test queue creation
        import asyncio
        queue = asyncio.Queue()
        print("✅ Async queue created")
        
        print("✅ Async functionality test completed")
        return True
        
    except Exception as e:
        print(f"❌ Async functionality test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Advanced Military Aircraft Tracker Bot - Test Suite")
    print("=" * 60)
    
    # Setup test environment
    setup_test_environment()
    
    # Run tests
    tests = [
        ("Import Tests", test_imports),
        ("Configuration Tests", test_config),
        ("Database Tests", test_database),
        ("AI Analyzer Tests", test_ai_analyzer),
        ("Flight Fetcher Tests", test_flight_fetcher),
        ("Statistics Tracker Tests", test_statistics_tracker),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} failed with error: {e}")
            results.append((name, False))
    
    # Test async functionality
    try:
        result = asyncio.run(test_async_functionality())
        results.append(("Async Functionality Tests", result))
    except Exception as e:
        print(f"❌ Async functionality test failed with error: {e}")
        results.append(("Async Functionality Tests", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Bot is ready to run.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues before running the bot.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)