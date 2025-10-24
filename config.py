# -*- coding: utf-8 -*-
"""
Configuration file for Military Flight Tracker Bot
Version: 2.0 - Advanced Intelligence System
"""

import os
from typing import List, Dict, Tuple

class Config:
    """Main configuration class for the Military Flight Tracker Bot"""
    
    # ========== Telegram Bot Configuration ==========
    # Replace with your actual bot token from @BotFather
    TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    
    # Replace with your channel ID (with @ prefix for public channels or -100 for private)
    CHANNEL_ID = "YOUR_CHANNEL_ID"
    
    # Admin user ID for reports and management
    ADMIN_ID = 7717672777
    
    # ========== Polling and Performance Configuration ==========
    # Interval between flight checks in seconds (recommended: 30-60)
    POLL_INTERVAL_SECONDS = 30
    
    # Memory cleanup interval in hours
    MEMORY_CLEANUP_HOURS = 24
    
    # Maximum number of concurrent AI analysis requests
    MAX_CONCURRENT_AI_REQUESTS = 5
    
    # Rate limiting delay between AI requests (seconds)
    AI_REQUEST_DELAY = 2
    
    # ========== Logging Configuration ==========
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE = "military_tracker.log"
    MAX_LOG_SIZE_MB = 10
    LOG_BACKUP_COUNT = 5
    
    # ========== Gemini AI Configuration ==========
    # Multiple API keys for redundancy and rate limiting
    GEMINI_API_KEYS = [
        "YOUR_GEMINI_API_KEY_1",  # Primary key
        "YOUR_GEMINI_API_KEY_2",  # Backup key 1
        "YOUR_GEMINI_API_KEY_3",  # Backup key 2
    ]
    
    # Gemini model configuration
    GEMINI_MODEL = "gemini-2.0-flash-exp"  # or "gemini-1.5-pro"
    
    # AI analysis timeout in seconds
    AI_ANALYSIS_TIMEOUT = 30
    
    # Confidence threshold for AI analysis (0.0-1.0)
    MIN_CONFIDENCE_THRESHOLD = 0.6
    
    # ========== Database Configuration ==========
    DATABASE_FILE = "military_aircraft.db"
    
    # Database backup settings
    BACKUP_INTERVAL_HOURS = 6
    MAX_BACKUP_FILES = 7
    
    # Cache settings
    AI_ANALYSIS_CACHE_HOURS = 24
    FLIGHT_HISTORY_RETENTION_DAYS = 30
    
    # ========== Flight Data Sources Configuration ==========
    # Primary flight data sources
    FLIGHT_SOURCES = [
        {
            "name": "ADSB.lol",
            "url": "https://api.adsb.lol/v2/mil",
            "timeout": 25,
            "priority": 1,
            "enabled": True
        },
        {
            "name": "OpenSky Network",
            "url": "https://opensky-network.org/api/states/all",
            "timeout": 30,
            "priority": 2,
            "enabled": False  # Enable if you have API key
        },
        {
            "name": "ADSB Exchange",
            "url": "https://api.adsbexchange.com/v2/mil",
            "timeout": 25,
            "priority": 3,
            "enabled": False  # Enable if you have API key
        }
    ]
    
    # OpenSky Network API key (optional)
    OPENSKY_API_KEY = None
    
    # ========== Geographic Configuration ==========
    # USA bounding box for filtering (min_lat, max_lat, min_lon, max_lon)
    USA_BBOX = (24.0, 50.0, -125.0, -66.0)
    
    # Additional regions to filter out (if needed)
    FILTER_REGIONS = [
        # Example: Europe region
        # {"name": "Europe", "bbox": (35.0, 71.0, -25.0, 40.0), "enabled": False}
    ]
    
    # ========== ICAO Country Code Ranges ==========
    ICAO_COUNTRY_RANGES = {
        "United States": (0xA00000, 0xAFFFFF),
        "Russia": (0x100000, 0x1FFFFF),
        "China": (0x780000, 0x7BFFFF),
        "United Kingdom": (0x400000, 0x43FFFF),
        "France": (0x380000, 0x3BFFFF),
        "Germany": (0x3C0000, 0x3FFFFF),
        "Iran": (0x730000, 0x737FFF),
        "Israel": (0x738000, 0x73FFFF),
        "Turkey": (0x4B0000, 0x4B7FFF),
        "Saudi Arabia": (0x710000, 0x717FFF),
        "Italy": (0x300000, 0x33FFFF),
        "Canada": (0xC00000, 0xC3FFFF),
        "India": (0x800000, 0x83FFFF),
        "Japan": (0x840000, 0x87FFFF),
        "South Korea": (0x700000, 0x707FFF),
        "Australia": (0x7C0000, 0x7FFFFF),
        "Brazil": (0xE00000, 0xE3FFFF),
        "Mexico": (0x0C0000, 0x0FFFFF),
        "Egypt": (0x040000, 0x07FFFF),
        "Pakistan": (0x800000, 0x83FFFF),
        "UAE": (0x896000, 0x896FFF),
        "Qatar": (0x06A000, 0x06AFFF),
        "Kuwait": (0x4A0000, 0x4A0FFF),
        "Jordan": (0x4B8000, 0x4B8FFF),
        "Lebanon": (0x4B9000, 0x4B9FFF),
        "Syria": (0x4BA000, 0x4BAFFF),
        "Iraq": (0x4BB000, 0x4BBFFF),
        "Afghanistan": (0x4BC000, 0x4BCFFF),
        "Kazakhstan": (0x4BD000, 0x4BDFFF),
        "Uzbekistan": (0x4BE000, 0x4BEFFF),
        "Turkmenistan": (0x4BF000, 0x4BFFFF),
        "Azerbaijan": (0x4C0000, 0x4C0FFF),
        "Armenia": (0x4C1000, 0x4C1FFF),
        "Georgia": (0x4C2000, 0x4C2FFF),
        "Ukraine": (0x4C3000, 0x4C3FFF),
        "Belarus": (0x4C4000, 0x4C4FFF),
        "Moldova": (0x4C5000, 0x4C5FFF),
        "Romania": (0x4C6000, 0x4C6FFF),
        "Bulgaria": (0x4C7000, 0x4C7FFF),
        "Greece": (0x4C8000, 0x4C8FFF),
        "Albania": (0x4C9000, 0x4C9FFF),
        "Macedonia": (0x4CA000, 0x4CAFFF),
        "Serbia": (0x4CB000, 0x4CBFFF),
        "Montenegro": (0x4CC000, 0x4CCFFF),
        "Bosnia": (0x4CD000, 0x4CDFFF),
        "Croatia": (0x4CE000, 0x4CEFFF),
        "Slovenia": (0x4CF000, 0x4CFFFF),
        "Hungary": (0x4D0000, 0x4D0FFF),
        "Slovakia": (0x4D1000, 0x4D1FFF),
        "Czech Republic": (0x4D2000, 0x4D2FFF),
        "Poland": (0x4D3000, 0x4D3FFF),
        "Lithuania": (0x4D4000, 0x4D4FFF),
        "Latvia": (0x4D5000, 0x4D5FFF),
        "Estonia": (0x4D6000, 0x4D6FFF),
        "Finland": (0x4D7000, 0x4D7FFF),
        "Sweden": (0x4D8000, 0x4D8FFF),
        "Norway": (0x4D9000, 0x4D9FFF),
        "Denmark": (0x4DA000, 0x4DAFFF),
        "Iceland": (0x4DB000, 0x4DBFFF),
        "Ireland": (0x4DC000, 0x4DCFFF),
        "Portugal": (0x4DD000, 0x4DDFFF),
        "Spain": (0x4DE000, 0x4DEFFF),
        "Andorra": (0x4DF000, 0x4DFFFF),
        "Monaco": (0x4E0000, 0x4E0FFF),
        "Switzerland": (0x4E1000, 0x4E1FFF),
        "Austria": (0x4E2000, 0x4E2FFF),
        "Liechtenstein": (0x4E3000, 0x4E3FFF),
        "Malta": (0x4E4000, 0x4E4FFF),
        "Cyprus": (0x4E5000, 0x4E5FFF),
        "Luxembourg": (0x4E6000, 0x4E6FFF),
        "Belgium": (0x4E7000, 0x4E7FFF),
        "Netherlands": (0x4E8000, 0x4E8FFF),
        "Vatican": (0x4E9000, 0x4E9FFF),
        "San Marino": (0x4EA000, 0x4EAFFF),
    }
    
    # ========== Military Aircraft Type Codes ==========
    MILITARY_TYPE_CODES = {
        # Fighter Aircraft
        "F-16": ["F16", "F-16", "F16C", "F16D"],
        "F-15": ["F15", "F-15", "F15C", "F15D", "F15E"],
        "F-22": ["F22", "F-22", "F22A"],
        "F-35": ["F35", "F-35", "F35A", "F35B", "F35C"],
        "F-18": ["F18", "F-18", "F18C", "F18D", "F18E", "F18F"],
        "F-14": ["F14", "F-14", "F14A", "F14B", "F14D"],
        "F-5": ["F5", "F-5", "F5E", "F5F"],
        "F-4": ["F4", "F-4", "F4E", "F4F"],
        "F-104": ["F104", "F-104"],
        "F-105": ["F105", "F-105"],
        "F-106": ["F106", "F-106"],
        "F-111": ["F111", "F-111"],
        "F-117": ["F117", "F-117"],
        
        # Russian Aircraft
        "Su-27": ["SU27", "SU-27", "SU27S", "SU27SM"],
        "Su-30": ["SU30", "SU-30", "SU30M", "SU30SM"],
        "Su-33": ["SU33", "SU-33"],
        "Su-34": ["SU34", "SU-34"],
        "Su-35": ["SU35", "SU-35"],
        "Su-57": ["SU57", "SU-57"],
        "MiG-29": ["MIG29", "MIG-29", "MIG29A", "MIG29S"],
        "MiG-31": ["MIG31", "MIG-31"],
        "MiG-35": ["MIG35", "MIG-35"],
        "Tu-95": ["TU95", "TU-95", "TU95MS"],
        "Tu-160": ["TU160", "TU-160"],
        "Tu-22M": ["TU22M", "TU-22M"],
        "Il-76": ["IL76", "IL-76", "IL76MD"],
        "An-124": ["AN124", "AN-124"],
        "An-225": ["AN225", "AN-225"],
        
        # Chinese Aircraft
        "J-10": ["J10", "J-10", "J10A", "J10B", "J10C"],
        "J-11": ["J11", "J-11", "J11A", "J11B"],
        "J-15": ["J15", "J-15"],
        "J-16": ["J16", "J-16"],
        "J-20": ["J20", "J-20"],
        "J-31": ["J31", "J-31"],
        "H-6": ["H6", "H-6", "H6K"],
        "Y-20": ["Y20", "Y-20"],
        
        # European Aircraft
        "Eurofighter": ["EF2000", "TYPHOON", "EF2000T"],
        "Rafale": ["RAFALE", "RAFALEC", "RAFALEB"],
        "Gripen": ["GRIPEN", "JAS39", "JAS39A", "JAS39C"],
        "Tornado": ["TORNADO", "TORNADOGR4"],
        "Harrier": ["HARRIER", "AV8B", "AV8BPLUS"],
        
        # Transport Aircraft
        "C-130": ["C130", "C-130", "C130H", "C130J"],
        "C-17": ["C17", "C-17"],
        "C-5": ["C5", "C-5", "C5M"],
        "A400M": ["A400M", "A400"],
        "C-295": ["C295", "C-295"],
        "C-27J": ["C27J", "C-27J"],
        
        # Helicopters
        "AH-64": ["AH64", "AH-64", "AH64D", "AH64E"],
        "AH-1": ["AH1", "AH-1", "AH1W", "AH1Z"],
        "UH-60": ["UH60", "UH-60", "UH60L", "UH60M"],
        "CH-47": ["CH47", "CH-47", "CH47D", "CH47F"],
        "CH-53": ["CH53", "CH-53", "CH53E", "CH53K"],
        "Mi-8": ["MI8", "MI-8", "MI8MT"],
        "Mi-17": ["MI17", "MI-17", "MI17V5"],
        "Mi-24": ["MI24", "MI-24", "MI24P", "MI24V"],
        "Mi-28": ["MI28", "MI-28", "MI28N"],
        "Ka-52": ["KA52", "KA-52"],
        "Ka-50": ["KA50", "KA-50"],
        
        # UAVs/Drones
        "MQ-9": ["MQ9", "MQ-9", "MQ9A", "MQ9B"],
        "MQ-1": ["MQ1", "MQ-1", "MQ1B"],
        "RQ-4": ["RQ4", "RQ-4", "RQ4A", "RQ4B"],
        "RQ-170": ["RQ170", "RQ-170"],
        "Global Hawk": ["GLOBALHAWK", "RQ4"],
        "Predator": ["PREDATOR", "MQ1"],
        "Reaper": ["REAPER", "MQ9"],
        
        # Special Purpose
        "E-3": ["E3", "E-3", "E3A", "E3C"],
        "E-2": ["E2", "E-2", "E2C", "E2D"],
        "P-3": ["P3", "P-3", "P3C"],
        "P-8": ["P8", "P-8", "P8A"],
        "RC-135": ["RC135", "RC-135", "RC135V", "RC135W"],
        "U-2": ["U2", "U-2", "U2S"],
        "SR-71": ["SR71", "SR-71"],
        "B-2": ["B2", "B-2"],
        "B-52": ["B52", "B-52", "B52H"],
        "B-1": ["B1", "B-1", "B1B"],
    }
    
    # ========== Military Operators ==========
    MILITARY_OPERATORS = {
        # US Military
        "USAF": "United States Air Force",
        "USN": "United States Navy",
        "USMC": "United States Marine Corps",
        "USARMY": "United States Army",
        "USCG": "United States Coast Guard",
        "ANG": "Air National Guard",
        "AFRC": "Air Force Reserve Command",
        "NAVY": "United States Navy",
        "MARINE": "United States Marine Corps",
        "ARMY": "United States Army",
        "COAST": "United States Coast Guard",
        
        # NATO
        "NATO": "North Atlantic Treaty Organization",
        "NATO1": "NATO E-3A Component",
        "NATO2": "NATO E-3A Component",
        "NATO3": "NATO E-3A Component",
        "NATO4": "NATO E-3A Component",
        "NATO5": "NATO E-3A Component",
        "NATO6": "NATO E-3A Component",
        "NATO7": "NATO E-3A Component",
        "NATO8": "NATO E-3A Component",
        "NATO9": "NATO E-3A Component",
        
        # Russian Military
        "RUSAF": "Russian Air Force",
        "RUSN": "Russian Navy",
        "RUSARMY": "Russian Army",
        "VVS": "Военно-воздушные силы России",
        "VMF": "Военно-морской флот России",
        "SV": "Сухопутные войска России",
        
        # Chinese Military
        "PLAAF": "People's Liberation Army Air Force",
        "PLAN": "People's Liberation Army Navy",
        "PLAGF": "People's Liberation Army Ground Force",
        
        # European Military
        "RAF": "Royal Air Force",
        "RN": "Royal Navy",
        "ARMY": "British Army",
        "LUFTWAFFE": "German Air Force",
        "ARMEE": "French Air Force",
        "AERONAUTICA": "Italian Air Force",
        "EJERCITO": "Spanish Air Force",
        "KONINKLIJKE": "Royal Netherlands Air Force",
        "FORCA": "Portuguese Air Force",
        "FORCES": "Belgian Air Force",
        "LUFTSTYRKERNE": "Royal Danish Air Force",
        "LUFTFORSVARET": "Royal Norwegian Air Force",
        "FLYGVAPNET": "Swedish Air Force",
        "ILMAVOIMAT": "Finnish Air Force",
        
        # Middle East
        "IRIAF": "Islamic Republic of Iran Air Force",
        "IAF": "Israeli Air Force",
        "TSK": "Turkish Armed Forces",
        "RSAF": "Royal Saudi Air Force",
        "UAEAF": "United Arab Emirates Air Force",
        "QAF": "Qatar Air Force",
        "KAF": "Kuwait Air Force",
        "JAF": "Jordanian Air Force",
        "LAF": "Lebanese Air Force",
        "SAF": "Syrian Air Force",
        "IQAF": "Iraqi Air Force",
        
        # Asian Military
        "IAF": "Indian Air Force",
        "IN": "Indian Navy",
        "JASDF": "Japan Air Self-Defense Force",
        "JMSDF": "Japan Maritime Self-Defense Force",
        "ROKAF": "Republic of Korea Air Force",
        "ROKN": "Republic of Korea Navy",
        "RAAF": "Royal Australian Air Force",
        "RAN": "Royal Australian Navy",
        "RCAF": "Royal Canadian Air Force",
        "RCN": "Royal Canadian Navy",
        "FAB": "Brazilian Air Force",
        "FAM": "Mexican Air Force",
        
        # Other
        "UN": "United Nations",
        "EU": "European Union",
        "OSCE": "Organization for Security and Co-operation in Europe",
    }
    
    # ========== Geographic Regions ==========
    GEOGRAPHIC_REGIONS = {
        # Middle East
        "Persian Gulf": (24.0, 30.0, 48.0, 56.0),
        "Red Sea": (12.0, 30.0, 32.0, 44.0),
        "Mediterranean": (30.0, 45.0, -6.0, 36.0),
        "Black Sea": (40.0, 47.0, 27.0, 42.0),
        "Caspian Sea": (36.0, 47.0, 46.0, 54.0),
        "Arabian Peninsula": (12.0, 32.0, 34.0, 60.0),
        "Levant": (29.0, 37.0, 34.0, 42.0),
        "Mesopotamia": (29.0, 37.0, 38.0, 48.0),
        
        # Europe
        "Western Europe": (35.0, 60.0, -10.0, 10.0),
        "Eastern Europe": (45.0, 60.0, 10.0, 40.0),
        "Scandinavia": (55.0, 72.0, 4.0, 32.0),
        "Balkans": (40.0, 47.0, 13.0, 29.0),
        "Caucasus": (40.0, 45.0, 37.0, 50.0),
        "Baltic States": (54.0, 60.0, 20.0, 28.0),
        
        # Asia
        "East Asia": (20.0, 55.0, 100.0, 150.0),
        "Southeast Asia": (-10.0, 25.0, 90.0, 150.0),
        "South Asia": (5.0, 40.0, 60.0, 100.0),
        "Central Asia": (35.0, 55.0, 45.0, 85.0),
        "Siberia": (50.0, 80.0, 60.0, 180.0),
        
        # Americas
        "North America": (15.0, 85.0, -180.0, -50.0),
        "South America": (-60.0, 15.0, -85.0, -30.0),
        "Caribbean": (10.0, 25.0, -85.0, -60.0),
        
        # Africa
        "North Africa": (15.0, 37.0, -20.0, 40.0),
        "Sub-Saharan Africa": (-35.0, 15.0, -20.0, 55.0),
        "Horn of Africa": (0.0, 15.0, 30.0, 55.0),
        
        # Oceans
        "Atlantic Ocean": (-60.0, 80.0, -100.0, 20.0),
        "Pacific Ocean": (-60.0, 80.0, 120.0, -60.0),
        "Indian Ocean": (-60.0, 30.0, 20.0, 120.0),
        "Arctic Ocean": (60.0, 90.0, -180.0, 180.0),
    }
    
    # ========== Notification Settings ==========
    # Minimum strategic importance to send notification (1-10)
    MIN_STRATEGIC_IMPORTANCE = 3
    
    # Maximum notifications per hour per aircraft
    MAX_NOTIFICATIONS_PER_HOUR = 2
    
    # Notification cooldown period (minutes)
    NOTIFICATION_COOLDOWN_MINUTES = 30
    
    # ========== Error Handling ==========
    # Maximum retry attempts for API calls
    MAX_RETRY_ATTEMPTS = 3
    
    # Retry delay in seconds
    RETRY_DELAY_SECONDS = 5
    
    # Circuit breaker settings
    CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT = 300  # 5 minutes
    
    # ========== Performance Settings ==========
    # Maximum memory usage (MB)
    MAX_MEMORY_USAGE_MB = 512
    
    # Garbage collection interval (seconds)
    GC_INTERVAL_SECONDS = 300
    
    # Database connection pool size
    DB_POOL_SIZE = 10
    
    # ========== Security Settings ==========
    # Enable request logging
    ENABLE_REQUEST_LOGGING = True
    
    # Enable response logging
    ENABLE_RESPONSE_LOGGING = False
    
    # API key rotation interval (hours)
    API_KEY_ROTATION_HOURS = 24
    
    # ========== Development Settings ==========
    # Enable debug mode
    DEBUG_MODE = False
    
    # Enable test mode (no real notifications)
    TEST_MODE = False
    
    # Enable verbose logging
    VERBOSE_LOGGING = False
    
    # ========== Validation Methods ==========
    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Check required settings
        if cls.TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
            errors.append("Telegram bot token not configured")
        
        if cls.CHANNEL_ID == "YOUR_CHANNEL_ID":
            errors.append("Channel ID not configured")
        
        if not any(key != "YOUR_GEMINI_API_KEY_1" for key in cls.GEMINI_API_KEYS):
            errors.append("No valid Gemini API keys configured")
        
        # Check numeric ranges
        if not (10 <= cls.POLL_INTERVAL_SECONDS <= 300):
            errors.append("Poll interval should be between 10 and 300 seconds")
        
        if not (0.0 <= cls.MIN_CONFIDENCE_THRESHOLD <= 1.0):
            errors.append("Confidence threshold should be between 0.0 and 1.0")
        
        if not (1 <= cls.MIN_STRATEGIC_IMPORTANCE <= 10):
            errors.append("Strategic importance should be between 1 and 10")
        
        return errors
    
    @classmethod
    def get_enabled_sources(cls) -> List[Dict]:
        """Get list of enabled flight data sources"""
        return [source for source in cls.FLIGHT_SOURCES if source.get("enabled", True)]
    
    @classmethod
    def get_region_from_coords(cls, lat: float, lon: float) -> str:
        """Get geographic region from coordinates"""
        for region_name, (min_lat, max_lat, min_lon, max_lon) in cls.GEOGRAPHIC_REGIONS.items():
            if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                return region_name
        return "Unknown Region"
    
    @classmethod
    def is_within_filtered_region(cls, lat: float, lon: float) -> bool:
        """Check if coordinates are within any filtered region"""
        # Check USA bbox
        min_lat, max_lat, min_lon, max_lon = cls.USA_BBOX
        if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
            return True
        
        # Check other filter regions
        for region in cls.FILTER_REGIONS:
            if region.get("enabled", False):
                min_lat, max_lat, min_lon, max_lon = region["bbox"]
                if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                    return True
        
        return False

# ========== Environment Variable Overrides ==========
def load_from_env():
    """Load configuration from environment variables"""
    # Telegram settings
    if os.getenv("TELEGRAM_TOKEN"):
        Config.TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    if os.getenv("TELEGRAM_CHANNEL_ID"):
        Config.CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
    
    if os.getenv("TELEGRAM_ADMIN_ID"):
        Config.ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID"))
    
    # Gemini API keys
    gemini_keys = []
    for i in range(1, 4):  # Support up to 3 keys
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key:
            gemini_keys.append(key)
    
    if gemini_keys:
        Config.GEMINI_API_KEYS = gemini_keys
    
    # Other settings
    if os.getenv("POLL_INTERVAL_SECONDS"):
        Config.POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS"))
    
    if os.getenv("LOG_LEVEL"):
        Config.LOG_LEVEL = os.getenv("LOG_LEVEL")
    
    if os.getenv("DEBUG_MODE", "").lower() == "true":
        Config.DEBUG_MODE = True
    
    if os.getenv("TEST_MODE", "").lower() == "true":
        Config.TEST_MODE = True

# Load environment variables
load_from_env()

# Validate configuration on import
config_errors = Config.validate_config()
if config_errors:
    print("Configuration errors found:")
    for error in config_errors:
        print(f"  - {error}")
    print("\nPlease fix these errors before running the bot.")