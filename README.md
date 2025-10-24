# Military Flight Tracker Bot v2.0
## Advanced Intelligence System with Gemini AI Integration

### 🚀 Overview
This is an advanced military flight tracker bot for Telegram that uses artificial intelligence to analyze and report military aircraft activities. The bot integrates with multiple data sources and uses Google's Gemini AI for intelligent analysis of flight data.

### ✨ Key Features

#### 🤖 AI-Powered Analysis
- **Gemini AI Integration**: Uses Google's Gemini 2.0 Flash for intelligent flight analysis
- **Multiple API Keys**: Supports up to 3 Gemini API keys for redundancy and rate limiting
- **Intelligent Fallback**: Automatically switches between API keys and falls back to cached data
- **Learning System**: Continuously learns from flight patterns to improve accuracy

#### 📊 Advanced Tracking
- **Multiple Data Sources**: Integrates with ADSB.lol, OpenSky Network, and ADSB Exchange
- **Real-time Monitoring**: Continuous monitoring with configurable intervals
- **Geographic Filtering**: Filters out USA flights and other specified regions
- **Smart Notifications**: Context-aware notifications with strategic importance scoring

#### 🧠 Learning Capabilities
- **Aircraft Profiles**: Builds detailed profiles of each aircraft over time
- **Pattern Recognition**: Learns flight patterns and geographic preferences
- **Confidence Scoring**: Provides confidence scores for all analyses
- **Historical Analysis**: Maintains comprehensive flight history

#### 📈 Analytics & Reporting
- **Real-time Statistics**: Live statistics and performance metrics
- **Hourly Reports**: Automated hourly status reports
- **Geographic Patterns**: Tracks aircraft movement patterns by region
- **API Usage Tracking**: Monitors API performance and usage

### 🛠️ Installation & Setup

#### Prerequisites
- Python 3.8 or higher
- Telegram Bot Token (from @BotFather)
- Telegram Channel ID
- Google Gemini API Key(s)

#### 1. Clone and Install
```bash
# Clone the repository
git clone <repository-url>
cd military-tracker-bot

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure the Bot
Edit the `config.py` file and update the following settings:

```python
# Telegram Configuration
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHANNEL_ID = "YOUR_CHANNEL_ID"
ADMIN_ID = 7717672777

# Gemini AI Configuration
GEMINI_API_KEYS = [
    "YOUR_GEMINI_API_KEY_1",
    "YOUR_GEMINI_API_KEY_2", 
    "YOUR_GEMINI_API_KEY_3"
]
```

#### 3. Get Required API Keys

##### Telegram Bot Token
1. Message @BotFather on Telegram
2. Use `/newbot` command
3. Follow the instructions to create your bot
4. Copy the token to `config.py`

##### Telegram Channel ID
1. Create a public channel or use existing one
2. Add your bot as administrator
3. For public channels: Use @channelname
4. For private channels: Use -100 followed by the channel ID

##### Gemini API Keys
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create API keys (up to 3 for redundancy)
3. Copy the keys to `config.py`

#### 4. Run the Bot
```bash
python military_tracker_bot.py
```

### 📁 File Structure

```
military-tracker-bot/
├── military_tracker_bot.py    # Main bot application
├── config.py                  # Configuration settings
├── database.py                # Advanced database module
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── military_aircraft.db       # SQLite database (created automatically)
```

### 🔧 Configuration Options

#### Basic Settings
- `POLL_INTERVAL_SECONDS`: Flight check interval (default: 30)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `MIN_STRATEGIC_IMPORTANCE`: Minimum importance for notifications (1-10)

#### AI Settings
- `GEMINI_MODEL`: AI model to use (gemini-2.0-flash-exp or gemini-1.5-pro)
- `AI_ANALYSIS_TIMEOUT`: Timeout for AI requests (seconds)
- `MIN_CONFIDENCE_THRESHOLD`: Minimum confidence for AI analysis (0.0-1.0)

#### Performance Settings
- `MAX_CONCURRENT_AI_REQUESTS`: Maximum concurrent AI requests
- `AI_REQUEST_DELAY`: Delay between AI requests (seconds)
- `MAX_MEMORY_USAGE_MB`: Maximum memory usage

### 🤖 Bot Commands

- `/start` - Start the bot and see available commands
- `/status` - Check bot status and statistics
- `/stats` - View detailed statistics
- `/test` - Send test message to channel
- `/help` - Show help information

### 📊 Database Schema

The bot uses SQLite with the following main tables:

- `spotted_aircraft`: Tracked aircraft information
- `ai_analysis_cache`: Cached AI analysis results
- `flight_history`: Complete flight history
- `aircraft_profiles`: Learned aircraft characteristics
- `geographic_patterns`: Aircraft movement patterns
- `statistics`: System performance metrics
- `api_usage`: API usage tracking

### 🔄 AI Analysis Process

1. **Flight Detection**: Bot detects military flights from data sources
2. **AI Analysis**: Sends flight data to Gemini AI for analysis
3. **Intelligent Processing**: AI analyzes role, model, operator, and strategic importance
4. **Learning Update**: Updates aircraft profiles with new information
5. **Notification**: Sends enhanced notification with AI insights
6. **Fallback**: Uses cached data if AI analysis fails

### 🛡️ Error Handling & Reliability

- **Multiple API Keys**: Automatic failover between Gemini API keys
- **Circuit Breaker**: Prevents cascading failures
- **Rate Limiting**: Respects API rate limits
- **Caching**: Intelligent caching reduces API calls
- **Fallback System**: Graceful degradation when AI is unavailable
- **Comprehensive Logging**: Detailed logging for troubleshooting

### 📈 Performance Features

- **Asynchronous Processing**: Non-blocking operations
- **Connection Pooling**: Efficient database connections
- **Memory Management**: Automatic cleanup and garbage collection
- **Background Tasks**: Separate threads for monitoring and notifications
- **Caching**: Multi-level caching for optimal performance

### 🔍 Monitoring & Analytics

The bot provides comprehensive monitoring through:

- **Real-time Statistics**: Live performance metrics
- **Hourly Reports**: Automated status updates
- **Database Analytics**: Detailed usage statistics
- **API Monitoring**: Track API performance and errors
- **Geographic Analysis**: Aircraft movement patterns

### 🚨 Troubleshooting

#### Common Issues

1. **Bot not responding**
   - Check if bot token is correct
   - Verify bot has admin rights in channel
   - Check internet connection

2. **No AI analysis**
   - Verify Gemini API keys are valid
   - Check API quota and limits
   - Review error logs

3. **Database errors**
   - Check file permissions
   - Ensure sufficient disk space
   - Review database logs

4. **High memory usage**
   - Adjust `MAX_MEMORY_USAGE_MB` setting
   - Enable more frequent cleanup
   - Check for memory leaks in logs

#### Log Analysis
Check the `military_tracker.log` file for detailed error information and system status.

### 🔒 Security Considerations

- **API Key Protection**: Store API keys securely
- **Access Control**: Limit bot access to trusted users
- **Data Privacy**: Be mindful of flight data sensitivity
- **Rate Limiting**: Respect API rate limits
- **Monitoring**: Monitor for unusual activity

### 🚀 Advanced Features

#### Custom Regions
Add custom geographic regions in `config.py`:
```python
FILTER_REGIONS = [
    {"name": "Custom Region", "bbox": (lat1, lat2, lon1, lon2), "enabled": True}
]
```

#### Additional Data Sources
Enable additional flight data sources:
```python
FLIGHT_SOURCES = [
    {"name": "Custom Source", "url": "https://api.example.com", "enabled": True}
]
```

#### Custom AI Prompts
Modify AI analysis prompts in the `GeminiAIAnalyzer` class for specialized analysis.

### 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

### 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

### 📞 Support

For support and questions:
- Check the troubleshooting section
- Review the logs for error details
- Open an issue on GitHub
- Contact the development team

### 🔄 Updates

The bot automatically updates its learning database and improves analysis accuracy over time. Regular updates to the codebase will include:
- New AI models and capabilities
- Enhanced data sources
- Improved analysis algorithms
- Performance optimizations

---

**Note**: This bot is designed for educational and research purposes. Please ensure compliance with all applicable laws and regulations regarding flight data collection and analysis.