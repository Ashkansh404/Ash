# -*- coding: utf-8 -*-
"""
ربات هوشمند ردیاب پروازهای نظامی
Intelligent Military Flight Tracker Bot

نسخه: 15.0 (AI-Enhanced Edition)
قابلیت‌ها:
- تحلیل هوشمند با Gemini 2.5 Pro
- سوییچ خودکار بین چند API Key
- یادگیری و ذخیره اطلاعات هواپیماها
- فالبک هوشمند به دیتابیس آفلاین
- مدیریت خطای پیشرفته
"""

import os
import sys
import time
import logging
import threading
import asyncio
import json
import io
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
import signal
import traceback
from contextlib import asynccontextmanager

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Telegram imports
from telegram import Bot
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TelegramError

# Import local modules
try:
    from config import (
        TOKEN, CHANNEL_ID, ADMIN_ID, GEMINI_API_KEYS, GEMINI_MODEL,
        POLL_INTERVAL_SECONDS, MEMORY_CLEANUP_HOURS, LOG_LEVEL, LOG_FILE,
        USA_BBOX, HTTP_RETRY_COUNT, API_TIMEOUT, MESSAGE_DELAY,
        MAX_GEMINI_RETRIES, GEMINI_TIMEOUT, DB_FILE
    )
    import database
except ImportError as e:
    print(f"❌ Error loading modules: {e}")
    print("Please ensure config.py and database.py exist.")
    sys.exit(1)

# ========== Logging Setup ==========
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ========== Data Dictionaries (Consolidated) ==========

# مناطق جغرافیایی گسترده (نام منطقه: (حداقل عرض، حداکثر عرض، حداقل طول، حداکثر طول))
GEO_REGIONS_EXTENDED = {
    # خاورمیانه
    "خلیج فارس": (24.0, 30.5, 48.0, 57.0),
    "تنگه هرمز": (25.5, 27.0, 55.5, 57.5),
    "دریای سرخ": (12.0, 30.0, 32.0, 44.0),
    "دریای مدیترانه شرقی": (30.0, 37.0, 28.0, 37.0),
    "عراق و سوریه": (29.0, 37.5, 36.0, 49.0),
    "شبه جزیره عربستان": (12.0, 32.0, 34.0, 60.0),
    
    # اروپا
    "اروپای شرقی (اوکراین)": (44.0, 53.0, 22.0, 41.0),
    "مرز لهستان-بلاروس": (51.0, 54.5, 22.0, 25.0),
    "دریای بالتیک": (53.0, 66.0, 10.0, 30.0),
    "دریای سیاه": (40.5, 47.0, 27.0, 42.0),
    
    # آسیا و اقیانوسیه
    "دریای چین جنوبی": (0.0, 24.0, 100.0, 121.0),
    "تنگه تایوان": (23.0, 26.0, 117.0, 122.0),
    "شبه جزیره کره": (33.0, 43.0, 124.0, 132.0),
    "افغانستان و پاکستان": (23.0, 38.0, 60.0, 78.0),
    
    # روسیه و آسیای مرکزی
    "غرب روسیه": (50.0, 70.0, 30.0, 60.0),
    "سیبری": (50.0, 80.0, 60.0, 180.0),
    "قفقاز": (38.0, 44.0, 38.0, 51.0),
    
    # آمریکا (برای شناسایی و فیلتر)
    "ایالات متحده آمریکا": (24.0, 50.0, -125.0, -66.0),
    "کانادا": (41.0, 84.0, -141.0, -52.0),
    
    # آفریقا
    "شمال آفریقا": (15.0, 37.0, -17.0, 52.0),
    "شاخ آفریقا": (-5.0, 18.0, 33.0, 52.0),
}

# نقش‌های هواپیماهای نظامی (کد: نقش فارسی)
ROLE_MAP_INVERTED = {
    # هواپیماهای جنگنده
    "F-15": "جنگنده تاکتیکی پیشرفته",
    "F-16": "جنگنده چندمنظوره سبک",
    "F-35": "جنگنده نسل پنجم نامرئی",
    "F-22": "جنگنده برتری هوایی نسل پنجم",
    "F/A-18": "جنگنده-بمب‌افکن ناوبری",
    "SU-27": "جنگنده برتری هوایی روسی",
    "SU-30": "جنگنده چندمنظوره پیشرفته",
    "SU-35": "جنگنده نسل 4++",
    "SU-57": "جنگنده نسل پنجم روسی",
    "MIG-29": "جنگنده سبک روسی",
    "MIG-31": "رهگیر سریع ارتفاع بالا",
    "J-10": "جنگنده چندمنظوره چینی",
    "J-20": "جنگنده نسل پنجم چینی",
    "RAFALE": "جنگنده چندمنظوره فرانسوی",
    "TYPHOON": "جنگنده اروپایی یوروفایتر",
    "TORNADO": "جنگنده-بمب‌افکن اروپایی",
    
    # هواپیماهای اطلاعاتی و نظارتی
    "RC-135": "هواپیمای جاسوسی الکترونیکی",
    "E-3": "هواپیمای رادار هشداردهنده زودهنگام (آواکس)",
    "E-8": "هواپیمای فرماندهی و کنترل نبرد زمینی",
    "E-2": "هواپیمای رادار هشداردهنده ناوبری",
    "P-8": "هواپیمای گشت دریایی و ضد زیردریایی",
    "P-3": "هواپیمای گشت دریایی",
    "RQ-4": "پهپاد جاسوسی ارتفاع بالا",
    "MQ-9": "پهپاد نظامی مسلح",
    "IL-20": "هواپیمای جاسوسی روسی",
    "TU-214R": "هواپیمای شناسایی استراتژیک روسی",
    
    # هواپیماهای سوخت‌رسانی
    "KC-135": "هواپیمای سوخت‌رسان هوایی",
    "KC-46": "سوخت‌رسان پیشرفته",
    "KC-10": "سوخت‌رسان سنگین",
    "KC-130": "سوخت‌رسان تاکتیکی",
    "IL-78": "سوخت‌رسان روسی",
    "A330 MRTT": "سوخت‌رسان چندمنظوره اروپایی",
    
    # بمب‌افکن‌ها
    "B-52": "بمب‌افکن استراتژیک سنگین",
    "B-1": "بمب‌افکن استراتژیک سریع",
    "B-2": "بمب‌افکن نامرئی استراتژیک",
    "TU-95": "بمب‌افکن استراتژیک روسی",
    "TU-160": "بمب‌افکن استراتژیک مافوق صوت",
    "TU-22": "بمب‌افکن متوسط روسی",
    "H-6": "بمب‌افکن استراتژیک چینی",
    
    # هواپیماهای حمل و نقل
    "C-130": "هواپیمای حمل و نقل تاکتیکی",
    "C-17": "حمل و نقل استراتژیک سنگین",
    "C-5": "حمل و نقل فوق سنگین",
    "C-2": "حمل و نقل ناوبری",
    "AN-124": "حمل و نقل فوق سنگین روسی",
    "IL-76": "حمل و نقل استراتژیک روسی",
    "Y-20": "حمل و نقل استراتژیک چینی",
    "A400M": "حمل و نقل نظامی اروپایی",
    
    # هواپیماهای ویژه
    "E-4": "مرکز فرماندهی هوایی ملی (روز قیامت)",
    "VC-25": "هواپیمای ریاست جمهوری (ایرفورس وان)",
    "DOOMSDAY": "هواپیمای فرماندهی اضطراری",
    
    # بالگردها
    "AH-64": "بالگرد تهاجمی آپاچی",
    "UH-60": "بالگرد چندمنظوره بلک‌هاوک",
    "CH-47": "بالگرد حمل و نقل چینوک",
    "MI-24": "بالگرد تهاجمی روسی",
    "MI-8": "بالگرد حمل و نقل روسی",
}

# پایگاه داده هواپیماها (کد: نام مدل)
AIRCRAFT_DATABASE = {
    # جنگنده‌های آمریکایی
    "F15": "McDonnell Douglas F-15 Eagle",
    "F-15": "McDonnell Douglas F-15 Eagle",
    "F16": "General Dynamics F-16 Fighting Falcon",
    "F-16": "General Dynamics F-16 Fighting Falcon",
    "F35": "Lockheed Martin F-35 Lightning II",
    "F-35": "Lockheed Martin F-35 Lightning II",
    "F22": "Lockheed Martin F-22 Raptor",
    "F-22": "Lockheed Martin F-22 Raptor",
    "FA18": "Boeing F/A-18 Super Hornet",
    "F/A-18": "Boeing F/A-18 Super Hornet",
    
    # جنگنده‌های روسی
    "SU27": "Sukhoi Su-27 Flanker",
    "SU-27": "Sukhoi Su-27 Flanker",
    "SU30": "Sukhoi Su-30 Flanker-C",
    "SU-30": "Sukhoi Su-30 Flanker-C",
    "SU35": "Sukhoi Su-35 Flanker-E",
    "SU-35": "Sukhoi Su-35 Flanker-E",
    "SU57": "Sukhoi Su-57 Felon",
    "SU-57": "Sukhoi Su-57 Felon",
    "MIG29": "Mikoyan MiG-29 Fulcrum",
    "MIG-29": "Mikoyan MiG-29 Fulcrum",
    "MIG31": "Mikoyan MiG-31 Foxhound",
    "MIG-31": "Mikoyan MiG-31 Foxhound",
    
    # جنگنده‌های اروپایی و دیگر کشورها
    "RAFALE": "Dassault Rafale",
    "TYPHOON": "Eurofighter Typhoon",
    "TORNADO": "Panavia Tornado",
    "GRIPEN": "Saab JAS 39 Gripen",
    "J10": "Chengdu J-10 Firebird",
    "J-10": "Chengdu J-10 Firebird",
    "J20": "Chengdu J-20 Mighty Dragon",
    "J-20": "Chengdu J-20 Mighty Dragon",
    
    # هواپیماهای اطلاعاتی
    "RC135": "Boeing RC-135 Rivet Joint",
    "RC-135": "Boeing RC-135 Rivet Joint",
    "E3": "Boeing E-3 Sentry (AWACS)",
    "E-3": "Boeing E-3 Sentry (AWACS)",
    "E8": "Northrop Grumman E-8 JSTARS",
    "E-8": "Northrop Grumman E-8 JSTARS",
    "E2": "Northrop Grumman E-2 Hawkeye",
    "E-2": "Northrop Grumman E-2 Hawkeye",
    "P8": "Boeing P-8 Poseidon",
    "P-8": "Boeing P-8 Poseidon",
    "P3": "Lockheed P-3 Orion",
    "P-3": "Lockheed P-3 Orion",
    "RQ4": "Northrop Grumman RQ-4 Global Hawk",
    "RQ-4": "Northrop Grumman RQ-4 Global Hawk",
    "MQ9": "General Atomics MQ-9 Reaper",
    "MQ-9": "General Atomics MQ-9 Reaper",
    
    # سوخت‌رسان‌ها
    "KC135": "Boeing KC-135 Stratotanker",
    "KC-135": "Boeing KC-135 Stratotanker",
    "KC46": "Boeing KC-46 Pegasus",
    "KC-46": "Boeing KC-46 Pegasus",
    "KC10": "McDonnell Douglas KC-10 Extender",
    "KC-10": "McDonnell Douglas KC-10 Extender",
    "KC130": "Lockheed KC-130 Hercules",
    "KC-130": "Lockheed KC-130 Hercules",
    "IL78": "Ilyushin Il-78 Midas",
    "IL-78": "Ilyushin Il-78 Midas",
    
    # بمب‌افکن‌ها
    "B52": "Boeing B-52 Stratofortress",
    "B-52": "Boeing B-52 Stratofortress",
    "B1": "Rockwell B-1 Lancer",
    "B-1": "Rockwell B-1 Lancer",
    "B2": "Northrop Grumman B-2 Spirit",
    "B-2": "Northrop Grumman B-2 Spirit",
    "TU95": "Tupolev Tu-95 Bear",
    "TU-95": "Tupolev Tu-95 Bear",
    "TU160": "Tupolev Tu-160 Blackjack",
    "TU-160": "Tupolev Tu-160 Blackjack",
    "TU22": "Tupolev Tu-22M Backfire",
    "TU-22": "Tupolev Tu-22M Backfire",
    
    # حمل و نقل
    "C130": "Lockheed C-130 Hercules",
    "C-130": "Lockheed C-130 Hercules",
    "C17": "Boeing C-17 Globemaster III",
    "C-17": "Boeing C-17 Globemaster III",
    "C5": "Lockheed C-5 Galaxy",
    "C-5": "Lockheed C-5 Galaxy",
    "AN124": "Antonov An-124 Ruslan",
    "AN-124": "Antonov An-124 Ruslan",
    "IL76": "Ilyushin Il-76 Candid",
    "IL-76": "Ilyushin Il-76 Candid",
    "A400M": "Airbus A400M Atlas",
    
    # ویژه
    "E4": "Boeing E-4 Nightwatch (Doomsday)",
    "E-4": "Boeing E-4 Nightwatch (Doomsday)",
    "VC25": "Boeing VC-25 (Air Force One)",
    "VC-25": "Boeing VC-25 (Air Force One)",
}

# اپراتورهای نظامی (پیشوند کال‌ساین: نام کامل)
MILITARY_OPERATORS = {
    # آمریکا
    "RCH": "U.S. Air Force Reach",
    "REACH": "U.S. Air Force Reach",
    "CNV": "U.S. Air Force Convoy",
    "CONVOY": "U.S. Air Force Convoy",
    "EVAL": "U.S. Air Force Eval",
    "SPAR": "U.S. Air Force Special Air Mission",
    "VMR": "U.S. Marine Corps",
    "NAVY": "U.S. Navy",
    "RAVEN": "U.S. Air Force Raven",
    "JAKE": "U.S. Air National Guard",
    "MAGMA": "U.S. Air Force Special Operations",
    "RULER": "U.S. Air Force",
    "FORTE": "U.S. Air Force Reconnaissance",
    
    # روسیه
    "RSD": "Russian Air Force",
    "RFF": "Russian Air Force",
    "RA": "Russian Military",
    "RUS": "Russian Air Force",
    
    # انگلستان
    "RRR": "Royal Air Force",
    "TARTAN": "Royal Air Force",
    "ASCOT": "Royal Air Force",
    "ZZ": "Royal Air Force",
    
    # ناتو
    "NATO": "NATO Alliance",
    "GHOST": "NATO AWACS",
    
    # سایر
    "GAF": "German Air Force (Luftwaffe)",
    "CTM": "French Air Force",
    "FAF": "French Air Force",
    "IAM": "Italian Air Force",
    "AME": "Spanish Air Force",
    "RSAF": "Royal Saudi Air Force",
    "IAF": "Israeli Air Force",
}

# محدوده‌های ICAO کشورها
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
    "Pakistan": (0x760000, 0x767FFF),
    "South Korea": (0x718000, 0x71FFFF),
    "Japan": (0x840000, 0x87FFFF),
    "Australia": (0x7C0000, 0x7FFFFF),
    "Ukraine": (0x508000, 0x50FFFF),
    "Poland": (0x480000, 0x487FFF),
    "Egypt": (0x010000, 0x03FFFF),
    "UAE": (0x896000, 0x897FFF),
}

# ========== Gemini AI Integration ==========

class GeminiAnalyzer:
    """
    تحلیلگر هوشمند با استفاده از Gemini AI
    با قابلیت سوییچ خودکار بین کلیدهای API
    """
    
    def __init__(self, api_keys: List[str], model: str = "gemini-2.0-flash-exp"):
        """
        مقداردهی اولیه
        
        Args:
            api_keys: لیست کلیدهای API
            model: نام مدل Gemini
        """
        self.api_keys = api_keys
        self.model = model
        self.current_key_index = 0
        self._lock = threading.Lock()
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
        logger.info(f"🤖 Gemini Analyzer initialized with {len(api_keys)} API keys")
    
    def _get_next_api_key(self) -> str:
        """دریافت کلید API بعدی (روتیشن خودکار)"""
        with self._lock:
            key = self.api_keys[self.current_key_index]
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            return key
    
    def _create_analysis_prompt(self, flight_data: Dict[str, Any]) -> str:
        """
        ایجاد پرامپت تحلیلی برای Gemini
        
        Args:
            flight_data: داده‌های پرواز
            
        Returns:
            پرامپت کامل
        """
        prompt = f"""شما یک تحلیلگر ارشد اطلاعات هوانوردی نظامی با دسترسی به داده‌های طبقه‌بندی‌شده هستید.

**داده‌های خام پرواز شناسایی شده:**
- کد ICAO (شناسه یکتا): {flight_data.get('icao24', 'N/A')}
- علامت تماس (Callsign): {flight_data.get('callsign', 'N/A')}
- کد نوع هواپیما (Type Code): {flight_data.get('typecode', 'N/A')}
- مختصات جغرافیایی: {flight_data.get('lat', 0):.4f}°N, {flight_data.get('lon', 0):.4f}°E
- ارتفاع: {flight_data.get('alt', 0):,} متر
- سرعت: {flight_data.get('vel', 0)} کیلومتر بر ساعت
- جهت: {flight_data.get('heading', 'N/A')}°
- کشور ثبت (بر اساس ICAO): {flight_data.get('country', 'Unknown')}

**وظیفه شما:**
بر اساس تمام شواهد موجود (کد نوع، کال‌ساین، کشور، موقعیت جغرافیایی)، تحلیل جامع زیر را ارائه دهید:

1. **شناسایی دقیق نقش و مدل**: دقیق‌ترین نقش عملیاتی و نام کامل مدل هواپیما را استنتاج کنید.
2. **تحلیل موقعیت مکانی**: یک تحلیل متنی کوتاه (حداکثر 15 کلمه فارسی) از اهمیت استراتژیک موقعیت فعلی پرواز ارائه دهید.
   - مثال: "در حال گشت‌زنی بر فراز مرز لهستان و بلاروس"
   - مثال: "در حال نزدیک شدن به تنگه هرمز از سمت دریای عمان"
3. **شناسایی اپراتور**: نام کامل سازمان یا نیروی نظامی عامل این پرواز را مشخص کنید.
4. **ارزیابی اهمیت استراتژیک**: یک امتیاز عددی بین 1 تا 10 برای اهمیت استراتژیک این پرواز در لحظه کنونی تعیین کنید.

**فرمت خروجی (فقط JSON معتبر برگردانید):**
{{
  "persian_role": "نقش شناسایی‌شده به فارسی",
  "aircraft_model": "نام کامل و دقیق مدل هواپیما",
  "operator_analysis": "نام کامل اپراتور شناسایی‌شده",
  "location_context": "تحلیل متنی کوتاه از موقعیت جغرافیایی (حداکثر 15 کلمه)",
  "strategic_importance": 8
}}

**نکات مهم:**
- فقط یک JSON معتبر برگردانید، بدون متن اضافی.
- اگر اطلاعات کافی ندارید، از "نامشخص" یا "N/A" استفاده کنید.
- امتیاز اهمیت را واقع‌بینانه و بر اساس موقعیت، نوع ماموریت، و تنش‌های جاری منطقه‌ای تعیین کنید.
"""
        return prompt
    
    async def analyze_flight(self, flight_data: Dict[str, Any], 
                           retry_count: int = MAX_GEMINI_RETRIES) -> Optional[Dict[str, Any]]:
        """
        تحلیل پرواز با استفاده از Gemini AI
        
        Args:
            flight_data: داده‌های پرواز
            retry_count: تعداد تلاش مجدد
            
        Returns:
            دیکشنری حاوی تحلیل یا None در صورت شکست
        """
        for attempt in range(retry_count):
            api_key = self._get_next_api_key()
            
            try:
                prompt = self._create_analysis_prompt(flight_data)
                
                url = f"{self.base_url}/{self.model}:generateContent?key={api_key}"
                
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.3,
                        "topK": 20,
                        "topP": 0.8,
                        "maxOutputTokens": 800,
                    }
                }
                
                # ارسال درخواست غیرهمزمان
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: requests.post(
                        url, 
                        json=payload, 
                        timeout=GEMINI_TIMEOUT,
                        headers={"Content-Type": "application/json"}
                    )
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # استخراج متن پاسخ
                    if 'candidates' in result and len(result['candidates']) > 0:
                        text = result['candidates'][0]['content']['parts'][0]['text']
                        
                        # پاکسازی و پارس JSON
                        text = text.strip()
                        # حذف markdown code blocks اگر وجود دارد
                        if text.startswith('```'):
                            text = text.split('```')[1]
                            if text.startswith('json'):
                                text = text[4:]
                        
                        analysis = json.loads(text.strip())
                        
                        # اعتبارسنجی پاسخ
                        required_keys = ['persian_role', 'aircraft_model', 
                                       'operator_analysis', 'location_context', 
                                       'strategic_importance']
                        
                        if all(key in analysis for key in required_keys):
                            database.get_db().log_api_usage(f"gemini_key_{self.current_key_index}", True)
                            logger.info(f"✅ Gemini analysis successful for {flight_data.get('icao24')}")
                            return analysis
                        else:
                            logger.warning(f"⚠️ Incomplete Gemini response, missing keys")
                
                elif response.status_code == 429:
                    logger.warning(f"⚠️ API key {self.current_key_index} rate limited, switching...")
                    database.get_db().log_api_usage(f"gemini_key_{self.current_key_index}", False, "Rate limited")
                    continue
                
                else:
                    logger.error(f"❌ Gemini API error {response.status_code}: {response.text}")
                    database.get_db().log_api_usage(f"gemini_key_{self.current_key_index}", False, 
                                                   f"HTTP {response.status_code}")
            
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse Gemini JSON response: {e}")
                database.get_db().log_api_usage(f"gemini_key_{self.current_key_index}", False, "JSON parse error")
            
            except requests.exceptions.Timeout:
                logger.error(f"⏱️ Gemini API timeout (attempt {attempt + 1}/{retry_count})")
                database.get_db().log_api_usage(f"gemini_key_{self.current_key_index}", False, "Timeout")
            
            except Exception as e:
                logger.error(f"❌ Gemini API error: {e}", exc_info=True)
                database.get_db().log_api_usage(f"gemini_key_{self.current_key_index}", False, str(e))
            
            # تاخیر کوتاه قبل از تلاش مجدد
            if attempt < retry_count - 1:
                await asyncio.sleep(2)
        
        logger.warning(f"⚠️ All Gemini attempts failed for {flight_data.get('icao24')}")
        return None


# ========== Helper Classes ==========

class StatisticsTracker:
    """ردیاب آمار عملکرد ربات"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self.reset()
    
    def reset(self):
        """بازنشانی آمار"""
        with self._lock:
            self.start_time = datetime.now(timezone.utc)
            self.scan_cycles = 0
            self.military_flights_found = 0
            self.ai_successes = 0
            self.ai_failures = 0
            self.cache_hits = 0
    
    def increment_scan(self):
        with self._lock:
            self.scan_cycles += 1
    
    def increment_military_flight(self):
        with self._lock:
            self.military_flights_found += 1
    
    def increment_ai_success(self):
        with self._lock:
            self.ai_successes += 1
    
    def increment_ai_failure(self):
        with self._lock:
            self.ai_failures += 1
    
    def increment_cache_hit(self):
        with self._lock:
            self.cache_hits += 1
    
    def get_report(self) -> str:
        """تولید گزارش آماری"""
        with self._lock:
            duration = datetime.now(timezone.utc) - self.start_time
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            
            ai_success_rate = (self.ai_successes / max(1, self.ai_successes + self.ai_failures)) * 100
            
            report = (
                f"📊 *گزارش وضعیت ساعتی ربات*\n\n"
                f"⏱️ *مدت زمان فعالیت:* {int(hours)} ساعت و {int(minutes)} دقیقه\n"
                f"🔄 *تعداد کل بررسی‌ها:* {self.scan_cycles}\n"
                f"🎯 *پروازهای شناسایی شده:* *{self.military_flights_found}*\n\n"
                f"🤖 *عملکرد AI:*\n"
                f"   - موفقیت: {self.ai_successes}\n"
                f"   - شکست: {self.ai_failures}\n"
                f"   - نرخ موفقیت: {ai_success_rate:.1f}%\n"
                f"   - استفاده از کش: {self.cache_hits}\n\n"
                f"⏰ *زمان گزارش:* `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}` UTC"
            )
            return report


# ========== Helper Functions ==========

def get_persian_role(typecode: str) -> str:
    """
    تشخیص نقش فارسی بر اساس کد نوع
    
    Args:
        typecode: کد نوع هواپیما
        
    Returns:
        نقش به فارسی
    """
    if not typecode or typecode == 'N/A':
        return "نقش نامشخص"
    
    uc_typecode = typecode.upper()
    best_match = ""
    found_role = "نقش نامشخص"
    
    for code, role in ROLE_MAP_INVERTED.items():
        if code in uc_typecode and len(code) > len(best_match):
            best_match = code
            found_role = role
    
    return found_role


def get_region_from_coords(lat: float, lon: float, country: str) -> str:
    """
    تشخیص منطقه جغرافیایی بر اساس مختصات
    
    Args:
        lat: عرض جغرافیایی
        lon: طول جغرافیایی
        country: کشور
        
    Returns:
        نام منطقه
    """
    found_regions = []
    
    for name, (min_lat, max_lat, min_lon, max_lon) in GEO_REGIONS_EXTENDED.items():
        if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
            area = (max_lat - min_lat) * (max_lon - min_lon)
            found_regions.append((name, area))
    
    if not found_regions:
        return country if country != "Unknown" else "منطقه نامشخص"
    
    # انتخاب کوچکترین منطقه (دقیق‌ترین)
    found_regions.sort(key=lambda x: x[1])
    return found_regions[0][0]


def get_country_from_icao(icao24: str) -> str:
    """
    تشخیص کشور بر اساس کد ICAO
    
    Args:
        icao24: کد ICAO
        
    Returns:
        نام کشور
    """
    try:
        icao_int = int(icao24, 16)
        for country, (start, end) in ICAO_COUNTRY_RANGES.items():
            if start <= icao_int <= end:
                return country
        return "Unknown"
    except (ValueError, TypeError):
        return "Invalid ICAO"


def get_aircraft_model_local(typecode: str) -> str:
    """
    جستجوی مدل هواپیما در دیتابیس محلی
    
    Args:
        typecode: کد نوع
        
    Returns:
        نام مدل
    """
    if not typecode:
        return 'N/A'
    
    uc_typecode = typecode.upper()
    best_match_code = ""
    model = 'N/A'
    
    for code, name in AIRCRAFT_DATABASE.items():
        if code in uc_typecode and len(code) > len(best_match_code):
            best_match_code = code
            model = name
    
    return model


def get_operator_from_callsign(callsign: str) -> str:
    """
    تشخیص اپراتور بر اساس کال‌ساین
    
    Args:
        callsign: علامت تماس
        
    Returns:
        نام اپراتور
    """
    if not callsign or callsign == "N/A":
        return 'N/A'
    
    callsign_upper = callsign.upper()
    
    for prefix, full_name in MILITARY_OPERATORS.items():
        if callsign_upper.startswith(prefix):
            return full_name
    
    return 'N/A'


def create_http_session() -> requests.Session:
    """
    ایجاد session HTTP با قابلیت retry
    
    Returns:
        Session آماده
    """
    session = requests.Session()
    retry = Retry(
        total=HTTP_RETRY_COUNT,
        read=HTTP_RETRY_COUNT,
        connect=HTTP_RETRY_COUNT,
        backoff_factor=0.5,
        status_forcelist=(500, 502, 503, 504)
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def fetch_from_adsblol(session: requests.Session) -> Dict:
    """
    دریافت داده‌های پرواز از ADSB.lol API
    
    Args:
        session: HTTP session
        
    Returns:
        دیکشنری پروازها
    """
    API_URL = "https://api.adsb.lol/v2/mil"
    all_flights = {}
    
    try:
        logger.info(f"📡 Fetching military data from {API_URL}...")
        response = session.get(API_URL, timeout=API_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        
        if 'ac' in data and data['ac']:
            for a in data['ac']:
                # فیلتر هواپیماهای روی زمین یا بدون موقعیت
                alt = a.get('alt_baro')
                if ('lat' not in a or 'lon' not in a or 
                    (isinstance(alt, str) and alt == 'ground') or 
                    (isinstance(alt, (int, float)) and alt <= 0)):
                    continue
                
                flight = {
                    'icao24': a['hex'].lower(),
                    'callsign': a.get('flight', "N/A").strip(),
                    'lat': a['lat'],
                    'lon': a['lon'],
                    'alt': int(alt * 0.3048) if isinstance(alt, (int, float)) else 0,  # feet to meters
                    'vel': int(a.get('gs', 0) * 1.852),  # knots to km/h
                    'heading': a.get('track'),
                    'typecode': a.get('t'),
                    'source': 'ADSB.lol'
                }
                all_flights[flight['icao24']] = flight
            
            logger.info(f"✅ ADSB.lol: Retrieved {len(all_flights)} military flights.")
    
    except Exception as e:
        logger.error(f"❌ ADSB.lol Error: {e}", exc_info=False)
    
    return all_flights


async def analyze_flight_with_ai(
    flight: Dict[str, Any], 
    gemini: GeminiAnalyzer, 
    stats: StatisticsTracker
) -> Dict[str, Any]:
    """
    تحلیل پرواز با استفاده از AI + فالبک هوشمند
    
    Args:
        flight: داده‌های پرواز
        gemini: نمونه Gemini Analyzer
        stats: ردیاب آمار
        
    Returns:
        دیکشنری حاوی تحلیل کامل
    """
    icao24 = flight['icao24']
    db = database.get_db()
    
    # مرحله 1: بررسی کش دیتابیس (بر اساس ICAO)
    cached = db.get_cached_intelligence(icao24)
    if cached and cached.get('confidence_score', 0) >= 0.7:
        logger.info(f"💾 Using cached data for {icao24} (confidence: {cached['confidence_score']:.2f})")
        stats.increment_cache_hit()
        return cached
    
    # مرحله 2: جستجو بر اساس Callsign (برای هواپیماهایی که ICAO تغییر کرده)
    if flight['callsign'] != "N/A":
        callsign_match = db.search_by_callsign(flight['callsign'])
        if callsign_match and callsign_match.get('confidence_score', 0) >= 0.6:
            logger.info(f"💾 Using callsign match for {flight['callsign']}")
            stats.increment_cache_hit()
            return callsign_match
    
    # مرحله 3: تلاش برای تحلیل با AI
    flight['country'] = get_country_from_icao(icao24)
    ai_response = await gemini.analyze_flight(flight)
    
    if ai_response:
        # ذخیره نتیجه AI در دیتابیس برای استفاده‌های بعدی
        db.save_ai_analysis(icao24, flight, ai_response, source="gemini")
        stats.increment_ai_success()
        logger.info(f"🤖 AI analysis successful for {icao24}")
        return ai_response
    else:
        stats.increment_ai_failure()
    
    # مرحله 4: فالبک به روش‌های سنتی (دیکشنری‌های محلی)
    logger.info(f"📚 Using fallback methods for {icao24}")
    
    fallback_analysis = {
        'persian_role': get_persian_role(flight.get('typecode')),
        'aircraft_model': get_aircraft_model_local(flight.get('typecode')),
        'operator_analysis': get_operator_from_callsign(flight['callsign']),
        'location_context': get_region_from_coords(flight['lat'], flight['lon'], flight.get('country', 'Unknown')),
        'strategic_importance': 5.0,  # پیش‌فرض متوسط
        'cached': False,
        'fallback': True
    }
    
    # اگر اطلاعات مفیدی پیدا شد، آن را ذخیره کن (با confidence پایین)
    if fallback_analysis['persian_role'] != "نقش نامشخص" or fallback_analysis['aircraft_model'] != 'N/A':
        db.save_ai_analysis(icao24, flight, fallback_analysis, source="fallback")
    else:
        # ثبت به عنوان ناشناس برای گزارش روزانه
        db.add_unidentified_flight(
            icao24, 
            flight['callsign'], 
            flight.get('typecode', 'N/A'),
            flight.get('country', 'Unknown'),
            flight.get('lat', 0),
            flight.get('lon', 0)
        )
    
    return fallback_analysis


async def send_telegram_notification(bot: Bot, flight: Dict[str, Any], 
                                    analysis: Dict[str, Any]) -> bool:
    """
    ارسال اعلان تلگرام با اطلاعات تحلیل شده
    
    Args:
        bot: نمونه Bot
        flight: داده‌های پرواز
        analysis: تحلیل انجام شده
        
    Returns:
        True در صورت موفقیت
    """
    try:
        # آیکون‌های بصری بر اساس اهمیت
        importance = analysis.get('strategic_importance', 5)
        if importance >= 8:
            importance_icon = "🔴"
        elif importance >= 6:
            importance_icon = "🟠"
        elif importance >= 4:
            importance_icon = "🟡"
        else:
            importance_icon = "🟢"
        
        # آیکون منبع داده
        source_icon = "🤖" if not analysis.get('fallback') else "📚"
        
        message = (
            f"*شناسایی پرواز نظامی* {importance_icon}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"**نقش عملیاتی:** {analysis['persian_role']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"**🛩️ اطلاعات هواپیما:**\n"
            f"   • *علامت تماس:* `{flight['callsign']}`\n"
            f"   • *مدل:* {analysis['aircraft_model']}\n"
            f"   • *کد نوع:* `{flight.get('typecode', 'N/A')}`\n"
            f"   • *کشور ثبت:* {flight.get('country', 'Unknown')}\n"
            f"   • *اپراتور:* {analysis['operator_analysis']}\n"
            f"   • *شناسه ICAO:* `{flight['icao24']}`\n\n"
            f"**📍 اطلاعات موقعیت:**\n"
            f"   • *منطقه:* **{analysis['location_context']}**\n"
            f"   • *ارتفاع:* {flight['alt']:,} متر\n"
            f"   • *سرعت:* {flight['vel']:,} کیلومتر بر ساعت\n"
            f"   • *جهت:* {flight.get('heading', 'N/A')}°\n\n"
            f"**📊 تحلیل استراتژیک:**\n"
            f"   • *اهمیت:* {importance_icon} {importance:.1f}/10\n"
            f"   • *منبع تحلیل:* {source_icon} {'هوش مصنوعی' if not analysis.get('fallback') else 'پایگاه داده'}\n"
            f"   • *منبع رصد:* {flight.get('source', 'Unknown')}\n"
            f"   • *زمان:* `{datetime.now(timezone.utc).strftime('%H:%M:%S')}` UTC\n\n"
            f"**🔗 پیوندها:**\n"
            f"   • [🗺️ مشاهده روی نقشه](https://globe.adsbexchange.com/?icao={flight['icao24']})\n"
            f"   • [📡 جزئیات بیشتر](https://www.adsbexchange.com/api-search/?icao={flight['icao24']})"
        )
        
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=message,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False
        )
        
        logger.info(f"✅ Notification sent for {flight['callsign']} ({flight['icao24']})")
        return True
    
    except Exception as e:
        logger.error(f"❌ Failed to send notification: {e}", exc_info=True)
        return False


# ========== Main Scanning Logic ==========

async def check_flights_producer(
    session: requests.Session,
    stats: StatisticsTracker,
    queue: asyncio.Queue
) -> None:
    """
    تولیدکننده: اسکن پروازها و افزودن به صف
    
    Args:
        session: HTTP session
        stats: ردیاب آمار
        queue: صف پروازها
    """
    try:
        stats.increment_scan()
        logger.info(f"🔍 Starting flight check cycle #{stats.scan_cycles}...")
        
        all_flights = fetch_from_adsblol(session)
        
        new_flights = 0
        for icao, flight in all_flights.items():
            if not database.get_db().is_flight_spotted(icao):
                database.get_db().mark_flight_spotted(icao, flight['callsign'])
                await queue.put(flight)
                new_flights += 1
                logger.info(f"🆕 New flight queued: {flight['callsign']} ({icao})")
        
        if new_flights > 0:
            logger.info(f"📋 Queued {new_flights} new flights for analysis")
        else:
            logger.info(f"✅ Scan complete, no new flights")
    
    except Exception as e:
        logger.error(f"❌ Critical error in check_flights_producer: {e}", exc_info=True)


async def notification_sender_consumer(
    bot: Bot,
    queue: asyncio.Queue,
    gemini: GeminiAnalyzer,
    stats: StatisticsTracker
) -> None:
    """
    مصرف‌کننده: پردازش پروازها و ارسال اعلان
    
    Args:
        bot: نمونه Bot
        queue: صف پروازها
        gemini: تحلیلگر AI
        stats: ردیاب آمار
    """
    logger.info("🚀 Notification sender task started.")
    
    while True:
        try:
            flight = await queue.get()
            
            # فیلتر پروازهای داخل آمریکا
            lat, lon = flight['lat'], flight['lon']
            min_lat, max_lat, min_lon, max_lon = USA_BBOX
            
            if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                logger.info(f"🇺🇸 Filtering US airspace: {flight['callsign']}")
                queue.task_done()
                continue
            
            logger.info(f"🔄 Processing: {flight['callsign']} ({flight['icao24']})")
            
            # تحلیل پرواز (AI + فالبک هوشمند)
            analysis = await analyze_flight_with_ai(flight, gemini, stats)
            
            # ارسال اعلان
            if await send_telegram_notification(bot, flight, analysis):
                stats.increment_military_flight()
            
            queue.task_done()
            
            # تاخیر برای جلوگیری از محدودیت تلگرام
            await asyncio.sleep(MESSAGE_DELAY)
        
        except Exception as e:
            logger.error(f"❌ Error in notification_sender_consumer: {e}", exc_info=True)
            queue.task_done()


# ========== Telegram Job & Command Handlers ==========

async def periodic_check(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Job: بررسی دوره‌ای پروازها"""
    job_data = context.job.data
    await check_flights_producer(
        job_data['session'],
        job_data['stats'],
        job_data['queue']
    )


async def send_hourly_report(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Job: ارسال گزارش ساعتی"""
    stats = context.job.data['stats']
    
    try:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=stats.get_report(),
            parse_mode=ParseMode.MARKDOWN
        )
        logger.info("📊 Hourly report sent")
    except Exception as e:
        logger.error(f"❌ Failed to send hourly report: {e}")
    finally:
        stats.reset()


async def daily_report_and_clear_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Job: گزارش روزانه پروازهای ناشناس"""
    logger.info("📅 Starting daily unidentified aircraft report...")
    
    db = database.get_db()
    records = db.get_unidentified_flights()
    
    if not records:
        logger.info("✅ No unidentified aircraft to report")
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text="📋 *گزارش روزانه*\n\nهیچ هواپیمای ناشناسی در ۲۴ ساعت گذشته ثبت نشده است. ✅",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"❌ Failed to send no-report message: {e}")
    else:
        report_str = f"گزارش هواپیماهای شناسایی نشده - {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n"
        report_str += "=" * 70 + "\n\n"
        report_str += "{:<15} {:<15} {:<15} {:<25}\n".format("ICAO", "Callsign", "Type Code", "Timestamp (UTC)")
        report_str += "-" * 70 + "\n"
        
        for record in records:
            icao, callsign, typecode, ts = record
            report_str += "{:<15} {:<15} {:<15} {:<25}\n".format(
                icao or 'N/A',
                callsign or 'N/A',
                typecode or 'N/A',
                ts
            )
        
        # ارسال به عنوان فایل
        try:
            report_bytes = report_str.encode('utf-8')
            report_file = io.BytesIO(report_bytes)
            report_file.name = f"unidentified_report_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.txt"
            
            await context.bot.send_document(
                chat_id=ADMIN_ID,
                document=report_file,
                caption=f"📋 گزارش روزانه: {len(records)} هواپیمای شناسایی نشده"
            )
            logger.info(f"✅ Daily report sent with {len(records)} records")
        except Exception as e:
            logger.error(f"❌ Failed to send daily report: {e}")
    
    # پاکسازی دیتابیس
    db.clear_unidentified_flights()
    db.cleanup_old_records(MEMORY_CLEANUP_HOURS)
    
    logger.info("🗑️ Daily cleanup completed")


async def start_command(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Command: /start"""
    await update.message.reply_text(
        "🚀 *ربات هوشمند ردیاب هواپیماهای نظامی*\n"
        "نسخه 15.0 - AI Enhanced\n\n"
        "دستورات:\n"
        "/status - مشاهده وضعیت ربات\n"
        "/stats - آمار دیتابیس\n"
        "/apiстат - آمار استفاده از API\n"
        "/test - ارسال پیام تست به کانال",
        parse_mode=ParseMode.MARKDOWN
    )


async def status_command(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Command: /status"""
    try:
        jobs = context.job_queue.jobs()
        if not jobs:
            status_msg = "❌ ربات غیرفعال است."
        else:
            job_data = jobs[0].data
            stats = job_data['stats']
            queue_size = job_data['queue'].qsize()
            
            status_msg = (
                "📊 *وضعیت ربات*\n\n"
                f"✅ وضعیت: *فعال و عملیاتی*\n"
                f"🔄 بازه بررسی: هر *{POLL_INTERVAL_SECONDS}* ثانیه\n"
                f"⏳ پروازهای در صف: *{queue_size}*\n"
                f"🎯 پروازهای ارسال شده: *{stats.military_flights_found}*\n"
                f"🤖 موفقیت AI: *{stats.ai_successes}*\n"
                f"💾 استفاده از کش: *{stats.cache_hits}*\n"
                f"⏰ زمان سرور: `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}` UTC"
            )
    except Exception as e:
        status_msg = f"❌ خطا در دریافت وضعیت: {e}"
    
    await update.message.reply_text(status_msg, parse_mode=ParseMode.MARKDOWN)


async def stats_command(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Command: /stats - آمار دیتابیس"""
    try:
        db_stats = database.get_db().get_database_stats()
        
        stats_msg = (
            "📊 *آمار پایگاه داده*\n\n"
            f"✈️ پروازهای رصد شده: *{db_stats['spotted_flights']}*\n"
            f"🧠 هواپیماهای یادگرفته شده: *{db_stats['learned_aircraft']}*\n"
            f"⭐ هواپیماهای با اعتماد بالا: *{db_stats['high_confidence_aircraft']}*\n"
            f"❓ پروازهای ناشناس فعلی: *{db_stats['unidentified_flights']}*\n\n"
            f"💡 دیتابیس به طور مداوم در حال رشد و یادگیری است."
        )
        
        await update.message.reply_text(stats_msg, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")


async def api_stats_command(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Command: /apistats - آمار API"""
    try:
        api_stats = database.get_db().get_api_stats()
        
        if not api_stats:
            stats_msg = "📊 هنوز آماری ثبت نشده است."
        else:
            stats_msg = "📊 *آمار استفاده از API ها*\n\n"
            for stat in api_stats:
                total = stat['success'] + stat['failure']
                success_rate = (stat['success'] / max(1, total)) * 100
                stats_msg += (
                    f"*{stat['api_name']}*\n"
                    f"  ✅ موفق: {stat['success']}\n"
                    f"  ❌ ناموفق: {stat['failure']}\n"
                    f"  📈 نرخ موفقیت: {success_rate:.1f}%\n\n"
                )
        
        await update.message.reply_text(stats_msg, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")


async def test_command(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Command: /test"""
    try:
        test_msg = (
            f"🧪 *پیام تست*\n\n"
            f"✅ ربات به درستی کار می‌کند.\n"
            f"⏰ زمان: `{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}` UTC"
        )
        
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=test_msg,
            parse_mode=ParseMode.MARKDOWN
        )
        await update.message.reply_text("✅ پیام تست به کانال ارسال شد.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در ارسال: {e}")


def signal_handler(signum, frame):
    """مدیریت سیگنال‌های سیستم برای خاموش شدن امن"""
    logger.info(f"⚠️ Received signal {signum}. Shutting down gracefully...")
    
    # ذخیره آخرین وضعیت دیتابیس
    try:
        database.get_db().cleanup_old_records(MEMORY_CLEANUP_HOURS)
        logger.info("✅ Final database cleanup completed")
    except:
        pass
    
    sys.exit(0)


# ========== Bot Initialization ==========

async def post_init(application: Application) -> None:
    """
    مقداردهی اولیه بعد از راه‌اندازی ربات
    """
    logger.info("=" * 80)
    logger.info("🚀 Military Aircraft Tracker Bot v15.0 (AI-Enhanced Edition)")
    logger.info("=" * 80)
    
    # مقداردهی دیتابیس
    database.init_db()
    
    # ایجاد صف اعلان‌ها
    notification_queue = asyncio.Queue()
    
    # ایجاد تحلیلگر Gemini
    gemini = GeminiAnalyzer(GEMINI_API_KEYS, GEMINI_MODEL)
    
    # داده‌های مشترک job ها
    job_data = {
        'session': create_http_session(),
        'stats': StatisticsTracker(),
        'queue': notification_queue,
        'gemini': gemini
    }
    
    # راه‌اندازی consumer task
    application.create_task(
        notification_sender_consumer(
            application.bot,
            notification_queue,
            gemini,
            job_data['stats']
        )
    )
    
    # راه‌اندازی job های دوره‌ای
    job_queue = application.job_queue
    
    # بررسی دوره‌ای پروازها
    job_queue.run_repeating(
        periodic_check,
        interval=POLL_INTERVAL_SECONDS,
        first=10,
        data=job_data
    )
    
    # گزارش ساعتی
    job_queue.run_repeating(
        send_hourly_report,
        interval=3600,
        first=3600,
        data=job_data
    )
    
    # گزارش و پاکسازی روزانه
    job_queue.run_repeating(
        daily_report_and_clear_job,
        interval=timedelta(hours=24),
        first=timedelta(hours=24),
        data=job_data
    )
    
    logger.info("✅ Bot initialized successfully")
    logger.info(f"📡 Monitoring interval: {POLL_INTERVAL_SECONDS}s")
    logger.info(f"🤖 AI Model: {GEMINI_MODEL}")
    logger.info(f"🔑 API Keys loaded: {len(GEMINI_API_KEYS)}")
    logger.info("🎯 Bot is now running. Press Ctrl+C to stop.")
    logger.info("=" * 80)


def main():
    """نقطه ورود اصلی برنامه"""
    # ثبت signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # ساخت و راه‌اندازی Application
        application = (
            Application.builder()
            .token(TOKEN)
            .post_init(post_init)
            .build()
        )
        
        # ثبت command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("stats", stats_command))
        application.add_handler(CommandHandler("apistats", api_stats_command))
        application.add_handler(CommandHandler("test", test_command))
        
        # اجرای ربات
        application.run_polling(drop_pending_updates=True)
    
    except Exception as e:
        logger.critical(f"💥 Fatal error in main loop: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # بررسی نسخه Python
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        sys.exit(1)
    
    main()
