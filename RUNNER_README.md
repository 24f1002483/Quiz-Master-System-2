# Quiz Master 2 - Project Runner Scripts

This directory contains comprehensive scripts to run all components of the Quiz Master 2 application with a single command.

## Available Scripts

### 1. `run_quiz_master.sh` (Linux/macOS)
Bash script for Unix-like systems with full color output and advanced features.

### 2. `run_quiz_master.bat` (Windows)
Batch script for Windows Command Prompt with basic functionality.

### 3. `run_quiz_master.ps1` (Windows PowerShell)
PowerShell script for Windows with enhanced features and better error handling.

## Quick Start

### Linux/macOS
```bash
# Make executable and run
chmod +x run_quiz_master.sh
./run_quiz_master.sh
```

### Windows (Command Prompt)
```cmd
run_quiz_master.bat
```

### Windows (PowerShell)
```powershell
.\run_quiz_master.ps1
```

## Commands

All scripts support the following commands:

| Command | Description |
|---------|-------------|
| `start` | Start all services (default) |
| `stop` | Stop all services |
| `restart` | Restart all services |
| `status` | Show service status |
| `logs` | Show logs for all services |
| `logs [service]` | Show logs for specific service |
| `build` | Build Docker images |
| `cleanup` | Remove all containers, volumes, and networks |
| `help` | Show help message |

## Services Started

The scripts will start the following services:

1. **Redis** (Port 6379) - Caching and message broker
2. **Flask Application** (Port 5000) - Main web application
3. **Celery Worker** - Background task processor
4. **Celery Beat** - Task scheduler
5. **Flower** (Port 5555) - Celery monitoring dashboard

## Access URLs

After starting the services:

- **Main Application**: http://localhost:5000
- **Flower (Celery Monitoring)**: http://localhost:5555

## Default Admin Credentials

- **Username**: admin@quizmaster.com
- **Password**: admin123

## Prerequisites

### Required Software
- Docker Desktop
- Docker Compose

### System Requirements
- **RAM**: Minimum 4GB, Recommended 8GB
- **Disk Space**: At least 2GB free space
- **OS**: Windows 10+, macOS 10.14+, or Linux

## Environment Configuration

The scripts will automatically create a `docker.env` file from `env.example` if it doesn't exist. You should edit this file with your actual configuration values:

```env
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
```

## Usage Examples

### Start All Services
```bash
# Linux/macOS
./run_quiz_master.sh start

# Windows
run_quiz_master.bat start
# or
.\run_quiz_master.ps1 start
```

### Check Service Status
```bash
# Linux/macOS
./run_quiz_master.sh status

# Windows
run_quiz_master.bat status
# or
.\run_quiz_master.ps1 status
```

### View Logs
```bash
# All services
./run_quiz_master.sh logs

# Specific service
./run_quiz_master.sh logs redis
./run_quiz_master.sh logs app
./run_quiz_master.sh logs celery-worker
```

### Stop All Services
```bash
./run_quiz_master.sh stop
```

### Clean Up Everything
```bash
./run_quiz_master.sh cleanup
```

## Troubleshooting

### Common Issues

1. **Docker not running**
   - Start Docker Desktop
   - Wait for it to fully initialize

2. **Port already in use**
   - Stop other services using the same ports
   - Or modify the port configuration in the scripts

3. **Permission denied (Linux/macOS)**
   ```bash
   chmod +x run_quiz_master.sh
   ```

4. **PowerShell execution policy (Windows)**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

### Service-Specific Issues

1. **Redis connection failed**
   - Check if Redis container is running
   - Verify Redis port (6379) is not blocked

2. **Flask app not accessible**
   - Check if app container is running
   - Verify port 5000 is not blocked by firewall

3. **Celery tasks not processing**
   - Check Celery worker logs
   - Verify Redis connection from Celery

### Logs and Debugging

- Use `logs` command to view real-time logs
- Check Docker container status with `docker-compose ps`
- View individual container logs with `docker-compose logs [service]`

## Development Mode

For development, you can run services individually:

```bash
# Start only Redis
docker-compose up -d redis

# Start only the Flask app
docker-compose up -d app

# Start only Celery worker
docker-compose up -d celery-worker
```

## Production Deployment

For production deployment:

1. Update `docker.env` with production values
2. Set strong SECRET_KEY and JWT_SECRET_KEY
3. Configure proper email settings
4. Use a production database (PostgreSQL/MySQL)
5. Set up proper SSL certificates
6. Configure reverse proxy (nginx/Apache)

## Script Features

### Linux/macOS Script (`run_quiz_master.sh`)
- ✅ Full color output
- ✅ Advanced port checking
- ✅ Service health monitoring
- ✅ Automatic retry logic
- ✅ Comprehensive error handling

### Windows Batch Script (`run_quiz_master.bat`)
- ✅ Basic functionality
- ✅ Port checking
- ✅ Service management
- ✅ Error handling

### PowerShell Script (`run_quiz_master.ps1`)
- ✅ Enhanced Windows compatibility
- ✅ Better error handling
- ✅ PowerShell-native features
- ✅ Improved logging

## Support

If you encounter issues:

1. Check the logs using the `logs` command
2. Verify all prerequisites are installed
3. Ensure Docker Desktop is running
4. Check system resources (RAM, disk space)
5. Review the troubleshooting section above

## License

This project is part of Quiz Master 2. Please refer to the main project license for usage terms.



