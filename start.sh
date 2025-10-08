#!/bin/bash

# Language Detection Tool - Startup Script
# This script helps you get started with the language detection tool

echo "🧠 Language Detection Tool - Setup & Launch"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $python_version detected. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python $python_version detected"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "🚀 Setup complete! Choose how to run the application:"
echo ""
echo "1. CLI Version (Simple command-line interface):"
echo "   python 0169.py"
echo "   python 0169.py 'Your text here'"
echo ""
echo "2. Web Application (Full-featured web interface):"
echo "   python main.py"
echo "   Then visit: http://localhost:8000"
echo ""
echo "3. Run tests:"
echo "   python -m pytest test_main.py -v"
echo ""

# Ask user what they want to do
read -p "What would you like to do? (1/2/3): " choice

case $choice in
    1)
        echo "🚀 Starting CLI version..."
        python 0169.py
        ;;
    2)
        echo "🚀 Starting web application..."
        echo "📱 Open your browser and go to: http://localhost:8000"
        echo "⏹️  Press Ctrl+C to stop the server"
        python main.py
        ;;
    3)
        echo "🧪 Running tests..."
        python -m pytest test_main.py -v
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again and choose 1, 2, or 3."
        ;;
esac
