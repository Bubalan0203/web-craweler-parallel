@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo Web Crawler Setup Script
echo ==========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed. Please install Python 3.8 or higher.
    exit /b 1
)

echo [OK] Python detected
echo.

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

echo Installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
echo [OK] Dependencies installed
echo.

if not exist ".env" (
    echo Creating .env file...
    (
        echo # Supabase Configuration (Optional^)
        echo # Uncomment and fill in if you want to use Supabase for data persistence
        echo # VITE_SUPABASE_URL=your_supabase_url_here
        echo # VITE_SUPABASE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
        echo.
        echo # Application Configuration
        echo DEBUG=True
        echo HOST=0.0.0.0
        echo PORT=5000
        echo URLS_FILE=urls.txt
        echo LOG_LEVEL=INFO
    ) > .env
    echo [OK] .env file created
) else (
    echo [OK] .env file already exists
)
echo.

if not exist "urls.txt" (
    echo Error: urls.txt file not found!
    exit /b 1
)

echo Running tests...
python -m unittest discover -s . -p "test_*.py" -v
echo [OK] All tests passed
echo.

echo ==========================================
echo Setup completed successfully!
echo ==========================================
echo.
echo To start the application:
echo   1. Activate the virtual environment: venv\Scripts\activate.bat
echo   2. Run the application: python app.py
echo   3. Open your browser to: http://localhost:5000
echo.
echo Optional: Configure Supabase in .env for data persistence
echo.

pause
