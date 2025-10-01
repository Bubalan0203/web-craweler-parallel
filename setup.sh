#!/bin/bash

set -e

echo "=========================================="
echo "Web Crawler Setup Script"
echo "=========================================="
echo ""

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python 3.8 or higher is required. You have Python $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python 3 detected: $(python3 --version)"
echo ""

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Supabase Configuration (Optional)
# Uncomment and fill in if you want to use Supabase for data persistence
# VITE_SUPABASE_URL=your_supabase_url_here
# VITE_SUPABASE_SUPABASE_ANON_KEY=your_supabase_anon_key_here

# Application Configuration
DEBUG=True
HOST=0.0.0.0
PORT=5000
URLS_FILE=urls.txt
LOG_LEVEL=INFO
EOF
    echo "✓ .env file created"
else
    echo "✓ .env file already exists"
fi
echo ""

if [ ! -f "urls.txt" ]; then
    echo "Error: urls.txt file not found!"
    exit 1
fi

echo "Running tests..."
python -m unittest discover -s . -p "test_*.py" -v
echo "✓ All tests passed"
echo ""

echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "To start the application:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Run the application: python app.py"
echo "  3. Open your browser to: http://localhost:5000"
echo ""
echo "Optional: Configure Supabase in .env for data persistence"
echo ""
