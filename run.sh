#!/bin/bash
# run.sh - Run the Meshtastic Status Board

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠ Virtual environment not found. Run setup.sh first."
    echo "   ./setup.sh"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the main application
python3 main.py
