# -*- coding: utf-8 -*-
"""
Advanced Database Module for Military Flight Tracker Bot
Version: 2.0 - AI Learning and Fallback System
"""

import sqlite3
import json
import logging
import threading
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import pickle
import gzip
import os
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class AircraftProfile:
    """Aircraft profile with learned characteristics"""
    icao24: str
    callsign_patterns: List[str]
    common_typecode: str
    common_country: str
    common_operator: str
    flight_frequency: int
    last_seen: datetime
    confidence_score: float
    ai_analysis_history: List[Dict]
    created_at: datetime
    updated_at: datetime

@dataclass
class FlightRecord:
    """Individual flight record"""
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
    ai_analysis: Optional[Dict]
    strategic_importance: Optional[int]
    confidence_score: Optional[float]

class AdvancedDatabaseManager:
    """Advanced database manager with AI learning capabilities"""
    
    def __init__(self, db_file: str):
        self.db_file = db_file
        self._lock = threading.RLock()
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
        self.init_database()
        self.load_aircraft_profiles()
    
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
                    total_sightings INTEGER DEFAULT 1,
                    confidence_score REAL DEFAULT 0.0,
                    is_military BOOLEAN DEFAULT 1
                )
            ''')
            
            # AI analysis cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_analysis_cache (
                    icao24 TEXT PRIMARY KEY,
                    analysis_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    confidence_score REAL,
                    api_used TEXT,
                    model_version TEXT,
                    expires_at TIMESTAMP
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
                    strategic_importance INTEGER,
                    confidence_score REAL,
                    FOREIGN KEY (icao24) REFERENCES spotted_aircraft(icao24)
                )
            ''')
            
            # Aircraft profiles table (AI learning)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS aircraft_profiles (
                    icao24 TEXT PRIMARY KEY,
                    profile_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    learning_score REAL DEFAULT 0.0
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
                    learning_updates INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # API usage tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_name TEXT,
                    endpoint TEXT,
                    success_count INTEGER DEFAULT 0,
                    error_count INTEGER DEFAULT 0,
                    last_used TIMESTAMP,
                    rate_limit_reset TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Geographic patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS geographic_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    icao24 TEXT,
                    region TEXT,
                    frequency INTEGER DEFAULT 1,
                    first_seen TIMESTAMP,
                    last_seen TIMESTAMP,
                    FOREIGN KEY (icao24) REFERENCES spotted_aircraft(icao24)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_flight_history_icao ON flight_history(icao24)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_flight_history_timestamp ON flight_history(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ai_cache_icao ON ai_analysis_cache(icao24)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ai_cache_expires ON ai_analysis_cache(expires_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_geo_patterns_icao ON geographic_patterns(icao24)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_geo_patterns_region ON geographic_patterns(region)')
            
            conn.commit()
    
    def load_aircraft_profiles(self):
        """Load aircraft profiles from database into memory cache"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT icao24, profile_data FROM aircraft_profiles')
                    
                    for icao24, profile_data in cursor.fetchall():
                        if profile_data:
                            profile_dict = json.loads(profile_data)
                            # Convert datetime strings back to datetime objects
                            for key in ['last_seen', 'created_at', 'updated_at']:
                                if key in profile_dict and profile_dict[key]:
                                    profile_dict[key] = datetime.fromisoformat(profile_dict[key])
                            
                            self._cache[icao24] = AircraftProfile(**profile_dict)
                
                logger.info(f"Loaded {len(self._cache)} aircraft profiles from database")
            except Exception as e:
                logger.error(f"Error loading aircraft profiles: {e}")
    
    def get_aircraft_profile(self, icao24: str) -> Optional[AircraftProfile]:
        """Get aircraft profile from cache"""
        with self._lock:
            return self._cache.get(icao24)
    
    def update_aircraft_profile(self, icao24: str, flight_record: FlightRecord, ai_analysis: Optional[Dict] = None):
        """Update aircraft profile with new flight data"""
        with self._lock:
            try:
                profile = self._cache.get(icao24)
                current_time = datetime.now(timezone.utc)
                
                if profile:
                    # Update existing profile
                    profile.callsign_patterns.append(flight_record.callsign)
                    profile.callsign_patterns = list(set(profile.callsign_patterns))  # Remove duplicates
                    
                    # Update most common values
                    if flight_record.typecode != 'N/A':
                        profile.common_typecode = flight_record.typecode
                    if flight_record.country != 'Unknown':
                        profile.common_country = flight_record.country
                    
                    profile.flight_frequency += 1
                    profile.last_seen = current_time
                    profile.updated_at = current_time
                    
                    # Add AI analysis to history
                    if ai_analysis:
                        profile.ai_analysis_history.append({
                            'analysis': ai_analysis,
                            'timestamp': current_time.isoformat(),
                            'confidence': ai_analysis.get('confidence_score', 0.0)
                        })
                        # Keep only last 10 analyses
                        profile.ai_analysis_history = profile.ai_analysis_history[-10:]
                    
                    # Update confidence score based on consistency
                    profile.confidence_score = self._calculate_confidence_score(profile)
                    
                else:
                    # Create new profile
                    profile = AircraftProfile(
                        icao24=icao24,
                        callsign_patterns=[flight_record.callsign],
                        common_typecode=flight_record.typecode,
                        common_country=flight_record.country,
                        common_operator=ai_analysis.get('operator_analysis', 'N/A') if ai_analysis else 'N/A',
                        flight_frequency=1,
                        last_seen=current_time,
                        confidence_score=0.5,
                        ai_analysis_history=[{
                            'analysis': ai_analysis,
                            'timestamp': current_time.isoformat(),
                            'confidence': ai_analysis.get('confidence_score', 0.0)
                        }] if ai_analysis else [],
                        created_at=current_time,
                        updated_at=current_time
                    )
                
                # Update cache
                self._cache[icao24] = profile
                
                # Save to database
                self._save_aircraft_profile(profile)
                
                # Update geographic pattern
                self._update_geographic_pattern(icao24, flight_record.lat, flight_record.lon)
                
            except Exception as e:
                logger.error(f"Error updating aircraft profile for {icao24}: {e}")
    
    def _calculate_confidence_score(self, profile: AircraftProfile) -> float:
        """Calculate confidence score based on profile consistency"""
        score = 0.0
        
        # Base score from flight frequency
        score += min(profile.flight_frequency * 0.1, 0.5)
        
        # Consistency in callsign patterns
        if len(set(profile.callsign_patterns)) == 1:
            score += 0.2
        elif len(set(profile.callsign_patterns)) <= 3:
            score += 0.1
        
        # Consistency in typecode
        if profile.common_typecode != 'N/A':
            score += 0.2
        
        # Consistency in country
        if profile.common_country != 'Unknown':
            score += 0.1
        
        # Recent AI analysis quality
        if profile.ai_analysis_history:
            recent_analyses = [a for a in profile.ai_analysis_history 
                             if (datetime.now(timezone.utc) - datetime.fromisoformat(a['timestamp'])).days < 7]
            if recent_analyses:
                avg_confidence = sum(a['confidence'] for a in recent_analyses) / len(recent_analyses)
                score += avg_confidence * 0.2
        
        return min(score, 1.0)
    
    def _save_aircraft_profile(self, profile: AircraftProfile):
        """Save aircraft profile to database"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Convert to dict and handle datetime serialization
                profile_dict = asdict(profile)
                for key in ['last_seen', 'created_at', 'updated_at']:
                    if key in profile_dict and profile_dict[key]:
                        profile_dict[key] = profile_dict[key].isoformat()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO aircraft_profiles 
                    (icao24, profile_data, updated_at, learning_score)
                    VALUES (?, ?, ?, ?)
                ''', (
                    profile.icao24,
                    json.dumps(profile_dict),
                    profile.updated_at.isoformat(),
                    profile.confidence_score
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error saving aircraft profile: {e}")
    
    def _update_geographic_pattern(self, icao24: str, lat: float, lon: float):
        """Update geographic pattern for aircraft"""
        try:
            # Simple region detection (can be enhanced)
            region = self._get_region_from_coords(lat, lon)
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Check if pattern exists
                cursor.execute('''
                    SELECT id, frequency FROM geographic_patterns 
                    WHERE icao24 = ? AND region = ?
                ''', (icao24, region))
                
                result = cursor.fetchone()
                current_time = datetime.now(timezone.utc)
                
                if result:
                    # Update existing pattern
                    pattern_id, frequency = result
                    cursor.execute('''
                        UPDATE geographic_patterns 
                        SET frequency = frequency + 1, last_seen = ?
                        WHERE id = ?
                    ''', (current_time.isoformat(), pattern_id))
                else:
                    # Create new pattern
                    cursor.execute('''
                        INSERT INTO geographic_patterns 
                        (icao24, region, frequency, first_seen, last_seen)
                        VALUES (?, ?, 1, ?, ?)
                    ''', (icao24, region, current_time.isoformat(), current_time.isoformat()))
                
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating geographic pattern: {e}")
    
    def _get_region_from_coords(self, lat: float, lon: float) -> str:
        """Get region name from coordinates"""
        # Simple region mapping (can be enhanced with more detailed regions)
        if 24.0 <= lat <= 50.0 and -125.0 <= lon <= -66.0:
            return "North America"
        elif 35.0 <= lat <= 60.0 and -10.0 <= lon <= 40.0:
            return "Europe"
        elif 20.0 <= lat <= 55.0 and 100.0 <= lon <= 150.0:
            return "East Asia"
        elif 5.0 <= lat <= 40.0 and 60.0 <= lon <= 100.0:
            return "South Asia"
        elif 15.0 <= lat <= 40.0 and 30.0 <= lon <= 60.0:
            return "Middle East"
        else:
            return "Other"
    
    def add_spotted_aircraft(self, icao24: str, callsign: str, confidence: float = 0.0):
        """Add or update spotted aircraft"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    current_time = datetime.now(timezone.utc)
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO spotted_aircraft 
                        (icao24, callsign, last_seen, total_sightings, confidence_score)
                        VALUES (?, ?, ?, 
                            COALESCE((SELECT total_sightings FROM spotted_aircraft WHERE icao24 = ?), 0) + 1,
                            ?)
                    ''', (icao24, callsign, current_time.isoformat(), icao24, confidence))
                    conn.commit()
            except Exception as e:
                logger.error(f"Error adding spotted aircraft: {e}")
    
    def check_if_spotted(self, icao24: str) -> bool:
        """Check if aircraft was already spotted recently"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    # Check if spotted in last 24 hours
                    cursor.execute('''
                        SELECT icao24 FROM spotted_aircraft 
                        WHERE icao24 = ? AND last_seen > datetime('now', '-24 hours')
                    ''', (icao24,))
                    return cursor.fetchone() is not None
            except Exception as e:
                logger.error(f"Error checking spotted aircraft: {e}")
                return False
    
    def cache_ai_analysis(self, icao24: str, analysis: Dict, confidence: float, api_used: str, model_version: str = "2.0"):
        """Cache AI analysis result"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    current_time = datetime.now(timezone.utc)
                    expires_at = current_time + timedelta(hours=24)
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO ai_analysis_cache 
                        (icao24, analysis_data, confidence_score, api_used, model_version, expires_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        icao24,
                        json.dumps(analysis),
                        confidence,
                        api_used,
                        model_version,
                        expires_at.isoformat()
                    ))
                    conn.commit()
            except Exception as e:
                logger.error(f"Error caching AI analysis: {e}")
    
    def get_cached_analysis(self, icao24: str) -> Optional[Dict]:
        """Get cached AI analysis if still valid"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT analysis_data FROM ai_analysis_cache 
                        WHERE icao24 = ? AND expires_at > datetime('now')
                        ORDER BY created_at DESC LIMIT 1
                    ''', (icao24,))
                    result = cursor.fetchone()
                    return json.loads(result[0]) if result else None
            except Exception as e:
                logger.error(f"Error getting cached analysis: {e}")
                return None
    
    def add_flight_history(self, flight_record: FlightRecord):
        """Add flight to history"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO flight_history 
                        (icao24, callsign, lat, lon, alt, vel, heading, typecode, country, 
                         source, timestamp, ai_analysis, strategic_importance, confidence_score)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        flight_record.icao24, flight_record.callsign, flight_record.lat, 
                        flight_record.lon, flight_record.alt, flight_record.vel, 
                        flight_record.heading, flight_record.typecode, flight_record.country,
                        flight_record.source, flight_record.timestamp.isoformat(),
                        json.dumps(flight_record.ai_analysis) if flight_record.ai_analysis else None,
                        flight_record.strategic_importance, flight_record.confidence_score
                    ))
                    conn.commit()
            except Exception as e:
                logger.error(f"Error adding flight history: {e}")
    
    def get_statistics(self) -> Dict:
        """Get comprehensive system statistics"""
        with self._lock:
            try:
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
                    
                    # Get AI analyses count (24h)
                    cursor.execute('''
                        SELECT COUNT(*) FROM ai_analysis_cache 
                        WHERE created_at > datetime('now', '-24 hours')
                    ''')
                    ai_analyses_24h = cursor.fetchone()[0]
                    
                    # Get learning updates
                    cursor.execute('''
                        SELECT COUNT(*) FROM aircraft_profiles 
                        WHERE updated_at > datetime('now', '-24 hours')
                    ''')
                    learning_updates = cursor.fetchone()[0]
                    
                    # Get API usage stats
                    cursor.execute('''
                        SELECT api_name, success_count, error_count 
                        FROM api_usage 
                        ORDER BY last_used DESC
                    ''')
                    api_stats = cursor.fetchall()
                    
                    # Get geographic patterns
                    cursor.execute('''
                        SELECT region, COUNT(*) as count 
                        FROM geographic_patterns 
                        GROUP BY region 
                        ORDER BY count DESC 
                        LIMIT 10
                    ''')
                    geo_patterns = cursor.fetchall()
                    
                    return {
                        'total_aircraft': total_aircraft,
                        'today_flights': today_flights,
                        'ai_analyses_24h': ai_analyses_24h,
                        'learning_updates': learning_updates,
                        'api_stats': api_stats,
                        'geo_patterns': geo_patterns,
                        'cached_profiles': len(self._cache)
                    }
            except Exception as e:
                logger.error(f"Error getting statistics: {e}")
                return {}
    
    def get_aircraft_learning_data(self, icao24: str) -> Optional[Dict]:
        """Get learning data for aircraft to improve AI analysis"""
        profile = self.get_aircraft_profile(icao24)
        if not profile:
            return None
        
        # Get recent flight history
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT callsign, typecode, country, strategic_importance, confidence_score
                FROM flight_history 
                WHERE icao24 = ? 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''', (icao24,))
            recent_flights = cursor.fetchall()
        
        return {
            'profile': asdict(profile),
            'recent_flights': recent_flights,
            'learning_score': profile.confidence_score,
            'suggested_analysis': self._generate_analysis_suggestion(profile)
        }
    
    def _generate_analysis_suggestion(self, profile: AircraftProfile) -> Dict:
        """Generate analysis suggestion based on learned patterns"""
        suggestion = {
            'persian_role': 'نقش نامشخص',
            'aircraft_model': 'N/A',
            'operator_analysis': 'N/A',
            'location_context': 'موقعیت نامشخص',
            'strategic_importance': 5,
            'confidence_score': profile.confidence_score
        }
        
        # Use most common typecode to suggest role
        if profile.common_typecode != 'N/A':
            # Simple mapping (can be enhanced)
            if 'F' in profile.common_typecode:
                suggestion['persian_role'] = 'جنگنده'
            elif 'C' in profile.common_typecode:
                suggestion['persian_role'] = 'ترابری'
            elif 'H' in profile.common_typecode:
                suggestion['persian_role'] = 'هلیکوپتر'
            elif 'E' in profile.common_typecode:
                suggestion['persian_role'] = 'هواپیمای نظارتی'
        
        # Use most common country for operator
        if profile.common_country != 'Unknown':
            suggestion['operator_analysis'] = f"نیروی هوایی {profile.common_country}"
        
        # Use geographic patterns for location context
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT region, frequency 
                FROM geographic_patterns 
                WHERE icao24 = ? 
                ORDER BY frequency DESC 
                LIMIT 1
            ''', (profile.icao24,))
            result = cursor.fetchone()
            if result:
                region, frequency = result
                suggestion['location_context'] = f"منطقه {region}"
        
        return suggestion
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old data to maintain performance"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    
                    # Clean up old flight history
                    cursor.execute('''
                        DELETE FROM flight_history 
                        WHERE timestamp < datetime('now', '-{} days')
                    '''.format(days))
                    
                    # Clean up expired AI analysis cache
                    cursor.execute('''
                        DELETE FROM ai_analysis_cache 
                        WHERE expires_at < datetime('now')
                    ''')
                    
                    # Clean up old statistics
                    cursor.execute('''
                        DELETE FROM statistics 
                        WHERE created_at < datetime('now', '-{} days')
                    '''.format(days * 2))
                    
                    conn.commit()
                    logger.info(f"Cleaned up data older than {days} days")
            except Exception as e:
                logger.error(f"Error cleaning up old data: {e}")
    
    def backup_database(self, backup_path: str):
        """Create compressed backup of database"""
        try:
            with sqlite3.connect(self.db_file) as source:
                with gzip.open(backup_path, 'wb') as backup:
                    for line in source.iterdump():
                        backup.write((line + '\n').encode('utf-8'))
            logger.info(f"Database backed up to {backup_path}")
        except Exception as e:
            logger.error(f"Error creating database backup: {e}")
    
    def get_performance_metrics(self) -> Dict:
        """Get database performance metrics"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_file) as conn:
                    cursor = conn.cursor()
                    
                    # Get table sizes
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    
                    table_sizes = {}
                    for table_name, in tables:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name[0]}")
                        count = cursor.fetchone()[0]
                        table_sizes[table_name[0]] = count
                    
                    # Get database file size
                    db_size = os.path.getsize(self.db_file) if os.path.exists(self.db_file) else 0
                    
                    return {
                        'table_sizes': table_sizes,
                        'database_size_mb': db_size / (1024 * 1024),
                        'cache_size': len(self._cache),
                        'cache_hit_ratio': self._calculate_cache_hit_ratio()
                    }
            except Exception as e:
                logger.error(f"Error getting performance metrics: {e}")
                return {}
    
    def _calculate_cache_hit_ratio(self) -> float:
        """Calculate cache hit ratio (simplified)"""
        # This would need proper tracking in a real implementation
        return 0.85  # Placeholder value

# ========== Global Database Instance ==========
db_manager = None

def init_database(db_file: str = "military_aircraft.db"):
    """Initialize global database manager"""
    global db_manager
    db_manager = AdvancedDatabaseManager(db_file)
    logger.info("Database initialized successfully")

def get_database() -> AdvancedDatabaseManager:
    """Get global database manager instance"""
    global db_manager
    if db_manager is None:
        init_database()
    return db_manager