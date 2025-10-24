# 📐 مستندات فنی ربات ردیاب پروازهای نظامی

<div dir="rtl">

## 🏗️ معماری سیستم

### نمای کلی (High-Level Architecture)

```
┌─────────────────────────────────────────────────────────────────┐
│                    TELEGRAM BOT INTERFACE                        │
│              (Commands, Notifications, Reports)                  │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MAIN BOT ENGINE                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Flight     │  │   Queue      │  │   Statistics         │  │
│  │   Checker    │  │  Processor   │  │   Tracker            │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────────────────┘  │
└─────────┼──────────────────┼─────────────────────────────────────┘
          │                  │
          ▼                  ▼
┌─────────────────┐  ┌─────────────────────────────────────────┐
│   ADSB.lol API  │  │      GEMINI AI MANAGER                  │
│  (Flight Data)  │  │  ┌────────┐ ┌────────┐ ┌────────┐       │
└─────────────────┘  │  │ Key #1 │ │ Key #2 │ │ Key #3 │       │
                     │  └────────┘ └────────┘ └────────┘       │
                     │         ▼        ▼        ▼              │
                     │    Auto-Rotation & Fallback              │
                     └─────────────┬───────────────────────────┘
                                   │
                                   ▼
                     ┌─────────────────────────────┐
                     │   SQLITE DATABASE           │
                     │  ┌─────────────────────┐    │
                     │  │ AI Analysis Cache   │    │
                     │  │ Flight History      │    │
                     │  │ Spotted Aircraft    │    │
                     │  │ Statistics          │    │
                     │  └─────────────────────┘    │
                     └─────────────────────────────┘
```

---

## 🧩 اجزای اصلی سیستم

### 1. **Bot Engine** (`bot.py`)

**مسئولیت‌ها:**
- مدیریت چرخه حیات اپلیکیشن
- هماهنگی بین ماژول‌های مختلف
- مدیریت Job Queue ها
- پردازش Commands

**کلاس‌های کلیدی:**

#### `GeminiAIManager`
```python
class GeminiAIManager:
    """مدیریت چند کلید API با سوییچ خودکار"""
    
    - __init__(api_keys: List[str])
    - analyze_flight(flight: Dict) -> Optional[Dict]
    - _rotate_api_key() -> bool
    - _build_analysis_prompt(flight: Dict) -> str
    - get_statistics() -> Dict
```

**ویژگی‌های پیشرفته:**
- ✅ Auto-rotation بر اساس quota و error rate
- ✅ Intelligent prompt engineering
- ✅ JSON validation و error handling
- ✅ Performance tracking

#### توابع اصلی:

```python
async def fetch_military_flights(session) -> Dict[str, Dict]
    """دریافت داده از ADSB.lol API"""
    - Rate limiting
    - Retry logic
    - Data validation
    - Ground filter

async def process_new_flight(bot, flight, session) -> bool
    """پردازش و تحلیل پرواز جدید"""
    1. Geographic filtering (USA exclusion)
    2. Country detection from ICAO
    3. AI analysis (with cache check)
    4. Fallback to local database
    5. Strategic importance filter
    6. Notification sending
    7. Database recording

async def send_telegram_notification(bot, flight, analysis) -> bool
    """ارسال اعلان فرمت‌شده"""
    - Markdown formatting
    - Emoji mapping
    - Link generation
    - Retry handling
```

---

### 2. **Database Module** (`database.py`)

**معماری دیتابیس:**

```sql
┌──────────────────────────────────────────────────────────────┐
│                   SQLITE DATABASE SCHEMA                      │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓     │
│  ┃          spotted_aircraft                           ┃     │
│  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫     │
│  ┃ icao24 (PK) │ callsign │ first_seen │ last_seen   ┃     │
│  ┃ notification_sent │ times_spotted                  ┃     │
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛     │
│                         │                                     │
│                         ▼                                     │
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓     │
│  ┃          ai_analysis_cache ⭐ (CRITICAL)            ┃     │
│  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫     │
│  ┃ icao24 (PK) │ callsign │ type_code │ country      ┃     │
│  ┃ persian_role │ aircraft_model │ operator_analysis ┃     │
│  ┃ strategic_importance │ analysis_timestamp          ┃     │
│  ┃ times_used │ last_used │ raw_analysis (JSON)      ┃     │
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛     │
│                                                               │
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓     │
│  ┃          flight_history                             ┃     │
│  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫     │
│  ┃ id (PK) │ icao24 (FK) │ lat │ lon │ altitude │... ┃     │
│  ┃ timestamp │ strategic_importance                   ┃     │
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛     │
│                                                               │
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓     │
│  ┃          unidentified_aircraft                      ┃     │
│  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫     │
│  ┃ id (PK) │ icao24 │ callsign │ type_code │ reason  ┃     │
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛     │
│                                                               │
│  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓     │
│  ┃          statistics                                 ┃     │
│  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫     │
│  ┃ id │ date │ hour │ flights_detected │ cache_hits  ┃     │
│  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛     │
└──────────────────────────────────────────────────────────────┘
```

**کلاس اصلی:**

```python
class MilitaryFlightDatabase:
    """پایگاه داده پیشرفته با قابلیت کش AI"""
    
    # Thread-safe operations
    - _get_connection() [Context Manager]
    
    # AI Cache Management ⭐
    - get_ai_analysis(icao24, type_code) -> Optional[Dict]
    - save_ai_analysis(icao24, callsign, ..., analysis)
    
    # Flight Tracking
    - is_aircraft_spotted(icao24) -> bool
    - add_spotted_aircraft(icao24, callsign) -> bool
    - add_flight_record(flight_data) -> bool
    
    # Reporting
    - add_unidentified_aircraft(...)
    - get_unidentified_aircraft() -> List[Tuple]
    
    # Maintenance
    - cleanup_old_records(days=30) -> Dict
    - get_database_stats() -> Dict
```

**نکات فنی:**
- ✅ Context Manager برای safe connection handling
- ✅ Thread-safe با استفاده از `threading.Lock()`
- ✅ Automatic indexing برای performance
- ✅ VACUUM operation برای بهینه‌سازی فضا

---

### 3. **Configuration Module** (`config.py`)

**ساختار:**

```python
┌────────────────────────────────────────────────┐
│          CONFIGURATION LAYERS                   │
├────────────────────────────────────────────────┤
│                                                 │
│  Layer 1: CORE CONFIG                          │
│  ├─ Telegram (Token, Channel, Admin)           │
│  ├─ Gemini (API Keys, Model, Temperature)      │
│  └─ API Endpoints (ADSB.lol)                   │
│                                                 │
│  Layer 2: OPERATIONAL SETTINGS                 │
│  ├─ Intervals (Polling, Reports)               │
│  ├─ Thresholds (Importance, Cache)             │
│  └─ Filters (USA Bbox, Strategic Regions)      │
│                                                 │
│  Layer 3: STATIC DATABASES                     │
│  ├─ ICAO Country Ranges (30+ countries)        │
│  ├─ Aircraft Database (50+ models)             │
│  ├─ Military Operators (40+ operators)         │
│  ├─ Role Classification Map                    │
│  └─ Strategic Regions                          │
│                                                 │
│  Layer 4: VALIDATION                           │
│  └─ validate_config() -> bool                  │
└────────────────────────────────────────────────┘
```

**اطلاعات کلیدی:**

| بخش | تعداد رکورد | هدف |
|-----|-------------|------|
| `ICAO_COUNTRY_RANGES` | 30 کشور | تشخیص کشور از ICAO24 |
| `AIRCRAFT_DATABASE` | 50+ مدل | شناسایی نوع هواپیما |
| `MILITARY_OPERATORS` | 40+ اپراتور | شناسایی واحد نظامی |
| `STRATEGIC_REGIONS` | 9 منطقه | تحلیل موقعیت جغرافیایی |
| `ROLE_MAP` | 10 نقش | طبقه‌بندی ماموریت |

---

## 🔄 جریان داده (Data Flow)

### سناریو 1: پرواز جدید با AI موفق

```
1. ADSB.lol API Call
   └─> 150 aircraft detected
       └─> Filter grounded & invalid
           └─> 120 valid flights

2. For Each Flight:
   └─> Check spotted_aircraft table
       ├─> IF exists: SKIP
       └─> IF new:
           ├─> Add to spotted_aircraft
           └─> Add to queue

3. Queue Processor:
   └─> Get flight from queue
       ├─> Check USA airspace → FILTER if true
       ├─> Get country from ICAO
       ├─> Get region from coordinates
       └─> Request AI analysis

4. Gemini AI Manager:
   └─> Check ai_analysis_cache
       ├─> IF cached: Return cached (increment times_used)
       └─> IF not cached:
           ├─> Build intelligent prompt
           ├─> Call Gemini API (Key #1)
           ├─> Parse JSON response
           ├─> Validate fields
           └─> Save to cache

5. Strategic Filter:
   └─> Check strategic_importance >= MIN
       ├─> IF too low: SKIP notification
       └─> IF important enough: Continue

6. Send Notification:
   └─> Format message (Markdown + Emoji)
       └─> Send to Telegram channel
           ├─> Success: Record in flight_history
           └─> Failure: Log error

7. Statistics Update:
   └─> Increment counters
       └─> Update hourly stats table
```

### سناریو 2: پرواز جدید با AI Quota Exceeded

```
1-3. [Same as Scenario 1]

4. Gemini AI Manager:
   └─> Check cache → MISS
       └─> Call Gemini API (Key #1)
           └─> Response: 429 Quota Exceeded
               ├─> Mark key #1 as exhausted
               ├─> Rotate to Key #2
               └─> Retry with Key #2
                   ├─> Success: Return analysis
                   └─> Failure: Try Key #3
                       └─> All failed: Return None

5. Fallback Handler:
   └─> Call get_fallback_analysis()
       ├─> Match type_code in AIRCRAFT_DATABASE
       ├─> Match callsign in MILITARY_OPERATORS
       ├─> Estimate strategic_importance
       └─> Return basic analysis

6-7. [Continue as Scenario 1]
```

---

## 🎨 Gemini Prompt Engineering

### ساختار Prompt

```
┌───────────────────────────────────────────────┐
│          GEMINI PROMPT STRUCTURE               │
├───────────────────────────────────────────────┤
│                                                │
│  [1] PERSONA DEFINITION                        │
│      "You are a senior military aviation       │
│       intelligence analyst..."                 │
│                                                │
│  [2] MISSION STATEMENT                         │
│      "Analyze the following detection..."      │
│                                                │
│  [3] RAW DATA (Structured)                     │
│      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━         │
│      ICAO24: ae1234                            │
│      Callsign: RCH123                          │
│      Type Code: C17                            │
│      Country: United States                    │
│      Position: 35.5°N, 51.3°E                  │
│      Altitude: 8,500m                          │
│      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━         │
│                                                │
│  [4] ANALYSIS REQUIREMENTS (4 dimensions)      │
│      1. Aircraft Identification                │
│      2. Operator Analysis                      │
│      3. Strategic Location Context             │
│      4. Importance Score (1-10)                │
│                                                │
│  [5] OUTPUT FORMAT (Strict JSON)               │
│      {                                         │
│        "persian_role": "...",                  │
│        "aircraft_model": "...",                │
│        "operator_analysis": "...",             │
│        "location_context": "...",              │
│        "strategic_importance": 8               │
│      }                                         │
│                                                │
│  [6] INSTRUCTION EMPHASIS                      │
│      "You MUST respond ONLY with valid JSON"   │
└───────────────────────────────────────────────┘
```

**چرا این Prompt موثر است؟**

1. **Clear Persona**: به AI نقش مشخصی می‌دهد
2. **Structured Data**: داده‌ها به صورت سازمان‌یافته ارائه می‌شوند
3. **Explicit Requirements**: 4 بعد تحلیل مشخص شده
4. **Strict Format**: فرمت JSON الزامی
5. **Persian Context**: درخواست خروجی فارسی برای فیلدهای مشخص

**پارامترهای مدل:**

```python
GenerativeModel(
    model_name="gemini-2.0-flash-exp",  # Fast & Efficient
    generation_config={
        "temperature": 0.3,              # Low = More factual
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 1024,
    },
    safety_settings=BLOCK_NONE          # Military data not harmful
)
```

---

## 🔐 Security & Error Handling

### 1. API Key Management

```python
# Multi-layer protection
1. Environment isolation (no .env needed, config.py)
2. Validation on startup
3. Never logged or exposed
4. Automatic rotation on failure
```

### 2. Database Safety

```python
# Thread-safe operations
with self._lock:
    with self._get_connection() as conn:
        # Operations
        conn.commit()  # Auto-commit
    # Auto-rollback on error
```

### 3. Network Resilience

```python
# Retry Strategy
Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=(500, 502, 503, 504, 429)
)

# Timeout Protection
- ADSB API: 25s timeout
- Gemini API: 15s timeout
- Async timeout wrapper
```

### 4. Error Recovery

```
┌─────────────────────────────────────────┐
│        ERROR RECOVERY MATRIX             │
├─────────────────────────────────────────┤
│ Error Type      │ Recovery Strategy     │
├─────────────────────────────────────────┤
│ API 429 (Quota) │ → Rotate API Key      │
│ API Timeout     │ → Retry (3x)          │
│ Network Error   │ → Skip cycle, log     │
│ Invalid JSON    │ → Fallback analysis   │
│ Telegram Error  │ → Queue for retry     │
│ DB Lock         │ → Wait with timeout   │
│ AI Unavailable  │ → Local database      │
└─────────────────────────────────────────┘
```

---

## 📊 Performance Optimization

### 1. Caching Strategy

```
Hit Rate Target: >70%

Strategy:
- Cache all AI analyses
- Never expire high-usage entries
- Track times_used
- Cleanup only unused entries after 90 days
```

### 2. Database Indexing

```sql
-- Performance-critical indices
CREATE INDEX idx_spotted_icao ON spotted_aircraft(icao24);
CREATE INDEX idx_ai_cache_icao ON ai_analysis_cache(icao24);
CREATE INDEX idx_flight_history_timestamp ON flight_history(timestamp);
```

### 3. Async Operations

```python
# All I/O operations are async
- API calls: asyncio.to_thread()
- Database: Context managers
- Notifications: Queue-based processing
```

### 4. Memory Management

```python
# Automatic cleanup
- Old records: 30 days
- Unused AI cache: 90 days
- VACUUM on cleanup
- Rotating log files (5x 10MB)
```

---

## 🧪 Testing & Monitoring

### Built-in Health Checks

```python
# Available commands for monitoring
/status  → Quick health check
/stats   → Detailed performance metrics
/ai      → AI system status
/test    → End-to-end test
```

### Log Levels

```
DEBUG   → Detailed flow (cache hits, etc.)
INFO    → Major events (new flights, AI calls)
WARNING → Degraded performance (API rotation)
ERROR   → Failures (network, parsing)
CRITICAL→ Fatal errors (config, startup)
```

### Key Metrics

| Metric | Target | Monitoring |
|--------|--------|------------|
| AI Success Rate | >80% | `/ai` command |
| Cache Hit Rate | >70% | `/stats` command |
| Notification Delivery | >95% | Hourly reports |
| Database Size | <100MB | Auto-cleanup |

---

## 🚀 Deployment Recommendations

### Production Environment

```bash
# 1. Use virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure systemd service
[Unit]
Description=Military Flight Tracker Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/opt/military-tracker
ExecStart=/opt/military-tracker/venv/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# 4. Enable and start
systemctl enable military-tracker
systemctl start military-tracker
```

### Resource Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 256 MB | 512 MB |
| CPU | 1 core | 2 cores |
| Disk | 500 MB | 2 GB |
| Network | Stable | Low latency |

---

## 📈 Scalability

### Current Capacity

- **Flights/hour**: ~500
- **AI Analyses/hour**: ~50 (with caching)
- **Notifications/hour**: ~20-40
- **Database growth**: ~5 MB/day

### Scaling Options

1. **Horizontal**: Multiple instances with different regions
2. **Vertical**: Increase API keys (5-10 keys)
3. **Optimization**: Increase cache retention

---

## 🔄 Future Enhancements

### Planned Features (V16.0)

- [ ] Multi-source data aggregation (FlightRadar24, etc.)
- [ ] Machine learning-based anomaly detection
- [ ] Historical pattern analysis
- [ ] Interactive map visualization
- [ ] User subscription system
- [ ] Custom alert rules

---

**نسخه:** 15.0  
**تاریخ:** 2025-10-24  
**معماری:** Production-Ready

</div>
