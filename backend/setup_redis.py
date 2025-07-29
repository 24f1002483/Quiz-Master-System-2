#!/usr/bin/env python3
"""
Redis setup and test script
Helps set up Redis for local testing
"""

import subprocess
import sys
import time
import redis
from datetime import datetime

def check_redis_installation():
    """Check if Redis is installed and running"""
    print("🔍 Checking Redis installation...")
    
    try:
        # Try to connect to Redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis is running on localhost:6379")
        return True
    except redis.ConnectionError:
        print("❌ Redis is not running or not accessible")
        return False
    except Exception as e:
        print(f"❌ Redis check failed: {e}")
        return False

def install_redis_windows():
    """Install Redis on Windows using Chocolatey"""
    print("🔧 Installing Redis on Windows...")
    
    try:
        # Check if Chocolatey is installed
        result = subprocess.run(['choco', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Chocolatey not found. Please install Chocolatey first:")
            print("   https://chocolatey.org/install")
            return False
        
        # Install Redis
        print("📦 Installing Redis via Chocolatey...")
        result = subprocess.run(['choco', 'install', 'redis-64', '-y'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Redis installed successfully")
            return True
        else:
            print(f"❌ Redis installation failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ Chocolatey not found. Please install Chocolatey first.")
        return False
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False

def start_redis_windows():
    """Start Redis service on Windows"""
    print("🚀 Starting Redis service...")
    
    try:
        # Start Redis service
        result = subprocess.run(['net', 'start', 'Redis'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Redis service started")
            return True
        else:
            print(f"⚠️  Redis service start result: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start Redis: {e}")
        return False

def test_redis_operations():
    """Test basic Redis operations"""
    print("🧪 Testing Redis operations...")
    
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Test basic operations
        r.set('test_key', 'test_value', ex=60)
        value = r.get('test_key')
        assert value == 'test_value', f"Expected 'test_value', got {value}"
        print("✅ Basic Redis operations working")
        
        # Test different databases
        r1 = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r2 = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)
        
        r1.set('db0_key', 'db0_value')
        r2.set('db1_key', 'db1_value')
        
        assert r1.get('db0_key') == 'db0_value'
        assert r2.get('db1_key') == 'db1_value'
        assert r1.get('db1_key') is None  # Should not exist in db 0
        print("✅ Multiple Redis databases working")
        
        # Test list operations
        r.lpush('test_list', 'item1', 'item2', 'item3')
        items = r.lrange('test_list', 0, -1)
        assert len(items) == 3, f"Expected 3 items, got {len(items)}"
        print("✅ Redis list operations working")
        
        # Test hash operations
        r.hset('test_hash', mapping={'field1': 'value1', 'field2': 'value2'})
        hash_data = r.hgetall('test_hash')
        assert len(hash_data) == 2, f"Expected 2 fields, got {len(hash_data)}"
        print("✅ Redis hash operations working")
        
        # Clean up
        r.delete('test_key', 'db0_key', 'db1_key', 'test_list', 'test_hash')
        r2.delete('db1_key')
        
        return True
        
    except Exception as e:
        print(f"❌ Redis operations test failed: {e}")
        return False

def setup_redis_config():
    """Set up Redis configuration for the application"""
    print("⚙️  Setting up Redis configuration...")
    
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Configure Redis for optimal performance
        configs = {
            'maxmemory-policy': 'allkeys-lru',
            'maxmemory': '256mb',
            'timeout': '300',
            'tcp-keepalive': '60',
            'save': '',  # Disable persistence for cache
            'appendonly': 'no'  # Disable AOF for cache
        }
        
        for key, value in configs.items():
            try:
                r.config_set(key, value)
                print(f"✅ Set {key} = {value}")
            except Exception as e:
                print(f"⚠️  Could not set {key}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis configuration failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Redis Setup for Quiz Master Application")
    print("=" * 50)
    
    # Check if Redis is already running
    if check_redis_installation():
        print("✅ Redis is already running!")
    else:
        print("❌ Redis is not running. Attempting to install and start...")
        
        # Try to install Redis
        if not install_redis_windows():
            print("❌ Failed to install Redis automatically.")
            print("💡 Please install Redis manually:")
            print("   1. Download from https://redis.io/download")
            print("   2. Or use Chocolatey: choco install redis-64")
            return False
        
        # Try to start Redis
        if not start_redis_windows():
            print("❌ Failed to start Redis service.")
            print("💡 Please start Redis manually:")
            print("   net start Redis")
            return False
    
    # Test Redis operations
    if not test_redis_operations():
        print("❌ Redis operations test failed.")
        return False
    
    # Set up configuration
    if not setup_redis_config():
        print("❌ Redis configuration failed.")
        return False
    
    print("\n🎉 Redis setup completed successfully!")
    print("📋 Next steps:")
    print("   1. Run the test script: python test_redis_celery.py")
    print("   2. Start Celery worker: celery -A celery_app worker --loglevel=info")
    print("   3. Start Celery beat: celery -A celery_app beat --loglevel=info")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 