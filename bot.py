# -*- coding: utf-8 -*-
"""
Military Flight Tracker Bot - Enhanced with Gemini AI
Advanced military aviation intelligence system with AI-powered analysis
Version: 15.0 (Gemini-Powered Edition)
"""

import os
import sys
import time
import logging
import threading
import asyncio
import json
import io
import signal
import traceback
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from logging.handlers import RotatingFileHandler

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from telegram import Bot
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TelegramError, RetryAfter, TimedOut

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Import local modules
try:
    import config
    import database as db
except ImportError as e:
    print(f"❌ Error loading modules: {e}")
    print("Please ensure config.py and database.py exist in the same directory.")
    sys.exit(1)

# ========== Enhanced Logging Setup ==========
def setup_logging():
    """Configure advanced logging with rotation"""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()


# ========== Gemini AI Manager ==========
class GeminiAIManager:
    """
    Manages multiple Gemini API keys with automatic rotation and intelligent caching
    """
    
    def __init__(self, api_keys: List[str]):
        self.api_keys = [key for key in api_keys if key and "YOUR_GEMINI" not in key]
        self.current_key_index = 0
        self.key_failure_counts = {i: 0 for i in range(len(self.api_keys))}
        self.key_last_used = {i: None for i in range(len(self.api_keys))}
        self._lock = threading.Lock()
        self.total_requests = 0
        self.successful_requests = 0
        self.cache_hits = 0
        
        if not self.api_keys:
            logger.warning("⚠️ No valid Gemini API keys configured! AI analysis disabled.")
            self.enabled = False
        else:
            self.enabled = True
            self._configure_current_key()
            logger.info(f"✅ Gemini AI Manager initialized with {len(self.api_keys)} API key(s)")
    
    def _configure_current_key(self):
        """Configure Gemini with current API key"""
        if not self.enabled:
            return
        
        try:
            current_key = self.api_keys[self.current_key_index]
            genai.configure(api_key=current_key)
            logger.info(f"🔑 Configured Gemini with API key #{self.current_key_index + 1}")
        except Exception as e:
            logger.error(f"Failed to configure Gemini key #{self.current_key_index + 1}: {e}")
    
    def _rotate_api_key(self) -> bool:
        """Rotate to next available API key"""
        with self._lock:
            if len(self.api_keys) <= 1:
                logger.warning("⚠️ No alternative API keys available for rotation")
                return False
            
            # Find next key with lowest failure count
            best_key_index = min(
                range(len(self.api_keys)),
                key=lambda i: (
                    self.key_failure_counts[i],
                    -(self.key_last_used[i] or 0)
                )
            )
            
            old_index = self.current_key_index
            self.current_key_index = best_key_index
            self._configure_current_key()
            
            logger.info(f"🔄 Rotated API key from #{old_index + 1} to #{best_key_index + 1}")
            return True
    
    def _build_analysis_prompt(self, flight: Dict[str, Any]) -> str:
        """
        Build highly optimized prompt for Gemini AI analysis
        Critical: Prompt quality directly affects analysis accuracy
        """
        prompt = f"""You are a senior military aviation intelligence analyst with access to classified databases and real-time flight tracking systems. Your expertise includes aircraft identification, operational pattern analysis, and strategic threat assessment.

MISSION: Analyze the following military aircraft detection and provide comprehensive intelligence assessment.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AIRCRAFT DETECTION DATA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IDENTIFICATION:
  • ICAO24 Hex Code: {flight.get('icao24', 'UNKNOWN')}
  • Callsign: {flight.get('callsign', 'N/A')}
  • Type Code: {flight.get('typecode', 'N/A')}
  • Registration Country: {flight.get('country', 'Unknown')}

POSITION & FLIGHT DATA:
  • Coordinates: {flight.get('lat', 0):.4f}°N, {flight.get('lon', 0):.4f}°E
  • Altitude: {flight.get('alt', 0):,} meters
  • Velocity: {flight.get('vel', 0):,} km/h
  • Heading: {flight.get('heading', 'N/A')}°
  • Detection Source: {flight.get('source', 'ADSB.lol')}

CONTEXT:
  • Detection Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC
  • Region: {flight.get('region', 'Unknown')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ANALYSIS REQUIREMENTS:

1. AIRCRAFT IDENTIFICATION:
   - Determine the EXACT military role/mission type (in Persian)
   - Identify the COMPLETE aircraft model name (in English with Persian description)
   - Consider: Type code patterns, callsign prefixes, country of origin, altitude/speed profile

2. OPERATOR ANALYSIS:
   - Identify the military operator/unit based on callsign and country
   - Provide full official name (e.g., "US Air Force Air Mobility Command")

3. STRATEGIC LOCATION ANALYSIS:
   - Provide a brief contextual analysis (MAX 15 words in Persian) of why this location is strategically significant
   - Consider: Proximity to borders, conflict zones, military bases, strategic waterways
   - Examples: "گشت‌زنی بر فراز مرز روسیه و لهستان" or "نزدیک به تنگه هرمز از سمت خلیج فارس"

4. STRATEGIC IMPORTANCE SCORE:
   - Rate 1-10 based on:
     * Aircraft capabilities (10 = strategic bomber/AWACS, 1 = routine transport)
     * Location sensitivity (10 = conflict zone, 1 = domestic airspace)
     * Operational pattern (10 = unusual/covert, 1 = routine)
   
CRITICAL: You MUST respond ONLY with valid JSON in this EXACT format (no additional text):

{{
  "persian_role": "نقش دقیق هواپیما به فارسی (مثال: بمب‌افکن استراتژیک، جنگنده چندمنظوره، سوخت‌رسان هوایی)",
  "aircraft_model": "Full model name in English (Example: Boeing KC-135R Stratotanker (سوخت‌رسان استراتژیک))",
  "operator_analysis": "Complete operator name (Example: US Air Force Air Mobility Command)",
  "location_context": "تحلیل کوتاه موقعیت به فارسی - حداکثر ۱۵ کلمه",
  "strategic_importance": 8
}}

Analyze now:"""
        
        return prompt
    
    async def analyze_flight(self, flight: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze flight using Gemini AI with caching and fallback
        """
        if not self.enabled or not config.ENABLE_AI_ANALYSIS:
            logger.info("AI analysis disabled, using fallback")
            return None
        
        icao24 = flight.get('icao24', '').lower()
        type_code = flight.get('typecode', '')
        
        # Check cache first
        if config.USE_AI_CACHE:
            cached_analysis = db.get_database().get_ai_analysis(icao24, type_code)
            if cached_analysis:
                self.cache_hits += 1
                logger.info(f"💾 Using cached AI analysis for {icao24}")
                return cached_analysis
        
        # Perform new AI analysis
        self.total_requests += 1
        
        for attempt in range(len(self.api_keys)):
            try:
                logger.info(f"🤖 Requesting Gemini AI analysis for {icao24} (attempt {attempt + 1})")
                
                # Configure model with safety settings
                model = genai.GenerativeModel(
                    model_name=config.GEMINI_MODEL,
                    generation_config={
                        "temperature": config.GEMINI_TEMPERATURE,
                        "top_p": 0.95,
                        "top_k": 40,
                        "max_output_tokens": 1024,
                    },
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    }
                )
                
                # Build prompt and generate
                prompt = self._build_analysis_prompt(flight)
                response = await asyncio.wait_for(
                    asyncio.to_thread(model.generate_content, prompt),
                    timeout=config.GEMINI_TIMEOUT
                )
                
                # Parse response
                if response and response.text:
                    # Extract JSON from response (handle markdown code blocks)
                    text = response.text.strip()
                    if "```json" in text:
                        text = text.split("```json")[1].split("```")[0].strip()
                    elif "```" in text:
                        text = text.split("```")[1].split("```")[0].strip()
                    
                    analysis = json.loads(text)
                    
                    # Validate required fields
                    required_fields = ['persian_role', 'aircraft_model', 'operator_analysis', 
                                     'location_context', 'strategic_importance']
                    if all(field in analysis for field in required_fields):
                        self.successful_requests += 1
                        self.key_failure_counts[self.current_key_index] = 0
                        self.key_last_used[self.current_key_index] = time.time()
                        
                        # Save to cache
                        db.get_database().save_ai_analysis(
                            icao24,
                            flight.get('callsign', ''),
                            type_code,
                            flight.get('country', 'Unknown'),
                            analysis
                        )
                        
                        logger.info(f"✅ Gemini AI analysis successful: {analysis['aircraft_model']}")
                        return analysis
                    else:
                        logger.warning(f"⚠️ Incomplete AI response, missing fields")
                
            except asyncio.TimeoutError:
                logger.error(f"⏱️ Gemini API timeout for key #{self.current_key_index + 1}")
                self.key_failure_counts[self.current_key_index] += 1
                if not self._rotate_api_key():
                    break
                    
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse Gemini JSON response: {e}")
                logger.debug(f"Response text: {response.text if response else 'None'}")
                self.key_failure_counts[self.current_key_index] += 1
                if not self._rotate_api_key():
                    break
                    
            except Exception as e:
                error_msg = str(e).lower()
                if "quota" in error_msg or "limit" in error_msg or "429" in error_msg:
                    logger.warning(f"⚠️ API key #{self.current_key_index + 1} quota exceeded, rotating...")
                    self.key_failure_counts[self.current_key_index] = 999  # Mark as exhausted
                    if not self._rotate_api_key():
                        logger.error("❌ All Gemini API keys exhausted!")
                        break
                else:
                    logger.error(f"❌ Gemini API error: {e}", exc_info=False)
                    self.key_failure_counts[self.current_key_index] += 1
                    if attempt >= config.GEMINI_MAX_RETRIES - 1:
                        break
        
        logger.warning(f"⚠️ AI analysis failed for {icao24}, will use fallback")
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get AI manager statistics"""
        success_rate = (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0
        cache_rate = (self.cache_hits / (self.cache_hits + self.total_requests) * 100) if (self.cache_hits + self.total_requests) > 0 else 0
        
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'cache_hits': self.cache_hits,
            'success_rate': f"{success_rate:.1f}%",
            'cache_hit_rate': f"{cache_rate:.1f}%",
            'current_key_index': self.current_key_index + 1,
            'total_keys': len(self.api_keys)
        }


# ========== Global Instances ==========
gemini_manager = None
statistics = {'scan_cycles': 0, 'flights_detected': 0, 'notifications_sent': 0, 'start_time': None}
stats_lock = threading.Lock()


# ========== Helper Functions ==========
def get_country_from_icao(icao24: str) -> str:
    """Determine country from ICAO24 hex code"""
    try:
        icao_int = int(icao24, 16)
        for country, (start, end) in config.ICAO_COUNTRY_RANGES.items():
            if start <= icao_int <= end:
                return country
        return "Unknown"
    except (ValueError, TypeError):
        return "Invalid ICAO"


def get_fallback_analysis(flight: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fallback analysis using local databases when AI is unavailable
    """
    typecode = (flight.get('typecode') or '').upper()
    callsign = (flight.get('callsign') or '').upper()
    country = flight.get('country', 'Unknown')
    
    # Try to match aircraft model from database
    aircraft_model = "هواپیمای نظامی (مدل نامشخص)"
    persian_role = "نقش نامشخص"
    
    for code, model in config.AIRCRAFT_DATABASE.items():
        if code in typecode:
            aircraft_model = model
            # Find role from role map
            for role, codes in config.ROLE_MAP.items():
                if code in codes:
                    persian_role = role
                    break
            break
    
    # Try to match operator
    operator = "اپراتور نامشخص"
    for prefix, full_name in config.MILITARY_OPERATORS.items():
        if callsign.startswith(prefix):
            operator = full_name
            break
    
    # Default strategic importance based on aircraft type
    strategic_importance = 5
    if any(term in persian_role for term in ["بمب‌افکن", "رادارگریز", "استراتژیک"]):
        strategic_importance = 8
    elif any(term in persian_role for term in ["جنگنده", "رهگیر"]):
        strategic_importance = 7
    elif any(term in persian_role for term in ["هشدار", "اطلاعات"]):
        strategic_importance = 9
    
    return {
        'persian_role': persian_role,
        'aircraft_model': aircraft_model,
        'operator_analysis': operator,
        'location_context': f"پرواز در منطقه {flight.get('region', 'نامشخص')}",
        'strategic_importance': strategic_importance,
        'source': 'fallback'
    }


def get_region_from_coords(lat: float, lon: float) -> str:
    """Determine region from coordinates"""
    # Check strategic regions first
    for region_name, (min_lat, max_lat, min_lon, max_lon) in config.STRATEGIC_REGIONS.items():
        if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
            return region_name
    
    # Fallback to general regions
    if 24 <= lat <= 31 and 48 <= lon <= 57:
        return "خلیج فارس"
    elif 30 <= lat <= 37 and 23 <= lon <= 36:
        return "دریای مدیترانه"
    elif 41 <= lat <= 47 and 27 <= lon <= 42:
        return "دریای سیاه"
    elif 46 <= lat <= 52 and 22 <= lon <= 40:
        return "اروپای شرقی"
    else:
        return "منطقه نامشخص"


def is_in_usa_airspace(lat: float, lon: float) -> bool:
    """Check if coordinates are within USA domestic airspace"""
    bbox = config.USA_BBOX
    return (bbox['min_lat'] <= lat <= bbox['max_lat'] and 
            bbox['min_lon'] <= lon <= bbox['max_lon'])


def create_http_session() -> requests.Session:
    """Create HTTP session with retry logic"""
    session = requests.Session()
    retry = Retry(
        total=config.ADSB_RETRY_COUNT,
        read=config.ADSB_RETRY_COUNT,
        connect=config.ADSB_RETRY_COUNT,
        backoff_factor=0.5,
        status_forcelist=(500, 502, 503, 504, 429)
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=20)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


# ========== Main Flight Tracking Functions ==========
async def fetch_military_flights(session: requests.Session) -> Dict[str, Dict[str, Any]]:
    """
    Fetch military flights from ADSB.lol API
    """
    all_flights = {}
    
    try:
        logger.info(f"📡 Fetching military data from {config.ADSB_API_URL}...")
        
        response = await asyncio.wait_for(
            asyncio.to_thread(
                session.get,
                config.ADSB_API_URL,
                timeout=config.ADSB_TIMEOUT
            ),
            timeout=config.ADSB_TIMEOUT + 5
        )
        response.raise_for_status()
        data = response.json()
        
        if 'ac' in data and data['ac']:
            for aircraft in data['ac']:
                # Validate essential data
                if 'hex' not in aircraft or 'lat' not in aircraft or 'lon' not in aircraft:
                    continue
                
                # Skip grounded aircraft
                alt = aircraft.get('alt_baro')
                if isinstance(alt, str) and alt.lower() == 'ground':
                    continue
                if isinstance(alt, (int, float)) and alt <= 0:
                    continue
                
                # Parse flight data
                flight = {
                    'icao24': aircraft['hex'].lower(),
                    'callsign': aircraft.get('flight', 'N/A').strip(),
                    'lat': aircraft['lat'],
                    'lon': aircraft['lon'],
                    'alt': int(alt * 0.3048) if isinstance(alt, (int, float)) else 0,  # feet to meters
                    'vel': int(aircraft.get('gs', 0) * 1.852),  # knots to km/h
                    'heading': aircraft.get('track'),
                    'typecode': aircraft.get('t'),
                    'source': 'ADSB.lol'
                }
                
                all_flights[flight['icao24']] = flight
            
            logger.info(f"✅ Retrieved {len(all_flights)} military flights")
        else:
            logger.info("ℹ️ No military flights currently tracked")
    
    except asyncio.TimeoutError:
        logger.error(f"⏱️ Timeout fetching from ADSB API")
    except requests.RequestException as e:
        logger.error(f"❌ Network error fetching flights: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON response from API: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error fetching flights: {e}", exc_info=True)
    
    return all_flights


async def process_new_flight(bot: Bot, flight: Dict[str, Any], session: requests.Session) -> bool:
    """
    Process and analyze a newly detected flight
    """
    try:
        icao24 = flight['icao24']
        lat, lon = flight['lat'], flight['lon']
        
        # Filter USA domestic flights
        if is_in_usa_airspace(lat, lon):
            logger.info(f"🇺🇸 Filtering US domestic flight: {flight['callsign']}")
            return False
        
        # Add geographic context
        flight['country'] = get_country_from_icao(icao24)
        flight['region'] = get_region_from_coords(lat, lon)
        
        # Perform AI analysis (with caching and fallback)
        analysis = await gemini_manager.analyze_flight(flight)
        
        if not analysis:
            logger.info(f"⚙️ Using fallback analysis for {icao24}")
            analysis = get_fallback_analysis(flight)
            
            # Record as unidentified if fallback used
            if analysis.get('source') == 'fallback' and analysis['persian_role'] == "نقش نامشخص":
                db.get_database().add_unidentified_aircraft(
                    icao24,
                    flight['callsign'],
                    flight.get('typecode', 'N/A'),
                    reason="AI analysis failed, fallback inconclusive"
                )
        
        # Check strategic importance threshold
        if analysis['strategic_importance'] < config.MIN_STRATEGIC_IMPORTANCE:
            logger.info(
                f"ℹ️ Flight {flight['callsign']} has low strategic importance "
                f"({analysis['strategic_importance']}), skipping notification"
            )
            return False
        
        # Send notification
        success = await send_telegram_notification(bot, flight, analysis)
        
        if success:
            # Record in flight history
            flight_record = {**flight, **analysis}
            db.get_database().add_flight_record(flight_record)
            db.get_database().increment_statistic('notifications_sent')
            
            with stats_lock:
                statistics['notifications_sent'] += 1
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Error processing flight {flight.get('icao24')}: {e}", exc_info=True)
        return False


async def send_telegram_notification(
    bot: Bot,
    flight: Dict[str, Any],
    analysis: Dict[str, Any]
) -> bool:
    """
    Send enhanced Telegram notification with AI analysis
    """
    try:
        # Build comprehensive message
        emoji_map = {
            "بمب‌افکن": "💣",
            "جنگنده": "✈️",
            "رادارگریز": "👻",
            "سوخت‌رسان": "⛽",
            "هشدار": "📡",
            "اطلاعات": "🔍",
            "حمل": "📦",
            "گشت": "🌊",
            "VIP": "👑"
        }
        
        role_emoji = "🎯"
        for keyword, emoji in emoji_map.items():
            if keyword in analysis['persian_role']:
                role_emoji = emoji
                break
        
        importance = analysis['strategic_importance']
        importance_stars = "⭐" * min(importance, 10)
        
        # Determine urgency indicator
        if importance >= 9:
            urgency = "🔴 *بسیار مهم*"
        elif importance >= 7:
            urgency = "🟡 *مهم*"
        else:
            urgency = "🟢 *عادی*"
        
        message = f"""
🚨 *شناسایی پرواز نظامی* 🚨
{'━' * 35}

{urgency}  •  {importance_stars} ({importance}/10)

{role_emoji} *نقش:* {analysis['persian_role']}

{'━' * 35}
🛩️ *مشخصات هواپیما:*

  ▫️ *علامت تماس:* `{flight['callsign']}`
  ▫️ *مدل:* {analysis['aircraft_model']}
  ▫️ *اپراتور:* {analysis['operator_analysis']}
  ▫️ *کشور ثبت:* {flight['country']}
  ▫️ *شناسه ICAO:* `{flight['icao24'].upper()}`

{'━' * 35}
📍 *موقعیت و پرواز:*

  ▫️ *منطقه:* {analysis['location_context']}
  ▫️ *مختصات:* `{flight['lat']:.4f}°, {flight['lon']:.4f}°`
  ▫️ *ارتفاع:* {flight['alt']:,} متر
  ▫️ *سرعت:* {flight['vel']:,} کیلومتر بر ساعت
  ▫️ *جهت:* {flight.get('heading', 'N/A')}°

{'━' * 35}
🔍 *اطلاعات تکمیلی:*

  ▫️ *منبع داده:* {flight.get('source', 'ADSB.lol')}
  ▫️ *منبع تحلیل:* {'🤖 Gemini AI' if analysis.get('source') != 'fallback' else '💾 پایگاه داده محلی'}
  ▫️ *زمان شناسایی:* `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}` UTC
  
📊 [مشاهده آنلاین](https://globe.adsbexchange.com/?icao={flight['icao24']}) | 🗺️ [Google Maps](https://www.google.com/maps?q={flight['lat']},{flight['lon']})
"""
        
        await bot.send_message(
            chat_id=config.TELEGRAM_CHANNEL_ID,
            text=message.strip(),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        
        logger.info(f"✅ Notification sent: {flight['callsign']} ({analysis['aircraft_model']})")
        return True
        
    except RetryAfter as e:
        logger.warning(f"⏳ Rate limited, waiting {e.retry_after} seconds")
        await asyncio.sleep(e.retry_after)
        return False
    except TelegramError as e:
        logger.error(f"❌ Telegram error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to send notification: {e}", exc_info=True)
        return False


# ========== Background Tasks ==========
async def periodic_flight_check(context: ContextTypes.DEFAULT_TYPE):
    """
    Periodic job to check for new military flights
    """
    job_data = context.job.data
    session = job_data['session']
    queue = job_data['queue']
    
    try:
        with stats_lock:
            statistics['scan_cycles'] += 1
            scan_num = statistics['scan_cycles']
        
        logger.info(f"🔄 Starting scan cycle #{scan_num}")
        
        flights = await fetch_military_flights(session)
        db.get_database().increment_statistic('flights_detected')
        
        new_flight_count = 0
        for icao24, flight in flights.items():
            if not db.get_database().is_aircraft_spotted(icao24):
                db.get_database().add_spotted_aircraft(icao24, flight['callsign'])
                await queue.put(flight)
                new_flight_count += 1
                logger.info(f"🆕 New flight queued: {flight['callsign']} ({icao24})")
        
        if new_flight_count > 0:
            logger.info(f"✅ Scan #{scan_num}: {new_flight_count} new flights detected")
        else:
            logger.info(f"ℹ️ Scan #{scan_num}: No new flights")
            
    except Exception as e:
        logger.error(f"❌ Error in periodic check: {e}", exc_info=True)


async def notification_queue_processor(bot: Bot, queue: asyncio.Queue, session: requests.Session):
    """
    Background task to process notification queue
    """
    logger.info("🚀 Notification queue processor started")
    
    while True:
        try:
            flight = await queue.get()
            
            logger.info(f"📋 Processing queued flight: {flight['callsign']}")
            await process_new_flight(bot, flight, session)
            
            queue.task_done()
            
            # Delay between notifications
            await asyncio.sleep(config.NOTIFICATION_DELAY_SECONDS)
            
        except Exception as e:
            logger.error(f"❌ Error in queue processor: {e}", exc_info=True)
            await asyncio.sleep(5)


async def send_hourly_report(context: ContextTypes.DEFAULT_TYPE):
    """
    Send hourly statistics report
    """
    try:
        db_stats = db.get_database().get_hourly_statistics()
        ai_stats = gemini_manager.get_statistics()
        
        with stats_lock:
            uptime = datetime.now(timezone.utc) - statistics['start_time']
            hours, remainder = divmod(uptime.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
        
        report = f"""
📊 *گزارش ساعتی ربات*
{'━' * 35}

⏱️ *زمان فعالیت:* {int(hours)} ساعت و {int(minutes)} دقیقه

🔄 *عملکرد:*
  ▫️ تعداد بررسی‌ها: {statistics['scan_cycles']}
  ▫️ پروازهای شناسایی شده: {db_stats['flights_detected']}
  ▫️ اعلان‌های ارسال شده: {statistics['notifications_sent']}

🤖 *تحلیل هوش مصنوعی:*
  ▫️ درخواست‌ها: {ai_stats['total_requests']}
  ▫️ موفق: {ai_stats['successful_requests']}
  ▫️ استفاده از حافظه: {ai_stats['cache_hits']}
  ▫️ نرخ موفقیت: {ai_stats['success_rate']}
  ▫️ کلید فعال: #{ai_stats['current_key_index']}/{ai_stats['total_keys']}

📁 *پایگاه داده:*
  ▫️ هواپیماهای رصد شده: {db.get_database().get_spotted_count()}

⏰ *زمان گزارش:* `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}` UTC
"""
        
        await context.bot.send_message(
            chat_id=config.TELEGRAM_CHANNEL_ID,
            text=report.strip(),
            parse_mode=ParseMode.MARKDOWN
        )
        
        logger.info("✅ Hourly report sent")
        
    except Exception as e:
        logger.error(f"❌ Failed to send hourly report: {e}")


async def send_daily_unidentified_report(context: ContextTypes.DEFAULT_TYPE):
    """
    Send daily report of unidentified aircraft to admin
    """
    try:
        logger.info("📝 Generating daily unidentified aircraft report...")
        
        records = db.get_database().get_unidentified_aircraft()
        
        if not records:
            await context.bot.send_message(
                chat_id=config.ADMIN_USER_ID,
                text="✅ گزارش روزانه: هیچ هواپیمای ناشناسی در ۲۴ ساعت گذشته ثبت نشده است."
            )
        else:
            report_lines = [
                f"گزارش هواپیماهای شناسایی ناقص - {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
                "=" * 70,
                f"تعداد کل: {len(records)}",
                "=" * 70,
                "",
                f"{'ICAO':<12} {'Callsign':<12} {'Type':<10} {'Reason':<25} {'Timestamp':<20}",
                "-" * 70
            ]
            
            for record in records:
                icao, callsign, typecode, timestamp, reason = record
                report_lines.append(
                    f"{icao or 'N/A':<12} {callsign or 'N/A':<12} "
                    f"{typecode or 'N/A':<10} {reason[:24]:<25} {timestamp:<20}"
                )
            
            report_str = "\n".join(report_lines)
            report_file = io.BytesIO(report_str.encode('utf-8'))
            report_file.name = f"unidentified_{datetime.now(timezone.utc).strftime('%Y%m%d')}.txt"
            
            await context.bot.send_document(
                chat_id=config.ADMIN_USER_ID,
                document=report_file,
                caption=f"📋 گزارش روزانه هواپیماهای شناسایی ناقص\n\n"
                       f"تعداد: {len(records)} مورد"
            )
            
            logger.info(f"✅ Daily report sent to admin: {len(records)} unidentified aircraft")
        
        # Clear unidentified aircraft table
        db.get_database().clear_unidentified_aircraft()
        
        # Perform database cleanup
        cleanup_stats = db.get_database().cleanup_old_records(days=config.DB_CLEANUP_DAYS)
        logger.info(f"🧹 Database cleanup completed: {cleanup_stats}")
        
    except Exception as e:
        logger.error(f"❌ Failed to send daily report: {e}", exc_info=True)


# ========== Command Handlers ==========
async def cmd_start(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "🚀 *ربات ردیاب هواپیماهای نظامی* (نسخه هوشمند)\n\n"
        "این ربات با استفاده از هوش مصنوعی Gemini، پروازهای نظامی را شناسایی و تحلیل می‌کند.\n\n"
        "*دستورات موجود:*\n"
        "/status - وضعیت سیستم\n"
        "/stats - آمار تفصیلی\n"
        "/test - ارسال پیام تست\n"
        "/ai - وضعیت هوش مصنوعی",
        parse_mode=ParseMode.MARKDOWN
    )


async def cmd_status(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    try:
        with stats_lock:
            uptime = datetime.now(timezone.utc) - statistics['start_time']
            hours, remainder = divmod(uptime.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
        
        queue_size = context.job_queue.jobs()[0].data['queue'].qsize() if context.job_queue.jobs() else 0
        
        status = f"""
📊 *وضعیت ربات*

✅ *وضعیت:* فعال و در حال کار
⏱️ *مدت فعالیت:* {int(hours)}h {int(minutes)}m
🔄 *بازه بررسی:* هر {config.POLL_INTERVAL_SECONDS} ثانیه
⏳ *صف پردازش:* {queue_size} پرواز

📈 *آمار کلی:*
  ▫️ تعداد بررسی‌ها: {statistics['scan_cycles']}
  ▫️ اعلان‌های ارسال شده: {statistics['notifications_sent']}
  ▫️ هواپیماهای رصد شده: {db.get_database().get_spotted_count()}

⏰ *زمان سرور:* `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}` UTC
"""
        await update.message.reply_text(status.strip(), parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")


async def cmd_stats(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command - detailed statistics"""
    try:
        ai_stats = gemini_manager.get_statistics()
        db_stats = db.get_database().get_database_stats()
        
        stats_msg = f"""
📊 *آمار تفصیلی سیستم*
{'━' * 35}

🤖 *هوش مصنوعی Gemini:*
  ▫️ کل درخواست‌ها: {ai_stats['total_requests']}
  ▫️ موفقیت‌آمیز: {ai_stats['successful_requests']}
  ▫️ نرخ موفقیت: {ai_stats['success_rate']}
  ▫️ استفاده از حافظه: {ai_stats['cache_hits']}
  ▫️ نرخ حافظه: {ai_stats['cache_hit_rate']}
  ▫️ کلید فعال: {ai_stats['current_key_index']}/{ai_stats['total_keys']}

📁 *پایگاه داده:*
  ▫️ هواپیماهای رصد شده: {db_stats['spotted_aircraft_count']}
  ▫️ حافظه تحلیل AI: {db_stats['ai_analysis_cache_count']}
  ▫️ تاریخچه پروازها: {db_stats['flight_history_count']}
  ▫️ ناشناس‌های فعلی: {db_stats['unidentified_aircraft_count']}
  ▫️ نرخ استفاده از حافظه: {db_stats['cache_hit_rate']:.1f}%
  ▫️ حجم دیتابیس: {db_stats['database_size_mb']:.2f} MB
"""
        await update.message.reply_text(stats_msg.strip(), parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")


async def cmd_test(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /test command"""
    try:
        test_msg = f"""
🧪 *پیام تست سیستم*

✅ ارتباط با API تلگرام برقرار است
⏰ زمان: `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}` UTC
🤖 نسخه: 15.0 (Gemini-Powered)
"""
        await context.bot.send_message(
            chat_id=config.TELEGRAM_CHANNEL_ID,
            text=test_msg.strip(),
            parse_mode=ParseMode.MARKDOWN
        )
        await update.message.reply_text("✅ پیام تست با موفقیت ارسال شد.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در ارسال: {e}")


async def cmd_ai(update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ai command - AI system status"""
    try:
        ai_stats = gemini_manager.get_statistics()
        
        status_emoji = "✅" if gemini_manager.enabled else "❌"
        status_text = "فعال" if gemini_manager.enabled else "غیرفعال"
        
        ai_msg = f"""
🤖 *وضعیت سیستم هوش مصنوعی*
{'━' * 35}

{status_emoji} *وضعیت:* {status_text}
🔑 *کلید فعال:* #{ai_stats['current_key_index']} از {ai_stats['total_keys']}
🎯 *مدل:* {config.GEMINI_MODEL}

📊 *عملکرد:*
  ▫️ کل تحلیل‌ها: {ai_stats['total_requests']}
  ▫️ موفق: {ai_stats['successful_requests']}
  ▫️ از حافظه: {ai_stats['cache_hits']}
  ▫️ نرخ موفقیت: {ai_stats['success_rate']}
  ▫️ نرخ حافظه: {ai_stats['cache_hit_rate']}

⚙️ *تنظیمات:*
  ▫️ دما (Temperature): {config.GEMINI_TEMPERATURE}
  ▫️ زمان انتظار: {config.GEMINI_TIMEOUT}s
  ▫️ تلاش مجدد: {config.GEMINI_MAX_RETRIES}
"""
        await update.message.reply_text(ai_msg.strip(), parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")


# ========== Application Initialization ==========
async def post_init(application: Application):
    """Initialize bot after application setup"""
    global gemini_manager, statistics
    
    logger.info("=" * 60)
    logger.info("🚀 Military Flight Tracker Bot v15.0 (Gemini AI Edition)")
    logger.info("=" * 60)
    
    # Initialize database
    db.init_db(config.DATABASE_FILE)
    
    # Initialize Gemini AI
    gemini_manager = GeminiAIManager(config.GEMINI_API_KEYS)
    
    # Initialize statistics
    statistics['start_time'] = datetime.now(timezone.utc)
    
    # Create HTTP session
    session = create_http_session()
    
    # Create notification queue
    notification_queue = asyncio.Queue()
    
    # Store in job data
    job_data = {
        'session': session,
        'queue': notification_queue
    }
    
    # Start background queue processor
    application.create_task(
        notification_queue_processor(application.bot, notification_queue, session)
    )
    
    # Schedule periodic jobs
    job_queue = application.job_queue
    
    # Flight checking job
    job_queue.run_repeating(
        periodic_flight_check,
        interval=config.POLL_INTERVAL_SECONDS,
        first=10,
        data=job_data
    )
    
    # Hourly report job
    job_queue.run_repeating(
        send_hourly_report,
        interval=config.HOURLY_REPORT_INTERVAL,
        first=config.HOURLY_REPORT_INTERVAL
    )
    
    # Daily unidentified aircraft report
    job_queue.run_daily(
        send_daily_unidentified_report,
        time=datetime.time(hour=config.DAILY_REPORT_HOUR, minute=0, second=0)
    )
    
    logger.info("✅ All jobs scheduled successfully")
    logger.info(f"🔄 Flight check interval: {config.POLL_INTERVAL_SECONDS}s")
    logger.info(f"📊 Hourly reports: Enabled")
    logger.info(f"📋 Daily reports: {config.DAILY_REPORT_HOUR}:00 UTC")
    logger.info(f"🤖 AI Analysis: {'Enabled' if gemini_manager.enabled else 'Disabled'}")
    logger.info("=" * 60)
    logger.info("🎯 Bot is ready! Press Ctrl+C to stop.")


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"⚠️ Received signal {signum}, shutting down gracefully...")
    
    # Final statistics
    if statistics.get('start_time'):
        uptime = datetime.now(timezone.utc) - statistics['start_time']
        logger.info(f"📊 Final Statistics:")
        logger.info(f"  - Uptime: {uptime}")
        logger.info(f"  - Scans: {statistics['scan_cycles']}")
        logger.info(f"  - Notifications: {statistics['notifications_sent']}")
        if gemini_manager:
            ai_stats = gemini_manager.get_statistics()
            logger.info(f"  - AI Analyses: {ai_stats['successful_requests']}/{ai_stats['total_requests']}")
    
    sys.exit(0)


def main():
    """Main entry point"""
    # Validate configuration
    if not config.validate_config():
        logger.error("❌ Configuration validation failed!")
        logger.error("Please edit config.py and add your credentials.")
        sys.exit(1)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Build application
        application = (
            Application.builder()
            .token(config.TELEGRAM_BOT_TOKEN)
            .post_init(post_init)
            .build()
        )
        
        # Add command handlers
        application.add_handler(CommandHandler("start", cmd_start))
        application.add_handler(CommandHandler("status", cmd_status))
        application.add_handler(CommandHandler("stats", cmd_stats))
        application.add_handler(CommandHandler("test", cmd_test))
        application.add_handler(CommandHandler("ai", cmd_ai))
        
        # Start bot
        logger.info("🚀 Starting bot...")
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message"]
        )
        
    except Exception as e:
        logger.critical(f"💥 Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    main()
