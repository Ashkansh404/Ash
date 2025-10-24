# -*- coding: utf-8 -*-
"""
Military Flight Tracker - Configuration Module
Advanced configuration with multi-API key rotation and comprehensive settings
"""

# ========== Telegram Configuration ==========
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
TELEGRAM_CHANNEL_ID = "@your_channel_id_here"  # e.g., @military_flights or -1001234567890
ADMIN_USER_ID = 7717672777  # Admin user ID for reports

# ========== Gemini AI Configuration ==========
# Multiple Gemini API keys for automatic rotation when limits are reached
GEMINI_API_KEYS = [
    "YOUR_GEMINI_API_KEY_1_HERE",
    "YOUR_GEMINI_API_KEY_2_HERE",
    "YOUR_GEMINI_API_KEY_3_HERE",
    # Add more keys as needed
]

# Gemini Model Configuration
GEMINI_MODEL = "gemini-2.0-flash-exp"  # Latest available model
GEMINI_TEMPERATURE = 0.3  # Lower for more consistent, factual outputs
GEMINI_MAX_RETRIES = 3  # Max retries per API key before switching
GEMINI_TIMEOUT = 15  # Timeout in seconds for Gemini API calls

# ========== Flight Data API Configuration ==========
ADSB_API_URL = "https://api.adsb.lol/v2/mil"
ADSB_TIMEOUT = 25  # Timeout in seconds
ADSB_RETRY_COUNT = 3  # Number of retries for failed requests

# ========== Bot Operation Settings ==========
POLL_INTERVAL_SECONDS = 120  # How often to check for new flights (2 minutes)
NOTIFICATION_DELAY_SECONDS = 45  # Delay between notifications to avoid spam
HOURLY_REPORT_INTERVAL = 3600  # Send statistics every hour
DAILY_REPORT_HOUR = 0  # Hour (UTC) to send daily unidentified aircraft report

# ========== Geographic Filtering ==========
# Exclude USA domestic flights (reduce noise)
USA_BBOX = {
    'min_lat': 24.0,
    'max_lat': 50.0,
    'min_lon': -125.0,
    'max_lon': -66.0
}

# Strategic regions for enhanced monitoring
STRATEGIC_REGIONS = {
    "خلیج فارس": (24.0, 30.5, 48.0, 57.0),
    "دریای سرخ": (12.0, 30.0, 32.0, 45.0),
    "دریای مدیترانه شرقی": (30.0, 37.0, 23.0, 36.5),
    "دریای سیاه": (41.0, 47.0, 27.0, 42.0),
    "مرز اوکراین-روسیه": (46.0, 52.0, 22.0, 40.0),
    "دریای بالتیک": (53.0, 66.0, 10.0, 30.0),
    "کره‌جنوبی": (33.0, 39.0, 124.0, 132.0),
    "تایوان": (21.0, 26.0, 119.0, 122.5),
    "خاورمیانه": (12.0, 42.0, 34.0, 63.0),
}

# ========== Database Configuration ==========
DATABASE_FILE = "military_flights.db"
DB_CLEANUP_DAYS = 30  # Keep spotted aircraft records for 30 days
AI_CACHE_DAYS = 90  # Keep AI analysis cache for 90 days

# ========== Logging Configuration ==========
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "military_tracker.log"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5  # Keep 5 backup log files

# ========== Advanced Features ==========
ENABLE_AI_ANALYSIS = True  # Enable/disable Gemini AI analysis
USE_AI_CACHE = True  # Use cached AI analysis for known aircraft
MIN_STRATEGIC_IMPORTANCE = 5  # Only notify for flights with importance >= 5
ENABLE_LOCATION_ENRICHMENT = True  # Add strategic location context

# ========== ICAO Country Allocation ==========
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
    "United Arab Emirates": (0x896000, 0x897FFF),
    "Italy": (0x300000, 0x33FFFF),
    "Spain": (0x340000, 0x37FFFF),
    "Canada": (0xC00000, 0xC3FFFF),
    "Australia": (0x7C0000, 0x7FFFFF),
    "India": (0x800000, 0x83FFFF),
    "Japan": (0x840000, 0x87FFFF),
    "South Korea": (0x718000, 0x71FFFF),
    "Poland": (0x498000, 0x49FFFF),
    "Ukraine": (0x508000, 0x50FFFF),
    "Egypt": (0x010000, 0x03FFFF),
    "Pakistan": (0x760000, 0x767FFF),
    "Qatar": (0x06C000, 0x06CFFF),
    "Kuwait": (0x0A4000, 0x0A4FFF),
    "Bahrain": (0x894000, 0x894FFF),
    "Oman": (0x0A8000, 0x0A8FFF),
    "Sweden": (0x4A0000, 0x4A7FFF),
    "Norway": (0x478000, 0x47FFFF),
    "Finland": (0x460000, 0x467FFF),
    "Belgium": (0x448000, 0x44FFFF),
    "Netherlands": (0x480000, 0x487FFF),
    "Greece": (0x468000, 0x46FFFF),
    "Romania": (0x4A8000, 0x4AFFFF),
}

# ========== Military Operators Recognition ==========
MILITARY_OPERATORS = {
    # US Military
    "RCH": "US Air Force Air Mobility Command",
    "CNV": "US Air Force Mobility Command",
    "EVAC": "US Air Force Medical Evacuation",
    "LION": "US Air Force Special Operations",
    "SPAR": "US Air Force Special Air Mission",
    "VALOR": "US Air Force Special Operations",
    "REACH": "US Air Force Air Mobility Command",
    "BOXER": "US Air Force Airlift",
    "NAVY": "US Navy",
    "VVLL": "US Navy VIP Transport",
    "GTMO": "US Navy Guantanamo Operations",
    
    # NATO
    "NAF": "NATO Air Force",
    "NATO": "NATO Operations",
    
    # UK Military
    "RRR": "UK Royal Air Force",
    "TARTN": "UK Royal Air Force Transport",
    "RAFAIR": "UK Royal Air Force",
    "ASCOT": "UK Royal Air Force Transport",
    "TYPHON": "UK RAF Typhoon Operations",
    
    # Russian Military  
    "RFF": "Russian Air Force",
    "RSD": "Russian Special Flight",
    
    # Israeli Military
    "IAF": "Israeli Air Force",
    "GOLF": "Israeli Air Force Transport",
    
    # Turkish Military
    "THY": "Turkish Air Force",
    "TUAF": "Turkish Air Force",
    
    # French Military
    "FAF": "French Air Force",
    "CTM": "French Air Force Transport",
    
    # German Military
    "GAF": "German Air Force (Luftwaffe)",
    "DKBRD": "German Air Force Special Flight",
    
    # Other Nations
    "RSAF": "Royal Saudi Air Force",
    "UAEAF": "UAE Air Force",
    "JTFC": "Japan Air Self-Defense Force",
    "RSAF": "Republic of Singapore Air Force",
    "ROKAF": "Republic of Korea Air Force",
}

# ========== Aircraft Database ==========
AIRCRAFT_DATABASE = {
    # Strategic Bombers
    "B52": "Boeing B-52 Stratofortress (بمب‌افکن استراتژیک)",
    "B1": "Rockwell B-1 Lancer (بمب‌افکن استراتژیک)",
    "B2": "Northrop B-2 Spirit (بمب‌افکن رادارگریز)",
    "TU95": "Tupolev Tu-95 Bear (بمب‌افکن استراتژیک روسی)",
    "TU160": "Tupolev Tu-160 Blackjack (بمب‌افکن استراتژیک روسی)",
    "TU22": "Tupolev Tu-22M Backfire (بمب‌افکن تاکتیکی)",
    
    # Fighters & Interceptors
    "F35": "Lockheed Martin F-35 Lightning II (جنگنده نسل پنجم)",
    "F22": "Lockheed Martin F-22 Raptor (جنگنده رادارگریز)",
    "F16": "General Dynamics F-16 Fighting Falcon (جنگنده چندمنظوره)",
    "F15": "McDonnell Douglas F-15 Eagle (جنگنده برتری هوایی)",
    "F18": "Boeing F/A-18 Super Hornet (جنگنده-بمب‌افکن)",
    "SU35": "Sukhoi Su-35 Flanker-E (جنگنده روسی)",
    "SU57": "Sukhoi Su-57 Felon (جنگنده نسل پنجم روسی)",
    "MIG31": "Mikoyan MiG-31 Foxhound (جنگنده رهگیر)",
    "MIG29": "Mikoyan MiG-29 Fulcrum (جنگنده)",
    "J20": "Chengdu J-20 (جنگنده رادارگریز چینی)",
    "EUFI": "Eurofighter Typhoon (جنگنده اروپایی)",
    "RFAL": "Dassault Rafale (جنگنده فرانسوی)",
    
    # Strategic Assets
    "C17": "Boeing C-17 Globemaster III (هواپیمای حمل استراتژیک)",
    "C5": "Lockheed C-5 Galaxy (هواپیمای حمل فوق‌سنگین)",
    "C130": "Lockheed C-130 Hercules (هواپیمای حمل تاکتیکی)",
    "KC135": "Boeing KC-135 Stratotanker (هواپیمای سوخت‌رسان)",
    "KC10": "McDonnell Douglas KC-10 Extender (سوخت‌رسان)",
    "KC46": "Boeing KC-46 Pegasus (سوخت‌رسان مدرن)",
    "A400M": "Airbus A400M Atlas (حمل نظامی اروپایی)",
    "IL76": "Ilyushin Il-76 (حمل استراتژیک روسی)",
    "AN124": "Antonov An-124 Ruslan (حمل فوق‌سنگین)",
    
    # ISR & Special Missions
    "E3": "Boeing E-3 Sentry (هواپیمای رادار هشداردهنده)",
    "E8": "Northrop Grumman E-8 JSTARS (نظارت میدان نبرد)",
    "RC135": "Boeing RC-135 (جمع‌آوری اطلاعات الکترونیکی)",
    "P8": "Boeing P-8 Poseidon (گشت دریایی)",
    "RQ4": "Northrop Grumman RQ-4 Global Hawk (پهپاد شناسایی)",
    "MQ9": "General Atomics MQ-9 Reaper (پهپاد مسلح)",
    "AWACS": "AWACS (سیستم هشدار زودهنگام)",
    "E2": "Northrop Grumman E-2 Hawkeye (رادار هوابرد)",
    
    # Maritime Patrol
    "P3": "Lockheed P-3 Orion (گشت دریایی)",
    "A319": "Airbus A319CJ (VIP/گشت)",
    
    # VIP & Command
    "B757": "Boeing 757 (حمل VIP)",
    "B737": "Boeing 737 (حمل نظامی/VIP)",
    "GLF5": "Gulfstream V (جت خصوصی نظامی)",
    "GLEX": "Bombardier Global Express (جت خصوصی نظامی)",
}

# ========== Role Classification ==========
ROLE_MAP = {
    "بمب‌افکن استراتژیک": ["B52", "B1", "B2", "TU95", "TU160"],
    "جنگنده رادارگریز": ["F22", "F35", "B2", "SU57", "J20"],
    "جنگنده چندمنظوره": ["F16", "F15", "F18", "SU35", "EUFI", "RFAL"],
    "هواپیمای حمل استراتژیک": ["C17", "C5", "IL76", "AN124", "A400M"],
    "هواپیمای سوخت‌رسان": ["KC135", "KC10", "KC46"],
    "سیستم هشدار زودهنگام": ["E3", "AWACS", "E2"],
    "جمع‌آوری اطلاعات": ["RC135", "E8", "RQ4"],
    "گشت دریایی": ["P8", "P3"],
    "پهپاد نظامی": ["RQ4", "MQ9"],
    "حمل VIP نظامی": ["B757", "B737", "GLF5", "GLEX"],
}

# ========== Validation ==========
def validate_config():
    """Validate configuration settings"""
    errors = []
    
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        errors.append("❌ TELEGRAM_BOT_TOKEN not configured")
    
    if not TELEGRAM_CHANNEL_ID or TELEGRAM_CHANNEL_ID == "@your_channel_id_here":
        errors.append("❌ TELEGRAM_CHANNEL_ID not configured")
    
    if not GEMINI_API_KEYS or GEMINI_API_KEYS[0] == "YOUR_GEMINI_API_KEY_1_HERE":
        errors.append("❌ GEMINI_API_KEYS not configured")
    
    if errors:
        print("\n⚠️  Configuration Errors Found:")
        for error in errors:
            print(f"  {error}")
        print("\n📝 Please edit config.py and add your credentials.\n")
        return False
    
    return True

if __name__ == "__main__":
    if validate_config():
        print("✅ Configuration validated successfully!")
    else:
        print("❌ Configuration validation failed!")
