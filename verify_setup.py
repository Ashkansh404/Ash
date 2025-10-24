#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت تایید نصب و تنظیمات
Setup Verification Script

این اسکریپت قبل از اجرای ربات، تمام تنظیمات را بررسی می‌کند.
"""

import sys
import os

print("=" * 70)
print("🔍 بررسی تنظیمات ربات ردیاب پروازهای نظامی")
print("=" * 70)
print()

# ========== بررسی نسخه Python ==========
print("📌 بررسی نسخه Python...")
if sys.version_info < (3, 8):
    print("❌ نسخه Python باید 3.8 یا بالاتر باشد!")
    print(f"   نسخه فعلی: {sys.version}")
    sys.exit(1)
else:
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
print()

# ========== بررسی کتابخانه‌ها ==========
print("📌 بررسی کتابخانه‌های مورد نیاز...")
required_packages = {
    'telegram': 'python-telegram-bot',
    'requests': 'requests',
}

missing_packages = []
for module, package in required_packages.items():
    try:
        __import__(module)
        print(f"✅ {package}")
    except ImportError:
        print(f"❌ {package} نصب نشده")
        missing_packages.append(package)

if missing_packages:
    print()
    print("⚠️ لطفاً کتابخانه‌های زیر را نصب کنید:")
    print(f"   pip install {' '.join(missing_packages)}")
    print()
    sys.exit(1)
print()

# ========== بررسی فایل config.py ==========
print("📌 بررسی فایل تنظیمات...")
try:
    import config
    print("✅ فایل config.py موجود است")
except ImportError:
    print("❌ فایل config.py یافت نشد!")
    print("   لطفاً config.example.py را به config.py کپی کرده و تنظیم کنید.")
    sys.exit(1)
print()

# ========== بررسی تنظیمات Telegram ==========
print("📌 بررسی تنظیمات Telegram...")

# بررسی TOKEN
if hasattr(config, 'TOKEN'):
    if config.TOKEN and not config.TOKEN.startswith('YOUR_'):
        print(f"✅ TOKEN تنظیم شده")
    else:
        print("❌ TOKEN تنظیم نشده است!")
        print("   لطفاً توکن ربات را از @BotFather دریافت کرده و در config.py قرار دهید.")
        sys.exit(1)
else:
    print("❌ TOKEN در config.py تعریف نشده!")
    sys.exit(1)

# بررسی CHANNEL_ID
if hasattr(config, 'CHANNEL_ID'):
    if config.CHANNEL_ID and not config.CHANNEL_ID.startswith('YOUR_'):
        print(f"✅ CHANNEL_ID تنظیم شده: {config.CHANNEL_ID}")
    else:
        print("❌ CHANNEL_ID تنظیم نشده است!")
        print("   لطفاً آیدی یا یوزرنیم کانال را در config.py قرار دهید.")
        sys.exit(1)
else:
    print("❌ CHANNEL_ID در config.py تعریف نشده!")
    sys.exit(1)

# بررسی ADMIN_ID
if hasattr(config, 'ADMIN_ID'):
    if config.ADMIN_ID and config.ADMIN_ID != 7717672777:
        print(f"✅ ADMIN_ID تنظیم شده")
    else:
        print("⚠️ ADMIN_ID پیش‌فرض است. لطفاً آیدی خود را در config.py قرار دهید.")
else:
    print("⚠️ ADMIN_ID در config.py تعریف نشده!")

print()

# ========== بررسی تنظیمات Gemini ==========
print("📌 بررسی تنظیمات Gemini AI...")

if hasattr(config, 'GEMINI_API_KEYS'):
    if isinstance(config.GEMINI_API_KEYS, list) and len(config.GEMINI_API_KEYS) > 0:
        valid_keys = [k for k in config.GEMINI_API_KEYS if k and not k.startswith('YOUR_')]
        if valid_keys:
            print(f"✅ {len(valid_keys)} کلید API Gemini تنظیم شده")
            if len(valid_keys) >= 3:
                print("   ✨ عالی! استفاده از چند کلید باعث پایداری بیشتر می‌شود.")
            elif len(valid_keys) == 2:
                print("   👍 خوب! برای پایداری بیشتر، کلید سوم اضافه کنید.")
            else:
                print("   💡 توصیه: حداقل 2-3 کلید برای جلوگیری از محدودیت استفاده کنید.")
        else:
            print("❌ کلید API Gemini تنظیم نشده است!")
            print("   لطفاً از https://aistudio.google.com/apikey کلید دریافت کنید.")
            sys.exit(1)
    else:
        print("❌ GEMINI_API_KEYS باید یک لیست باشد!")
        sys.exit(1)
else:
    print("❌ GEMINI_API_KEYS در config.py تعریف نشده!")
    sys.exit(1)

# بررسی مدل
if hasattr(config, 'GEMINI_MODEL'):
    print(f"✅ مدل Gemini: {config.GEMINI_MODEL}")
else:
    print("⚠️ GEMINI_MODEL تعریف نشده، از مقدار پیش‌فرض استفاده می‌شود.")

print()

# ========== بررسی فایل database.py ==========
print("📌 بررسی ماژول database...")
try:
    import database
    print("✅ ماژول database قابل import است")
except ImportError as e:
    print(f"❌ خطا در import ماژول database: {e}")
    sys.exit(1)
print()

# ========== تست اتصال به Telegram API ==========
print("📌 تست اتصال به Telegram API...")
try:
    from telegram import Bot
    bot = Bot(config.TOKEN)
    
    # تست غیرهمزمان
    import asyncio
    async def test_bot():
        me = await bot.get_me()
        return me
    
    me = asyncio.run(test_bot())
    print(f"✅ اتصال موفق! نام ربات: @{me.username}")
except Exception as e:
    print(f"❌ خطا در اتصال به Telegram: {e}")
    print("   لطفاً TOKEN را بررسی کنید.")
    sys.exit(1)
print()

# ========== تست اتصال به ADSB.lol API ==========
print("📌 تست اتصال به ADSB.lol API...")
try:
    import requests
    response = requests.get("https://api.adsb.lol/v2/mil", timeout=10)
    if response.status_code == 200:
        data = response.json()
        flight_count = len(data.get('ac', []))
        print(f"✅ اتصال موفق! {flight_count} پرواز نظامی فعلاً در حال پرواز است.")
    else:
        print(f"⚠️ پاسخ غیرعادی: {response.status_code}")
except Exception as e:
    print(f"⚠️ خطا در اتصال به ADSB.lol: {e}")
    print("   این مشکل معمولاً موقتی است.")
print()

# ========== بررسی فضای دیسک ==========
print("📌 بررسی فضای دیسک...")
try:
    import shutil
    total, used, free = shutil.disk_usage(".")
    free_gb = free // (2**30)
    if free_gb > 1:
        print(f"✅ فضای آزاد: {free_gb} GB")
    else:
        print(f"⚠️ فضای کم! فقط {free_gb} GB آزاد است.")
except:
    print("⚠️ نتوانستیم فضای دیسک را بررسی کنیم")
print()

# ========== خلاصه نهایی ==========
print("=" * 70)
print("✅ تمام بررسی‌ها با موفقیت انجام شد!")
print("=" * 70)
print()
print("🚀 ربات آماده اجرا است. برای شروع:")
print()
print("   python bott.py")
print()
print("📖 برای راهنمای کامل، README.md را مطالعه کنید.")
print("⚡ برای راهنمای سریع، QUICKSTART.md را مطالعه کنید.")
print()
print("=" * 70)
print("موفق باشید! 🎉")
print("=" * 70)
