# -*- coding: utf-8 -*-
"""
Enhanced Military Flight Tracker Bot with Gemini AI Integration
Version: 2.0 - Advanced Intelligence System
Author: AI Assistant
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
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
import signal
import traceback
import sqlite3
from dataclasses import dataclass
from enum import Enum

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
import aiohttp
import google.generativeai as genai

# Telegram imports
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.error import TelegramError, NetworkError, TimedOut

# ========== Configuration ==========
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
    
    # Gemini AI Configuration
    GEMINI_API_KEYS = [
        "YOUR_GEMINI_API_KEY_1",
        "YOUR_GEMINI_API_KEY_2", 
        "YOUR_GEMINI_API_KEY_3"
    ]
    
    # Database Configuration
    DATABASE_FILE = "military_aircraft.db"
    
    # Flight Data Sources
    FLIGHT_SOURCES = [
        "https://api.adsb.lol/v2/mil",
        "https://opensky-network.org/api/states/all",
        "https://api.adsbexchange.com/v2/mil"
    ]
    
    # Geographic Regions
    USA_BBOX = (24.0, 50.0, -125.0, -66.0)
    
    # ICAO Country Ranges
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
    }

# ========== Enums and Data Classes ==========
class FlightStatus(Enum):
    UNKNOWN = "unknown"
    IDENTIFIED = "identified"
    ANALYZED = "analyzed"
    ERROR = "error"

@dataclass
class FlightData:
    icao24: str
    callsign: str
    lat: float
    lon: float
    alt: int
    vel: int
    heading: Optional[int]
    typecode: str
    country: str
    source: str
    timestamp: datetime
    status: FlightStatus = FlightStatus.UNKNOWN
    ai_analysis: Optional[Dict] = None

@dataclass
class AIAnalysis:
    persian_role: str
    aircraft_model: str
    operator_analysis: str
    location_context: str
    strategic_importance: int
    confidence_score: float
    analysis_timestamp: datetime

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
    def __init__(self, db_file: str):
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
                    analysis_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    confidence_score REAL,
                    api_used TEXT
                )
            ''')
            
            # Flight history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS flight_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    icao24 TEXT,
                    callsign TEXT,
                    lat REAL,
                    lon REAL,
                    alt INTEGER,
                    vel INTEGER,
                    heading INTEGER,
                    typecode TEXT,
                    country TEXT,
                    source TEXT,
                    timestamp TIMESTAMP,
                    ai_analysis TEXT,
                    FOREIGN KEY (icao24) REFERENCES spotted_aircraft(icao24)
                )
            ''')
            
            # Statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    total_flights INTEGER,
                    military_flights INTEGER,
                    ai_analyses INTEGER,
                    api_errors INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def add_spotted_aircraft(self, icao24: str, callsign: str):
        """Add or update spotted aircraft"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO spotted_aircraft (icao24, callsign, last_seen, total_sightings)
                VALUES (?, ?, CURRENT_TIMESTAMP, 
                    COALESCE((SELECT total_sightings FROM spotted_aircraft WHERE icao24 = ?), 0) + 1)
            ''', (icao24, callsign, icao24))
            conn.commit()
    
    def check_if_spotted(self, icao24: str) -> bool:
        """Check if aircraft was already spotted"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT icao24 FROM spotted_aircraft WHERE icao24 = ?', (icao24,))
            return cursor.fetchone() is not None
    
    def cache_ai_analysis(self, icao24: str, analysis: Dict, confidence: float, api_used: str):
        """Cache AI analysis result"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO ai_analysis_cache 
                (icao24, analysis_data, confidence_score, api_used)
                VALUES (?, ?, ?, ?)
            ''', (icao24, json.dumps(analysis), confidence, api_used))
            conn.commit()
    
    def get_cached_analysis(self, icao24: str) -> Optional[Dict]:
        """Get cached AI analysis"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT analysis_data FROM ai_analysis_cache 
                WHERE icao24 = ? AND created_at > datetime('now', '-24 hours')
            ''', (icao24,))
            result = cursor.fetchone()
            return json.loads(result[0]) if result else None
    
    def add_flight_history(self, flight: FlightData):
        """Add flight to history"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO flight_history 
                (icao24, callsign, lat, lon, alt, vel, heading, typecode, country, source, timestamp, ai_analysis)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                flight.icao24, flight.callsign, flight.lat, flight.lon, 
                flight.alt, flight.vel, flight.heading, flight.typecode,
                flight.country, flight.source, flight.timestamp.isoformat(),
                json.dumps(flight.ai_analysis) if flight.ai_analysis else None
            ))
            conn.commit()
    
    def get_statistics(self) -> Dict:
        """Get system statistics"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Get total spotted aircraft
            cursor.execute('SELECT COUNT(*) FROM spotted_aircraft')
            total_aircraft = cursor.fetchone()[0]
            
            # Get today's flights
            cursor.execute('''
                SELECT COUNT(*) FROM flight_history 
                WHERE date(timestamp) = date('now')
            ''')
            today_flights = cursor.fetchone()[0]
            
            # Get AI analyses count
            cursor.execute('''
                SELECT COUNT(*) FROM ai_analysis_cache 
                WHERE created_at > datetime('now', '-24 hours')
            ''')
            ai_analyses = cursor.fetchone()[0]
            
            return {
                'total_aircraft': total_aircraft,
                'today_flights': today_flights,
                'ai_analyses_24h': ai_analyses
            }

# ========== AI Analysis Engine ==========
class GeminiAIAnalyzer:
    def __init__(self, api_keys: List[str]):
        self.api_keys = api_keys
        self.current_key_index = 0
        self.session = None
        self.setup_gemini()
    
    def setup_gemini(self):
        """Setup Gemini AI with current API key"""
        try:
            current_key = self.api_keys[self.current_key_index]
            genai.configure(api_key=current_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info(f"Gemini AI configured with key index {self.current_key_index}")
        except Exception as e:
            logger.error(f"Failed to setup Gemini AI: {e}")
    
    def switch_api_key(self):
        """Switch to next API key"""
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self.setup_gemini()
        logger.info(f"Switched to Gemini API key index {self.current_key_index}")
    
    def create_analysis_prompt(self, flight: FlightData) -> str:
        """Create comprehensive analysis prompt for Gemini"""
        prompt = f"""
You are a senior military aviation intelligence analyst with access to classified flight tracking data. Your expertise includes aircraft identification, military operations analysis, and strategic threat assessment.

FLIGHT DATA TO ANALYZE:
- ICAO Code: {flight.icao24}
- Callsign: {flight.callsign}
- Type Code: {flight.typecode}
- Coordinates: {flight.lat:.6f}, {flight.lon:.6f}
- Altitude: {flight.alt} meters
- Speed: {flight.vel} km/h
- Heading: {flight.heading} degrees
- Country: {flight.country}
- Data Source: {flight.source}
- Timestamp: {flight.timestamp.isoformat()}

ANALYSIS REQUIREMENTS:
1. Identify the exact military role and full aircraft model name
2. Determine the most likely operator based on callsign patterns and country
3. Provide strategic location analysis (max 15 words) describing the flight's current position significance
4. Assess strategic importance on a scale of 1-10
5. Provide confidence score (0.0-1.0) for your analysis

RESPONSE FORMAT (JSON only):
{{
    "persian_role": "نقش شناسایی‌شده به فارسی",
    "aircraft_model": "نام کامل و دقیق مدل هواپیما",
    "operator_analysis": "نام کامل اپراتور شناسایی‌شده",
    "location_context": "تحلیل متنی کوتاه از موقعیت جغرافیایی",
    "strategic_importance": 8,
    "confidence_score": 0.85
}}

Analyze this flight data and provide your assessment in the exact JSON format above.
"""
        return prompt
    
    async def analyze_flight(self, flight: FlightData) -> Optional[AIAnalysis]:
        """Analyze flight using Gemini AI"""
        max_retries = len(self.api_keys)
        
        for attempt in range(max_retries):
            try:
                prompt = self.create_analysis_prompt(flight)
                response = await asyncio.to_thread(self.model.generate_content, prompt)
                
                if response and response.text:
                    # Extract JSON from response
                    json_text = response.text.strip()
                    if json_text.startswith('```json'):
                        json_text = json_text[7:-3]
                    elif json_text.startswith('```'):
                        json_text = json_text[3:-3]
                    
                    analysis_data = json.loads(json_text)
                    
                    return AIAnalysis(
                        persian_role=analysis_data.get('persian_role', 'نقش نامشخص'),
                        aircraft_model=analysis_data.get('aircraft_model', 'N/A'),
                        operator_analysis=analysis_data.get('operator_analysis', 'N/A'),
                        location_context=analysis_data.get('location_context', 'موقعیت نامشخص'),
                        strategic_importance=analysis_data.get('strategic_importance', 5),
                        confidence_score=analysis_data.get('confidence_score', 0.5),
                        analysis_timestamp=datetime.now(timezone.utc)
                    )
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error in Gemini response: {e}")
                continue
            except Exception as e:
                logger.error(f"Gemini API error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    self.switch_api_key()
                    await asyncio.sleep(2)
                continue
        
        logger.error("All Gemini API keys failed")
        return None

# ========== Flight Data Collector ==========
class FlightDataCollector:
    def __init__(self):
        self.session = self.create_http_session()
        self.db = DatabaseManager(Config.DATABASE_FILE)
    
    def create_http_session(self) -> requests.Session:
        """Create HTTP session with retry strategy"""
        session = requests.Session()
        retry = Retry(
            total=3,
            read=3,
            connect=3,
            backoff_factor=0.5,
            status_forcelist=(500, 502, 503, 504)
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
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
    
    def is_within_usa_bbox(self, lat: float, lon: float) -> bool:
        """Check if coordinates are within USA bounding box"""
        min_lat, max_lat, min_lon, max_lon = Config.USA_BBOX
        return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon
    
    async def fetch_from_adsblol(self) -> List[FlightData]:
        """Fetch military flights from ADSB.lol"""
        flights = []
        try:
            logger.info("Fetching military data from ADSB.lol...")
            response = self.session.get(Config.FLIGHT_SOURCES[0], timeout=25)
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
                    flights.append(flight)
            
            logger.info(f"ADSB.lol: Retrieved {len(flights)} military flights")
            
        except Exception as e:
            logger.error(f"ADSB.lol Error: {e}")
        
        return flights
    
    async def collect_all_flights(self) -> List[FlightData]:
        """Collect flights from all available sources"""
        all_flights = []
        
        # Primary source: ADSB.lol
        flights = await self.fetch_from_adsblol()
        all_flights.extend(flights)
        
        # Add more sources here if needed
        # flights = await self.fetch_from_opensky()
        # all_flights.extend(flights)
        
        return all_flights

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
            self.api_errors = 0
    
    def increment_scan(self):
        with self._lock:
            self.scan_cycles += 1
    
    def increment_military_flight(self):
        with self._lock:
            self.military_flights_found += 1
    
    def increment_ai_analysis(self):
        with self._lock:
            self.ai_analyses_performed += 1
    
    def increment_api_error(self):
        with self._lock:
            self.api_errors += 1
    
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
                f"🤖 *تحلیل‌های هوش مصنوعی:* *{self.ai_analyses_performed}*\n"
                f"❌ *خطاهای API:* *{self.api_errors}*"
            )
            report += f"\n⏰ *زمان گزارش:* `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}` UTC"
            return report

# ========== Notification System ==========
class NotificationSystem:
    def __init__(self, bot: Bot, db: DatabaseManager):
        self.bot = bot
        self.db = db
    
    async def send_enhanced_notification(self, flight: FlightData, analysis: AIAnalysis) -> bool:
        """Send enhanced notification with AI analysis"""
        try:
            # Create interactive keyboard
            keyboard = [
                [InlineKeyboardButton("📍 موقعیت در نقشه", url=f"https://globe.adsbexchange.com/?icao={flight.icao24}")],
                [InlineKeyboardButton("📊 جزئیات بیشتر", callback_data=f"details_{flight.icao24}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Format message with AI analysis
            message = (
                f"🚁 *شناسایی پرواز نظامی هوشمند*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"**🎯 نقش:** {analysis.persian_role}\n"
                f"**✈️ مدل:** {analysis.aircraft_model}\n"
                f"**🏢 اپراتور:** {analysis.operator_analysis}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"**📡 اطلاعات پروازی:**\n"
                f"   • *علامت تماس:* `{flight.callsign}`\n"
                f"   • *کشور:* {flight.country}\n"
                f"   • *شناسه ICAO:* `{flight.icao24}`\n"
                f"   • *ارتفاع:* {flight.alt:,} متر\n"
                f"   • *سرعت:* {flight.vel:,} کیلومتر بر ساعت\n"
                f"   • *جهت:* {flight.heading or 'N/A'} درجه\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"**🧠 تحلیل هوشمند:**\n"
                f"   • *موقعیت:* {analysis.location_context}\n"
                f"   • *اهمیت استراتژیک:* {analysis.strategic_importance}/10\n"
                f"   • *اعتماد تحلیل:* {analysis.confidence_score:.0%}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"**📊 جزئیات فنی:**\n"
                f"   • *منبع داده:* {flight.source}\n"
                f"   • *زمان شناسایی:* `{datetime.now(timezone.utc).strftime('%H:%M:%S')}` UTC\n"
                f"   • *نوع هواپیما:* `{flight.typecode}`"
            )
            
            await self.bot.send_message(
                chat_id=Config.CHANNEL_ID,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=False
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send enhanced notification: {e}", exc_info=True)
            return False
    
    async def send_fallback_notification(self, flight: FlightData) -> bool:
        """Send fallback notification without AI analysis"""
        try:
            message = (
                f"🚁 *شناسایی پرواز نظامی*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"**📡 اطلاعات پروازی:**\n"
                f"   • *علامت تماس:* `{flight.callsign}`\n"
                f"   • *کشور:* {flight.country}\n"
                f"   • *شناسه ICAO:* `{flight.icao24}`\n"
                f"   • *ارتفاع:* {flight.alt:,} متر\n"
                f"   • *سرعت:* {flight.vel:,} کیلومتر بر ساعت\n"
                f"   • *جهت:* {flight.heading or 'N/A'} درجه\n"
                f"   • *نوع هواپیما:* `{flight.typecode}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"**📊 جزئیات فنی:**\n"
                f"   • *منبع داده:* {flight.source}\n"
                f"   • *زمان شناسایی:* `{datetime.now(timezone.utc).strftime('%H:%M:%S')}` UTC\n"
                f"   • *نقشه:* [مشاهده آنلاین](https://globe.adsbexchange.com/?icao={flight.icao24})"
            )
            
            await self.bot.send_message(
                chat_id=Config.CHANNEL_ID,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=False
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send fallback notification: {e}", exc_info=True)
            return False

# ========== Main Bot Class ==========
class MilitaryTrackerBot:
    def __init__(self):
        self.db = DatabaseManager(Config.DATABASE_FILE)
        self.ai_analyzer = GeminiAIAnalyzer(Config.GEMINI_API_KEYS)
        self.data_collector = FlightDataCollector()
        self.notification_system = None
        self.stats = StatisticsTracker()
        self.notification_queue = asyncio.Queue()
        self.is_running = False
    
    async def initialize(self, bot: Bot):
        """Initialize bot components"""
        self.notification_system = NotificationSystem(bot, self.db)
        logger.info("Military Tracker Bot initialized successfully")
    
    async def process_flight(self, flight: FlightData) -> None:
        """Process a single flight with AI analysis"""
        try:
            # Check if already spotted
            if self.db.check_if_spotted(flight.icao24):
                return
            
            # Add to spotted aircraft
            self.db.add_spotted_aircraft(flight.icao24, flight.callsign)
            
            # Try AI analysis
            analysis = await self.ai_analyzer.analyze_flight(flight)
            
            if analysis:
                # Cache the analysis
                self.db.cache_ai_analysis(
                    flight.icao24, 
                    analysis.__dict__, 
                    analysis.confidence_score,
                    f"gemini_{self.ai_analyzer.current_key_index}"
                )
                
                flight.ai_analysis = analysis.__dict__
                flight.status = FlightStatus.ANALYZED
                self.stats.increment_ai_analysis()
                
                # Send enhanced notification
                if await self.notification_system.send_enhanced_notification(flight, analysis):
                    self.stats.increment_military_flight()
            else:
                # Fallback to cached analysis or basic notification
                cached_analysis = self.db.get_cached_analysis(flight.icao24)
                if cached_analysis:
                    flight.ai_analysis = cached_analysis
                    flight.status = FlightStatus.ANALYZED
                    # Send notification with cached data
                    analysis_obj = AIAnalysis(**cached_analysis)
                    if await self.notification_system.send_enhanced_notification(flight, analysis_obj):
                        self.stats.increment_military_flight()
                else:
                    # Send basic notification
                    flight.status = FlightStatus.IDENTIFIED
                    if await self.notification_system.send_fallback_notification(flight):
                        self.stats.increment_military_flight()
            
            # Add to flight history
            self.db.add_flight_history(flight)
            
        except Exception as e:
            logger.error(f"Error processing flight {flight.icao24}: {e}", exc_info=True)
            self.stats.increment_api_error()
    
    async def flight_check_cycle(self) -> None:
        """Main flight checking cycle"""
        try:
            self.stats.increment_scan()
            logger.info(f"Starting flight check cycle #{self.stats.scan_cycles}")
            
            # Collect flights from all sources
            flights = await self.data_collector.collect_all_flights()
            
            # Process each flight
            for flight in flights:
                # Skip USA flights
                if self.data_collector.is_within_usa_bbox(flight.lat, flight.lon):
                    logger.info(f"Filtering out USA aircraft: {flight.callsign}")
                    continue
                
                # Process flight
                await self.process_flight(flight)
                
                # Rate limiting
                await asyncio.sleep(1)
            
            logger.info(f"Completed flight check cycle. Processed {len(flights)} flights")
            
        except Exception as e:
            logger.error(f"Error in flight check cycle: {e}", exc_info=True)
            self.stats.increment_api_error()
    
    async def start_monitoring(self):
        """Start the monitoring loop"""
        self.is_running = True
        logger.info("Starting flight monitoring...")
        
        while self.is_running:
            try:
                await self.flight_check_cycle()
                await asyncio.sleep(Config.POLL_INTERVAL_SECONDS)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(30)  # Wait before retry
    
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.is_running = False
        logger.info("Stopping flight monitoring...")

# ========== Global Bot Instance ==========
bot_instance = MilitaryTrackerBot()

# ========== Command Handlers ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    await update.message.reply_text(
        "🚀 *ربات ردیاب هوشمند هواپیماهای نظامی*\n\n"
        "🤖 *قابلیت‌های پیشرفته:*\n"
        "• تحلیل هوش مصنوعی با Gemini AI\n"
        "• شناسایی دقیق نقش و مدل هواپیما\n"
        "• تحلیل موقعیت استراتژیک\n"
        "• ارزیابی اهمیت پروازها\n\n"
        "📋 *دستورات موجود:*\n"
        "/status - مشاهده وضعیت ربات\n"
        "/stats - آمار تفصیلی سیستم\n"
        "/test - ارسال پیام تست\n"
        "/help - راهنمای کامل",
        parse_mode=ParseMode.MARKDOWN
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command"""
    try:
        stats_data = bot_instance.db.get_statistics()
        status_msg = (
            "📊 *وضعیت سیستم*\n\n"
            f"✅ *وضعیت:* فعال\n"
            f"🔄 *بازه بررسی:* هر {Config.POLL_INTERVAL_SECONDS} ثانیه\n"
            f"✈️ *هواپیماهای شناسایی شده:* {stats_data['total_aircraft']}\n"
            f"📈 *پروازهای امروز:* {stats_data['today_flights']}\n"
            f"🤖 *تحلیل‌های AI (24h):* {stats_data['ai_analyses_24h']}\n"
            f"⏰ *زمان سرور:* `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}` UTC"
        )
        await update.message.reply_text(status_msg, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در دریافت وضعیت: {e}")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stats command"""
    try:
        report = bot_instance.stats.get_report()
        await update.message.reply_text(report, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در دریافت آمار: {e}")

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /test command"""
    try:
        test_msg = (
            f"🧪 *پیام تست سیستم*\n\n"
            f"✅ *وضعیت:* سیستم فعال\n"
            f"⏰ *زمان:* `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}` UTC\n"
            f"🤖 *نسخه:* 2.0 - Advanced Intelligence"
        )
        await context.bot.send_message(
            chat_id=Config.CHANNEL_ID, 
            text=test_msg, 
            parse_mode=ParseMode.MARKDOWN
        )
        await update.message.reply_text("✅ پیام تست به کانال ارسال شد.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در ارسال تست: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = (
        "📚 *راهنمای کامل ربات*\n\n"
        "🤖 *درباره ربات:*\n"
        "این ربات با استفاده از هوش مصنوعی پیشرفته، پروازهای نظامی را شناسایی و تحلیل می‌کند.\n\n"
        "🔧 *دستورات:*\n"
        "/start - شروع و معرفی ربات\n"
        "/status - وضعیت فعلی سیستم\n"
        "/stats - آمار تفصیلی عملکرد\n"
        "/test - ارسال پیام تست\n"
        "/help - این راهنما\n\n"
        "🧠 *قابلیت‌های هوش مصنوعی:*\n"
        "• شناسایی دقیق نقش هواپیما\n"
        "• تحلیل موقعیت استراتژیک\n"
        "• ارزیابی اهمیت پرواز\n"
        "• یادگیری از داده‌های قبلی\n\n"
        "📊 *منابع داده:*\n"
        "• ADSB.lol\n"
        "• OpenSky Network\n"
        "• ADSB Exchange"
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def details_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle details button callback"""
    query = update.callback_query
    await query.answer()
    
    icao24 = query.data.split('_')[1]
    
    # Get flight details from database
    try:
        with sqlite3.connect(Config.DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM flight_history 
                WHERE icao24 = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (icao24,))
            result = cursor.fetchone()
            
            if result:
                details_msg = (
                    f"📊 *جزئیات پرواز*\n\n"
                    f"**ICAO:** `{result[1]}`\n"
                    f"**Callsign:** `{result[2]}`\n"
                    f"**موقعیت:** {result[3]:.6f}, {result[4]:.6f}\n"
                    f"**ارتفاع:** {result[5]:,} متر\n"
                    f"**سرعت:** {result[6]:,} کیلومتر بر ساعت\n"
                    f"**جهت:** {result[7] or 'N/A'} درجه\n"
                    f"**نوع:** `{result[8]}`\n"
                    f"**کشور:** {result[9]}\n"
                    f"**منبع:** {result[10]}\n"
                    f"**زمان:** {result[11]}"
                )
                await query.edit_message_text(details_msg, parse_mode=ParseMode.MARKDOWN)
            else:
                await query.edit_message_text("❌ اطلاعات پرواز یافت نشد.")
    except Exception as e:
        await query.edit_message_text(f"❌ خطا در دریافت جزئیات: {e}")

# ========== Job Handlers ==========
async def periodic_check_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Periodic flight check job"""
    await bot_instance.flight_check_cycle()

async def hourly_report_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Hourly statistics report job"""
    try:
        report = bot_instance.stats.get_report()
        await context.bot.send_message(
            chat_id=Config.CHANNEL_ID,
            text=report,
            parse_mode=ParseMode.MARKDOWN
        )
        bot_instance.stats.reset()
    except Exception as e:
        logger.error(f"Failed to send hourly report: {e}")

# ========== Signal Handlers ==========
def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}. Shutting down...")
    bot_instance.stop_monitoring()
    sys.exit(0)

# ========== Main Application ==========
async def post_init(application: Application) -> None:
    """Post-initialization setup"""
    logger.info("="*80)
    logger.info("🚀 Military Aircraft Tracker Bot v2.0 - Advanced Intelligence System")
    logger.info("="*80)
    
    # Initialize bot
    await bot_instance.initialize(application.bot)
    
    # Setup job queue
    job_queue = application.job_queue
    job_queue.run_repeating(
        periodic_check_job, 
        interval=Config.POLL_INTERVAL_SECONDS, 
        first=10
    )
    job_queue.run_repeating(
        hourly_report_job, 
        interval=3600, 
        first=3600
    )
    
    # Start monitoring in background
    asyncio.create_task(bot_instance.start_monitoring())
    
    logger.info("✅ Bot started successfully with all features enabled")
    logger.info("🤖 AI Analysis: ENABLED")
    logger.info("📊 Database: ENABLED")
    logger.info("🔄 Monitoring: ACTIVE")

def main():
    """Main application entry point"""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create application
        application = Application.builder().token(Config.TOKEN).post_init(post_init).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("stats", stats_command))
        application.add_handler(CommandHandler("test", test_command))
        application.add_handler(CommandHandler("help", help_command))
        
        # Add callback query handler
        application.add_handler(CallbackQueryHandler(details_callback, pattern="^details_"))
        
        # Run application
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.critical(f"Fatal error in main loop: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        sys.exit(1)
    
    # Check required environment variables
    if Config.TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("Error: Please set your Telegram bot token in the Config class.")
        sys.exit(1)
    
    if not any(key != "YOUR_GEMINI_API_KEY_1" for key in Config.GEMINI_API_KEYS):
        print("Error: Please set at least one Gemini API key in the Config class.")
        sys.exit(1)
    
    main()