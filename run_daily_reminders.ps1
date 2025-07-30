# Daily Reminders System - Email Only
# PowerShell script to run daily quiz reminders

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Daily Reminders System - Email Only" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to backend directory
Set-Location "backend"

Write-Host "Starting daily reminders system..." -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  WARNING: .env file not found" -ForegroundColor Yellow
    Write-Host "Please create .env file with your email configuration" -ForegroundColor Yellow
    Write-Host "See env_template.txt for example" -ForegroundColor Yellow
    Write-Host ""
    
    if (Test-Path "env_template.txt") {
        Write-Host "Creating .env from template..." -ForegroundColor Green
        Copy-Item "env_template.txt" ".env"
        Write-Host ""
        Write-Host "Please edit .env file with your email credentials:" -ForegroundColor Yellow
        Write-Host "  EMAIL_FROM=your-email@gmail.com" -ForegroundColor Gray
        Write-Host "  SMTP_HOST=smtp.gmail.com" -ForegroundColor Gray
        Write-Host "  SMTP_PORT=587" -ForegroundColor Gray
        Write-Host "  SMTP_USERNAME=your-email@gmail.com" -ForegroundColor Gray
        Write-Host "  SMTP_PASSWORD=your-app-password" -ForegroundColor Gray
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    } else {
        Write-Host "❌ ERROR: env_template.txt not found" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Check command line arguments
$command = $args[0]
if (-not $command) {
    $command = "test"
}

Write-Host "Running daily reminders with command: $command" -ForegroundColor Green
Write-Host ""

# Run the daily reminders
try {
    $result = python run_daily_reminders.py $command 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ SUCCESS: Daily reminders completed" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "❌ ERROR: Daily reminders failed" -ForegroundColor Red
        Write-Host "Check the logs for more details" -ForegroundColor Yellow
    }
} catch {
    Write-Host ""
    Write-Host "❌ ERROR: Failed to run daily reminders" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

Write-Host ""
Write-Host "Available commands:" -ForegroundColor Cyan
Write-Host "  test     - Run a single reminder test" -ForegroundColor Gray
Write-Host "  monitor  - Start continuous monitoring" -ForegroundColor Gray
Write-Host "  schedule - Show scheduled tasks" -ForegroundColor Gray

Read-Host "Press Enter to exit" 