#!/bin/bash
set -e
# setup.sh - First time setup for Meshtastic Status Board

echo "🚀 Setting up Meshtastic Status Board..."
echo "========================================"

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Python version: $python_version"

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv || { echo "❌ Failed to create virtual environment"; exit 1; }
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate and install dependencies
echo "📥 Installing dependencies..."
source venv/bin/activate

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt || { echo "❌ Failed to install dependencies"; exit 1; }
    echo "✓ Dependencies installed"
else
    echo "❌ requirements.txt not found"
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure your Meshtastic device is powered on"
echo "2. Enable Bluetooth on your device if using BLE"
echo "3. Run the application: ./run.sh"
echo "4. Add your device addresses to the 'nodes' file"
echo ""
echo "For help, check the README.md file"
