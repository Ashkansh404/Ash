# -*- coding: utf-8 -*-
"""
Advanced Military Aircraft Tracker Configuration
Version 2.0 - Enhanced Configuration Management
"""

import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# ========== Environment Variables ==========
def get_env_var(key: str, default: str = None, required: bool = True) -> str:
    """Get environment variable with validation"""
    value = os.getenv(key, default)
    if required and not value:
        raise ValueError(f"Required environment variable {key} not set")
    return value

# ========== Telegram Configuration ==========
@dataclass
class TelegramConfig:
    """Telegram bot configuration"""
    TOKEN: str = get_env_var("TELEGRAM_BOT_TOKEN", required=True)
    CHANNEL_ID: str = get_env_var("TELEGRAM_CHANNEL_ID", required=True)
    ADMIN_ID: int = int(get_env_var("TELEGRAM_ADMIN_ID", "7717672777"))
    
    # Message formatting
    MAX_MESSAGE_LENGTH: int = 4096
    PARSE_MODE: str = "Markdown"
    DISABLE_WEB_PREVIEW: bool = False

# ========== AI Configuration ==========
@dataclass
class AIConfig:
    """AI analysis configuration"""
    # Gemini API Keys (Multiple for redundancy)
    GEMINI_API_KEYS: List[str] = None
    
    # Gemini Model Configuration
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    GEMINI_TIMEOUT: int = 30
    GEMINI_RATE_LIMIT_DELAY: float = 2.0
    GEMINI_MAX_RETRIES: int = 3
    
    # Analysis Configuration
    ANALYSIS_CACHE_TTL_HOURS: int = 24
    CONFIDENCE_THRESHOLD: float = 0.7
    FALLBACK_TO_CACHE: bool = True
    
    def __post_init__(self):
        if self.GEMINI_API_KEYS is None:
            # Try to get from environment variables
            keys = []
            for i in range(1, 4):  # Support up to 3 API keys
                key = os.getenv(f"GEMINI_API_KEY_{i}")
                if key:
                    keys.append(key)
            
            if not keys:
                # Fallback to single key
                key = os.getenv("GEMINI_API_KEY")
                if key:
                    keys = [key]
            
            self.GEMINI_API_KEYS = keys

# ========== Flight Tracking Configuration ==========
@dataclass
class FlightTrackingConfig:
    """Flight tracking APIs configuration"""
    # Primary API
    ADSB_LOL_API: str = "https://api.adsb.lol/v2/mil"
    ADSB_LOL_TIMEOUT: int = 25
    ADSB_LOL_RETRIES: int = 3
    
    # Secondary APIs (for redundancy)
    OPENSKY_API: str = "https://opensky-network.org/api/states/all"
    OPENSKY_TIMEOUT: int = 20
    OPENSKY_RETRIES: int = 2
    
    ADSBX_API: str = "https://adsbexchange-com1.p.rapidapi.com/v2/mil"
    ADSBX_TIMEOUT: int = 30
    ADSBX_RETRIES: int = 2
    
    # Polling Configuration
    POLL_INTERVAL_SECONDS: int = int(get_env_var("POLL_INTERVAL", "30"))
    MAX_CONCURRENT_REQUESTS: int = 5
    REQUEST_DELAY: float = 1.0
    
    # Data Processing
    MIN_ALTITUDE_METERS: int = 100
    MAX_ALTITUDE_METERS: int = 50000
    MIN_SPEED_KMH: int = 50
    MAX_SPEED_KMH: int = 2000

# ========== Geographic Configuration ==========
@dataclass
class GeographicConfig:
    """Geographic filtering and analysis configuration"""
    # USA Bounding Box (to filter out)
    USA_BBOX: Tuple[float, float, float, float] = (24.0, 50.0, -125.0, -66.0)
    
    # ICAO Country Code Ranges (Extended)
    ICAO_COUNTRY_RANGES: Dict[str, Tuple[int, int]] = None
    
    # Geographic Regions for Analysis
    STRATEGIC_REGIONS: Dict[str, Tuple[float, float, float, float]] = None
    
    def __post_init__(self):
        if self.ICAO_COUNTRY_RANGES is None:
            self.ICAO_COUNTRY_RANGES = {
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
                "South Korea": (0x71C000, 0x71FFFF),
                "Australia": (0x7C0000, 0x7FFFFF),
                "Brazil": (0xE00000, 0xE3FFFF),
                "Mexico": (0x0D0000, 0x0DFFFF),
                "Egypt": (0x010000, 0x01FFFF),
                "Pakistan": (0x760000, 0x767FFF),
                "Ukraine": (0x508000, 0x50FFFF),
                "Poland": (0x480000, 0x487FFF),
                "Romania": (0x4D0000, 0x4D7FFF),
                "Bulgaria": (0x4B8000, 0x4BFFFF),
                "Greece": (0x468000, 0x46FFFF),
                "Spain": (0x340000, 0x37FFFF),
                "Netherlands": (0x480000, 0x487FFF),
                "Belgium": (0x448000, 0x44FFFF),
                "Switzerland": (0x4B8000, 0x4BFFFF),
                "Austria": (0x440000, 0x447FFF),
                "Czech Republic": (0x498000, 0x49FFFF),
                "Slovakia": (0x508000, 0x50FFFF),
                "Hungary": (0x508000, 0x50FFFF),
                "Croatia": (0x4D0000, 0x4D7FFF),
                "Serbia": (0x4D0000, 0x4D7FFF),
                "Bosnia": (0x4D0000, 0x4D7FFF),
                "Montenegro": (0x4D0000, 0x4D7FFF),
                "Albania": (0x4D0000, 0x4D7FFF),
                "North Macedonia": (0x4D0000, 0x4D7FFF),
                "Kosovo": (0x4D0000, 0x4D7FFF),
                "Moldova": (0x508000, 0x50FFFF),
                "Belarus": (0x508000, 0x50FFFF),
                "Lithuania": (0x508000, 0x50FFFF),
                "Latvia": (0x508000, 0x50FFFF),
                "Estonia": (0x508000, 0x50FFFF),
                "Finland": (0x508000, 0x50FFFF),
                "Sweden": (0x508000, 0x50FFFF),
                "Norway": (0x508000, 0x50FFFF),
                "Denmark": (0x448000, 0x44FFFF),
                "Iceland": (0x508000, 0x50FFFF),
                "Ireland": (0x4C0000, 0x4C7FFF),
                "Portugal": (0x490000, 0x497FFF),
                "Luxembourg": (0x4C0000, 0x4C7FFF),
                "Malta": (0x4D0000, 0x4D7FFF),
                "Cyprus": (0x4D0000, 0x4D7FFF),
                "Slovenia": (0x4D0000, 0x4D7FFF),
            }
        
        if self.STRATEGIC_REGIONS is None:
            self.STRATEGIC_REGIONS = {
                "Persian Gulf": (24.0, 30.0, 48.0, 56.0),
                "Strait of Hormuz": (25.0, 27.0, 56.0, 58.0),
                "Black Sea": (40.0, 47.0, 27.0, 42.0),
                "Mediterranean": (30.0, 45.0, -6.0, 36.0),
                "Baltic Sea": (54.0, 66.0, 9.0, 30.0),
                "North Sea": (51.0, 62.0, -2.0, 9.0),
                "South China Sea": (0.0, 25.0, 105.0, 120.0),
                "East China Sea": (25.0, 35.0, 120.0, 130.0),
                "Yellow Sea": (35.0, 40.0, 120.0, 125.0),
                "Sea of Japan": (35.0, 45.0, 128.0, 142.0),
                "Red Sea": (12.0, 30.0, 32.0, 44.0),
                "Arabian Sea": (10.0, 25.0, 50.0, 75.0),
                "Caspian Sea": (36.0, 47.0, 46.0, 55.0),
                "Arctic Ocean": (66.0, 90.0, -180.0, 180.0),
                "North Atlantic": (30.0, 70.0, -80.0, 0.0),
                "North Pacific": (30.0, 70.0, 120.0, -120.0),
            }

# ========== Database Configuration ==========
@dataclass
class DatabaseConfig:
    """Database configuration"""
    DATABASE_FILE: str = get_env_var("DATABASE_FILE", "military_aircraft.db")
    BACKUP_INTERVAL_HOURS: int = 6
    CLEANUP_INTERVAL_HOURS: int = 24
    MAX_DATABASE_SIZE_MB: int = 500
    
    # Table configurations
    SPOTTED_AIRCRAFT_TTL_HOURS: int = 168  # 7 days
    AI_ANALYSIS_CACHE_TTL_HOURS: int = 72  # 3 days
    FLIGHT_PATTERNS_TTL_HOURS: int = 240   # 10 days
    UNIDENTIFIED_TTL_HOURS: int = 720      # 30 days
    
    # Performance settings
    WAL_MODE: bool = True
    SYNCHRONOUS: str = "NORMAL"
    JOURNAL_MODE: str = "WAL"
    CACHE_SIZE: int = -2000  # 2MB

# ========== Logging Configuration ==========
@dataclass
class LoggingConfig:
    """Logging configuration"""
    LOG_LEVEL: str = get_env_var("LOG_LEVEL", "INFO")
    LOG_FILE: str = get_env_var("LOG_FILE", "military_tracker.log")
    MAX_LOG_SIZE_MB: int = 50
    BACKUP_COUNT: int = 5
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    
    # Log rotation
    ROTATE_WHEN: str = "midnight"
    ROTATE_INTERVAL: int = 1
    ROTATE_BACKUP_COUNT: int = 30

# ========== Security Configuration ==========
@dataclass
class SecurityConfig:
    """Security and rate limiting configuration"""
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE: int = 60
    MAX_REQUESTS_PER_HOUR: int = 1000
    MAX_REQUESTS_PER_DAY: int = 10000
    
    # API security
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0
    BACKOFF_FACTOR: float = 2.0
    
    # Data validation
    MAX_ICAO_LENGTH: int = 6
    MAX_CALLSIGN_LENGTH: int = 20
    MAX_TYPECODE_LENGTH: int = 10
    COORDINATE_PRECISION: int = 6
    
    # Input sanitization
    ALLOWED_CHARACTERS: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    MAX_MESSAGE_LENGTH: int = 4096

# ========== Performance Configuration ==========
@dataclass
class PerformanceConfig:
    """Performance optimization configuration"""
    # Threading
    MAX_WORKER_THREADS: int = 10
    MAX_ASYNC_TASKS: int = 50
    TASK_TIMEOUT: int = 300
    
    # Memory management
    MAX_MEMORY_USAGE_MB: int = 512
    GARBAGE_COLLECTION_INTERVAL: int = 100
    CACHE_SIZE_LIMIT: int = 1000
    
    # Network optimization
    CONNECTION_POOL_SIZE: int = 20
    KEEP_ALIVE: bool = True
    TCP_NODELAY: bool = True
    
    # Database optimization
    BATCH_SIZE: int = 100
    COMMIT_INTERVAL: int = 10
    VACUUM_INTERVAL_HOURS: int = 24

# ========== Notification Configuration ==========
@dataclass
class NotificationConfig:
    """Notification system configuration"""
    # Message formatting
    ENABLE_RICH_FORMATTING: bool = True
    ENABLE_EMOJIS: bool = True
    ENABLE_LINKS: bool = True
    ENABLE_LOCATION_MAPS: bool = True
    
    # Notification filtering
    MIN_STRATEGIC_IMPORTANCE: int = 3
    MIN_THREAT_LEVEL: str = "LOW"
    ENABLE_FILTERING: bool = True
    
    # Rate limiting
    MAX_NOTIFICATIONS_PER_HOUR: int = 50
    MIN_NOTIFICATION_INTERVAL: int = 30  # seconds
    
    # Message templates
    NOTIFICATION_TEMPLATE: str = "enhanced"
    INCLUDE_ANALYSIS: bool = True
    INCLUDE_THREAT_ASSESSMENT: bool = True
    INCLUDE_LOCATION_CONTEXT: bool = True

# ========== Main Configuration Class ==========
@dataclass
class Config:
    """Main configuration class"""
    telegram: TelegramConfig = None
    ai: AIConfig = None
    flight_tracking: FlightTrackingConfig = None
    geographic: GeographicConfig = None
    database: DatabaseConfig = None
    logging: LoggingConfig = None
    security: SecurityConfig = None
    performance: PerformanceConfig = None
    notification: NotificationConfig = None
    
    def __post_init__(self):
        if self.telegram is None:
            self.telegram = TelegramConfig()
        if self.ai is None:
            self.ai = AIConfig()
        if self.flight_tracking is None:
            self.flight_tracking = FlightTrackingConfig()
        if self.geographic is None:
            self.geographic = GeographicConfig()
        if self.database is None:
            self.database = DatabaseConfig()
        if self.logging is None:
            self.logging = LoggingConfig()
        if self.security is None:
            self.security = SecurityConfig()
        if self.performance is None:
            self.performance = PerformanceConfig()
        if self.notification is None:
            self.notification = NotificationConfig()
    
    def validate(self) -> bool:
        """Validate configuration"""
        try:
            # Validate required fields
            if not self.telegram.TOKEN:
                raise ValueError("Telegram bot token is required")
            if not self.telegram.CHANNEL_ID:
                raise ValueError("Telegram channel ID is required")
            if not self.ai.GEMINI_API_KEYS:
                raise ValueError("At least one Gemini API key is required")
            
            # Validate numeric ranges
            if self.flight_tracking.POLL_INTERVAL_SECONDS < 10:
                raise ValueError("Poll interval must be at least 10 seconds")
            if self.ai.CONFIDENCE_THRESHOLD < 0 or self.ai.CONFIDENCE_THRESHOLD > 1:
                raise ValueError("Confidence threshold must be between 0 and 1")
            
            return True
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False

# ========== Configuration Factory ==========
def create_config() -> Config:
    """Create and validate configuration"""
    config = Config()
    
    if not config.validate():
        raise ValueError("Invalid configuration")
    
    return config

# ========== Environment Setup ==========
def setup_environment():
    """Setup environment variables and paths"""
    import os
    import sys
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Set default environment variables if not set
    os.environ.setdefault('LOG_LEVEL', 'INFO')
    os.environ.setdefault('DATABASE_FILE', 'military_aircraft.db')
    os.environ.setdefault('POLL_INTERVAL', '30')

# ========== Configuration Constants ==========
# Create global config instance
config = create_config()

# Export commonly used values for backward compatibility
TOKEN = config.telegram.TOKEN
CHANNEL_ID = config.telegram.CHANNEL_ID
ADMIN_ID = config.telegram.ADMIN_ID
POLL_INTERVAL_SECONDS = config.flight_tracking.POLL_INTERVAL_SECONDS
LOG_LEVEL = config.logging.LOG_LEVEL
LOG_FILE = config.logging.LOG_FILE
DATABASE_FILE = config.database.DATABASE_FILE
GEMINI_API_KEYS = config.ai.GEMINI_API_KEYS
GEMINI_MODEL = config.ai.GEMINI_MODEL
USA_BBOX = config.geographic.USA_BBOX
ICAO_COUNTRY_RANGES = config.geographic.ICAO_COUNTRY_RANGES

# ========== Utility Functions ==========
def get_config() -> Config:
    """Get current configuration"""
    return config

def reload_config() -> Config:
    """Reload configuration from environment"""
    global config
    config = create_config()
    return config

def is_development() -> bool:
    """Check if running in development mode"""
    return os.getenv('ENVIRONMENT', 'production').lower() == 'development'

def is_production() -> bool:
    """Check if running in production mode"""
    return os.getenv('ENVIRONMENT', 'production').lower() == 'production'

# ========== Initialization ==========
if __name__ == "__main__":
    setup_environment()
    config = create_config()
    print("Configuration loaded successfully")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'production')}")
    print(f"Log level: {config.logging.LOG_LEVEL}")
    print(f"Database: {config.database.DATABASE_FILE}")
    print(f"Poll interval: {config.flight_tracking.POLL_INTERVAL_SECONDS}s")
    print(f"Gemini API keys: {len(config.ai.GEMINI_API_KEYS)} configured")