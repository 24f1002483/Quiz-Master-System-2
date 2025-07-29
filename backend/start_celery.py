#!/usr/bin/env python3
"""
Celery startup script
Helps start Celery workers and beat scheduler
"""

import os
import sys
import subprocess
import time
import signal
import threading
from datetime import datetime

def check_redis_connection():
    """Check if Redis is available for Celery"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        return True
    except:
        return False

def start_celery_worker():
    """Start Celery worker process"""
    print("🚀 Starting Celery worker...")
    
    try:
        # Set environment variables
        env = os.environ.copy()
        env['REDIS_URL'] = 'redis://localhost:6379/0'
        
        # Start worker
        worker_process = subprocess.Popen([
            sys.executable, '-m', 'celery', '-A', 'celery_app', 
            'worker', '--loglevel=info', '--concurrency=4'
        ], env=env, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        print(f"✅ Celery worker started with PID: {worker_process.pid}")
        return worker_process
        
    except Exception as e:
        print(f"❌ Failed to start Celery worker: {e}")
        return None

def start_celery_beat():
    """Start Celery beat scheduler"""
    print("⏰ Starting Celery beat scheduler...")
    
    try:
        # Set environment variables
        env = os.environ.copy()
        env['REDIS_URL'] = 'redis://localhost:6379/0'
        
        # Start beat
        beat_process = subprocess.Popen([
            sys.executable, '-m', 'celery', '-A', 'celery_app', 
            'beat', '--loglevel=info'
        ], env=env, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        print(f"✅ Celery beat started with PID: {beat_process.pid}")
        return beat_process
        
    except Exception as e:
        print(f"❌ Failed to start Celery beat: {e}")
        return None

def test_celery_tasks():
    """Test Celery task creation and execution"""
    print("🧪 Testing Celery tasks...")
    
    try:
        from celery_app import send_daily_reminders, generate_monthly_reports
        
        # Test daily reminders task
        print("📧 Testing daily reminders task...")
        daily_task = send_daily_reminders.delay()
        print(f"✅ Daily reminders task created: {daily_task.id}")
        
        # Test monthly reports task
        print("📊 Testing monthly reports task...")
        monthly_task = generate_monthly_reports.delay()
        print(f"✅ Monthly reports task created: {monthly_task.id}")
        
        # Wait a bit for tasks to process
        time.sleep(2)
        
        # Check task status
        daily_status = daily_task.status
        monthly_status = monthly_task.status
        
        print(f"📈 Daily task status: {daily_status}")
        print(f"📈 Monthly task status: {monthly_status}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Celery test failed: {e}")
        return False

def monitor_processes(worker_process, beat_process):
    """Monitor running processes"""
    print("👀 Monitoring Celery processes...")
    print("Press Ctrl+C to stop all processes")
    
    try:
        while True:
            # Check if processes are still running
            if worker_process and worker_process.poll() is not None:
                print("⚠️  Celery worker has stopped")
                break
                
            if beat_process and beat_process.poll() is not None:
                print("⚠️  Celery beat has stopped")
                break
                
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping Celery processes...")
        
        # Stop worker
        if worker_process:
            worker_process.terminate()
            try:
                worker_process.wait(timeout=10)
                print("✅ Celery worker stopped")
            except subprocess.TimeoutExpired:
                worker_process.kill()
                print("⚠️  Celery worker force killed")
        
        # Stop beat
        if beat_process:
            beat_process.terminate()
            try:
                beat_process.wait(timeout=10)
                print("✅ Celery beat stopped")
            except subprocess.TimeoutExpired:
                beat_process.kill()
                print("⚠️  Celery beat force killed")

def show_scheduled_tasks():
    """Show scheduled tasks configuration"""
    print("📅 Scheduled Tasks Configuration:")
    print("=" * 40)
    
    try:
        from config import Config
        
        schedule = Config.CELERYBEAT_SCHEDULE
        
        for task_name, task_config in schedule.items():
            print(f"\n🎯 Task: {task_name}")
            print(f"   Schedule: {task_config['schedule']}")
            print(f"   Time Limit: {task_config['options']['time_limit']}s")
            print(f"   Soft Time Limit: {task_config['options']['soft_time_limit']}s")
            
    except Exception as e:
        print(f"❌ Could not load scheduled tasks: {e}")

def show_redis_info():
    """Show Redis information"""
    print("🔍 Redis Information:")
    print("=" * 30)
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        info = r.info()
        print(f"Redis Version: {info.get('redis_version', 'Unknown')}")
        print(f"Connected Clients: {info.get('connected_clients', 'Unknown')}")
        print(f"Used Memory: {info.get('used_memory_human', 'Unknown')}")
        print(f"Total Commands: {info.get('total_commands_processed', 'Unknown')}")
        
        # Check Celery keys
        celery_keys = r.keys('celery*')
        print(f"Celery Keys: {len(celery_keys)}")
        
    except Exception as e:
        print(f"❌ Could not get Redis info: {e}")

def main():
    """Main function"""
    print("🚀 Celery Setup for Quiz Master Application")
    print("=" * 50)
    
    # Check Redis connection
    if not check_redis_connection():
        print("❌ Redis is not available. Please start Redis first.")
        print("💡 Run: python setup_redis.py")
        return False
    
    print("✅ Redis connection available")
    
    # Show configuration
    show_scheduled_tasks()
    show_redis_info()
    
    # Ask user what to do
    print("\n🎛️  Choose an option:")
    print("1. Start Celery worker only")
    print("2. Start Celery beat only")
    print("3. Start both worker and beat")
    print("4. Test Celery tasks only")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    worker_process = None
    beat_process = None
    
    try:
        if choice == '1':
            worker_process = start_celery_worker()
            if worker_process:
                monitor_processes(worker_process, None)
                
        elif choice == '2':
            beat_process = start_celery_beat()
            if beat_process:
                monitor_processes(None, beat_process)
                
        elif choice == '3':
            worker_process = start_celery_worker()
            time.sleep(2)  # Give worker time to start
            beat_process = start_celery_beat()
            if worker_process and beat_process:
                monitor_processes(worker_process, beat_process)
                
        elif choice == '4':
            test_celery_tasks()
            
        elif choice == '5':
            print("👋 Goodbye!")
            return True
            
        else:
            print("❌ Invalid choice")
            return False
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        
    finally:
        # Clean up processes
        if worker_process:
            worker_process.terminate()
        if beat_process:
            beat_process.terminate()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 