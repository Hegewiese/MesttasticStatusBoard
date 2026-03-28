#!/bin/bash
# setup.sh - First time setup

echo "Setting up MeshtasticStatusBoard..."

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate and install dependencies
source venv/bin/activate
pip install -r requirements.txt

echo "✓ Setup complete! Run with: ./run.sh"