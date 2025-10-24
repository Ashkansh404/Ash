# 🚀 راهنمای سریع شروع کار
## Quick Start Guide - 5 دقیقه تا اجرا!

---

## گام 1️⃣: نصب Python (اگر نصب نیست)

### Windows:
```
https://www.python.org/downloads/
```
✅ حتماً گزینه "Add Python to PATH" را انتخاب کنید

### Linux/Ubuntu:
```bash
sudo apt update
sudo apt install python3 python3-pip -y
```

### macOS:
```bash
brew install python3
```

---

## گام 2️⃣: نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

یا به صورت دستی:
```bash
pip install python-telegram-bot==21.7 requests==2.32.3
```

---

## گام 3️⃣: دریافت کلیدها

### 🤖 Telegram Bot Token:
1. به [@BotFather](https://t.me/botfather) در تلگرام بروید
2. دستور `/newbot` را بزنید
3. نام ربات را وارد کنید
4. یوزرنیم ربات را وارد کنید (باید با `_bot` تمام شود)
5. توکن را کپی کنید

### 📢 Channel ID:
**روش 1 (یوزرنیم):**
```python
CHANNEL_ID = "@your_channel_username"
```

**روش 2 (آیدی عددی):**
1. ربات [@userinfobot](https://t.me/userinfobot) را به کانال اضافه کنید
2. آیدی عددی را کپی کنید (مثلاً: `-1001234567890`)
```python
CHANNEL_ID = -1001234567890
```

**⚠️ نکته مهم:** ربات را حتماً به عنوان **ادمین** به کانال اضافه کنید!

### 🧠 Gemini API Key:
1. به [Google AI Studio](https://aistudio.google.com/apikey) بروید
2. با اکانت گوگل وارد شوید
3. روی "Create API Key" کلیک کنید
4. کلید را کپی کنید

**💡 توصیه:** حداقل 2-3 کلید بسازید (محدودیت رایگان: 15 درخواست/دقیقه)

---

## گام 4️⃣: تنظیم config.py

فایل `config.py` را باز کنید و این خطوط را ویرایش کنید:

```python
# ========== Telegram Configuration ==========
TOKEN = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"  # توکن ربات
CHANNEL_ID = "@your_channel"                         # آیدی کانال
ADMIN_ID = 123456789                                 # آیدی شما (برای گزارش‌ها)

# ========== Gemini AI Configuration ==========
GEMINI_API_KEYS = [
    "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",  # کلید اول
    "AIzaSyYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY",  # کلید دوم (اختیاری)
    "AIzaSyZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ",  # کلید سوم (اختیاری)
]
```

### 🔍 چگونه آیدی عددی خودم را پیدا کنم؟
1. [@userinfobot](https://t.me/userinfobot) را استارت کنید
2. شماره شما را نشان می‌دهد (مثلاً: `Your ID: 123456789`)

---

## گام 5️⃣: اجرای ربات

```bash
python bott.py
```

اگر همه چیز درست باشد، باید این پیام‌ها را ببینید:
```
🚀 Military Aircraft Tracker Bot v15.0 (AI-Enhanced Edition)
✅ Database initialized: flight_tracker.db
🤖 Gemini Analyzer initialized with 3 API keys
✅ Bot initialized successfully
🎯 Bot is now running. Press Ctrl+C to stop.
```

---

## گام 6️⃣: تست ربات

در تلگرام به ربات خود پیام دهید:
```
/start
```

سپس برای تست کانال:
```
/test
```

اگر پیام تست در کانال ظاهر شد، همه چیز آماده است! ✅

---

## ⚙️ تنظیمات توصیه شده

### برای استفاده معمولی:
```python
POLL_INTERVAL_SECONDS = 120  # بررسی هر 2 دقیقه
MESSAGE_DELAY = 40           # تاخیر 40 ثانیه بین پیام‌ها
GEMINI_MODEL = "gemini-2.0-flash-exp"  # سریع و رایگان
```

### برای استفاده سنگین (با چند API key):
```python
POLL_INTERVAL_SECONDS = 60   # بررسی هر 1 دقیقه
MESSAGE_DELAY = 30           # تاخیر کمتر
GEMINI_MODEL = "gemini-2.0-flash-exp"
```

### برای دقت بیشتر:
```python
GEMINI_MODEL = "gemini-1.5-pro"  # دقیق‌تر اما کندتر
```

---

## 🐛 رفع مشکلات متداول

### ❌ `ModuleNotFoundError: No module named 'telegram'`
```bash
pip install python-telegram-bot==21.7
```

### ❌ `TelegramError: Unauthorized`
- توکن ربات اشتباه است
- دوباره از BotFather توکن بگیرید

### ❌ `TelegramError: Chat not found`
- ربات به کانال اضافه نشده
- یا CHANNEL_ID اشتباه است

### ❌ `TelegramError: Need administrator rights`
- ربات باید ادمین کانال باشد
- حق "Post Messages" را به ربات بدهید

### ❌ Gemini جواب نمی‌دهد
- کلید API را بررسی کنید
- به محدودیت رایگان رسیده‌اید (منتظر بمانید یا کلید دیگر اضافه کنید)

### ❌ پروازی شناسایی نمی‌شود
- صبر کنید! ممکن است چند دقیقه طول بکشد
- API ممکن است پروازی نداشته باشد
- با `/status` وضعیت را چک کنید

---

## 📊 دستورات مفید

```
/status     - وضعیت ربات
/stats      - آمار دیتابیس
/apistats   - آمار API ها
/test       - تست ارسال به کانال
```

---

## 🔄 اجرا در پس‌زمینه (Production)

### Linux (با nohup):
```bash
nohup python bott.py > bot_output.log 2>&1 &
```

### با screen:
```bash
screen -S military_bot
python bott.py
# Ctrl+A, D برای detach
```

برای بازگشت:
```bash
screen -r military_bot
```

### با systemd (توصیه می‌شود):
فایل `/etc/systemd/system/military-bot.service` بسازید:
```ini
[Unit]
Description=Military Flight Tracker Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/bot
ExecStart=/usr/bin/python3 /path/to/bot/bott.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

سپس:
```bash
sudo systemctl daemon-reload
sudo systemctl enable military-bot
sudo systemctl start military-bot
sudo systemctl status military-bot
```

---

## 📈 نظارت بر عملکرد

### مشاهده لاگ‌ها:
```bash
tail -f bot.log
```

### مشاهده دیتابیس:
```bash
sqlite3 flight_tracker.db
sqlite> SELECT COUNT(*) FROM aircraft_intelligence;
sqlite> SELECT * FROM spotted_flights LIMIT 10;
sqlite> .quit
```

---

## ✅ چک‌لیست راه‌اندازی

- [ ] Python 3.8+ نصب شده
- [ ] `requirements.txt` نصب شده
- [ ] توکن ربات در `config.py` قرار داده شده
- [ ] آیدی کانال در `config.py` قرار داده شده
- [ ] حداقل یک Gemini API Key اضافه شده
- [ ] ربات به کانال اضافه شده (به عنوان ادمین)
- [ ] `/test` با موفقیت اجرا شد
- [ ] `/status` وضعیت "فعال" را نشان می‌دهد

---

## 🎉 تبریک!

ربات شما آماده است! حالا فقط صبر کنید تا پروازهای نظامی شناسایی شوند.

**چند نکته آخر:**
- اولین بار ممکن است 5-10 دقیقه طول بکشد
- پایگاه داده هر روز قوی‌تر می‌شود
- پس از چند روز، بیشتر پروازها از کش شناسایی می‌شوند (سریع‌تر)

**سوالی دارید؟** README.md کامل را بخوانید.

---

**موفق باشید! 🚀**
