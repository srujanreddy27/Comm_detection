@echo off
REM Setup script for Social Network Analysis Project

echo =========================================
echo Social Network Analysis - Setup
echo =========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
python --version
echo.

echo [2/4] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    echo Virtual environment created!
)
echo.

echo [3/4] Activating virtual environment...
call venv\Scripts\activate
echo.

echo [4/4] Installing dependencies...
pip install -r requirements.txt
echo.

echo =========================================
echo Setup Complete!
echo =========================================
echo.
echo To run the analysis:
echo   1. Activate virtual environment: venv\Scripts\activate
echo   2. Run the main script: python main.py
echo.
pause
