# Quiz Master 2 - Complete Project Runner (PowerShell)
# This script starts all components of the Quiz Master application

param(
    [Parameter(Position=0)]
    [string]$Command = "start"
)

# Project configuration
# $PROJECT_NAME = "quiz-master-2"
$BACKEND_PORT = 5000
$FRONTEND_PORT = 8080
$REDIS_PORT = 6379
$FLOWER_PORT = 5555

# Colors for output
$RED = "Red"
$GREEN = "Green"
$YELLOW = "Yellow"
$BLUE = "Blue"
$CYAN = "Cyan"

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $BLUE
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $GREEN
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $YELLOW
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $RED
}

function Write-Header {
    Write-Host "================================" -ForegroundColor $CYAN
    Write-Host "  Quiz Master 2 - Project Runner" -ForegroundColor $CYAN
    Write-Host "================================" -ForegroundColor $CYAN
    Write-Host ""
}

# Function to check if command exists
function Test-Command {
    param([string]$CommandName)
    $null = Get-Command $CommandName -ErrorAction SilentlyContinue
    return $?
}

# Function to check if port is in use
function Test-Port {
    param([int]$Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return $null -ne $connection
}

# Function to wait for service to be ready
function Wait-ForService {
    param(
        [string]$TargetHost = "localhost",
        [int]$Port,
        [string]$ServiceName,
        [int]$MaxAttempts = 30
    )
    
    Write-Status "Waiting for $ServiceName to be ready on $TargetHost`:$Port..."
    
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        if (Test-Port $Port) {
            Write-Success "$ServiceName is ready!"
            return $true
        }
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 2
    }
    
    Write-Error "$ServiceName failed to start within expected time"
    return $false
}

# Function to check prerequisites
function Test-Prerequisites {
    Write-Status "Checking prerequisites..."
    
    if (-not (Test-Command "docker")) {
        Write-Error "Docker is not installed. Please install Docker Desktop first."
        exit 1
    }
    
    if (-not (Test-Command "docker-compose")) {
        Write-Error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    }
    
    try {
        docker info | Out-Null
    }
    catch {
        Write-Error "Docker daemon is not running. Please start Docker Desktop first."
        exit 1
    }
    
    if (Test-Port $BACKEND_PORT) {
        Write-Warning "Port $BACKEND_PORT is already in use. The Flask app might already be running."
    }
    if (Test-Port $REDIS_PORT) {
        Write-Warning "Port $REDIS_PORT is already in use. Redis might already be running."
    }
    
    Write-Success "Prerequisites check completed"
}

function Start-Mailhog {
    Write-Status "Starting MailHog (email testing)..."
    docker-compose up -d mailhog | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to start MailHog"
        return
    }
    Write-Success "MailHog started successfully"
}

# Function to create environment file if it doesn't exist
function Initialize-Environment {
    Write-Status "Setting up environment configuration..."
    
    if (-not (Test-Path "docker.env")) {
        if (Test-Path "env.example") {
            Write-Status "Creating docker.env from env.example..."
            Copy-Item "env.example" "docker.env"
            Write-Warning "Please edit docker.env with your actual configuration values"
        }
        else {
            Write-Error "env.example file not found. Creating basic docker.env..."
            $envContent = @"
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here-change-this-in-production
DATABASE_URL=sqlite:///quiz.db

# Session Configuration
SESSION_TIMEOUT_MINUTES=30

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Email Configuration (for notifications)
EMAIL_FROM=noreply@quizmaster.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
"@
            $envContent | Out-File -FilePath "docker.env" -Encoding UTF8
            Write-Warning "Created basic docker.env. Please edit it with your actual values."
        }
    }
    else {
        Write-Success "docker.env already exists"
    }
}

function Start-Frontend {
    Write-Status "Starting Frontend (Vue/React app)..."
    docker-compose up -d frontend | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to start Frontend"
        exit 1
    }
    Write-Success "Frontend started successfully"
    Wait-ForService -Port $FRONTEND_PORT -ServiceName "Frontend"
}

# Function to build Docker images
function Invoke-BuildImages {
    Write-Status "Building Docker images..."
    
    docker-compose build | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to build Docker images"
        exit 1
    }
    
    Write-Success "Docker images built successfully"
}

# Function to start Redis
function Start-Redis {
    Write-Status "Starting Redis..."
    
    docker-compose up -d redis | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to start Redis"
        exit 1
    }
    
    Write-Success "Redis started successfully"
    Wait-ForService -Port $REDIS_PORT -ServiceName "Redis"
}

# Function to start Celery worker
function Start-CeleryWorker {
    Write-Status "Starting Celery worker..."
    
    docker-compose up -d celery-worker | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to start Celery worker"
        exit 1
    }
    
    Write-Success "Celery worker started successfully"
}

# Function to start Celery beat
function Start-CeleryBeat {
    Write-Status "Starting Celery beat (scheduler)..."
    
    docker-compose up -d celery-beat | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to start Celery beat"
        exit 1
    }
    
    Write-Success "Celery beat started successfully"
}

# Function to start Flask application
function Start-FlaskApp {
    Write-Status "Starting Flask application..."
    
    docker-compose up -d backend | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to start Flask application"
        exit 1
    }
    
    Write-Success "Flask application started successfully"
    Wait-ForService -Port $BACKEND_PORT -ServiceName "Flask App"
}

# Function to start Flower
function Start-Flower {
    Write-Status "Starting Flower (Celery monitoring)..."
    
    docker-compose up -d flower | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Failed to start Flower (optional component)"
        return
    }
    
    Write-Success "Flower started successfully"
    Wait-ForService -Port $FLOWER_PORT -ServiceName "Flower"
}

# Function to start all services
function Start-AllServices {
    Write-Status "Starting all Quiz Master services..."
    
    Start-Redis
    Start-CeleryWorker
    Start-CeleryBeat
    Start-FlaskApp
    Start-Flower
    Start-Mailhog
    Start-Frontend
    
    Write-Success "All services started successfully!"
}

# Function to show service status
function Show-Status {
    Write-Status "Checking service status..."
    Write-Host ""
    
    if (Test-Port $REDIS_PORT) {
        Write-Success "Redis: Running on port $REDIS_PORT"
    } else {
        Write-Error "Redis: Not running"
    }
    
    if (Test-Port $BACKEND_PORT) {
        Write-Success "Flask App: Running on port $BACKEND_PORT"
    } else {
        Write-Error "Flask App: Not running"
    }
    
    if (Test-Port $FLOWER_PORT) {
        Write-Success "Flower: Running on port $FLOWER_PORT"
    } else {
        Write-Warning "Flower: Not running"
    }
    
    Write-Host ""
    Write-Status "Docker containers status:"
    docker-compose ps
}

# Function to show logs
function Show-Logs {
    param([string]$Service = "")
    
    if ($Service) {
        Write-Status "Showing logs for $Service..."
        docker-compose logs -f $Service
    }
    else {
        Write-Status "Showing logs for all services..."
        docker-compose logs -f
    }
}

# Function to stop all services
function Stop-AllServices {
    Write-Status "Stopping all Quiz Master services..."
    
    docker-compose down | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to stop some services"
        exit 1
    }
    
    Write-Success "All services stopped successfully"
}

# Function to restart all services
function Restart-AllServices {
    Write-Status "Restarting all Quiz Master services..."
    Stop-AllServices
    Start-Sleep -Seconds 3
    Start-AllServices
}

# Function to clean up
function Remove-AllResources {
    Write-Status "Cleaning up Quiz Master resources..."
    
    $response = Read-Host "This will remove all containers, volumes, and networks. Are you sure? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        docker-compose down -v --remove-orphans | Out-Null
        docker system prune -f | Out-Null
        Write-Success "Cleanup completed"
    }
    else {
        Write-Status "Cleanup cancelled"
    }
}

# Function to show help
function Show-Help {
    Write-Host "Quiz Master 2 - Project Runner"
    Write-Host ""
    Write-Host "Usage: .\run_quiz_master.ps1 [COMMAND]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  start       Start all services (default)"
    Write-Host "  stop        Stop all services"
    Write-Host "  restart     Restart all services"
    Write-Host "  status      Show service status"
    Write-Host "  logs        Show logs for all services"
    Write-Host "  logs [svc]  Show logs for specific service"
    Write-Host "  build       Build Docker images"
    Write-Host "  cleanup     Remove all containers, volumes, networks"
    Write-Host "  help        Show this help message"
    Write-Host ""
    Write-Host "Services:"
    Write-Host "  - Redis (port $REDIS_PORT)"
    Write-Host "  - Flask App (port $BACKEND_PORT)"
    Write-Host "  - Celery Worker"
    Write-Host "  - Celery Beat (scheduler)"
    Write-Host "  - Flower (port $FLOWER_PORT)"
    Write-Host ""
    Write-Host "URLs:"
    Write-Host "  - Application: http://localhost:$BACKEND_PORT"
    Write-Host "  - Flower: http://localhost:$FLOWER_PORT"
    Write-Host ""
    Write-Host "Default admin credentials:"
    Write-Host "  Username: admin@quizmaster.com"
    Write-Host "  Password: admin123"
}

# Main execution
function Main {
    Write-Header
    
    switch ($Command.ToLower()) {
        "start" {
            Test-Prerequisites
            Initialize-Environment
            Invoke-BuildImages
            Start-AllServices
            Write-Host ""
            Write-Success "Quiz Master 2 is now running!"
            Write-Host ""
            Write-Host "Access URLs:" -ForegroundColor $CYAN
            Write-Host "  Application: http://localhost:$BACKEND_PORT" -ForegroundColor $GREEN
            Write-Host "  Flower (Celery): http://localhost:$FLOWER_PORT" -ForegroundColor $GREEN
            Write-Host ""
            Write-Host "Default Admin Credentials:" -ForegroundColor $CYAN
            Write-Host "  Username: admin@quizmaster.com" -ForegroundColor $GREEN
            Write-Host "  Password: admin123" -ForegroundColor $GREEN
            Write-Host ""
            Write-Status "Use '.\run_quiz_master.ps1 status' to check service status"
            Write-Status "Use '.\run_quiz_master.ps1 logs' to view logs"
            Write-Status "Use '.\run_quiz_master.ps1 stop' to stop all services"
        }
        "stop" {
            Stop-AllServices
        }
        "restart" {
            Restart-AllServices
        }
        "status" {
            Show-Status
        }
        "logs" {
            Show-Logs
        }
        "build" {
            Test-Prerequisites
            Invoke-BuildImages
        }
        "cleanup" {
            Remove-AllResources
        }
        "help" {
            Show-Help
        }
        default {
            Write-Error "Unknown command: $Command"
            Write-Host ""
            Show-Help
            exit 1
        }
    }
}

# Run main function
Main