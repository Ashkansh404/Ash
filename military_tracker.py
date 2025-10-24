# -*- coding: utf-8 -*-
"""
Advanced Military Aircraft Tracker Bot with Gemini AI Integration
Version 2.0 - Enhanced with AI Analysis and Multi-API Support
"""

import os
import sys
import time
import logging
import threading
import asyncio
import json
import io
import hashlib
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
import signal
import traceback
from dataclasses import dataclass
from enum import Enum

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
import aiohttp
import google.generativeai as genai

# Telegram imports
from telegram import Bot, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TelegramError

# ========== Configuration and Constants ==========
class Config:
    # Telegram Configuration
    TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    CHANNEL_ID = "YOUR_CHANNEL_ID"
    ADMIN_ID = 7717672777
    
    # Polling Configuration
    POLL_INTERVAL_SECONDS = 30
    MEMORY_CLEANUP_HOURS = 24
    
    # Logging Configuration
    LOG_LEVEL = "INFO"
    LOG_FILE = "military_tracker.log"
    
    # Gemini AI Configuration (Multiple API Keys for Redundancy)
    GEMINI_API_KEYS = [
        "YOUR_GEMINI_API_KEY_1",
        "YOUR_GEMINI_API_KEY_2", 
        "YOUR_GEMINI_API_KEY_3"
    ]
    GEMINI_MODEL = "gemini-2.0-flash-exp"
    GEMINI_TIMEOUT = 30
    GEMINI_RATE_LIMIT_DELAY = 2
    
    # Flight Tracking APIs
    ADSB_LOL_API = "https://api.adsb.lol/v2/mil"
    OPENSKY_API = "https://opensky-network.org/api/states/all"
    ADSBX_API = "https://adsbexchange-com1.p.rapidapi.com/v2/mil"
    
    # Database Configuration
    DATABASE_FILE = "military_aircraft.db"
    
    # Geographic Configuration
    USA_BBOX = (24.0, 50.0, -125.0, -66.0)
    
    # ICAO Country Ranges (Extended)
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
        "South Korea": (0x71C000, 0x71FFFF),
        "Australia": (0x7C0000, 0x7FFFFF),
        "Brazil": (0xE00000, 0xE3FFFF),
        "Mexico": (0x0D0000, 0x0DFFFF),
        "Egypt": (0x010000, 0x01FFFF),
        "Pakistan": (0x760000, 0x767FFF),
    }

# ========== Data Classes ==========
@dataclass
class FlightData:
    icao24: str
    callsign: str
    lat: float
    lon: float
    alt: int
    vel: int
    heading: Optional[float]
    typecode: str
    country: str
    source: str
    timestamp: datetime

@dataclass
class AIAnalysis:
    persian_role: str
    aircraft_model: str
    operator_analysis: str
    location_context: str
    strategic_importance: int
    confidence_score: float
    threat_level: str
    mission_type: str

class ThreatLevel(Enum):
    LOW = "کم"
    MEDIUM = "متوسط"
    HIGH = "بالا"
    CRITICAL = "بحرانی"

# ========== Logging Setup ==========
def setup_logging():
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# ========== Database Manager ==========
class DatabaseManager:
    def __init__(self, db_file: str = Config.DATABASE_FILE):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Initialize database with all required tables"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Spotted aircraft table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS spotted_aircraft (
                    icao24 TEXT PRIMARY KEY,
                    callsign TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_sightings INTEGER DEFAULT 1
                )
            ''')
            
            # AI analysis cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_analysis_cache (
                    icao24 TEXT PRIMARY KEY,
                    typecode TEXT,
                    country TEXT,
                    persian_role TEXT,
                    aircraft_model TEXT,
                    operator_analysis TEXT,
                    location_context TEXT,
                    strategic_importance INTEGER,
                    confidence_score REAL,
                    threat_level TEXT,
                    mission_type TEXT,
                    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    hash_key TEXT UNIQUE
                )
            ''')
            
            # Flight patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS flight_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    icao24 TEXT,
                    pattern_type TEXT,
                    coordinates TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (icao24) REFERENCES spotted_aircraft (icao24)
                )
            ''')
            
            # Unidentified aircraft table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS unidentified_aircraft (
                    icao24 TEXT PRIMARY KEY,
                    callsign TEXT,
                    typecode TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sighting_count INTEGER DEFAULT 1
                )
            ''')
            
            conn.commit()
    
    def add_spotted_aircraft(self, icao24: str, callsign: str):
        """Add or update spotted aircraft"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO spotted_aircraft 
                (icao24, callsign, last_seen, total_sightings)
                VALUES (?, ?, CURRENT_TIMESTAMP, 
                    COALESCE((SELECT total_sightings FROM spotted_aircraft WHERE icao24 = ?), 0) + 1)
            ''', (icao24, callsign, icao24))
            conn.commit()
    
    def check_if_spotted(self, icao24: str) -> bool:
        """Check if aircraft was already spotted"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM spotted_aircraft WHERE icao24 = ?', (icao24,))
            return cursor.fetchone() is not None
    
    def cache_ai_analysis(self, icao24: str, typecode: str, country: str, analysis: AIAnalysis):
        """Cache AI analysis for future use"""
        hash_key = hashlib.md5(f"{icao24}_{typecode}_{country}".encode()).hexdigest()
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO ai_analysis_cache 
                (icao24, typecode, country, persian_role, aircraft_model, 
                 operator_analysis, location_context, strategic_importance, 
                 confidence_score, threat_level, mission_type, hash_key)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (icao24, typecode, country, analysis.persian_role, analysis.aircraft_model,
                  analysis.operator_analysis, analysis.location_context, analysis.strategic_importance,
                  analysis.confidence_score, analysis.threat_level, analysis.mission_type, hash_key))
            conn.commit()
    
    def get_cached_analysis(self, icao24: str, typecode: str, country: str) -> Optional[AIAnalysis]:
        """Get cached AI analysis if available"""
        hash_key = hashlib.md5(f"{icao24}_{typecode}_{country}".encode()).hexdigest()
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT persian_role, aircraft_model, operator_analysis, location_context,
                       strategic_importance, confidence_score, threat_level, mission_type
                FROM ai_analysis_cache WHERE hash_key = ?
            ''', (hash_key,))
            result = cursor.fetchone()
            if result:
                return AIAnalysis(
                    persian_role=result[0],
                    aircraft_model=result[1],
                    operator_analysis=result[2],
                    location_context=result[3],
                    strategic_importance=result[4],
                    confidence_score=result[5],
                    threat_level=result[6],
                    mission_type=result[7]
                )
        return None
    
    def add_unidentified_aircraft(self, icao24: str, callsign: str, typecode: str):
        """Add unidentified aircraft to tracking"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO unidentified_aircraft 
                (icao24, callsign, typecode, last_seen, sighting_count)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, 
                    COALESCE((SELECT sighting_count FROM unidentified_aircraft WHERE icao24 = ?), 0) + 1)
            ''', (icao24, callsign, typecode, icao24))
            conn.commit()
    
    def get_unidentified_aircraft(self) -> List[Tuple]:
        """Get all unidentified aircraft records"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT icao24, callsign, typecode, last_seen 
                FROM unidentified_aircraft 
                ORDER BY last_seen DESC
            ''')
            return cursor.fetchall()
    
    def clear_old_data(self):
        """Clear old data to prevent database bloat"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=Config.MEMORY_CLEANUP_HOURS)
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM spotted_aircraft WHERE last_seen < ?', (cutoff_time,))
            cursor.execute('DELETE FROM ai_analysis_cache WHERE analysis_timestamp < ?', (cutoff_time,))
            cursor.execute('DELETE FROM flight_patterns WHERE timestamp < ?', (cutoff_time,))
            conn.commit()

# ========== AI Analysis Engine ==========
class GeminiAIAnalyzer:
    def __init__(self):
        self.current_api_key_index = 0
        self.rate_limiter = asyncio.Semaphore(1)
        self.setup_gemini()
    
    def setup_gemini(self):
        """Setup Gemini AI with current API key"""
        if Config.GEMINI_API_KEYS:
            genai.configure(api_key=Config.GEMINI_API_KEYS[self.current_api_key_index])
    
    def switch_api_key(self):
        """Switch to next available API key"""
        self.current_api_key_index = (self.current_api_key_index + 1) % len(Config.GEMINI_API_KEYS)
        self.setup_gemini()
        logger.info(f"Switched to Gemini API key index: {self.current_api_key_index}")
    
    def create_analysis_prompt(self, flight_data: FlightData) -> str:
        """Create comprehensive prompt for Gemini AI analysis"""
        prompt = f"""
شما یک تحلیلگر ارشد اطلاعات هوانوردی نظامی با دسترسی به داده‌های طبقه‌بندی‌شده هستید. 
لطفاً بر اساس اطلاعات زیر، تحلیل کاملی از این پرواز نظامی ارائه دهید:

=== اطلاعات پرواز ===
شناسه ICAO: {flight_data.icao24}
علامت تماس: {flight_data.callsign}
کد نوع هواپیما: {flight_data.typecode}
کشور ثبت: {flight_data.country}
مختصات: {flight_data.lat:.6f}, {flight_data.lon:.6f}
ارتفاع: {flight_data.alt:,} متر
سرعت: {flight_data.vel:,} کیلومتر بر ساعت
جهت: {flight_data.heading if flight_data.heading else 'نامشخص'} درجه
منبع داده: {flight_data.source}
زمان شناسایی: {flight_data.timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC

=== وظایف تحلیل ===
1. شناسایی دقیق نقش و مدل هواپیما بر اساس کد نوع و سایر شواهد
2. تحلیل موقعیت مکانی و اهمیت استراتژیک آن (حداکثر 15 کلمه)
3. شناسایی اپراتور احتمالی بر اساس کال‌ساین و کشور
4. ارزیابی اهمیت استراتژیک (1-10)
5. تعیین سطح تهدید (کم/متوسط/بالا/بحرانی)
6. تشخیص نوع ماموریت احتمالی

=== قوانین مهم ===
- پاسخ باید حتماً در قالب JSON باشد
- از اطلاعات دقیق و به‌روز استفاده کنید
- در صورت عدم اطمینان، سطح اعتماد را کاهش دهید
- تحلیل باید بر اساس الگوهای شناخته‌شده هوانوردی نظامی باشد

لطفاً پاسخ خود را در قالب زیر ارائه دهید:
"""
        return prompt
    
    async def analyze_flight(self, flight_data: FlightData) -> Optional[AIAnalysis]:
        """Analyze flight data using Gemini AI"""
        async with self.rate_limiter:
            try:
                # Check cache first
                cached = database.get_cached_analysis(
                    flight_data.icao24, flight_data.typecode, flight_data.country
                )
                if cached:
                    logger.info(f"Using cached analysis for {flight_data.icao24}")
                    return cached
                
                # Create prompt
                prompt = self.create_analysis_prompt(flight_data)
                
                # Generate content with Gemini
                model = genai.GenerativeModel(Config.GEMINI_MODEL)
                response = await asyncio.to_thread(
                    model.generate_content, prompt
                )
                
                # Parse JSON response
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:-3]
                elif response_text.startswith('```'):
                    response_text = response_text[3:-3]
                
                analysis_data = json.loads(response_text)
                
                # Create AIAnalysis object
                analysis = AIAnalysis(
                    persian_role=analysis_data.get('persian_role', 'نقش نامشخص'),
                    aircraft_model=analysis_data.get('aircraft_model', 'مدل نامشخص'),
                    operator_analysis=analysis_data.get('operator_analysis', 'اپراتور نامشخص'),
                    location_context=analysis_data.get('location_context', 'موقعیت نامشخص'),
                    strategic_importance=analysis_data.get('strategic_importance', 5),
                    confidence_score=analysis_data.get('confidence_score', 0.7),
                    threat_level=analysis_data.get('threat_level', 'متوسط'),
                    mission_type=analysis_data.get('mission_type', 'ماموریت نامشخص')
                )
                
                # Cache the analysis
                database.cache_ai_analysis(
                    flight_data.icao24, flight_data.typecode, flight_data.country, analysis
                )
                
                logger.info(f"AI analysis completed for {flight_data.icao24}")
                return analysis
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {e}")
                return None
            except Exception as e:
                logger.error(f"Gemini AI analysis failed: {e}")
                # Try switching API key
                self.switch_api_key()
                return None

# ========== Flight Data Fetchers ==========
class FlightDataFetcher:
    def __init__(self):
        self.session = self.create_http_session()
    
    def create_http_session(self) -> requests.Session:
        """Create HTTP session with retry strategy"""
        session = requests.Session()
        retry = Retry(
            total=3, read=3, connect=3,
            backoff_factor=0.5,
            status_forcelist=(500, 502, 503, 504)
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    def fetch_from_adsb_lol(self) -> Dict[str, FlightData]:
        """Fetch military flights from ADSB.lol"""
        flights = {}
        try:
            logger.info("Fetching data from ADSB.lol...")
            response = self.session.get(Config.ADSB_LOL_API, timeout=25)
            response.raise_for_status()
            data = response.json()
            
            if 'ac' in data and data['ac']:
                for aircraft in data['ac']:
                    alt = aircraft.get('alt_baro')
                    if ('lat' not in aircraft or 'lon' not in aircraft or 
                        (isinstance(alt, str) and alt == 'ground') or 
                        (isinstance(alt, (int, float)) and alt <= 0)):
                        continue
                    
                    flight = FlightData(
                        icao24=aircraft['hex'].lower(),
                        callsign=aircraft.get('flight', "N/A").strip(),
                        lat=aircraft['lat'],
                        lon=aircraft['lon'],
                        alt=int(alt * 0.3048) if isinstance(alt, (int, float)) else 0,
                        vel=int(aircraft.get('gs', 0) * 1.852),
                        heading=aircraft.get('track'),
                        typecode=aircraft.get('t', 'N/A'),
                        country=self.get_country_from_icao(aircraft['hex']),
                        source='ADSB.lol',
                        timestamp=datetime.now(timezone.utc)
                    )
                    flights[flight.icao24] = flight
                
                logger.info(f"ADSB.lol: Retrieved {len(flights)} military flights")
        except Exception as e:
            logger.error(f"ADSB.lol Error: {e}")
        
        return flights
    
    def get_country_from_icao(self, icao24: str) -> str:
        """Get country from ICAO code"""
        try:
            icao_int = int(icao24, 16)
            for country, (start, end) in Config.ICAO_COUNTRY_RANGES.items():
                if start <= icao_int <= end:
                    return country
            return "Unknown"
        except (ValueError, TypeError):
            return "Invalid ICAO"

# ========== Statistics Tracker ==========
class StatisticsTracker:
    def __init__(self):
        self._lock = threading.Lock()
        self.reset()
    
    def reset(self):
        with self._lock:
            self.start_time = datetime.now(timezone.utc)
            self.scan_cycles = 0
            self.military_flights_found = 0
            self.ai_analyses_performed = 0
            self.cache_hits = 0
    
    def increment_scan(self):
        with self._lock:
            self.scan_cycles += 1
    
    def increment_military_flight(self):
        with self._lock:
            self.military_flights_found += 1
    
    def increment_ai_analysis(self):
        with self._lock:
            self.ai_analyses_performed += 1
    
    def increment_cache_hit(self):
        with self._lock:
            self.cache_hits += 1
    
    def get_report(self) -> str:
        with self._lock:
            duration = datetime.now(timezone.utc) - self.start_time
            h, r = divmod(duration.total_seconds(), 3600)
            m, _ = divmod(r, 60)
            
            report = (
                f"📊 *گزارش وضعیت ساعتی ربات*\n\n"
                f"⏱️ *مدت زمان فعالیت:* {int(h)} ساعت و {int(m)} دقیقه\n"
                f"🔄 *تعداد کل بررسی‌ها:* {self.scan_cycles}\n"
                f"🎯 *پروازهای شناسایی شده:* *{self.military_flights_found}*\n"
                f"🤖 *تحلیل‌های AI انجام شده:* {self.ai_analyses_performed}\n"
                f"💾 *استفاده از کش:* {self.cache_hits}\n"
                f"📈 *نرخ موفقیت AI:* {(self.ai_analyses_performed / max(self.military_flights_found, 1) * 100):.1f}%"
            )
            report += f"\n⏰ *زمان گزارش:* `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}` UTC"
            return report

# ========== Notification System ==========
class NotificationSystem:
    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def send_telegram_notification(self, flight_data: FlightData, analysis: AIAnalysis) -> bool:
        """Send enhanced Telegram notification with AI analysis"""
        try:
            # Determine threat level emoji
            threat_emoji = {
                "کم": "🟢",
                "متوسط": "🟡", 
                "بالا": "🟠",
                "بحرانی": "🔴"
            }.get(analysis.threat_level, "🟡")
            
            # Create enhanced message
            message = (
                f"{threat_emoji} *شناسایی پرواز نظامی*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"**🎯 نقش:** {analysis.persian_role}\n"
                f"**✈️ مدل:** {analysis.aircraft_model}\n"
                f"**🏢 اپراتور:** {analysis.operator_analysis}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"**📡 اطلاعات پروازی:**\n"
                f"   • *علامت تماس:* `{flight_data.callsign}`\n"
                f"   • *کشور:* {flight_data.country}\n"
                f"   • *شناسه ICAO:* `{flight_data.icao24}`\n"
                f"   • *ارتفاع:* {flight_data.alt:,} متر\n"
                f"   • *سرعت:* {flight_data.vel:,} کیلومتر بر ساعت\n"
                f"   • *جهت:* {flight_data.heading if flight_data.heading else 'نامشخص'}°\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"**🌍 تحلیل موقعیت:**\n"
                f"   {analysis.location_context}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"**⚡ ارزیابی تهدید:**\n"
                f"   • *سطح تهدید:* {analysis.threat_level}\n"
                f"   • *اهمیت استراتژیک:* {analysis.strategic_importance}/10\n"
                f"   • *نوع ماموریت:* {analysis.mission_type}\n"
                f"   • *اعتماد تحلیل:* {analysis.confidence_score:.1%}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"**🔍 جزئیات فنی:**\n"
                f"   • *منبع داده:* {flight_data.source}\n"
                f"   • *زمان شناسایی:* `{flight_data.timestamp.strftime('%H:%M:%S')}` UTC\n"
                f"   • *نقشه زنده:* [مشاهده آنلاین](https://globe.adsbexchange.com/?icao={flight_data.icao24})\n"
                f"   • *ردیابی:* [FlightRadar24](https://www.flightradar24.com/{flight_data.icao24})"
            )
            
            await self.bot.send_message(
                chat_id=Config.CHANNEL_ID,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=False
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}", exc_info=True)
            return False

# ========== Main Bot Class ==========
class MilitaryAircraftTracker:
    def __init__(self):
        self.database = DatabaseManager()
        self.ai_analyzer = GeminiAIAnalyzer()
        self.flight_fetcher = FlightDataFetcher()
        self.stats = StatisticsTracker()
        self.notification_system = None
        
    async def check_flights_producer(self, queue: asyncio.Queue) -> None:
        """Main flight checking producer"""
        try:
            self.stats.increment_scan()
            logger.info(f"Starting flight check cycle #{self.stats.scan_cycles}")
            
            # Fetch flights from multiple sources
            all_flights = self.flight_fetcher.fetch_from_adsb_lol()
            
            for icao, flight_data in all_flights.items():
                if not self.database.check_if_spotted(icao):
                    self.database.add_spotted_aircraft(icao, flight_data.callsign)
                    await queue.put(flight_data)
                    logger.info(f"Queued for analysis: {flight_data.callsign} ({icao})")
            
        except Exception as e:
            logger.error(f"Error in flight producer: {e}", exc_info=True)
    
    async def notification_consumer(self, queue: asyncio.Queue) -> None:
        """Notification consumer with AI analysis"""
        logger.info("Notification consumer started")
        
        while True:
            try:
                flight_data = await queue.get()
                
                # Filter out USA flights
                lat, lon = flight_data.lat, flight_data.lon
                min_lat, max_lat, min_lon, max_lon = Config.USA_BBOX
                if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                    logger.info(f"Filtering out USA flight: {flight_data.callsign}")
                    queue.task_done()
                    continue
                
                logger.info(f"Processing non-USA flight: {flight_data.callsign}")
                
                # Get AI analysis
                analysis = await self.ai_analyzer.analyze_flight(flight_data)
                
                if analysis:
                    self.stats.increment_ai_analysis()
                    
                    # Send notification
                    if await self.notification_system.send_telegram_notification(flight_data, analysis):
                        self.stats.increment_military_flight()
                else:
                    # Fallback to basic identification
                    logger.warning(f"AI analysis failed for {flight_data.icao24}, using fallback")
                    self.database.add_unidentified_aircraft(
                        flight_data.icao24, flight_data.callsign, flight_data.typecode
                    )
                
                queue.task_done()
                await asyncio.sleep(Config.GEMINI_RATE_LIMIT_DELAY)
                
            except Exception as e:
                logger.error(f"Error in notification consumer: {e}", exc_info=True)
    
    async def periodic_check(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Periodic flight check job"""
        job_data = context.job.data
        await self.check_flights_producer(job_data['queue'])
    
    async def send_hourly_report(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send hourly statistics report"""
        try:
            await context.bot.send_message(
                chat_id=Config.CHANNEL_ID,
                text=self.stats.get_report(),
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Failed to send hourly report: {e}")
        finally:
            self.stats.reset()
    
    async def daily_cleanup(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Daily cleanup and report"""
        logger.info("Starting daily cleanup...")
        
        # Generate unidentified aircraft report
        records = self.database.get_unidentified_aircraft()
        
        if records:
            report_str = f"گزارش هواپیماهای ناشناس - {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n"
            report_str += "="*50 + "\n\n"
            report_str += f"{'ICAO':<15} {'Callsign':<15} {'Type':<15} {'Last Seen':<20}\n"
            report_str += "-"*65 + "\n"
            
            for record in records:
                icao, callsign, typecode, last_seen = record
                report_str += f"{icao or 'N/A':<15} {callsign or 'N/A':<15} {typecode or 'N/A':<15} {last_seen:<20}\n"
            
            try:
                report_bytes = report_str.encode('utf-8')
                report_file = io.BytesIO(report_bytes)
                report_file.name = f"unidentified_report_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.txt"
                
                await context.bot.send_document(
                    chat_id=Config.ADMIN_ID,
                    document=report_file,
                    caption="گزارش روزانه هواپیماهای ناشناس"
                )
            except Exception as e:
                logger.error(f"Failed to send daily report: {e}")
        
        # Clean old data
        self.database.clear_old_data()
        logger.info("Daily cleanup completed")

# ========== Command Handlers ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler"""
    await update.message.reply_text(
        "🚀 *ربات ردیاب پیشرفته هواپیماهای نظامی*\n\n"
        "🤖 *قابلیت‌های جدید:*\n"
        "• تحلیل هوشمند با Gemini AI\n"
        "• شناسایی دقیق نقش و مدل هواپیما\n"
        "• ارزیابی سطح تهدید\n"
        "• کش هوشمند برای بهبود عملکرد\n\n"
        "📋 *دستورات:*\n"
        "/status - وضعیت ربات\n"
        "/test - ارسال پیام تست\n"
        "/stats - آمار تفصیلی",
        parse_mode=ParseMode.MARKDOWN
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Status command handler"""
    try:
        job_data = context.job_queue.jobs()[0].data
        stats = job_data['stats']
        queue_size = job_data['queue'].qsize()
        
        status_msg = (
            "📊 *وضعیت ربات*\n\n"
            f"✅ *وضعیت:* فعال\n"
            f"🔄 *بازه بررسی:* هر {Config.POLL_INTERVAL_SECONDS} ثانیه\n"
            f"⏳ *صف پردازش:* {queue_size} پرواز\n"
            f"🎯 *پروازهای ارسال شده:* {stats.military_flights_found}\n"
            f"🤖 *تحلیل‌های AI:* {stats.ai_analyses_performed}\n"
            f"💾 *استفاده از کش:* {stats.cache_hits}\n"
            f"⏰ *زمان سرور:* `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}` UTC"
        )
    except (IndexError, AttributeError):
        status_msg = "❌ ربات غیرفعال است"
    
    await update.message.reply_text(status_msg, parse_mode=ParseMode.MARKDOWN)

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test command handler"""
    try:
        test_msg = (
            f"🧪 *پیام تست سیستم*\n\n"
            f"✅ *ربات:* فعال\n"
            f"🤖 *AI:* آماده\n"
            f"📡 *APIs:* متصل\n"
            f"⏰ *زمان:* `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}` UTC"
        )
        await context.bot.send_message(
            chat_id=Config.CHANNEL_ID,
            text=test_msg,
            parse_mode=ParseMode.MARKDOWN
        )
        await update.message.reply_text("✅ پیام تست ارسال شد")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Detailed statistics command"""
    try:
        job_data = context.job_queue.jobs()[0].data
        stats = job_data['stats']
        
        stats_msg = stats.get_report()
        await update.message.reply_text(stats_msg, parse_mode=ParseMode.MARKDOWN)
    except (IndexError, AttributeError):
        await update.message.reply_text("❌ آمار در دسترس نیست")

# ========== Signal Handlers ==========
def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}. Shutting down...")
    sys.exit(0)

# ========== Main Application ==========
async def post_init(application: Application) -> None:
    """Post-initialization setup"""
    logger.info("="*80)
    logger.info("🚀 Advanced Military Aircraft Tracker Bot v2.0")
    logger.info("🤖 Enhanced with Gemini AI Integration")
    logger.info("="*80)
    
    # Initialize tracker
    tracker = MilitaryAircraftTracker()
    tracker.notification_system = NotificationSystem(application.bot)
    
    # Create notification queue
    notification_queue = asyncio.Queue()
    
    # Job data
    job_data = {
        'tracker': tracker,
        'stats': tracker.stats,
        'queue': notification_queue
    }
    
    # Start notification consumer
    application.create_task(tracker.notification_consumer(notification_queue))
    
    # Schedule jobs
    job_queue = application.job_queue
    job_queue.run_repeating(
        tracker.periodic_check,
        interval=Config.POLL_INTERVAL_SECONDS,
        first=10,
        data=job_data
    )
    job_queue.run_repeating(
        tracker.send_hourly_report,
        interval=3600,
        first=3600,
        data=job_data
    )
    job_queue.run_repeating(
        tracker.daily_cleanup,
        interval=timedelta(hours=24),
        first=timedelta(hours=24),
        data=job_data
    )
    
    logger.info("✅ Bot initialized successfully")
    logger.info("🤖 AI analysis engine ready")
    logger.info("📡 Flight tracking active")

def main():
    """Main application entry point"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create application
        application = Application.builder().token(Config.TOKEN).post_init(post_init).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("test", test_command))
        application.add_handler(CommandHandler("stats", stats_command))
        
        # Run bot
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher required")
        sys.exit(1)
    main()