@echo off
echo ============================================
echo   LibraSync Setup and Run Script (Windows)
echo ============================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment if not exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate and install
echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo ============================================
echo  Starting LibraSync at http://127.0.0.1:5000
echo  Default Login: admin / admin123
echo ============================================
echo.

python run.py
pause
