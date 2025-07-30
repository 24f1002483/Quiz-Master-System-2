#!/usr/bin/env python3
"""
Enhanced Celery startup script
Helps start Celery workers and beat scheduler with optimized configuration
"""

import os
import sys
import subprocess
import time
import signal
import threading
from datetime import datetime
import logging

# Setup logging with UTF-8 encoding for Windows compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('celery_startup.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)  # Use stdout instead of stderr for better encoding support
    ]
)
logger = logging.getLogger(__name__)

# Replace emoji characters with text equivalents for Windows compatibility
def safe_log(message):
    """Log message with emoji replacement for Windows compatibility"""
    # Replace emojis with text equivalents
    replacements = {
        '✅': '[PASS]',
        '❌': '[FAIL]',
        '🔍': '[TEST]',
        '🔧': '[CONFIG]',
        '📦': '[IMPORT]',
        '📧': '[EMAIL]',
        '📊': '[REPORT]',
        '🧹': '[CLEANUP]',
        '📱': '[SMS]',
        '⚡': '[PERF]',
        '📋': '[QUEUE]',
        '🛡️': '[ERROR]',
        '📊': '[MONITOR]',
        '📄': '[FILE]',
        '🎉': '[SUCCESS]',
        '⚠️': '[WARN]',
        '🚀': '[START]',
        '⏰': '[TIME]',
        '🌸': '[FLOWER]',
        '👀': '[MONITOR]',
        '🛑': '[STOP]',
        '👋': '[EXIT]',
        '📅': '[SCHEDULE]',
        '🔍': '[INFO]',
        '📈': '[STATS]',
        '👥': '[WORKERS]',
        '🟢': '[ONLINE]',
        '⚪': '[IDLE]',
        '🌐': '[WEB]',
        '🎯': '[TARGET]',
        '🗑️': '[DELETE]'
    }
    
    for emoji, text in replacements.items():
        message = message.replace(emoji, text)
    
    logger.info(message)

def check_redis_connection():
    """Check if Redis is available for Celery"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        safe_log("[PASS] Redis connection successful")
        return True
    except Exception as e:
        safe_log(f"[FAIL] Redis connection failed: {e}")
        return False

def optimize_redis():
    """Optimize Redis settings for better performance"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Set memory policy
        r.config_set('maxmemory-policy', 'allkeys-lru')
        
        # Set persistence settings
        r.config_set('save', '900 1 300 10 60 10000')
        
        # Set TCP keepalive
        r.config_set('tcp-keepalive', '300')
        
        # Enable slow log
        r.config_set('slowlog-log-slower-than', '10000')
        r.config_set('slowlog-max-len', '128')
        
        safe_log("[PASS] Redis optimization completed")
        return True
    except Exception as e:
        safe_log(f"[FAIL] Redis optimization failed: {e}")
        return False

def start_celery_worker(queue_name='default', concurrency=4):
    """Start Celery worker process for specific queue"""
    safe_log(f"[START] Starting Celery worker for queue: {queue_name}")
    
    try:
        # Set environment variables
        env = os.environ.copy()
        env['REDIS_URL'] = 'redis://localhost:6379/0'
        
        # Start worker with queue-specific configuration
        worker_process = subprocess.Popen([
            sys.executable, '-m', 'celery', '-A', 'celery_app', 
            'worker', '--loglevel=info', f'--concurrency={concurrency}',
            f'--queues={queue_name}', '--hostname=worker@%h'
        ], env=env, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        safe_log(f"[PASS] Celery worker started for {queue_name} with PID: {worker_process.pid}")
        return worker_process
        
    except Exception as e:
        safe_log(f"[FAIL] Failed to start Celery worker for {queue_name}: {e}")
        return None

def start_celery_beat():
    """Start Celery beat scheduler"""
    safe_log("[TIME] Starting Celery beat scheduler...")
    
    try:
        # Set environment variables
        env = os.environ.copy()
        env['REDIS_URL'] = 'redis://localhost:6379/0'
        
        # Start beat with enhanced logging
        beat_process = subprocess.Popen([
            sys.executable, '-m', 'celery', '-A', 'celery_app', 
            'beat', '--loglevel=info', '--scheduler=celery.beat.PersistentScheduler'
        ], env=env, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        safe_log(f"[PASS] Celery beat started with PID: {beat_process.pid}")
        return beat_process
        
    except Exception as e:
        safe_log(f"[FAIL] Failed to start Celery beat: {e}")
        return None

def start_flower_monitoring():
    """Start Flower monitoring interface"""
    safe_log("[FLOWER] Starting Flower monitoring...")
    
    try:
        # Set environment variables
        env = os.environ.copy()
        env['REDIS_URL'] = 'redis://localhost:6379/0'
        
        # Start Flower
        flower_process = subprocess.Popen([
            sys.executable, '-m', 'flower', '-A', 'celery_app',
            '--port=5555', '--broker=redis://localhost:6379/0'
        ], env=env, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        safe_log(f"[PASS] Flower monitoring started with PID: {flower_process.pid}")
        safe_log("[WEB] Flower UI available at: http://localhost:5555")
        return flower_process
        
    except Exception as e:
        safe_log(f"[FAIL] Failed to start Flower: {e}")
        return None

def test_celery_tasks():
    """Test Celery task creation and execution"""
    safe_log("[TEST] Testing Celery tasks...")
    
    try:
        from celery_app import send_daily_reminders, generate_monthly_reports, cleanup_old_data
        
        # Test daily reminders task
        safe_log("[EMAIL] Testing daily reminders task...")
        daily_task = send_daily_reminders.delay()
        safe_log(f"[PASS] Daily reminders task created: {daily_task.id}")
        
        # Test monthly reports task
        safe_log("[REPORT] Testing monthly reports task...")
        monthly_task = generate_monthly_reports.delay()
        safe_log(f"[PASS] Monthly reports task created: {monthly_task.id}")
        
        # Test cleanup task
        safe_log("[CLEANUP] Testing cleanup task...")
        cleanup_task = cleanup_old_data.delay()
        safe_log(f"[PASS] Cleanup task created: {cleanup_task.id}")
        
        # Wait a bit for tasks to process
        time.sleep(3)
        
        # Check task status
        daily_status = daily_task.status
        monthly_status = monthly_task.status
        cleanup_status = cleanup_task.status
        
        safe_log(f"[STATS] Daily task status: {daily_status}")
        safe_log(f"[STATS] Monthly task status: {monthly_status}")
        safe_log(f"[STATS] Cleanup task status: {cleanup_status}")
        
        return True
        
    except ImportError as e:
        safe_log(f"[FAIL] Import error: {e}")
        return False
    except Exception as e:
        safe_log(f"[FAIL] Task testing error: {e}")
        return False

def monitor_processes(processes):
    """Monitor running processes and restart if needed"""
    safe_log("[MONITOR] Starting process monitoring...")
    
    while True:
        try:
            for name, process in processes.items():
                if process and process.poll() is not None:
                    safe_log(f"[WARN] Process {name} has stopped, restarting...")
                    
                    if name == 'beat':
                        processes[name] = start_celery_beat()
                    elif name == 'flower':
                        processes[name] = start_flower_monitoring()
                    elif name.startswith('worker_'):
                        queue_name = name.replace('worker_', '')
                        processes[name] = start_celery_worker(queue_name)
            
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            safe_log("[STOP] Process monitoring stopped by user")
            break
        except Exception as e:
            safe_log(f"[FAIL] Process monitoring error: {e}")
            time.sleep(60)  # Wait longer on error

def show_scheduled_tasks():
    """Show currently scheduled tasks"""
    try:
        from celery_app import celery
        from config import Config
        
        safe_log("[SCHEDULE] Scheduled Tasks:")
        for task_name, task_config in Config.beat_schedule.items():
            safe_log(f"  - {task_name}: {task_config['task']} (every {task_config['schedule']})")
        
    except Exception as e:
        safe_log(f"[FAIL] Error showing scheduled tasks: {e}")

def show_redis_info():
    """Show Redis information"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        info = r.info()
        
        safe_log("[INFO] Redis Information:")
        safe_log(f"  - Version: {info.get('redis_version', 'Unknown')}")
        safe_log(f"  - Memory Used: {info.get('used_memory_human', 'Unknown')}")
        safe_log(f"  - Connected Clients: {info.get('connected_clients', 0)}")
        safe_log(f"  - Uptime: {info.get('uptime_in_days', 0)} days")
        
    except Exception as e:
        safe_log(f"[FAIL] Error getting Redis info: {e}")

def show_queue_status():
    """Show current queue status"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        queues = ['default', 'reminders', 'reports', 'notifications', 'maintenance']
        
        safe_log("[QUEUE] Queue Status:")
        for queue in queues:
            length = r.llen(f'celery:{queue}')
            status = '[ONLINE] Active' if length > 0 else '[IDLE] Idle'
            safe_log(f"  - {queue}: {length} tasks {status}")
        
    except Exception as e:
        safe_log(f"[FAIL] Error getting queue status: {e}")

def cleanup_old_files():
    """Clean up old log files and temporary data"""
    try:
        import glob
        import os
        
        # Clean up old log files
        log_files = glob.glob('*.log')
        for log_file in log_files:
            if os.path.getmtime(log_file) < time.time() - (7 * 24 * 3600):  # 7 days
                os.remove(log_file)
                safe_log(f"[DELETE] Removed old log file: {log_file}")
        
        # Clean up old Celery schedule files
        schedule_files = glob.glob('celerybeat-schedule*')
        for schedule_file in schedule_files:
            if os.path.getmtime(schedule_file) < time.time() - (30 * 24 * 3600):  # 30 days
                os.remove(schedule_file)
                safe_log(f"[DELETE] Removed old schedule file: {schedule_file}")
        
    except Exception as e:
        safe_log(f"[FAIL] Error cleaning up files: {e}")

def main():
    """Main function to start all Celery services"""
    safe_log("[START] Starting Quiz Master Celery Services...")
    
    # Check Redis connection
    if not check_redis_connection():
        safe_log("[FAIL] Cannot start Celery without Redis")
        return
    
    # Optimize Redis
    optimize_redis()
    
    # Clean up old files
    cleanup_old_files()
    
    # Show system information
    show_redis_info()
    show_scheduled_tasks()
    show_queue_status()
    
    # Start workers for different queues
    processes = {}
    
    # Start main worker
    processes['worker_default'] = start_celery_worker('default', 2)
    
    # Start specialized workers
    processes['worker_reminders'] = start_celery_worker('reminders', 2)
    processes['worker_reports'] = start_celery_worker('reports', 1)
    processes['worker_notifications'] = start_celery_worker('notifications', 3)
    processes['worker_maintenance'] = start_celery_worker('maintenance', 1)
    
    # Start beat scheduler
    processes['beat'] = start_celery_beat()
    
    # Start Flower monitoring (optional)
    try:
        processes['flower'] = start_flower_monitoring()
    except ImportError:
        safe_log("[WARN] Flower not available, skipping monitoring UI")
    
    # Test tasks
    time.sleep(2)  # Wait for workers to start
    test_celery_tasks()
    
    # Start monitoring in a separate thread
    monitor_thread = threading.Thread(
        target=monitor_processes, 
        args=(processes,),
        daemon=True
    )
    monitor_thread.start()
    
    safe_log("[SUCCESS] All Celery services started successfully!")
    safe_log("[QUEUE] Available services:")
    safe_log("  - Celery Workers: Processing tasks")
    safe_log("  - Celery Beat: Scheduling tasks")
    safe_log("  - Flower: Monitoring UI (http://localhost:5555)")
    safe_log("  - Process Monitor: Auto-restart on failure")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(60)
            show_queue_status()
    except KeyboardInterrupt:
        safe_log("[STOP] Shutting down Celery services...")
        
        # Stop all processes
        for name, process in processes.items():
            if process:
                try:
                    process.terminate()
                    process.wait(timeout=10)
                    safe_log(f"[PASS] Stopped {name}")
                except subprocess.TimeoutExpired:
                    process.kill()
                    safe_log(f"[WARN] Force killed {name}")
                except Exception as e:
                    safe_log(f"[FAIL] Error stopping {name}: {e}")
        
        safe_log("[EXIT] Celery services stopped")

if __name__ == "__main__":
    main() 