# -*- coding: utf-8 -*-
"""
Advanced Database Module for Military Aircraft Tracker
Version 2.0 - Enhanced with AI Learning and Pattern Recognition
"""

import sqlite3
import json
import hashlib
import logging
import threading
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import pickle
import gzip
import os
import shutil
from pathlib import Path

from config import get_config

# ========== Logging Setup ==========
logger = logging.getLogger(__name__)

# ========== Data Classes ==========
@dataclass
class AircraftRecord:
    """Aircraft record data class"""
    icao24: str
    callsign: str
    first_seen: datetime
    last_seen: datetime
    total_sightings: int
    typecode: Optional[str] = None
    country: Optional[str] = None
    last_altitude: Optional[int] = None
    last_speed: Optional[int] = None
    last_heading: Optional[float] = None
    last_lat: Optional[float] = None
    last_lon: Optional[float] = None

@dataclass
class AIAnalysisRecord:
    """AI analysis record data class"""
    icao24: str
    typecode: str
    country: str
    persian_role: str
    aircraft_model: str
    operator_analysis: str
    location_context: str
    strategic_importance: int
    confidence_score: float
    threat_level: str
    mission_type: str
    analysis_timestamp: datetime
    hash_key: str

@dataclass
class FlightPattern:
    """Flight pattern data class"""
    id: Optional[int]
    icao24: str
    pattern_type: str
    coordinates: List[Tuple[float, float]]
    timestamp: datetime
    duration_minutes: Optional[int] = None
    distance_km: Optional[float] = None
    max_altitude: Optional[int] = None
    avg_speed: Optional[float] = None

@dataclass
class UnidentifiedAircraft:
    """Unidentified aircraft record data class"""
    icao24: str
    callsign: str
    typecode: str
    first_seen: datetime
    last_seen: datetime
    sighting_count: int
    last_analysis_attempt: Optional[datetime] = None
    analysis_attempts: int = 0

class PatternType(Enum):
    """Flight pattern types"""
    PATROL = "patrol"
    TRANSPORT = "transport"
    RECONNAISSANCE = "reconnaissance"
    TRAINING = "training"
    EMERGENCY = "emergency"
    UNKNOWN = "unknown"

# ========== Database Manager ==========
class AdvancedDatabaseManager:
    """Advanced database manager with AI learning capabilities"""
    
    def __init__(self, db_file: str = None):
        self.config = get_config()
        self.db_file = db_file or self.config.database.DATABASE_FILE
        self._lock = threading.RLock()
        self._connection_pool = []
        self._max_connections = 10
        self._init_database()
        self._setup_connection_pool()
    
    def _init_database(self):
        """Initialize database with all required tables and indexes"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Enable WAL mode for better concurrency
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=-2000")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.execute("PRAGMA mmap_size=268435456")  # 256MB
            
            # Spotted aircraft table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS spotted_aircraft (
                    icao24 TEXT PRIMARY KEY,
                    callsign TEXT NOT NULL,
                    first_seen TIMESTAMP NOT NULL,
                    last_seen TIMESTAMP NOT NULL,
                    total_sightings INTEGER DEFAULT 1,
                    typecode TEXT,
                    country TEXT,
                    last_altitude INTEGER,
                    last_speed INTEGER,
                    last_heading REAL,
                    last_lat REAL,
                    last_lon REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # AI analysis cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_analysis_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    icao24 TEXT NOT NULL,
                    typecode TEXT NOT NULL,
                    country TEXT NOT NULL,
                    persian_role TEXT NOT NULL,
                    aircraft_model TEXT NOT NULL,
                    operator_analysis TEXT NOT NULL,
                    location_context TEXT NOT NULL,
                    strategic_importance INTEGER NOT NULL,
                    confidence_score REAL NOT NULL,
                    threat_level TEXT NOT NULL,
                    mission_type TEXT NOT NULL,
                    analysis_timestamp TIMESTAMP NOT NULL,
                    hash_key TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_icao24 (icao24),
                    INDEX idx_hash_key (hash_key),
                    INDEX idx_timestamp (analysis_timestamp)
                )
            ''')
            
            # Flight patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS flight_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    icao24 TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    coordinates BLOB NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    duration_minutes INTEGER,
                    distance_km REAL,
                    max_altitude INTEGER,
                    avg_speed REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (icao24) REFERENCES spotted_aircraft (icao24),
                    INDEX idx_icao24 (icao24),
                    INDEX idx_pattern_type (pattern_type),
                    INDEX idx_timestamp (timestamp)
                )
            ''')
            
            # Unidentified aircraft table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS unidentified_aircraft (
                    icao24 TEXT PRIMARY KEY,
                    callsign TEXT NOT NULL,
                    typecode TEXT,
                    first_seen TIMESTAMP NOT NULL,
                    last_seen TIMESTAMP NOT NULL,
                    sighting_count INTEGER DEFAULT 1,
                    last_analysis_attempt TIMESTAMP,
                    analysis_attempts INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_last_seen (last_seen),
                    INDEX idx_analysis_attempts (analysis_attempts)
                )
            ''')
            
            # Aircraft statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS aircraft_statistics (
                    icao24 TEXT PRIMARY KEY,
                    total_flights INTEGER DEFAULT 0,
                    total_distance_km REAL DEFAULT 0,
                    avg_altitude INTEGER DEFAULT 0,
                    avg_speed REAL DEFAULT 0,
                    max_altitude INTEGER DEFAULT 0,
                    max_speed REAL DEFAULT 0,
                    countries_visited TEXT,
                    patterns_detected TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (icao24) REFERENCES spotted_aircraft (icao24)
                )
            ''')
            
            # System statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stat_name TEXT UNIQUE NOT NULL,
                    stat_value TEXT NOT NULL,
                    stat_type TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_spotted_last_seen ON spotted_aircraft (last_seen)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_spotted_callsign ON spotted_aircraft (callsign)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_spotted_country ON spotted_aircraft (country)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_unidentified_last_seen ON unidentified_aircraft (last_seen)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_patterns_icao24 ON flight_patterns (icao24)')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def _setup_connection_pool(self):
        """Setup connection pool for better performance"""
        for _ in range(self._max_connections):
            conn = sqlite3.connect(
                self.db_file,
                timeout=30.0,
                check_same_thread=False
            )
            conn.row_factory = sqlite3.Row
            self._connection_pool.append(conn)
    
    def _get_connection(self):
        """Get database connection from pool"""
        with self._lock:
            if self._connection_pool:
                return self._connection_pool.pop()
            else:
                conn = sqlite3.connect(
                    self.db_file,
                    timeout=30.0,
                    check_same_thread=False
                )
                conn.row_factory = sqlite3.Row
                return conn
    
    def _return_connection(self, conn):
        """Return connection to pool"""
        with self._lock:
            if len(self._connection_pool) < self._max_connections:
                self._connection_pool.append(conn)
            else:
                conn.close()
    
    def _serialize_coordinates(self, coordinates: List[Tuple[float, float]]) -> bytes:
        """Serialize coordinates for storage"""
        return gzip.compress(pickle.dumps(coordinates))
    
    def _deserialize_coordinates(self, data: bytes) -> List[Tuple[float, float]]:
        """Deserialize coordinates from storage"""
        return pickle.loads(gzip.decompress(data))
    
    # ========== Aircraft Management ==========
    def add_spotted_aircraft(self, icao24: str, callsign: str, 
                           typecode: str = None, country: str = None,
                           altitude: int = None, speed: int = None,
                           heading: float = None, lat: float = None, lon: float = None) -> bool:
        """Add or update spotted aircraft record"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if aircraft exists
                cursor.execute('SELECT * FROM spotted_aircraft WHERE icao24 = ?', (icao24,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing record
                    cursor.execute('''
                        UPDATE spotted_aircraft SET
                            callsign = COALESCE(?, callsign),
                            last_seen = CURRENT_TIMESTAMP,
                            total_sightings = total_sightings + 1,
                            typecode = COALESCE(?, typecode),
                            country = COALESCE(?, country),
                            last_altitude = COALESCE(?, last_altitude),
                            last_speed = COALESCE(?, last_speed),
                            last_heading = COALESCE(?, last_heading),
                            last_lat = COALESCE(?, last_lat),
                            last_lon = COALESCE(?, last_lon),
                            updated_at = CURRENT_TIMESTAMP
                        WHERE icao24 = ?
                    ''', (callsign, typecode, country, altitude, speed, heading, lat, lon, icao24))
                else:
                    # Insert new record
                    cursor.execute('''
                        INSERT INTO spotted_aircraft 
                        (icao24, callsign, first_seen, last_seen, typecode, country,
                         last_altitude, last_speed, last_heading, last_lat, last_lon)
                        VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?, ?)
                    ''', (icao24, callsign, typecode, country, altitude, speed, heading, lat, lon))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error adding spotted aircraft {icao24}: {e}")
            return False
        finally:
            self._return_connection(conn)
    
    def get_spotted_aircraft(self, icao24: str) -> Optional[AircraftRecord]:
        """Get spotted aircraft record"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM spotted_aircraft WHERE icao24 = ?', (icao24,))
                row = cursor.fetchone()
                
                if row:
                    return AircraftRecord(
                        icao24=row['icao24'],
                        callsign=row['callsign'],
                        first_seen=datetime.fromisoformat(row['first_seen']),
                        last_seen=datetime.fromisoformat(row['last_seen']),
                        total_sightings=row['total_sightings'],
                        typecode=row['typecode'],
                        country=row['country'],
                        last_altitude=row['last_altitude'],
                        last_speed=row['last_speed'],
                        last_heading=row['last_heading'],
                        last_lat=row['last_lat'],
                        last_lon=row['last_lon']
                    )
                return None
                
        except Exception as e:
            logger.error(f"Error getting spotted aircraft {icao24}: {e}")
            return None
        finally:
            self._return_connection(conn)
    
    def check_if_spotted(self, icao24: str) -> bool:
        """Check if aircraft was already spotted"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM spotted_aircraft WHERE icao24 = ?', (icao24,))
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking if spotted {icao24}: {e}")
            return False
        finally:
            self._return_connection(conn)
    
    # ========== AI Analysis Management ==========
    def cache_ai_analysis(self, analysis: AIAnalysisRecord) -> bool:
        """Cache AI analysis for future use"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO ai_analysis_cache 
                    (icao24, typecode, country, persian_role, aircraft_model,
                     operator_analysis, location_context, strategic_importance,
                     confidence_score, threat_level, mission_type, analysis_timestamp, hash_key)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (analysis.icao24, analysis.typecode, analysis.country,
                      analysis.persian_role, analysis.aircraft_model,
                      analysis.operator_analysis, analysis.location_context,
                      analysis.strategic_importance, analysis.confidence_score,
                      analysis.threat_level, analysis.mission_type,
                      analysis.analysis_timestamp, analysis.hash_key))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error caching AI analysis for {analysis.icao24}: {e}")
            return False
        finally:
            self._return_connection(conn)
    
    def get_cached_analysis(self, icao24: str, typecode: str, country: str) -> Optional[AIAnalysisRecord]:
        """Get cached AI analysis if available"""
        try:
            hash_key = hashlib.md5(f"{icao24}_{typecode}_{country}".encode()).hexdigest()
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM ai_analysis_cache WHERE hash_key = ?
                    ORDER BY analysis_timestamp DESC LIMIT 1
                ''', (hash_key,))
                row = cursor.fetchone()
                
                if row:
                    return AIAnalysisRecord(
                        icao24=row['icao24'],
                        typecode=row['typecode'],
                        country=row['country'],
                        persian_role=row['persian_role'],
                        aircraft_model=row['aircraft_model'],
                        operator_analysis=row['operator_analysis'],
                        location_context=row['location_context'],
                        strategic_importance=row['strategic_importance'],
                        confidence_score=row['confidence_score'],
                        threat_level=row['threat_level'],
                        mission_type=row['mission_type'],
                        analysis_timestamp=datetime.fromisoformat(row['analysis_timestamp']),
                        hash_key=row['hash_key']
                    )
                return None
        except Exception as e:
            logger.error(f"Error getting cached analysis for {icao24}: {e}")
            return None
        finally:
            self._return_connection(conn)
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get AI analysis statistics"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Total analyses
                cursor.execute('SELECT COUNT(*) as total FROM ai_analysis_cache')
                total_analyses = cursor.fetchone()['total']
                
                # Analyses by confidence level
                cursor.execute('''
                    SELECT 
                        CASE 
                            WHEN confidence_score >= 0.9 THEN 'High'
                            WHEN confidence_score >= 0.7 THEN 'Medium'
                            ELSE 'Low'
                        END as confidence_level,
                        COUNT(*) as count
                    FROM ai_analysis_cache
                    GROUP BY confidence_level
                ''')
                confidence_stats = dict(cursor.fetchall())
                
                # Analyses by threat level
                cursor.execute('''
                    SELECT threat_level, COUNT(*) as count
                    FROM ai_analysis_cache
                    GROUP BY threat_level
                ''')
                threat_stats = dict(cursor.fetchall())
                
                # Recent analyses (last 24 hours)
                cursor.execute('''
                    SELECT COUNT(*) as recent
                    FROM ai_analysis_cache
                    WHERE analysis_timestamp >= datetime('now', '-1 day')
                ''')
                recent_analyses = cursor.fetchone()['recent']
                
                return {
                    'total_analyses': total_analyses,
                    'confidence_distribution': confidence_stats,
                    'threat_distribution': threat_stats,
                    'recent_analyses_24h': recent_analyses
                }
        except Exception as e:
            logger.error(f"Error getting analysis statistics: {e}")
            return {}
        finally:
            self._return_connection(conn)
    
    # ========== Flight Pattern Management ==========
    def add_flight_pattern(self, pattern: FlightPattern) -> bool:
        """Add flight pattern record"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                coordinates_blob = self._serialize_coordinates(pattern.coordinates)
                
                cursor.execute('''
                    INSERT INTO flight_patterns
                    (icao24, pattern_type, coordinates, timestamp, duration_minutes,
                     distance_km, max_altitude, avg_speed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (pattern.icao24, pattern.pattern_type, coordinates_blob,
                      pattern.timestamp, pattern.duration_minutes,
                      pattern.distance_km, pattern.max_altitude, pattern.avg_speed))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding flight pattern for {pattern.icao24}: {e}")
            return False
        finally:
            self._return_connection(conn)
    
    def get_flight_patterns(self, icao24: str, limit: int = 10) -> List[FlightPattern]:
        """Get flight patterns for aircraft"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM flight_patterns
                    WHERE icao24 = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (icao24, limit))
                
                patterns = []
                for row in cursor.fetchall():
                    coordinates = self._deserialize_coordinates(row['coordinates'])
                    patterns.append(FlightPattern(
                        id=row['id'],
                        icao24=row['icao24'],
                        pattern_type=row['pattern_type'],
                        coordinates=coordinates,
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        duration_minutes=row['duration_minutes'],
                        distance_km=row['distance_km'],
                        max_altitude=row['max_altitude'],
                        avg_speed=row['avg_speed']
                    ))
                return patterns
        except Exception as e:
            logger.error(f"Error getting flight patterns for {icao24}: {e}")
            return []
        finally:
            self._return_connection(conn)
    
    def detect_flight_pattern(self, icao24: str, coordinates: List[Tuple[float, float, int, float]]) -> Optional[PatternType]:
        """Detect flight pattern from coordinates"""
        try:
            if len(coordinates) < 3:
                return PatternType.UNKNOWN
            
            # Simple pattern detection logic
            lats = [coord[0] for coord in coordinates]
            lons = [coord[1] for coord in coordinates]
            alts = [coord[2] for coord in coordinates]
            speeds = [coord[3] for coord in coordinates]
            
            # Calculate basic metrics
            lat_range = max(lats) - min(lats)
            lon_range = max(lons) - min(lons)
            alt_range = max(alts) - min(alts)
            avg_speed = sum(speeds) / len(speeds)
            
            # Pattern detection rules
            if lat_range < 0.01 and lon_range < 0.01:
                return PatternType.PATROL  # Small area, likely patrol
            elif alt_range > 5000 and avg_speed > 800:
                return PatternType.TRANSPORT  # High altitude, high speed
            elif alt_range < 1000 and avg_speed < 300:
                return PatternType.RECONNAISSANCE  # Low altitude, slow speed
            elif avg_speed < 200:
                return PatternType.TRAINING  # Very slow speed
            else:
                return PatternType.UNKNOWN
                
        except Exception as e:
            logger.error(f"Error detecting flight pattern for {icao24}: {e}")
            return PatternType.UNKNOWN
    
    # ========== Unidentified Aircraft Management ==========
    def add_unidentified_aircraft(self, icao24: str, callsign: str, typecode: str = None) -> bool:
        """Add unidentified aircraft to tracking"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO unidentified_aircraft 
                    (icao24, callsign, typecode, last_seen, sighting_count)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP, 
                        COALESCE((SELECT sighting_count FROM unidentified_aircraft WHERE icao24 = ?), 0) + 1)
                ''', (icao24, callsign, typecode, icao24))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding unidentified aircraft {icao24}: {e}")
            return False
        finally:
            self._return_connection(conn)
    
    def get_unidentified_aircraft(self, limit: int = 100) -> List[UnidentifiedAircraft]:
        """Get unidentified aircraft records"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM unidentified_aircraft 
                    ORDER BY last_seen DESC
                    LIMIT ?
                ''', (limit,))
                
                unidentified = []
                for row in cursor.fetchall():
                    unidentified.append(UnidentifiedAircraft(
                        icao24=row['icao24'],
                        callsign=row['callsign'],
                        typecode=row['typecode'],
                        first_seen=datetime.fromisoformat(row['first_seen']),
                        last_seen=datetime.fromisoformat(row['last_seen']),
                        sighting_count=row['sighting_count'],
                        last_analysis_attempt=datetime.fromisoformat(row['last_analysis_attempt']) if row['last_analysis_attempt'] else None,
                        analysis_attempts=row['analysis_attempts']
                    ))
                return unidentified
        except Exception as e:
            logger.error(f"Error getting unidentified aircraft: {e}")
            return []
        finally:
            self._return_connection(conn)
    
    def increment_analysis_attempts(self, icao24: str) -> bool:
        """Increment analysis attempts for unidentified aircraft"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE unidentified_aircraft 
                    SET analysis_attempts = analysis_attempts + 1,
                        last_analysis_attempt = CURRENT_TIMESTAMP
                    WHERE icao24 = ?
                ''', (icao24,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error incrementing analysis attempts for {icao24}: {e}")
            return False
        finally:
            self._return_connection(conn)
    
    # ========== Statistics and Analytics ==========
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Aircraft statistics
                cursor.execute('SELECT COUNT(*) as total FROM spotted_aircraft')
                stats['total_spotted_aircraft'] = cursor.fetchone()['total']
                
                cursor.execute('SELECT COUNT(*) as total FROM unidentified_aircraft')
                stats['total_unidentified_aircraft'] = cursor.fetchone()['total']
                
                cursor.execute('SELECT COUNT(*) as total FROM ai_analysis_cache')
                stats['total_ai_analyses'] = cursor.fetchone()['total']
                
                cursor.execute('SELECT COUNT(*) as total FROM flight_patterns')
                stats['total_flight_patterns'] = cursor.fetchone()['total']
                
                # Recent activity (last 24 hours)
                cursor.execute('''
                    SELECT COUNT(*) as recent
                    FROM spotted_aircraft
                    WHERE last_seen >= datetime('now', '-1 day')
                ''')
                stats['recent_aircraft_24h'] = cursor.fetchone()['recent']
                
                # Top countries
                cursor.execute('''
                    SELECT country, COUNT(*) as count
                    FROM spotted_aircraft
                    WHERE country IS NOT NULL
                    GROUP BY country
                    ORDER BY count DESC
                    LIMIT 10
                ''')
                stats['top_countries'] = dict(cursor.fetchall())
                
                # Top aircraft types
                cursor.execute('''
                    SELECT typecode, COUNT(*) as count
                    FROM spotted_aircraft
                    WHERE typecode IS NOT NULL AND typecode != 'N/A'
                    GROUP BY typecode
                    ORDER BY count DESC
                    LIMIT 10
                ''')
                stats['top_aircraft_types'] = dict(cursor.fetchall())
                
                return stats
        except Exception as e:
            logger.error(f"Error getting system statistics: {e}")
            return {}
        finally:
            self._return_connection(conn)
    
    def update_system_statistic(self, name: str, value: Any, stat_type: str = "string") -> bool:
        """Update system statistic"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO system_statistics
                    (stat_name, stat_value, stat_type, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (name, str(value), stat_type))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating system statistic {name}: {e}")
            return False
        finally:
            self._return_connection(conn)
    
    def get_system_statistic(self, name: str, default: Any = None) -> Any:
        """Get system statistic"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT stat_value, stat_type FROM system_statistics
                    WHERE stat_name = ?
                ''', (name,))
                row = cursor.fetchone()
                
                if row:
                    value = row['stat_value']
                    stat_type = row['stat_type']
                    
                    # Convert based on type
                    if stat_type == "int":
                        return int(value)
                    elif stat_type == "float":
                        return float(value)
                    elif stat_type == "bool":
                        return value.lower() == "true"
                    elif stat_type == "json":
                        return json.loads(value)
                    else:
                        return value
                return default
        except Exception as e:
            logger.error(f"Error getting system statistic {name}: {e}")
            return default
        finally:
            self._return_connection(conn)
    
    # ========== Maintenance and Cleanup ==========
    def cleanup_old_data(self) -> Dict[str, int]:
        """Clean up old data based on TTL settings"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cleanup_stats = {}
                
                # Clean spotted aircraft
                cutoff = datetime.now(timezone.utc) - timedelta(hours=self.config.database.SPOTTED_AIRCRAFT_TTL_HOURS)
                cursor.execute('DELETE FROM spotted_aircraft WHERE last_seen < ?', (cutoff,))
                cleanup_stats['spotted_aircraft'] = cursor.rowcount
                
                # Clean AI analysis cache
                cutoff = datetime.now(timezone.utc) - timedelta(hours=self.config.database.AI_ANALYSIS_CACHE_TTL_HOURS)
                cursor.execute('DELETE FROM ai_analysis_cache WHERE analysis_timestamp < ?', (cutoff,))
                cleanup_stats['ai_analysis_cache'] = cursor.rowcount
                
                # Clean flight patterns
                cutoff = datetime.now(timezone.utc) - timedelta(hours=self.config.database.FLIGHT_PATTERNS_TTL_HOURS)
                cursor.execute('DELETE FROM flight_patterns WHERE timestamp < ?', (cutoff,))
                cleanup_stats['flight_patterns'] = cursor.rowcount
                
                # Clean unidentified aircraft
                cutoff = datetime.now(timezone.utc) - timedelta(hours=self.config.database.UNIDENTIFIED_TTL_HOURS)
                cursor.execute('DELETE FROM unidentified_aircraft WHERE last_seen < ?', (cutoff,))
                cleanup_stats['unidentified_aircraft'] = cursor.rowcount
                
                conn.commit()
                logger.info(f"Cleanup completed: {cleanup_stats}")
                return cleanup_stats
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return {}
        finally:
            self._return_connection(conn)
    
    def vacuum_database(self) -> bool:
        """Vacuum database to reclaim space"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('VACUUM')
                conn.commit()
                logger.info("Database vacuum completed")
                return True
        except Exception as e:
            logger.error(f"Error vacuuming database: {e}")
            return False
        finally:
            self._return_connection(conn)
    
    def backup_database(self, backup_path: str = None) -> bool:
        """Create database backup"""
        try:
            if backup_path is None:
                backup_path = f"{self.db_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create backup directory if it doesn't exist
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # Copy database file
            shutil.copy2(self.db_file, backup_path)
            logger.info(f"Database backup created: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating database backup: {e}")
            return False
    
    def get_database_size(self) -> int:
        """Get database file size in bytes"""
        try:
            return os.path.getsize(self.db_file)
        except Exception as e:
            logger.error(f"Error getting database size: {e}")
            return 0
    
    def optimize_database(self) -> bool:
        """Optimize database performance"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Analyze tables for better query planning
                cursor.execute('ANALYZE')
                
                # Update statistics
                cursor.execute('PRAGMA optimize')
                
                conn.commit()
                logger.info("Database optimization completed")
                return True
        except Exception as e:
            logger.error(f"Error optimizing database: {e}")
            return False
        finally:
            self._return_connection(conn)
    
    # ========== Advanced Analytics ==========
    def get_aircraft_analytics(self, icao24: str) -> Dict[str, Any]:
        """Get detailed analytics for specific aircraft"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                analytics = {}
                
                # Basic aircraft info
                aircraft = self.get_spotted_aircraft(icao24)
                if aircraft:
                    analytics['aircraft'] = asdict(aircraft)
                
                # Flight patterns
                patterns = self.get_flight_patterns(icao24, 50)
                analytics['patterns'] = [asdict(p) for p in patterns]
                
                # AI analysis history
                cursor.execute('''
                    SELECT * FROM ai_analysis_cache
                    WHERE icao24 = ?
                    ORDER BY analysis_timestamp DESC
                ''', (icao24,))
                
                analyses = []
                for row in cursor.fetchall():
                    analyses.append({
                        'persian_role': row['persian_role'],
                        'aircraft_model': row['aircraft_model'],
                        'operator_analysis': row['operator_analysis'],
                        'strategic_importance': row['strategic_importance'],
                        'threat_level': row['threat_level'],
                        'confidence_score': row['confidence_score'],
                        'analysis_timestamp': row['analysis_timestamp']
                    })
                analytics['ai_analyses'] = analyses
                
                return analytics
        except Exception as e:
            logger.error(f"Error getting aircraft analytics for {icao24}: {e}")
            return {}
        finally:
            self._return_connection(conn)
    
    def get_threat_analysis(self) -> Dict[str, Any]:
        """Get threat analysis based on recent activity"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # High threat aircraft (last 24 hours)
                cursor.execute('''
                    SELECT sa.icao24, sa.callsign, sa.country, aac.threat_level, aac.strategic_importance
                    FROM spotted_aircraft sa
                    LEFT JOIN ai_analysis_cache aac ON sa.icao24 = aac.icao24
                    WHERE sa.last_seen >= datetime('now', '-1 day')
                    AND (aac.threat_level = 'بالا' OR aac.threat_level = 'بحرانی' OR aac.strategic_importance >= 8)
                    ORDER BY aac.strategic_importance DESC, sa.last_seen DESC
                ''')
                
                high_threat = []
                for row in cursor.fetchall():
                    high_threat.append({
                        'icao24': row['icao24'],
                        'callsign': row['callsign'],
                        'country': row['country'],
                        'threat_level': row['threat_level'],
                        'strategic_importance': row['strategic_importance']
                    })
                
                # Activity by country (last 24 hours)
                cursor.execute('''
                    SELECT country, COUNT(*) as count
                    FROM spotted_aircraft
                    WHERE last_seen >= datetime('now', '-1 day')
                    AND country IS NOT NULL
                    GROUP BY country
                    ORDER BY count DESC
                ''')
                
                country_activity = dict(cursor.fetchall())
                
                return {
                    'high_threat_aircraft': high_threat,
                    'country_activity_24h': country_activity,
                    'analysis_timestamp': datetime.now(timezone.utc).isoformat()
                }
        except Exception as e:
            logger.error(f"Error getting threat analysis: {e}")
            return {}
        finally:
            self._return_connection(conn)
    
    # ========== Connection Management ==========
    def close_all_connections(self):
        """Close all database connections"""
        with self._lock:
            for conn in self._connection_pool:
                try:
                    conn.close()
                except:
                    pass
            self._connection_pool.clear()
    
    def __del__(self):
        """Destructor to close connections"""
        self.close_all_connections()

# ========== Global Database Instance ==========
# Create global database instance
database = AdvancedDatabaseManager()

# Export commonly used functions for backward compatibility
def init_db():
    """Initialize database (backward compatibility)"""
    global database
    database = AdvancedDatabaseManager()

def add_spotted_aircraft(icao24: str, callsign: str, **kwargs):
    """Add spotted aircraft (backward compatibility)"""
    return database.add_spotted_aircraft(icao24, callsign, **kwargs)

def check_if_spotted(icao24: str) -> bool:
    """Check if spotted (backward compatibility)"""
    return database.check_if_spotted(icao24)

def add_unidentified_aircraft(icao24: str, callsign: str, typecode: str = None):
    """Add unidentified aircraft (backward compatibility)"""
    return database.add_unidentified_aircraft(icao24, callsign, typecode)

def get_unidentified_aircraft() -> List[Tuple]:
    """Get unidentified aircraft (backward compatibility)"""
    unidentified = database.get_unidentified_aircraft()
    return [(u.icao24, u.callsign, u.typecode, u.last_seen.isoformat()) for u in unidentified]

def clear_databases():
    """Clear old data (backward compatibility)"""
    return database.cleanup_old_data()

# ========== Initialization ==========
if __name__ == "__main__":
    # Test database functionality
    db = AdvancedDatabaseManager()
    
    # Test basic operations
    print("Testing database operations...")
    
    # Add test aircraft
    success = db.add_spotted_aircraft("test123", "TEST01", "C130", "United States")
    print(f"Add aircraft: {success}")
    
    # Check if spotted
    spotted = db.check_if_spotted("test123")
    print(f"Check spotted: {spotted}")
    
    # Get statistics
    stats = db.get_system_statistics()
    print(f"System statistics: {stats}")
    
    # Cleanup
    db.close_all_connections()
    print("Database test completed")