# -*- coding: utf-8 -*-
"""
پیکربندی اصلی سیستم ربات‌های دیسکورد اسرائیل
Israel Discord Bots Ecosystem Configuration
"""

import os
from typing import Dict, List, Any

# توکن‌های ربات‌های دیسکورد
DISCORD_TOKENS = {
    "star_of_david": "YOUR_STAR_OF_DAVID_BOT_TOKEN_HERE",
    "iron_dome": "YOUR_IRON_DOME_BOT_TOKEN_HERE", 
    "davids_sling": "YOUR_DAVIDS_SLING_BOT_TOKEN_HERE",
    "arrow_3": "YOUR_ARROW_3_BOT_TOKEN_HERE",
    "arrow_4": "YOUR_ARROW_4_BOT_TOKEN_HERE",
    "thaad": "YOUR_THAAD_BOT_TOKEN_HERE",
    "general_staff": "YOUR_GENERAL_STAFF_BOT_TOKEN_HERE",
    "air_force": "YOUR_AIR_FORCE_BOT_TOKEN_HERE",
    "ground_force": "YOUR_GROUND_FORCE_BOT_TOKEN_HERE",
    "navy": "YOUR_NAVY_BOT_TOKEN_HERE",
    "mossad": "YOUR_MOSSAD_BOT_TOKEN_HERE",
    "unit_8200": "YOUR_UNIT_8200_BOT_TOKEN_HERE",
    "bank_of_israel": "YOUR_BANK_OF_ISRAEL_BOT_TOKEN_HERE",
    "military_industries": "YOUR_MILITARY_INDUSTRIES_BOT_TOKEN_HERE",
    "israel_radio": "YOUR_ISRAEL_RADIO_BOT_TOKEN_HERE",
    "national_news": "YOUR_NATIONAL_NEWS_BOT_TOKEN_HERE"
}

# کلید API گوگل جیمینی
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"

# تنظیمات پایگاه داده
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "israel_rp_db",
    "user": "israel_rp_user",
    "password": "your_secure_password_here"
}

# تنظیمات سرور
SERVER_CONFIG = {
    "guild_id": 123456789012345678,  # شناسه سرور دیسکورد شما
    "owner_id": 123456789012345678,  # شناسه مالک سرور
    "language": "fa",  # زبان فارسی
    "timezone": "Asia/Jerusalem"
}

# نقش‌های سیستم
SYSTEM_ROLES = {
    "tourist": "گردشگر",
    "citizen": "شهروند",
    "soldier": "سرباز",
    "minister": "وزیر",
    "prime_minister": "نخست‌وزیر",
    "knesset_member": "عضو کنست",
    "scientist": "دانشمند",
    "doctor": "پزشک",
    "pilot": "خلبان",
    "mossad_agent": "عامل موساد",
    "judge": "قاضی",
    "criminal": "مجرم",
    "general": "ژنرال",
    "admiral": "دریاسالار",
    "air_commander": "فرمانده هوایی",
    "banker": "بانکدار",
    "engineer": "مهندس",
    "journalist": "روزنامه‌نگار",
    "teacher": "معلم",
    "police": "پلیس"
}

# دسته‌بندی‌های کانال
CHANNEL_CATEGORIES = {
    "government": "دولت و حکومت",
    "military": "نظامی",
    "economy": "اقتصاد",
    "intelligence": "اطلاعات",
    "civilian": "شهروندی",
    "education": "آموزش",
    "entertainment": "سرگرمی",
    "immigration": "مهاجرت",
    "court": "دادگاه",
    "university": "دانشگاه",
    "hospital": "بیمارستان",
    "bank": "بانک",
    "factory": "کارخانه",
    "radio": "رادیو",
    "news": "اخبار"
}

# کانال‌های متنی
TEXT_CHANNELS = {
    "general": "عمومی",
    "announcements": "اعلانات",
    "national_news": "اخبار ملی",
    "immigration_office": "دفتر مهاجرت",
    "knesset": "کنست",
    "cabinet": "کابینه",
    "diplomacy": "دیپلماسی",
    "war_room": "اتاق جنگ",
    "military_command": "فرماندهی نظامی",
    "air_force_hq": "ستاد نیروی هوایی",
    "ground_force_hq": "ستاد نیروی زمینی",
    "navy_hq": "ستاد نیروی دریایی",
    "mossad_hq": "ستاد موساد",
    "unit_8200_hq": "ستاد واحد ۸۲۰۰",
    "bank_operations": "عملیات بانکی",
    "factory_floor": "کف کارخانه",
    "labor_office": "دفتر کار",
    "court_room": "اتاق دادگاه",
    "university_main": "دانشگاه اصلی",
    "hospital_main": "بیمارستان اصلی",
    "radio_studio": "استودیو رادیو",
    "black_market": "بازار سیاه",
    "hall_of_fame": "تالار افتخارات"
}

# کانال‌های صوتی
VOICE_CHANNELS = {
    "general_voice": "عمومی صوتی",
    "government_voice": "دولت صوتی",
    "military_voice": "نظامی صوتی",
    "bank_voice": "بانک صوتی",
    "factory_voice": "کارخانه صوتی",
    "university_voice": "دانشگاه صوتی",
    "hospital_voice": "بیمارستان صوتی",
    "radio_broadcast": "پخش رادیو"
}

# تنظیمات اقتصادی
ECONOMY_CONFIG = {
    "currency_name": "شکل",
    "currency_symbol": "₪",
    "starting_balance": 1000,
    "daily_salary": 100,
    "tax_rate": 0.15,
    "inflation_rate": 0.02
}

# تنظیمات نظامی
MILITARY_CONFIG = {
    "defcon_levels": {
        5: "آرامش",
        4: "هشدار کم",
        3: "هشدار بالا", 
        2: "آماده‌باش",
        1: "جنگ"
    },
    "equipment_types": {
        "tanks": "تانک",
        "fighters": "جنگنده",
        "missiles": "موشک",
        "ships": "کشتی",
        "drones": "پهپاد"
    }
}

# تنظیمات رویدادها
EVENT_CONFIG = {
    "random_event_interval": 3600,  # ثانیه
    "election_interval": 604800,    # ثانیه (یک هفته)
    "day_night_cycle": 1800,        # ثانیه (۳۰ دقیقه)
    "weather_change_interval": 900  # ثانیه (۱۵ دقیقه)
}

# تنظیمات رنگ‌ها برای امبدها
EMBED_COLORS = {
    "success": 0x00FF00,      # سبز
    "error": 0xFF0000,        # قرمز
    "warning": 0xFFFF00,      # زرد
    "info": 0x0099FF,         # آبی
    "government": 0x0066CC,   # آبی تیره
    "military": 0x8B0000,     # قرمز تیره
    "economy": 0xFFD700,      # طلایی
    "intelligence": 0x800080, # بنفش
    "civilian": 0x32CD32,     # سبز روشن
    "criminal": 0x2F2F2F      # خاکستری تیره
}

# تنظیمات ایموجی‌ها
EMOJIS = {
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "money": "💰",
    "military": "⚔️",
    "government": "🏛️",
    "intelligence": "🕵️",
    "economy": "🏭",
    "education": "🎓",
    "health": "🏥",
    "radio": "📻",
    "news": "📰",
    "court": "⚖️",
    "university": "🎓",
    "hospital": "🏥",
    "bank": "🏦",
    "factory": "🏭",
    "star_of_david": "✡️",
    "israel_flag": "🇮🇱"
}

# تنظیمات پیام‌های خوشامدگویی
WELCOME_MESSAGES = [
    "به سرزمین مقدس اسرائیل خوش آمدید! ✡️🇮🇱",
    "شما وارد سرزمین موعود شده‌اید! خوش آمدید! 🏛️",
    "به خانه جدید خود در اسرائیل خوش آمدید! 🕊️",
    "امیدواریم در این سرزمین مقدس خوش بگذرانید! ✨"
]

# تنظیمات پیام‌های خداحافظی
GOODBYE_MESSAGES = [
    "امیدواریم دوباره به سرزمین مقدس بازگردید! 👋",
    "خداحافظ! همیشه در قلب ما خواهید بود! 💙",
    "امیدواریم تجربه خوبی در اسرائیل داشته باشید! ✨",
    "به امید دیدار دوباره در سرزمین موعود! 🕊️"
]

# تنظیمات رویدادهای ملی
NATIONAL_EVENTS = {
    "independence_day": {
        "name": "روز استقلال",
        "date": "05-14",
        "description": "جشن استقلال اسرائیل",
        "bonus": 1.5
    },
    "memorial_day": {
        "name": "روز یادبود",
        "date": "05-13", 
        "description": "یادبود شهدای اسرائیل",
        "bonus": 0.8
    },
    "hanukkah": {
        "name": "حانوکا",
        "date": "12-25",
        "description": "جشن روشنایی",
        "bonus": 1.3
    },
    "passover": {
        "name": "پسح",
        "date": "04-15",
        "description": "جشن آزادی",
        "bonus": 1.2
    }
}

# تنظیمات مشاغل
JOBS = {
    "doctor": {
        "name": "پزشک",
        "salary": 200,
        "requirements": ["university_degree"],
        "channels": ["hospital_main"],
        "description": "درمان بیماران و ارائه خدمات پزشکی"
    },
    "engineer": {
        "name": "مهندس",
        "salary": 180,
        "requirements": ["university_degree"],
        "channels": ["factory_floor"],
        "description": "طراحی و ساخت پروژه‌های مهندسی"
    },
    "scientist": {
        "name": "دانشمند",
        "salary": 250,
        "requirements": ["university_degree", "research_experience"],
        "channels": ["university_main"],
        "description": "انجام تحقیقات علمی و پیشرفت تکنولوژی"
    },
    "journalist": {
        "name": "روزنامه‌نگار",
        "salary": 120,
        "requirements": [],
        "channels": ["national_news"],
        "description": "گزارش اخبار و رویدادهای مهم"
    },
    "teacher": {
        "name": "معلم",
        "salary": 150,
        "requirements": ["university_degree"],
        "channels": ["university_main"],
        "description": "آموزش دانشجویان و انتقال دانش"
    },
    "banker": {
        "name": "بانکدار",
        "salary": 160,
        "requirements": [],
        "channels": ["bank_operations"],
        "description": "مدیریت حساب‌ها و خدمات بانکی"
    },
    "police": {
        "name": "پلیس",
        "salary": 140,
        "requirements": [],
        "channels": ["general"],
        "description": "حفظ نظم و امنیت جامعه"
    }
}

# تنظیمات مهارت‌ها
SKILLS = {
    "leadership": {
        "name": "رهبری",
        "max_level": 10,
        "cost_per_level": 100,
        "description": "توانایی رهبری و مدیریت تیم‌ها"
    },
    "negotiation": {
        "name": "مذاکره",
        "max_level": 10,
        "cost_per_level": 80,
        "description": "توانایی مذاکره و حل اختلافات"
    },
    "technical": {
        "name": "فنی",
        "max_level": 10,
        "cost_per_level": 120,
        "description": "مهارت‌های فنی و تکنیکی"
    },
    "combat": {
        "name": "نبرد",
        "max_level": 10,
        "cost_per_level": 150,
        "description": "مهارت‌های نظامی و نبرد"
    },
    "intelligence": {
        "name": "اطلاعات",
        "max_level": 10,
        "cost_per_level": 200,
        "description": "مهارت‌های اطلاعاتی و جاسوسی"
    }
}

# تنظیمات تجهیزات نظامی
MILITARY_EQUIPMENT = {
    "iron_dome_missile": {
        "name": "موشک گنبد آهنین",
        "cost": 50000,
        "production_time": 3600,
        "resources": {"steel": 10, "electronics": 5},
        "description": "سیستم دفاع موشکی پیشرفته"
    },
    "merkava_tank": {
        "name": "تانک مرکاوا",
        "cost": 200000,
        "production_time": 7200,
        "resources": {"steel": 50, "electronics": 20, "armor": 30},
        "description": "تانک اصلی ارتش اسرائیل"
    },
    "f35_fighter": {
        "name": "جنگنده اف-۳۵",
        "cost": 500000,
        "production_time": 14400,
        "resources": {"steel": 30, "electronics": 40, "avionics": 25},
        "description": "جنگنده نسل پنجم پیشرفته"
    },
    "saar_corvette": {
        "name": "کشتی سار",
        "cost": 300000,
        "production_time": 10800,
        "resources": {"steel": 40, "electronics": 25, "naval_tech": 20},
        "description": "کشتی جنگی پیشرفته"
    }
}

# تنظیمات منابع
RESOURCES = {
    "steel": "فولاد",
    "electronics": "الکترونیک",
    "armor": "زره",
    "avionics": "آویونیک",
    "naval_tech": "تکنولوژی دریایی",
    "water": "آب",
    "energy": "انرژی",
    "food": "مواد غذایی",
    "medicine": "دارو"
}

# تنظیمات دانشگاه
UNIVERSITY_DISCIPLINES = {
    "medicine": {
        "name": "پزشکی",
        "duration": 8,  # ترم
        "cost_per_semester": 5000,
        "description": "آموزش پزشکی و علوم سلامت"
    },
    "engineering": {
        "name": "مهندسی",
        "duration": 8,
        "cost_per_semester": 4000,
        "description": "آموزش مهندسی و تکنولوژی"
    },
    "science": {
        "name": "علوم",
        "duration": 8,
        "cost_per_semester": 3500,
        "description": "آموزش علوم پایه و تحقیقات"
    },
    "economics": {
        "name": "اقتصاد",
        "duration": 8,
        "cost_per_semester": 3000,
        "description": "آموزش اقتصاد و مدیریت"
    },
    "law": {
        "name": "حقوق",
        "duration": 8,
        "cost_per_semester": 3500,
        "description": "آموزش حقوق و قوانین"
    }
}

# تنظیمات املاک
REAL_ESTATE = {
    "tel_aviv": {
        "name": "تل آویو",
        "base_price": 100000,
        "description": "شهر مدرن و تجاری اسرائیل"
    },
    "jerusalem": {
        "name": "اورشلیم",
        "base_price": 150000,
        "description": "شهر مقدس و پایتخت اسرائیل"
    },
    "haifa": {
        "name": "حیفا",
        "base_price": 80000,
        "description": "شهر بندری و صنعتی"
    },
    "beer_sheva": {
        "name": "بئر السبع",
        "base_price": 60000,
        "description": "شهر جنوبی و دانشگاهی"
    }
}

# تنظیمات احزاب سیاسی
POLITICAL_PARTIES = {
    "likud": {
        "name": "لیکود",
        "ideology": "محافظه‌کار",
        "color": 0x0000FF,
        "description": "حزب محافظه‌کار و ملی‌گرا"
    },
    "labor": {
        "name": "کار",
        "ideology": "سوسیال دموکرات",
        "color": 0xFF0000,
        "description": "حزب کارگر و سوسیال دموکرات"
    },
    "yesh_atid": {
        "name": "یش عتید",
        "ideology": "لیبرال",
        "color": 0x00FF00,
        "description": "حزب لیبرال و اصلاح‌طلب"
    },
    "shas": {
        "name": "شاس",
        "ideology": "مذهبی",
        "color": 0x000000,
        "description": "حزب مذهبی و سنتی"
    }
}

# تنظیمات بحران‌ها
CRISIS_TYPES = {
    "natural_disaster": {
        "name": "بلایای طبیعی",
        "effects": {"economy": -0.3, "satisfaction": -0.4},
        "duration": 3600,
        "description": "زمین‌لرزه، سیل یا طوفان"
    },
    "political_scandal": {
        "name": "رسوایی سیاسی",
        "effects": {"satisfaction": -0.6, "government_approval": -0.5},
        "duration": 7200,
        "description": "فساد مالی یا اخلاقی در دولت"
    },
    "economic_crisis": {
        "name": "بحران اقتصادی",
        "effects": {"economy": -0.5, "satisfaction": -0.3},
        "duration": 10800,
        "description": "رکود اقتصادی یا تورم بالا"
    },
    "security_threat": {
        "name": "تهدید امنیتی",
        "effects": {"satisfaction": -0.4, "defense_budget": 0.3},
        "duration": 5400,
        "description": "تهدیدات امنیتی یا تروریستی"
    }
}

# تنظیمات دستاوردها
ACHIEVEMENTS = {
    "first_prime_minister": {
        "name": "نخستین نخست‌وزیر",
        "description": "اولین کسی که به مقام نخست‌وزیری رسید",
        "reward": 10000,
        "icon": "👑"
    },
    "first_billionaire": {
        "name": "نخستین میلیاردر",
        "description": "اولین کسی که به ثروت یک میلیارد شکل رسید",
        "reward": 50000,
        "icon": "💰"
    },
    "war_hero": {
        "name": "قهرمان جنگ",
        "description": "کسی که در جنگ‌ها نقش مهمی ایفا کرد",
        "reward": 15000,
        "icon": "⚔️"
    },
    "scientific_breakthrough": {
        "name": "پیشرفت علمی",
        "description": "کشف یا اختراع مهم علمی",
        "reward": 20000,
        "icon": "🔬"
    },
    "diplomatic_master": {
        "name": "استاد دیپلماسی",
        "description": "موفقیت در روابط دیپلماتیک",
        "reward": 12000,
        "icon": "🤝"
    }
}

# تنظیمات موسیقی رادیو
RADIO_PLAYLIST = [
    "https://www.youtube.com/watch?v=example1",
    "https://www.youtube.com/watch?v=example2",
    "https://www.youtube.com/watch?v=example3"
]

# تنظیمات لاگ
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "israel_rp_bots.log"
}

# تنظیمات امنیتی
SECURITY_CONFIG = {
    "max_messages_per_minute": 10,
    "max_mentions_per_message": 5,
    "spam_threshold": 5,
    "raid_protection": True,
    "suspicious_account_age": 86400  # 24 ساعت
}

print("✅ فایل پیکربندی با موفقیت بارگذاری شد!")
print("📝 لطفاً توکن‌های ربات‌ها و کلید API جیمینی را در این فایل تنظیم کنید.")