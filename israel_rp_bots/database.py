# -*- coding: utf-8 -*-
"""
پایگاه داده سیستم ربات‌های دیسکورد اسرائیل
Israel Discord Bots Ecosystem Database
"""

import asyncio
import asyncpg
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserRole(Enum):
    """نقش‌های کاربران"""
    TOURIST = "tourist"
    CITIZEN = "citizen"
    SOLDIER = "soldier"
    MINISTER = "minister"
    PRIME_MINISTER = "prime_minister"
    KNESSET_MEMBER = "knesset_member"
    SCIENTIST = "scientist"
    DOCTOR = "doctor"
    PILOT = "pilot"
    MOSSAD_AGENT = "mossad_agent"
    JUDGE = "judge"
    CRIMINAL = "criminal"
    GENERAL = "general"
    ADMIRAL = "admiral"
    AIR_COMMANDER = "air_commander"
    BANKER = "banker"
    ENGINEER = "engineer"
    JOURNALIST = "journalist"
    TEACHER = "teacher"
    POLICE = "police"

class JobType(Enum):
    """انواع مشاغل"""
    DOCTOR = "doctor"
    ENGINEER = "engineer"
    SCIENTIST = "scientist"
    JOURNALIST = "journalist"
    TEACHER = "teacher"
    BANKER = "banker"
    POLICE = "police"
    UNEMPLOYED = "unemployed"

class MilitaryBranch(Enum):
    """شاخه‌های نظامی"""
    AIR_FORCE = "air_force"
    GROUND_FORCE = "ground_force"
    NAVY = "navy"
    INTELLIGENCE = "intelligence"

class EquipmentType(Enum):
    """انواع تجهیزات"""
    TANKS = "tanks"
    FIGHTERS = "fighters"
    MISSILES = "missiles"
    SHIPS = "ships"
    DRONES = "drones"

@dataclass
class User:
    """کلاس کاربر"""
    user_id: int
    username: str
    display_name: str
    roles: List[str]
    balance: float
    job: Optional[str]
    skills: Dict[str, int]
    achievements: List[str]
    join_date: datetime
    last_active: datetime
    citizenship_status: str
    military_rank: Optional[str]
    education_level: str
    properties: List[str]
    political_party: Optional[str]
    criminal_record: List[str]
    health_status: str
    experience_points: int
    level: int

@dataclass
class Economy:
    """کلاس اقتصاد"""
    national_budget: float
    tax_rate: float
    inflation_rate: float
    unemployment_rate: float
    gdp: float
    foreign_reserves: float
    debt: float
    last_updated: datetime

@dataclass
class Military:
    """کلاس نظامی"""
    defcon_level: int
    active_personnel: int
    equipment_inventory: Dict[str, int]
    defense_budget: float
    research_projects: List[str]
    active_missions: List[str]
    war_status: str
    last_updated: datetime

@dataclass
class Government:
    """کلاس دولت"""
    prime_minister_id: Optional[int]
    cabinet_members: Dict[str, int]
    knesset_members: List[int]
    political_parties: Dict[str, List[int]]
    active_laws: List[str]
    pending_bills: List[str]
    election_date: Optional[datetime]
    public_satisfaction: float
    last_updated: datetime

@dataclass
class Event:
    """کلاس رویداد"""
    event_id: str
    event_type: str
    title: str
    description: str
    start_time: datetime
    end_time: Optional[datetime]
    participants: List[int]
    rewards: Dict[str, Any]
    status: str
    created_by: int

class DatabaseManager:
    """مدیر پایگاه داده"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pool = None
        self.connection = None
        
    async def connect(self):
        """اتصال به پایگاه داده"""
        try:
            self.pool = await asyncpg.create_pool(
                host=self.config["host"],
                port=self.config["port"],
                database=self.config["database"],
                user=self.config["user"],
                password=self.config["password"],
                min_size=5,
                max_size=20
            )
            logger.info("✅ اتصال به پایگاه داده با موفقیت برقرار شد")
            await self.create_tables()
        except Exception as e:
            logger.error(f"❌ خطا در اتصال به پایگاه داده: {e}")
            raise
    
    async def create_tables(self):
        """ایجاد جداول پایگاه داده"""
        async with self.pool.acquire() as conn:
            # جدول کاربران
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    display_name VARCHAR(255) NOT NULL,
                    roles JSONB DEFAULT '[]',
                    balance DECIMAL(15,2) DEFAULT 1000.00,
                    job VARCHAR(100),
                    skills JSONB DEFAULT '{}',
                    achievements JSONB DEFAULT '[]',
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    citizenship_status VARCHAR(50) DEFAULT 'tourist',
                    military_rank VARCHAR(100),
                    education_level VARCHAR(50) DEFAULT 'none',
                    properties JSONB DEFAULT '[]',
                    political_party VARCHAR(100),
                    criminal_record JSONB DEFAULT '[]',
                    health_status VARCHAR(50) DEFAULT 'healthy',
                    experience_points INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1
                )
            """)
            
            # جدول اقتصاد
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS economy (
                    id SERIAL PRIMARY KEY,
                    national_budget DECIMAL(20,2) DEFAULT 1000000.00,
                    tax_rate DECIMAL(5,4) DEFAULT 0.15,
                    inflation_rate DECIMAL(5,4) DEFAULT 0.02,
                    unemployment_rate DECIMAL(5,4) DEFAULT 0.05,
                    gdp DECIMAL(20,2) DEFAULT 5000000.00,
                    foreign_reserves DECIMAL(20,2) DEFAULT 2000000.00,
                    debt DECIMAL(20,2) DEFAULT 1000000.00,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول نظامی
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS military (
                    id SERIAL PRIMARY KEY,
                    defcon_level INTEGER DEFAULT 5,
                    active_personnel INTEGER DEFAULT 0,
                    equipment_inventory JSONB DEFAULT '{}',
                    defense_budget DECIMAL(15,2) DEFAULT 500000.00,
                    research_projects JSONB DEFAULT '[]',
                    active_missions JSONB DEFAULT '[]',
                    war_status VARCHAR(50) DEFAULT 'peace',
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول دولت
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS government (
                    id SERIAL PRIMARY KEY,
                    prime_minister_id BIGINT,
                    cabinet_members JSONB DEFAULT '{}',
                    knesset_members JSONB DEFAULT '[]',
                    political_parties JSONB DEFAULT '{}',
                    active_laws JSONB DEFAULT '[]',
                    pending_bills JSONB DEFAULT '[]',
                    election_date TIMESTAMP,
                    public_satisfaction DECIMAL(5,4) DEFAULT 0.70,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول رویدادها
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id VARCHAR(100) PRIMARY KEY,
                    event_type VARCHAR(100) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    participants JSONB DEFAULT '[]',
                    rewards JSONB DEFAULT '{}',
                    status VARCHAR(50) DEFAULT 'active',
                    created_by BIGINT NOT NULL
                )
            """)
            
            # جدول تراکنش‌ها
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id SERIAL PRIMARY KEY,
                    from_user_id BIGINT,
                    to_user_id BIGINT,
                    amount DECIMAL(15,2) NOT NULL,
                    transaction_type VARCHAR(50) NOT NULL,
                    description TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول تجهیزات
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS equipment (
                    id SERIAL PRIMARY KEY,
                    equipment_type VARCHAR(100) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    cost DECIMAL(15,2) NOT NULL,
                    production_time INTEGER NOT NULL,
                    resources JSONB DEFAULT '{}',
                    description TEXT,
                    quantity INTEGER DEFAULT 0
                )
            """)
            
            # جدول مشاغل
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id SERIAL PRIMARY KEY,
                    job_type VARCHAR(100) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    salary DECIMAL(10,2) NOT NULL,
                    requirements JSONB DEFAULT '[]',
                    channels JSONB DEFAULT '[]',
                    description TEXT
                )
            """)
            
            # جدول مهارت‌ها
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    id SERIAL PRIMARY KEY,
                    skill_name VARCHAR(100) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    max_level INTEGER DEFAULT 10,
                    cost_per_level INTEGER NOT NULL,
                    description TEXT
                )
            """)
            
            # جدول املاک
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS properties (
                    id SERIAL PRIMARY KEY,
                    property_type VARCHAR(100) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    base_price DECIMAL(15,2) NOT NULL,
                    description TEXT,
                    owner_id BIGINT,
                    purchase_date TIMESTAMP
                )
            """)
            
            # جدول احزاب سیاسی
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS political_parties (
                    id SERIAL PRIMARY KEY,
                    party_name VARCHAR(100) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    ideology VARCHAR(100) NOT NULL,
                    color INTEGER NOT NULL,
                    description TEXT,
                    leader_id BIGINT,
                    members JSONB DEFAULT '[]'
                )
            """)
            
            # جدول دانشگاه
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS university (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    discipline VARCHAR(100) NOT NULL,
                    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    graduation_date TIMESTAMP,
                    gpa DECIMAL(3,2) DEFAULT 0.00,
                    credits_earned INTEGER DEFAULT 0,
                    status VARCHAR(50) DEFAULT 'enrolled'
                )
            """)
            
            # جدول بیمارستان
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS hospital (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    doctor_id BIGINT,
                    diagnosis TEXT,
                    treatment TEXT,
                    admission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    discharge_date TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'admitted'
                )
            """)
            
            # جدول دادگاه
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS court_cases (
                    id SERIAL PRIMARY KEY,
                    case_id VARCHAR(100) UNIQUE NOT NULL,
                    plaintiff_id BIGINT NOT NULL,
                    defendant_id BIGINT NOT NULL,
                    judge_id BIGINT,
                    case_type VARCHAR(100) NOT NULL,
                    description TEXT,
                    evidence JSONB DEFAULT '[]',
                    verdict VARCHAR(50),
                    sentence TEXT,
                    filed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verdict_date TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'pending'
                )
            """)
            
            # جدول بازار سیاه
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS black_market (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    item_type VARCHAR(100) NOT NULL,
                    item_name VARCHAR(255) NOT NULL,
                    price DECIMAL(15,2) NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    seller_id BIGINT NOT NULL,
                    listing_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'active'
                )
            """)
            
            # جدول دستاوردها
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS achievements (
                    id SERIAL PRIMARY KEY,
                    achievement_id VARCHAR(100) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    reward DECIMAL(15,2) DEFAULT 0.00,
                    icon VARCHAR(10),
                    unlocked_by JSONB DEFAULT '[]'
                )
            """)
            
            # جدول بحران‌ها
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS crises (
                    id SERIAL PRIMARY KEY,
                    crisis_id VARCHAR(100) UNIQUE NOT NULL,
                    crisis_type VARCHAR(100) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    effects JSONB DEFAULT '{}',
                    duration INTEGER NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'active'
                )
            """)
            
            # جدول منابع
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS resources (
                    id SERIAL PRIMARY KEY,
                    resource_type VARCHAR(100) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    current_stock INTEGER DEFAULT 0,
                    production_rate INTEGER DEFAULT 0,
                    consumption_rate INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول آب و هوا
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS weather (
                    id SERIAL PRIMARY KEY,
                    weather_type VARCHAR(100) NOT NULL,
                    temperature DECIMAL(5,2),
                    humidity DECIMAL(5,2),
                    wind_speed DECIMAL(5,2),
                    description TEXT,
                    effects JSONB DEFAULT '{}',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # جدول لاگ‌ها
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id SERIAL PRIMARY KEY,
                    log_level VARCHAR(20) NOT NULL,
                    source VARCHAR(100) NOT NULL,
                    message TEXT NOT NULL,
                    user_id BIGINT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            logger.info("✅ جداول پایگاه داده با موفقیت ایجاد شدند")
    
    async def close(self):
        """بستن اتصال پایگاه داده"""
        if self.pool:
            await self.pool.close()
            logger.info("✅ اتصال پایگاه داده بسته شد")
    
    # متدهای کاربر
    async def create_user(self, user_id: int, username: str, display_name: str) -> User:
        """ایجاد کاربر جدید"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users (user_id, username, display_name, roles, citizenship_status)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (user_id) DO UPDATE SET
                username = $2, display_name = $3, last_active = CURRENT_TIMESTAMP
            """, user_id, username, display_name, json.dumps([UserRole.TOURIST.value]), UserRole.TOURIST.value)
            
            return await self.get_user(user_id)
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """دریافت اطلاعات کاربر"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
            if row:
                return User(
                    user_id=row['user_id'],
                    username=row['username'],
                    display_name=row['display_name'],
                    roles=json.loads(row['roles']),
                    balance=float(row['balance']),
                    job=row['job'],
                    skills=json.loads(row['skills']),
                    achievements=json.loads(row['achievements']),
                    join_date=row['join_date'],
                    last_active=row['last_active'],
                    citizenship_status=row['citizenship_status'],
                    military_rank=row['military_rank'],
                    education_level=row['education_level'],
                    properties=json.loads(row['properties']),
                    political_party=row['political_party'],
                    criminal_record=json.loads(row['criminal_record']),
                    health_status=row['health_status'],
                    experience_points=row['experience_points'],
                    level=row['level']
                )
            return None
    
    async def update_user(self, user: User) -> bool:
        """به‌روزرسانی اطلاعات کاربر"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE users SET
                username = $2, display_name = $3, roles = $4, balance = $5,
                job = $6, skills = $7, achievements = $8, last_active = $9,
                citizenship_status = $10, military_rank = $11, education_level = $12,
                properties = $13, political_party = $14, criminal_record = $15,
                health_status = $16, experience_points = $17, level = $18
                WHERE user_id = $1
            """, user.user_id, user.username, user.display_name, json.dumps(user.roles),
                user.balance, user.job, json.dumps(user.skills), json.dumps(user.achievements),
                user.last_active, user.citizenship_status, user.military_rank,
                user.education_level, json.dumps(user.properties), user.political_party,
                json.dumps(user.criminal_record), user.health_status, user.experience_points, user.level)
            return True
    
    async def add_user_role(self, user_id: int, role: str) -> bool:
        """افزودن نقش به کاربر"""
        user = await self.get_user(user_id)
        if user and role not in user.roles:
            user.roles.append(role)
            await self.update_user(user)
            return True
        return False
    
    async def remove_user_role(self, user_id: int, role: str) -> bool:
        """حذف نقش از کاربر"""
        user = await self.get_user(user_id)
        if user and role in user.roles:
            user.roles.remove(role)
            await self.update_user(user)
            return True
        return False
    
    # متدهای اقتصادی
    async def get_economy(self) -> Economy:
        """دریافت اطلاعات اقتصاد"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM economy ORDER BY id DESC LIMIT 1")
            if row:
                return Economy(
                    national_budget=float(row['national_budget']),
                    tax_rate=float(row['tax_rate']),
                    inflation_rate=float(row['inflation_rate']),
                    unemployment_rate=float(row['unemployment_rate']),
                    gdp=float(row['gdp']),
                    foreign_reserves=float(row['foreign_reserves']),
                    debt=float(row['debt']),
                    last_updated=row['last_updated']
                )
            else:
                # ایجاد رکورد اولیه
                await conn.execute("""
                    INSERT INTO economy DEFAULT VALUES
                """)
                return await self.get_economy()
    
    async def update_economy(self, economy: Economy) -> bool:
        """به‌روزرسانی اطلاعات اقتصاد"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE economy SET
                national_budget = $1, tax_rate = $2, inflation_rate = $3,
                unemployment_rate = $4, gdp = $5, foreign_reserves = $6,
                debt = $7, last_updated = CURRENT_TIMESTAMP
                WHERE id = (SELECT id FROM economy ORDER BY id DESC LIMIT 1)
            """, economy.national_budget, economy.tax_rate, economy.inflation_rate,
                economy.unemployment_rate, economy.gdp, economy.foreign_reserves, economy.debt)
            return True
    
    # متدهای نظامی
    async def get_military(self) -> Military:
        """دریافت اطلاعات نظامی"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM military ORDER BY id DESC LIMIT 1")
            if row:
                return Military(
                    defcon_level=row['defcon_level'],
                    active_personnel=row['active_personnel'],
                    equipment_inventory=json.loads(row['equipment_inventory']),
                    defense_budget=float(row['defense_budget']),
                    research_projects=json.loads(row['research_projects']),
                    active_missions=json.loads(row['active_missions']),
                    war_status=row['war_status'],
                    last_updated=row['last_updated']
                )
            else:
                # ایجاد رکورد اولیه
                await conn.execute("""
                    INSERT INTO military DEFAULT VALUES
                """)
                return await self.get_military()
    
    async def update_military(self, military: Military) -> bool:
        """به‌روزرسانی اطلاعات نظامی"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE military SET
                defcon_level = $1, active_personnel = $2, equipment_inventory = $3,
                defense_budget = $4, research_projects = $5, active_missions = $6,
                war_status = $7, last_updated = CURRENT_TIMESTAMP
                WHERE id = (SELECT id FROM military ORDER BY id DESC LIMIT 1)
            """, military.defcon_level, military.active_personnel, json.dumps(military.equipment_inventory),
                military.defense_budget, json.dumps(military.research_projects),
                json.dumps(military.active_missions), military.war_status)
            return True
    
    # متدهای دولت
    async def get_government(self) -> Government:
        """دریافت اطلاعات دولت"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM government ORDER BY id DESC LIMIT 1")
            if row:
                return Government(
                    prime_minister_id=row['prime_minister_id'],
                    cabinet_members=json.loads(row['cabinet_members']),
                    knesset_members=json.loads(row['knesset_members']),
                    political_parties=json.loads(row['political_parties']),
                    active_laws=json.loads(row['active_laws']),
                    pending_bills=json.loads(row['pending_bills']),
                    election_date=row['election_date'],
                    public_satisfaction=float(row['public_satisfaction']),
                    last_updated=row['last_updated']
                )
            else:
                # ایجاد رکورد اولیه
                await conn.execute("""
                    INSERT INTO government DEFAULT VALUES
                """)
                return await self.get_government()
    
    async def update_government(self, government: Government) -> bool:
        """به‌روزرسانی اطلاعات دولت"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE government SET
                prime_minister_id = $1, cabinet_members = $2, knesset_members = $3,
                political_parties = $4, active_laws = $5, pending_bills = $6,
                election_date = $7, public_satisfaction = $8, last_updated = CURRENT_TIMESTAMP
                WHERE id = (SELECT id FROM government ORDER BY id DESC LIMIT 1)
            """, government.prime_minister_id, json.dumps(government.cabinet_members),
                json.dumps(government.knesset_members), json.dumps(government.political_parties),
                json.dumps(government.active_laws), json.dumps(government.pending_bills),
                government.election_date, government.public_satisfaction)
            return True
    
    # متدهای تراکنش
    async def create_transaction(self, from_user_id: Optional[int], to_user_id: Optional[int],
                               amount: float, transaction_type: str, description: str = "") -> bool:
        """ایجاد تراکنش جدید"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO transactions (from_user_id, to_user_id, amount, transaction_type, description)
                VALUES ($1, $2, $3, $4, $5)
            """, from_user_id, to_user_id, amount, transaction_type, description)
            return True
    
    async def get_user_transactions(self, user_id: int, limit: int = 10) -> List[Dict]:
        """دریافت تراکنش‌های کاربر"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM transactions 
                WHERE from_user_id = $1 OR to_user_id = $1
                ORDER BY timestamp DESC LIMIT $2
            """, user_id, limit)
            return [dict(row) for row in rows]
    
    # متدهای رویداد
    async def create_event(self, event: Event) -> bool:
        """ایجاد رویداد جدید"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO events (event_id, event_type, title, description, start_time, end_time, participants, rewards, status, created_by)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """, event.event_id, event.event_type, event.title, event.description,
                event.start_time, event.end_time, json.dumps(event.participants),
                json.dumps(event.rewards), event.status, event.created_by)
            return True
    
    async def get_active_events(self) -> List[Event]:
        """دریافت رویدادهای فعال"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM events WHERE status = 'active' AND end_time > CURRENT_TIMESTAMP
            """)
            return [Event(
                event_id=row['event_id'],
                event_type=row['event_type'],
                title=row['title'],
                description=row['description'],
                start_time=row['start_time'],
                end_time=row['end_time'],
                participants=json.loads(row['participants']),
                rewards=json.loads(row['rewards']),
                status=row['status'],
                created_by=row['created_by']
            ) for row in rows]
    
    # متدهای لاگ
    async def log_event(self, level: str, source: str, message: str, user_id: Optional[int] = None):
        """ثبت لاگ"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO system_logs (log_level, source, message, user_id)
                VALUES ($1, $2, $3, $4)
            """, level, source, message, user_id)
    
    # متدهای آماری
    async def get_statistics(self) -> Dict[str, Any]:
        """دریافت آمار کلی سیستم"""
        async with self.pool.acquire() as conn:
            stats = {}
            
            # تعداد کاربران
            user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
            stats['total_users'] = user_count
            
            # تعداد شهروندان
            citizen_count = await conn.fetchval("""
                SELECT COUNT(*) FROM users WHERE citizenship_status = 'citizen'
            """)
            stats['citizens'] = citizen_count
            
            # تعداد سربازان
            soldier_count = await conn.fetchval("""
                SELECT COUNT(*) FROM users WHERE 'soldier' = ANY(roles)
            """)
            stats['soldiers'] = soldier_count
            
            # کل ثروت
            total_wealth = await conn.fetchval("SELECT SUM(balance) FROM users")
            stats['total_wealth'] = float(total_wealth) if total_wealth else 0.0
            
            # اقتصاد
            economy = await self.get_economy()
            stats['national_budget'] = economy.national_budget
            stats['gdp'] = economy.gdp
            
            # نظامی
            military = await self.get_military()
            stats['defcon_level'] = military.defcon_level
            stats['active_personnel'] = military.active_personnel
            
            # دولت
            government = await self.get_government()
            stats['public_satisfaction'] = government.public_satisfaction
            
            return stats

# نمونه استفاده
async def main():
    """تابع اصلی برای تست"""
    config = {
        "host": "localhost",
        "port": 5432,
        "database": "israel_rp_db",
        "user": "israel_rp_user",
        "password": "your_secure_password_here"
    }
    
    db = DatabaseManager(config)
    await db.connect()
    
    # تست ایجاد کاربر
    user = await db.create_user(123456789, "test_user", "کاربر تست")
    print(f"کاربر ایجاد شد: {user.display_name}")
    
    # تست آمار
    stats = await db.get_statistics()
    print(f"آمار سیستم: {stats}")
    
    await db.close()

if __name__ == "__main__":
    asyncio.run(main())