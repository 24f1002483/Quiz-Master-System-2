@echo off
echo ========================================
echo Daily Reminders System - Email Only
echo ========================================
echo.

cd backend

echo Starting daily reminders system...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found
    echo Please create .env file with your email configuration
    echo See env_template.txt for example
    echo.
    echo Creating .env from template...
    copy env_template.txt .env
    echo.
    echo Please edit .env file with your email credentials
    pause
    exit /b 1
)

REM Run the daily reminders
echo Running daily reminders...
python run_daily_reminders.py %*

if errorlevel 1 (
    echo.
    echo ERROR: Daily reminders failed
    echo Check the logs for more details
    pause
    exit /b 1
) else (
    echo.
    echo SUCCESS: Daily reminders completed
)

pause 