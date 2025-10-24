#!/bin/bash
# Military Flight Tracker Bot - Installation Script
# Version: 15.0

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Military Flight Tracker Bot - Installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Python version
echo "📌 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Found Python $PYTHON_VERSION"

# Check if Python version is 3.8+
REQUIRED_VERSION="3.8"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION or higher is required!"
    exit 1
fi

echo ""
echo "📦 Installing dependencies..."
pip3 install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🔍 Validating configuration..."
python3 config.py

if [ $? -eq 0 ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Installation completed successfully!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📝 Next steps:"
    echo ""
    echo "1. Edit config.py and add your credentials:"
    echo "   - TELEGRAM_BOT_TOKEN"
    echo "   - TELEGRAM_CHANNEL_ID"
    echo "   - ADMIN_USER_ID"
    echo "   - GEMINI_API_KEYS"
    echo ""
    echo "2. Run the bot:"
    echo "   python3 bot.py"
    echo ""
    echo "3. Test the bot:"
    echo "   - Send /start to your bot"
    echo "   - Send /status to check status"
    echo "   - Send /test to send test message to channel"
    echo ""
    echo "📖 For more information, see README.md or QUICK_START.md"
    echo ""
else
    echo ""
    echo "⚠️  Configuration needs to be updated!"
    echo ""
    echo "Please edit config.py and add your credentials:"
    echo "  - TELEGRAM_BOT_TOKEN"
    echo "  - TELEGRAM_CHANNEL_ID"
    echo "  - GEMINI_API_KEYS"
    echo ""
    echo "After updating config.py, run:"
    echo "  python3 bot.py"
    echo ""
fi
