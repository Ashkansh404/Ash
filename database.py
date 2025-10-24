# -*- coding: utf-8 -*-
"""
Military Flight Tracker - Advanced Database Module
Handles aircraft tracking, AI analysis caching, and persistent storage
"""

import sqlite3
import logging
import threading
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any
from contextlib import contextmanager

# Initialize logger
logger = logging.getLogger(__name__)


class MilitaryFlightDatabase:
    """
    Advanced database for military flight tracking with AI analysis caching
    """
    
    def __init__(self, db_file: str = "military_flights.db"):
        self.db_file = db_file
        self._lock = threading.Lock()
        self._initialize_database()
        logger.info(f"✅ Database initialized: {db_file}")
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
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
    
    def _initialize_database(self):
        """Create all necessary tables with advanced schema"""
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Table 1: Spotted Aircraft (prevents duplicate notifications)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS spotted_aircraft (
                    icao24 TEXT PRIMARY KEY,
                    callsign TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notification_sent BOOLEAN DEFAULT TRUE,
                    times_spotted INTEGER DEFAULT 1
                )
            """)
            
            # Table 2: AI Analysis Cache (stores Gemini analysis results)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_analysis_cache (
                    icao24 TEXT PRIMARY KEY,
                    callsign TEXT,
                    type_code TEXT,
                    country TEXT,
                    
                    -- AI Analysis Results
                    persian_role TEXT,
                    aircraft_model TEXT,
                    operator_analysis TEXT,
                    strategic_importance INTEGER,
                    
                    -- Metadata
                    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    analysis_source TEXT DEFAULT 'gemini',
                    confidence_score REAL DEFAULT 1.0,
                    
                    -- Usage Statistics
                    times_used INTEGER DEFAULT 0,
                    last_used TIMESTAMP,
                    
                    -- Raw Analysis Data (JSON)
                    raw_analysis TEXT
                )
            """)
            
            # Table 3: Unidentified Aircraft (for daily reports)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS unidentified_aircraft (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    icao24 TEXT,
                    callsign TEXT,
                    type_code TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reason TEXT
                )
            """)
            
            # Table 4: Flight History (comprehensive tracking)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS flight_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    icao24 TEXT,
                    callsign TEXT,
                    type_code TEXT,
                    country TEXT,
                    latitude REAL,
                    longitude REAL,
                    altitude INTEGER,
                    velocity INTEGER,
                    heading REAL,
                    region TEXT,
                    strategic_importance INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (icao24) REFERENCES spotted_aircraft(icao24)
                )
            """)
            
            # Table 5: Statistics (for hourly reports)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE DEFAULT CURRENT_DATE,
                    hour INTEGER,
                    flights_detected INTEGER DEFAULT 0,
                    notifications_sent INTEGER DEFAULT 0,
                    ai_analyses_performed INTEGER DEFAULT 0,
                    cache_hits INTEGER DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indices for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_spotted_icao ON spotted_aircraft(icao24)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_spotted_last_seen ON spotted_aircraft(last_seen)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_cache_icao ON ai_analysis_cache(icao24)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_cache_timestamp ON ai_analysis_cache(analysis_timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_flight_history_icao ON flight_history(icao24)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_flight_history_timestamp ON flight_history(timestamp)")
            
            conn.commit()
            logger.info("✅ Database tables and indices created successfully")
    
    # ========== Spotted Aircraft Management ==========
    
    def is_aircraft_spotted(self, icao24: str) -> bool:
        """Check if aircraft has been spotted before"""
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM spotted_aircraft WHERE icao24 = ?",
                (icao24.lower(),)
            )
            return cursor.fetchone() is not None
    
    def add_spotted_aircraft(self, icao24: str, callsign: str) -> bool:
        """Add newly spotted aircraft"""
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """INSERT INTO spotted_aircraft (icao24, callsign) 
                       VALUES (?, ?)""",
                    (icao24.lower(), callsign.strip())
                )
                logger.info(f"➕ Added spotted aircraft: {icao24} ({callsign})")
                return True
            except sqlite3.IntegrityError:
                # Already exists, update last_seen
                cursor.execute(
                    """UPDATE spotted_aircraft 
                       SET last_seen = CURRENT_TIMESTAMP, 
                           times_spotted = times_spotted + 1
                       WHERE icao24 = ?""",
                    (icao24.lower(),)
                )
                logger.debug(f"🔄 Updated existing aircraft: {icao24}")
                return False
    
    def get_spotted_count(self) -> int:
        """Get total number of spotted aircraft"""
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM spotted_aircraft")
            return cursor.fetchone()[0]
    
    # ========== AI Analysis Cache Management ==========
    
    def get_ai_analysis(self, icao24: str, type_code: str = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached AI analysis for an aircraft
        Returns None if not found or expired
        """
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM ai_analysis_cache 
                   WHERE icao24 = ?
                   ORDER BY analysis_timestamp DESC
                   LIMIT 1""",
                (icao24.lower(),)
            )
            row = cursor.fetchone()
            
            if row:
                # Update usage statistics
                cursor.execute(
                    """UPDATE ai_analysis_cache 
                       SET times_used = times_used + 1,
                           last_used = CURRENT_TIMESTAMP
                       WHERE icao24 = ?""",
                    (icao24.lower(),)
                )
                
                result = {
                    'icao24': row['icao24'],
                    'callsign': row['callsign'],
                    'type_code': row['type_code'],
                    'country': row['country'],
                    'persian_role': row['persian_role'],
                    'aircraft_model': row['aircraft_model'],
                    'operator_analysis': row['operator_analysis'],
                    'strategic_importance': row['strategic_importance'],
                    'analysis_timestamp': row['analysis_timestamp'],
                    'times_used': row['times_used'] + 1,
                    'source': 'cache'
                }
                
                logger.info(f"🎯 Cache HIT for {icao24}: {result['aircraft_model']}")
                self.increment_statistic('cache_hits')
                return result
            
            logger.debug(f"❌ Cache MISS for {icao24}")
            return None
    
    def save_ai_analysis(
        self, 
        icao24: str,
        callsign: str,
        type_code: str,
        country: str,
        analysis: Dict[str, Any]
    ) -> bool:
        """Save AI analysis results to cache"""
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """INSERT OR REPLACE INTO ai_analysis_cache 
                       (icao24, callsign, type_code, country, 
                        persian_role, aircraft_model, operator_analysis, 
                        strategic_importance, raw_analysis, analysis_timestamp)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                    (
                        icao24.lower(),
                        callsign.strip(),
                        type_code,
                        country,
                        analysis.get('persian_role', 'نامشخص'),
                        analysis.get('aircraft_model', 'نامشخص'),
                        analysis.get('operator_analysis', 'نامشخص'),
                        analysis.get('strategic_importance', 5),
                        json.dumps(analysis, ensure_ascii=False)
                    )
                )
                logger.info(f"💾 Saved AI analysis for {icao24}: {analysis.get('aircraft_model')}")
                self.increment_statistic('ai_analyses_performed')
                return True
            except Exception as e:
                logger.error(f"Failed to save AI analysis: {e}")
                return False
    
    # ========== Flight History ==========
    
    def add_flight_record(self, flight_data: Dict[str, Any]) -> bool:
        """Add detailed flight record to history"""
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """INSERT INTO flight_history 
                       (icao24, callsign, type_code, country, latitude, longitude,
                        altitude, velocity, heading, region, strategic_importance)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        flight_data.get('icao24', '').lower(),
                        flight_data.get('callsign', '').strip(),
                        flight_data.get('typecode'),
                        flight_data.get('country'),
                        flight_data.get('lat'),
                        flight_data.get('lon'),
                        flight_data.get('alt'),
                        flight_data.get('vel'),
                        flight_data.get('heading'),
                        flight_data.get('region'),
                        flight_data.get('strategic_importance', 5)
                    )
                )
                return True
            except Exception as e:
                logger.error(f"Failed to add flight record: {e}")
                return False
    
    def get_flight_history(self, icao24: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent flight history for an aircraft"""
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT * FROM flight_history 
                   WHERE icao24 = ?
                   ORDER BY timestamp DESC
                   LIMIT ?""",
                (icao24.lower(), limit)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    # ========== Unidentified Aircraft ==========
    
    def add_unidentified_aircraft(
        self, 
        icao24: str, 
        callsign: str, 
        type_code: str,
        reason: str = "Unknown role/model"
    ) -> bool:
        """Add aircraft that couldn't be fully identified"""
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """INSERT INTO unidentified_aircraft 
                       (icao24, callsign, type_code, reason)
                       VALUES (?, ?, ?, ?)""",
                    (icao24.lower(), callsign.strip(), type_code, reason)
                )
                logger.info(f"📝 Added unidentified aircraft: {icao24} ({callsign})")
                return True
            except Exception as e:
                logger.error(f"Failed to add unidentified aircraft: {e}")
                return False
    
    def get_unidentified_aircraft(self) -> List[Tuple]:
        """Get all unidentified aircraft for reporting"""
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT icao24, callsign, type_code, timestamp, reason
                   FROM unidentified_aircraft
                   ORDER BY timestamp DESC"""
            )
            return cursor.fetchall()
    
    def clear_unidentified_aircraft(self) -> int:
        """Clear unidentified aircraft table (after daily report)"""
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM unidentified_aircraft")
            deleted = cursor.rowcount
            logger.info(f"🗑️ Cleared {deleted} unidentified aircraft records")
            return deleted
    
    # ========== Statistics ==========
    
    def increment_statistic(self, stat_type: str) -> None:
        """Increment a statistic counter for current hour"""
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc)
            
            # Check if entry exists for current hour
            cursor.execute(
                """SELECT id FROM statistics 
                   WHERE date = DATE('now') AND hour = ?""",
                (now.hour,)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                column_map = {
                    'flights_detected': 'flights_detected',
                    'notifications_sent': 'notifications_sent',
                    'ai_analyses_performed': 'ai_analyses_performed',
                    'cache_hits': 'cache_hits'
                }
                if stat_type in column_map:
                    cursor.execute(
                        f"""UPDATE statistics 
                            SET {column_map[stat_type]} = {column_map[stat_type]} + 1
                            WHERE id = ?""",
                        (existing['id'],)
                    )
            else:
                # Create new record
                cursor.execute(
                    f"""INSERT INTO statistics (date, hour, {stat_type})
                        VALUES (DATE('now'), ?, 1)""",
                    (now.hour,)
                )
    
    def get_hourly_statistics(self) -> Dict[str, int]:
        """Get statistics for current hour"""
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc)
            cursor.execute(
                """SELECT * FROM statistics 
                   WHERE date = DATE('now') AND hour = ?""",
                (now.hour,)
            )
            row = cursor.fetchone()
            
            if row:
                return {
                    'flights_detected': row['flights_detected'],
                    'notifications_sent': row['notifications_sent'],
                    'ai_analyses_performed': row['ai_analyses_performed'],
                    'cache_hits': row['cache_hits']
                }
            return {
                'flights_detected': 0,
                'notifications_sent': 0,
                'ai_analyses_performed': 0,
                'cache_hits': 0
            }
    
    # ========== Cleanup Operations ==========
    
    def cleanup_old_records(self, days: int = 30) -> Dict[str, int]:
        """Remove old records to keep database size manageable"""
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Clean old spotted aircraft
            cursor.execute(
                "DELETE FROM spotted_aircraft WHERE last_seen < ?",
                (cutoff_date,)
            )
            spotted_deleted = cursor.rowcount
            
            # Clean old flight history
            cursor.execute(
                "DELETE FROM flight_history WHERE timestamp < ?",
                (cutoff_date,)
            )
            history_deleted = cursor.rowcount
            
            # Clean old AI cache (keep for longer - 90 days)
            ai_cutoff = datetime.now(timezone.utc) - timedelta(days=90)
            cursor.execute(
                "DELETE FROM ai_analysis_cache WHERE analysis_timestamp < ? AND times_used = 0",
                (ai_cutoff,)
            )
            cache_deleted = cursor.rowcount
            
            # Clean old statistics
            cursor.execute(
                "DELETE FROM statistics WHERE timestamp < ?",
                (cutoff_date,)
            )
            stats_deleted = cursor.rowcount
            
            # Vacuum database to reclaim space
            cursor.execute("VACUUM")
            
            logger.info(
                f"🧹 Cleanup complete: {spotted_deleted} spotted, "
                f"{history_deleted} history, {cache_deleted} cache, "
                f"{stats_deleted} stats deleted"
            )
            
            return {
                'spotted': spotted_deleted,
                'history': history_deleted,
                'cache': cache_deleted,
                'statistics': stats_deleted
            }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        with self._lock, self._get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Count records in each table
            for table in ['spotted_aircraft', 'ai_analysis_cache', 
                         'unidentified_aircraft', 'flight_history', 'statistics']:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f'{table}_count'] = cursor.fetchone()[0]
            
            # Get cache hit rate
            cursor.execute(
                """SELECT 
                    SUM(cache_hits) as total_hits,
                    SUM(ai_analyses_performed) as total_analyses
                   FROM statistics"""
            )
            row = cursor.fetchone()
            if row and row[1] and row[1] > 0:
                stats['cache_hit_rate'] = (row[0] / (row[0] + row[1])) * 100
            else:
                stats['cache_hit_rate'] = 0.0
            
            # Database file size
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            stats['database_size_mb'] = cursor.fetchone()[0] / (1024 * 1024)
            
            return stats


# ========== Global Database Instance ==========
_db_instance = None
_db_lock = threading.Lock()


def get_database(db_file: str = "military_flights.db") -> MilitaryFlightDatabase:
    """Get or create global database instance (thread-safe singleton)"""
    global _db_instance
    if _db_instance is None:
        with _db_lock:
            if _db_instance is None:
                _db_instance = MilitaryFlightDatabase(db_file)
    return _db_instance


# ========== Convenience Functions ==========
# These mirror the old API for backward compatibility

def init_db(db_file: str = "military_flights.db"):
    """Initialize database (compatibility function)"""
    get_database(db_file)


def check_if_spotted(icao24: str) -> bool:
    """Check if aircraft spotted (compatibility function)"""
    return get_database().is_aircraft_spotted(icao24)


def add_spotted_aircraft(icao24: str, callsign: str) -> bool:
    """Add spotted aircraft (compatibility function)"""
    return get_database().add_spotted_aircraft(icao24, callsign)


def add_unidentified_aircraft(icao24: str, callsign: str, type_code: str) -> bool:
    """Add unidentified aircraft (compatibility function)"""
    return get_database().add_unidentified_aircraft(icao24, callsign, type_code)


def get_unidentified_aircraft() -> List[Tuple]:
    """Get unidentified aircraft (compatibility function)"""
    return get_database().get_unidentified_aircraft()


def clear_databases() -> None:
    """Clear unidentified aircraft (compatibility function)"""
    get_database().clear_unidentified_aircraft()


if __name__ == "__main__":
    # Test database functionality
    print("🧪 Testing database module...")
    
    db = MilitaryFlightDatabase("test_military_flights.db")
    
    # Test spotted aircraft
    db.add_spotted_aircraft("ae1234", "TEST123")
    assert db.is_aircraft_spotted("ae1234")
    print("✅ Spotted aircraft test passed")
    
    # Test AI cache
    test_analysis = {
        'persian_role': 'جنگنده چندمنظوره',
        'aircraft_model': 'F-16 Fighting Falcon',
        'operator_analysis': 'US Air Force',
        'strategic_importance': 7
    }
    db.save_ai_analysis("ae1234", "TEST123", "F16", "United States", test_analysis)
    cached = db.get_ai_analysis("ae1234")
    assert cached is not None
    assert cached['aircraft_model'] == 'F-16 Fighting Falcon'
    print("✅ AI cache test passed")
    
    # Test statistics
    stats = db.get_database_stats()
    print(f"📊 Database stats: {stats}")
    
    print("\n✅ All database tests passed!")
