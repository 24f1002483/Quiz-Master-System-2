#!/usr/bin/env python3
"""
Simple Redis installation script for Windows
Downloads and runs Redis without complex setup
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import tempfile
from pathlib import Path

def download_redis():
    """Download Redis for Windows"""
    print("📥 Downloading Redis for Windows...")
    
    # Redis for Windows download URL
    redis_url = "https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.zip"
    
    try:
        # Create temp directory
        temp_dir = Path(tempfile.gettempdir()) / "redis_install"
        temp_dir.mkdir(exist_ok=True)
        
        # Download Redis
        zip_path = temp_dir / "redis.zip"
        print(f"Downloading from: {redis_url}")
        
        urllib.request.urlretrieve(redis_url, zip_path)
        print("✅ Redis downloaded successfully")
        
        # Extract Redis
        extract_path = temp_dir / "redis"
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        print("✅ Redis extracted successfully")
        
        # Find redis-server.exe
        redis_server = None
        for root, dirs, files in os.walk(extract_path):
            if "redis-server.exe" in files:
                redis_server = Path(root) / "redis-server.exe"
                break
        
        if redis_server:
            print(f"✅ Found Redis server at: {redis_server}")
            return redis_server
        else:
            print("❌ Could not find redis-server.exe")
            return None
            
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return None

def start_redis_server(redis_path):
    """Start Redis server"""
    print("🚀 Starting Redis server...")
    
    try:
        # Start Redis server in background
        process = subprocess.Popen([
            str(redis_path),
            "--port", "6379",
            "--maxmemory", "256mb",
            "--maxmemory-policy", "allkeys-lru"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"✅ Redis server started with PID: {process.pid}")
        print("📝 Redis is running on localhost:6379")
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start Redis: {e}")
        return None

def test_redis_connection():
    """Test Redis connection"""
    print("🧪 Testing Redis connection...")
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis connection successful!")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def main():
    """Main installation function"""
    print("🚀 Simple Redis Installation for Quiz Master")
    print("=" * 50)
    
    # Check if Redis is already running
    if test_redis_connection():
        print("✅ Redis is already running!")
        return True
    
    # Download and install Redis
    redis_path = download_redis()
    if not redis_path:
        print("❌ Failed to download Redis")
        return False
    
    # Start Redis server
    process = start_redis_server(redis_path)
    if not process:
        print("❌ Failed to start Redis server")
        return False
    
    # Wait a moment for Redis to start
    import time
    time.sleep(2)
    
    # Test connection
    if test_redis_connection():
        print("\n🎉 Redis is now running!")
        print("📋 You can now:")
        print("   1. Run: python test_redis_celery.py")
        print("   2. Start Celery: python start_celery.py")
        print("   3. Stop Redis when done: taskkill /PID " + str(process.pid))
        return True
    else:
        print("❌ Redis installation failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 