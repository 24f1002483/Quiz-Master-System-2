#!/usr/bin/env python3
"""
Script to restart Celery services and clear Redis cache after fixing configuration
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def run_command(command, description):
    """Run a shell command and return success status"""
    try:
        print(f"🔧 {description}...")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def check_redis_connection():
    """Check if Redis is running and accessible"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is running and accessible")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def clear_redis_cache():
    """Clear Redis cache to remove any corrupted data"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        
        # Get current key count
        key_count = r.dbsize()
        print(f"🔧 Clearing Redis cache (current keys: {key_count})...")
        
        # Clear all keys in database 0
        r.flushdb()
        
        new_key_count = r.dbsize()
        print(f"✅ Redis cache cleared (remaining keys: {new_key_count})")
        return True
    except Exception as e:
        print(f"❌ Failed to clear Redis cache: {e}")
        return False

def stop_celery_processes():
    """Stop any running Celery processes"""
    commands = [
        ("pkill -f celery", "Stopping Celery processes"),
        ("pkill -f 'celery worker'", "Stopping Celery workers"),
        ("pkill -f 'celery beat'", "Stopping Celery beat scheduler")
    ]
    
    for command, description in commands:
        run_command(command, description)
    
    # Wait a moment for processes to stop
    time.sleep(2)

def main():
    print("🔄 Service Restart Script")
    print("=" * 40)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if Redis is running
    if not check_redis_connection():
        print("⚠️  Redis is not running. Please start Redis first:")
        print("   - On Windows: Start Redis server")
        print("   - On Linux/Mac: redis-server")
        return
    
    # Stop Celery processes
    print("🛑 Stopping Celery processes...")
    stop_celery_processes()
    
    # Clear Redis cache
    clear_redis_cache()
    
    print()
    print("✅ Services have been reset!")
    print()
    print("📋 Next steps:")
    print("1. Start Celery worker:")
    print("   python -m celery -A celery_app worker --loglevel=info")
    print()
    print("2. Start Celery beat (in another terminal):")
    print("   python -m celery -A celery_app beat --loglevel=info")
    print()
    print("3. Test the export functionality in the web interface")
    print()
    print("4. Or run the test script:")
    print("   python test_export.py")
    
    print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()