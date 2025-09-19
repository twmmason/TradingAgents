#!/bin/bash

# TradingAgents Environment Setup Script
# This script sets up and activates the virtual environment for TradingAgents

echo "================================================"
echo "     TradingAgents Environment Setup"
echo "================================================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🚀 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Checking dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed/updated"

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found!"
    echo ""
    echo "Creating .env file from template..."
    if [ -f ".env.template" ]; then
        cp .env.template .env
        echo "✅ Created .env file from template"
        echo ""
        echo "📝 Please edit .env and add your API keys:"
        echo "   - FINNHUB_API_KEY"
        echo "   - GOOGLE_API_KEY"
    else
        # Create a basic .env file
        cat > .env << EOF
# TradingAgents Configuration
FINNHUB_API_KEY=your_finnhub_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
EOF
        echo "✅ Created basic .env file"
        echo ""
        echo "📝 Please edit .env and add your API keys"
    fi
else
    # Check if API keys are configured
    source .env
    echo ""
    if [ "$FINNHUB_API_KEY" = "your_finnhub_api_key_here" ] || [ -z "$FINNHUB_API_KEY" ]; then
        echo "⚠️  FINNHUB_API_KEY not configured in .env"
    else
        echo "✅ FINNHUB_API_KEY configured"
    fi
    
    if [ "$GOOGLE_API_KEY" = "your_google_api_key_here" ] || [ -z "$GOOGLE_API_KEY" ]; then
        echo "⚠️  GOOGLE_API_KEY not configured in .env"
    else
        echo "✅ GOOGLE_API_KEY configured"
    fi
fi

echo ""
echo "================================================"
echo "✨ Environment setup complete!"
echo ""
echo "You are now in the TradingAgents virtual environment."
echo ""
echo "To run the CLI interface:"
echo "  python -m cli.main"
echo ""
echo "To run a basic test:"
echo "  python main.py"
echo ""
echo "To deactivate the environment:"
echo "  deactivate"
echo "================================================"