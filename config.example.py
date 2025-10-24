# -*- coding: utf-8 -*-
"""
تنظیمات ربات ردیاب پروازهای نظامی - نمونه
این فایل یک الگو است. برای استفاده:
1. این فایل را به نام config.py کپی کنید
2. مقادیر YOUR_XXX_HERE را با اطلاعات واقعی جایگزین کنید
"""

# ========== Telegram Configuration ==========
# توکن ربات را از @BotFather دریافت کنید
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"

# آیدی کانال یا یوزرنیم کانال (مثال: "@my_channel" یا -1001234567890)
CHANNEL_ID = "@YOUR_CHANNEL_USERNAME"

# آیدی عددی شما برای دریافت گزارش‌های روزانه (از @userinfobot دریافت کنید)
ADMIN_ID = 7717672777

# ========== Gemini AI Configuration ==========
# کلیدهای API را از https://aistudio.google.com/apikey دریافت کنید
# حداقل 1 کلید الزامی است، 3 کلید توصیه می‌شود
GEMINI_API_KEYS = [
    "YOUR_GEMINI_API_KEY_1_HERE",
    "YOUR_GEMINI_API_KEY_2_HERE",  # اختیاری - برای فالبک
    "YOUR_GEMINI_API_KEY_3_HERE",  # اختیاری - برای فالبک
]

# مدل Gemini مورد استفاده
# گزینه‌ها:
#   - "gemini-2.0-flash-exp" (پیشنهادی: سریع و رایگان)
#   - "gemini-1.5-pro" (دقیق‌تر اما کندتر)
#   - "gemini-1.5-flash" (متعادل)
GEMINI_MODEL = "gemini-2.0-flash-exp"

# ========== Flight Tracking Configuration ==========
# بازه زمانی بررسی پروازها (به ثانیه)
# توصیه: 60-180 ثانیه (1-3 دقیقه)
POLL_INTERVAL_SECONDS = 120

# ========== Database Configuration ==========
# نام فایل دیتابیس (خودکار ایجاد می‌شود)
DB_FILE = "flight_tracker.db"

# پاکسازی رکوردهای قدیمی‌تر از این مدت (ساعت)
MEMORY_CLEANUP_HOURS = 24

# ========== Logging Configuration ==========
# سطح لاگ: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"

# نام فایل لاگ
LOG_FILE = "bot.log"

# ========== Advanced Settings ==========
# محدوده جغرافیایی آمریکا (پروازهای داخل آمریکا فیلتر می‌شوند)
# فرمت: (حداقل عرض، حداکثر عرض، حداقل طول، حداکثر طول)
USA_BBOX = (24.0, 50.0, -125.0, -66.0)

# تعداد تلاش مجدد برای درخواست‌های HTTP
HTTP_RETRY_COUNT = 3

# زمان انتظار برای درخواست‌های API (ثانیه)
API_TIMEOUT = 25

# تاخیر بین ارسال پیام‌ها (ثانیه) - برای جلوگیری از محدودیت تلگرام
MESSAGE_DELAY = 40

# حداکثر تلاش برای Gemini قبل از استفاده از fallback
MAX_GEMINI_RETRIES = 2

# تایم‌اوت برای درخواست‌های Gemini (ثانیه)
GEMINI_TIMEOUT = 15
