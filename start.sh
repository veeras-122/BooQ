#!/bin/bash
echo "============================================"
echo "  LibraSync Setup and Run Script (Linux/Mac)"
echo "============================================"

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found. Install Python 3.9+."
    exit 1
fi

# Create venv
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "Installing dependencies..."
pip install -r requirements.txt -q

echo ""
echo "============================================"
echo " Starting LibraSync at http://127.0.0.1:5000"
echo " Default Login: admin / admin123"
echo "============================================"
echo ""

python run.py
