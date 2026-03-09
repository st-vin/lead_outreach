#!/bin/bash

echo "🚀 Lead Outreach Tool v2.0 - Setup & Start"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Initializing database..."
python3 -c "from application.database import init_db; init_db(); print('✅ Database initialized')"

echo ""
echo "=========================================="
echo "✅ Setup complete! Starting application..."
echo "=========================================="
echo ""
echo "Access the app at: http://localhost:5000"
echo ""

python3 main.py
