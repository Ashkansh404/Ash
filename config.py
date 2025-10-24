# -*- coding: utf-8 -*-
"""
تنظیمات ربات ردیاب پروازهای نظامی
Military Flight Tracker Bot Configuration
"""

# ========== Telegram Configuration ==========
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
CHANNEL_ID = "@YOUR_CHANNEL_USERNAME"  # یا ID عددی کانال
ADMIN_ID = 7717672777  # آیدی عددی ادمین برای دریافت گزارش‌ها

# ========== Gemini AI Configuration ==========
# چند کلید API برای سوییچ خودکار در صورت محدودیت
GEMINI_API_KEYS = [
    "YOUR_GEMINI_API_KEY_1_HERE",
    "YOUR_GEMINI_API_KEY_2_HERE",
    "YOUR_GEMINI_API_KEY_3_HERE",
]

# مدل Gemini مورد استفاده
GEMINI_MODEL = "gemini-2.0-flash-exp"  # یا "gemini-1.5-pro" یا "gemini-2.5-pro"

# ========== Flight Tracking Configuration ==========
POLL_INTERVAL_SECONDS = 120  # بازه زمانی بررسی پروازها (ثانیه)

# ========== Database Configuration ==========
DB_FILE = "flight_tracker.db"  # نام فایل دیتابیس
MEMORY_CLEANUP_HOURS = 24  # پاکسازی حافظه بعد از این مدت

# ========== Logging Configuration ==========
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "bot.log"

# ========== Advanced Settings ==========
# محدوده جغرافیایی آمریکا برای فیلتر کردن (پروازهای داخل آمریکا ارسال نمی‌شوند)
USA_BBOX = (24.0, 50.0, -125.0, -66.0)  # (min_lat, max_lat, min_lon, max_lon)

# تعداد تلاش مجدد برای درخواست‌های شبکه
HTTP_RETRY_COUNT = 3

# زمان انتظار برای درخواست‌های API (ثانیه)
API_TIMEOUT = 25

# تاخیر بین ارسال پیام‌ها برای جلوگیری از محدودیت تلگرام (ثانیه)
MESSAGE_DELAY = 40

# حداکثر تلاش برای Gemini قبل از fallback
MAX_GEMINI_RETRIES = 2

# تایم‌اوت برای درخواست‌های Gemini (ثانیه)
GEMINI_TIMEOUT = 15
