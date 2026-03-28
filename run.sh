#!/bin/bash
# run.sh - Run the project

cd "$(dirname "$0")"
source venv/bin/activate
python3 connectAndSendNews.py
