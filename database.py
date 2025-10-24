# -*- coding: utf-8 -*-
"""
مدیریت پایگاه داده هوشمند ربات ردیاب پروازهای نظامی
Intelligent Database Manager for Military Flight Tracker Bot

این ماژول شامل:
- ذخیره پروازهای رصد شده
- یادگیری و ذخیره اطلاعات هواپیماها از تحلیل‌های AI
- کش هوشمند برای استفاده در صورت عدم دسترسی به AI
- مدیریت پروازهای ناشناس
"""

import sqlite3
import threading
import logging
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class FlightDatabase:
    """پایگاه داده هوشمند برای ذخیره و یادگیری اطلاعات پروازها"""
    
    def __init__(self, db_file: str = "flight_tracker.db"):
        """
        مقداردهی اولیه پایگاه داده
        
        Args:
            db_file: مسیر فایل دیتابیس SQLite
        """
        self.db_file = db_file
        self._lock = threading.Lock()
        self.init_db()
        logger.info(f"✅ Database initialized: {db_file}")
    
    @contextmanager
    def get_connection(self):
        """Context manager برای مدیریت امن اتصال به دیتابیس"""
        conn = sqlite3.connect(self.db_file, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}", exc_info=True)
            raise
        finally:
            conn.close()
    
    def init_db(self):
        """ایجاد جداول دیتابیس در صورت عدم وجود"""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            
            # جدول پروازهای رصد شده (برای جلوگیری از ارسال مجدد)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS spotted_flights (
                    icao24 TEXT PRIMARY KEY,
                    callsign TEXT,
                    first_spotted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    spot_count INTEGER DEFAULT 1
                )
            ''')
            
            # جدول دانش یادگرفته شده از AI (کش هوشمند)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS aircraft_intelligence (
                    icao24 TEXT PRIMARY KEY,
                    callsign TEXT,
                    aircraft_model TEXT,
                    persian_role TEXT,
                    operator TEXT,
                    country TEXT,
                    typecode TEXT,
                    strategic_importance REAL,
                    ai_analysis TEXT,
                    confidence_score REAL DEFAULT 0.0,
                    learned_from TEXT,
                    first_learned TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usage_count INTEGER DEFAULT 0
                )
            ''')
            
            # جدول پروازهای ناشناس (برای گزارش روزانه)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS unidentified_flights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    icao24 TEXT,
                    callsign TEXT,
                    typecode TEXT,
                    country TEXT,
                    latitude REAL,
                    longitude REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول آمار استفاده از API های مختلف
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_name TEXT,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_error TEXT
                )
            ''')
            
            # ایجاد ایندکس برای بهبود کارایی
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_spotted_icao ON spotted_flights(icao24)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_intelligence_icao ON aircraft_intelligence(icao24)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_intelligence_callsign ON aircraft_intelligence(callsign)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_unidentified_timestamp ON unidentified_flights(timestamp)')
            
            conn.commit()
    
    # ========== مدیریت پروازهای رصد شده ==========
    
    def is_flight_spotted(self, icao24: str) -> bool:
        """
        بررسی اینکه آیا پرواز قبلاً رصد شده است
        
        Args:
            icao24: کد ICAO هواپیما
            
        Returns:
            True اگر قبلاً رصد شده باشد
        """
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM spotted_flights WHERE icao24 = ?', (icao24,))
            return cursor.fetchone() is not None
    
    def mark_flight_spotted(self, icao24: str, callsign: str = "N/A"):
        """
        ثبت پرواز به عنوان رصد شده
        
        Args:
            icao24: کد ICAO هواپیما
            callsign: علامت تماس
        """
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO spotted_flights (icao24, callsign, first_spotted, last_seen, spot_count)
                VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)
                ON CONFLICT(icao24) DO UPDATE SET
                    last_seen = CURRENT_TIMESTAMP,
                    spot_count = spot_count + 1,
                    callsign = excluded.callsign
            ''', (icao24, callsign))
    
    # ========== مدیریت دانش یادگرفته شده از AI ==========
    
    def save_ai_analysis(self, icao24: str, flight_data: Dict[str, Any], 
                        ai_response: Dict[str, Any], source: str = "gemini"):
        """
        ذخیره تحلیل AI برای استفاده‌های آینده
        
        Args:
            icao24: کد ICAO هواپیما
            flight_data: داده‌های خام پرواز
            ai_response: پاسخ دریافتی از AI
            source: منبع تحلیل (gemini, manual, etc.)
        """
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            
            # محاسبه امتیاز اعتماد بر اساس کامل بودن اطلاعات
            confidence = self._calculate_confidence(ai_response)
            
            cursor.execute('''
                INSERT INTO aircraft_intelligence (
                    icao24, callsign, aircraft_model, persian_role, operator,
                    country, typecode, strategic_importance, ai_analysis,
                    confidence_score, learned_from, first_learned, last_updated, usage_count
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0)
                ON CONFLICT(icao24) DO UPDATE SET
                    callsign = excluded.callsign,
                    aircraft_model = CASE 
                        WHEN excluded.confidence_score > confidence_score 
                        THEN excluded.aircraft_model 
                        ELSE aircraft_model 
                    END,
                    persian_role = CASE 
                        WHEN excluded.confidence_score > confidence_score 
                        THEN excluded.persian_role 
                        ELSE persian_role 
                    END,
                    operator = CASE 
                        WHEN excluded.confidence_score > confidence_score 
                        THEN excluded.operator 
                        ELSE operator 
                    END,
                    confidence_score = MAX(confidence_score, excluded.confidence_score),
                    last_updated = CURRENT_TIMESTAMP
            ''', (
                icao24,
                flight_data.get('callsign', 'N/A'),
                ai_response.get('aircraft_model', 'N/A'),
                ai_response.get('persian_role', 'نقش نامشخص'),
                ai_response.get('operator_analysis', 'N/A'),
                flight_data.get('country', 'Unknown'),
                flight_data.get('typecode', 'N/A'),
                ai_response.get('strategic_importance', 5.0),
                json.dumps(ai_response, ensure_ascii=False),
                confidence,
                source
            ))
            
            logger.info(f"💾 Saved AI analysis for {icao24} (confidence: {confidence:.2f})")
    
    def get_cached_intelligence(self, icao24: str) -> Optional[Dict[str, Any]]:
        """
        بازیابی اطلاعات ذخیره شده از کش هوشمند
        
        Args:
            icao24: کد ICAO هواپیما
            
        Returns:
            دیکشنری حاوی اطلاعات یا None
        """
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT aircraft_model, persian_role, operator, country,
                       strategic_importance, ai_analysis, confidence_score
                FROM aircraft_intelligence
                WHERE icao24 = ?
            ''', (icao24,))
            
            row = cursor.fetchone()
            if row:
                # به‌روزرسانی شمارنده استفاده
                cursor.execute('''
                    UPDATE aircraft_intelligence 
                    SET usage_count = usage_count + 1 
                    WHERE icao24 = ?
                ''', (icao24,))
                
                return {
                    'aircraft_model': row['aircraft_model'],
                    'persian_role': row['persian_role'],
                    'operator_analysis': row['operator'],
                    'country': row['country'],
                    'strategic_importance': row['strategic_importance'],
                    'ai_analysis': row['ai_analysis'],
                    'confidence_score': row['confidence_score'],
                    'cached': True
                }
            return None
    
    def search_by_callsign(self, callsign: str) -> Optional[Dict[str, Any]]:
        """
        جستجوی هواپیما بر اساس علامت تماس
        
        Args:
            callsign: علامت تماس
            
        Returns:
            اطلاعات هواپیما یا None
        """
        if not callsign or callsign == "N/A":
            return None
            
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT aircraft_model, persian_role, operator, country,
                       strategic_importance, confidence_score
                FROM aircraft_intelligence
                WHERE callsign = ?
                ORDER BY confidence_score DESC, last_updated DESC
                LIMIT 1
            ''', (callsign.strip(),))
            
            row = cursor.fetchone()
            if row:
                return {
                    'aircraft_model': row['aircraft_model'],
                    'persian_role': row['persian_role'],
                    'operator_analysis': row['operator'],
                    'country': row['country'],
                    'strategic_importance': row['strategic_importance'],
                    'confidence_score': row['confidence_score'],
                    'cached': True
                }
            return None
    
    # ========== مدیریت پروازهای ناشناس ==========
    
    def add_unidentified_flight(self, icao24: str, callsign: str, 
                               typecode: str, country: str = "Unknown",
                               lat: float = 0.0, lon: float = 0.0):
        """
        افزودن پرواز ناشناس برای گزارش روزانه
        
        Args:
            icao24: کد ICAO
            callsign: علامت تماس
            typecode: کد نوع هواپیما
            country: کشور
            lat: عرض جغرافیایی
            lon: طول جغرافیایی
        """
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO unidentified_flights 
                (icao24, callsign, typecode, country, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (icao24, callsign, typecode, country, lat, lon))
    
    def get_unidentified_flights(self) -> List[Tuple]:
        """
        دریافت لیست پروازهای ناشناس برای گزارش
        
        Returns:
            لیست تاپل‌های حاوی اطلاعات پروازها
        """
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT icao24, callsign, typecode, 
                       datetime(timestamp) as timestamp
                FROM unidentified_flights
                ORDER BY timestamp DESC
            ''')
            return cursor.fetchall()
    
    def clear_unidentified_flights(self):
        """پاکسازی پروازهای ناشناس (بعد از ارسال گزارش)"""
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM unidentified_flights')
            logger.info("🗑️ Cleared unidentified flights table")
    
    # ========== مدیریت آمار API ==========
    
    def log_api_usage(self, api_name: str, success: bool, error: str = None):
        """
        ثبت استفاده از API برای آمارگیری
        
        Args:
            api_name: نام API
            success: موفق بود یا خیر
            error: پیام خطا (در صورت وجود)
        """
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            
            if success:
                cursor.execute('''
                    INSERT INTO api_stats (api_name, success_count, failure_count, last_used)
                    VALUES (?, 1, 0, CURRENT_TIMESTAMP)
                    ON CONFLICT(api_name) DO UPDATE SET
                        success_count = success_count + 1,
                        last_used = CURRENT_TIMESTAMP
                ''', (api_name,))
            else:
                cursor.execute('''
                    INSERT INTO api_stats (api_name, success_count, failure_count, last_used, last_error)
                    VALUES (?, 0, 1, CURRENT_TIMESTAMP, ?)
                    ON CONFLICT(api_name) DO UPDATE SET
                        failure_count = failure_count + 1,
                        last_used = CURRENT_TIMESTAMP,
                        last_error = excluded.last_error
                ''', (api_name, error))
    
    def get_api_stats(self) -> List[Dict[str, Any]]:
        """
        دریافت آمار استفاده از API ها
        
        Returns:
            لیست آمار API ها
        """
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT api_name, success_count, failure_count, 
                       last_used, last_error
                FROM api_stats
                ORDER BY last_used DESC
            ''')
            
            stats = []
            for row in cursor.fetchall():
                stats.append({
                    'api_name': row['api_name'],
                    'success': row['success_count'],
                    'failure': row['failure_count'],
                    'last_used': row['last_used'],
                    'last_error': row['last_error']
                })
            return stats
    
    # ========== پاکسازی و نگهداری ==========
    
    def cleanup_old_records(self, hours: int = 24):
        """
        پاکسازی رکوردهای قدیمی
        
        Args:
            hours: رکوردهای قدیمی‌تر از این مقدار پاک می‌شوند
        """
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            
            # پاکسازی پروازهای رصد شده قدیمی
            cursor.execute('''
                DELETE FROM spotted_flights
                WHERE last_seen < datetime('now', '-' || ? || ' hours')
            ''', (hours,))
            deleted_spotted = cursor.rowcount
            
            # پاکسازی پروازهای ناشناس قدیمی
            cursor.execute('''
                DELETE FROM unidentified_flights
                WHERE timestamp < datetime('now', '-' || ? || ' hours')
            ''', (hours,))
            deleted_unidentified = cursor.rowcount
            
            if deleted_spotted > 0 or deleted_unidentified > 0:
                logger.info(f"🗑️ Cleaned up {deleted_spotted} spotted flights "
                           f"and {deleted_unidentified} unidentified flights")
            
            # فشرده‌سازی دیتابیس
            cursor.execute('VACUUM')
    
    def get_database_stats(self) -> Dict[str, int]:
        """
        دریافت آمار کلی دیتابیس
        
        Returns:
            دیکشنری حاوی آمار
        """
        with self._lock, self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            cursor.execute('SELECT COUNT(*) as count FROM spotted_flights')
            stats['spotted_flights'] = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM aircraft_intelligence')
            stats['learned_aircraft'] = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM unidentified_flights')
            stats['unidentified_flights'] = cursor.fetchone()['count']
            
            cursor.execute('''
                SELECT COUNT(*) as count FROM aircraft_intelligence 
                WHERE confidence_score >= 0.8
            ''')
            stats['high_confidence_aircraft'] = cursor.fetchone()['count']
            
            return stats
    
    # ========== توابع کمکی ==========
    
    def _calculate_confidence(self, ai_response: Dict[str, Any]) -> float:
        """
        محاسبه امتیاز اعتماد بر اساس کامل بودن داده‌ها
        
        Args:
            ai_response: پاسخ AI
            
        Returns:
            امتیاز اعتماد بین 0 تا 1
        """
        score = 0.0
        total_fields = 4
        
        # بررسی وجود و کیفیت هر فیلد
        if ai_response.get('aircraft_model') and ai_response['aircraft_model'] != 'N/A':
            score += 0.3
        if ai_response.get('persian_role') and ai_response['persian_role'] != 'نقش نامشخص':
            score += 0.3
        if ai_response.get('operator_analysis') and ai_response['operator_analysis'] != 'N/A':
            score += 0.2
        if ai_response.get('strategic_importance') and isinstance(ai_response['strategic_importance'], (int, float)):
            score += 0.2
        
        return min(score, 1.0)


# ========== Singleton Instance ==========
_db_instance = None

def get_db(db_file: str = "flight_tracker.db") -> FlightDatabase:
    """
    دریافت نمونه singleton پایگاه داده
    
    Args:
        db_file: مسیر فایل دیتابیس
        
    Returns:
        نمونه FlightDatabase
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = FlightDatabase(db_file)
    return _db_instance


# ========== توابع سازگار با کد قدیمی ==========
def init_db():
    """مقداردهی اولیه دیتابیس (برای سازگاری با کد قدیمی)"""
    get_db()

def check_if_spotted(icao24: str) -> bool:
    """بررسی رصد شدن پرواز"""
    return get_db().is_flight_spotted(icao24)

def add_spotted_aircraft(icao24: str, callsign: str = "N/A"):
    """افزودن پرواز رصد شده"""
    get_db().mark_flight_spotted(icao24, callsign)

def add_unidentified_aircraft(icao24: str, callsign: str, typecode: str):
    """افزودن هواپیمای ناشناس"""
    get_db().add_unidentified_flight(icao24, callsign, typecode)

def get_unidentified_aircraft() -> List[Tuple]:
    """دریافت لیست هواپیماهای ناشناس"""
    return get_db().get_unidentified_flights()

def clear_databases():
    """پاکسازی دیتابیس"""
    get_db().clear_unidentified_flights()
