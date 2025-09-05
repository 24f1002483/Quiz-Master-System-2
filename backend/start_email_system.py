#!/usr/bin/env python3
"""
Start Email System Script
Starts the Celery scheduler to enable quiz emails
"""

import subprocess
import sys
import os
from dotenv import load_dotenv

def start_email_system():
    """Start the email notification system"""
    print("📧 Starting Quiz Master 2 Email System")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    print("🔍 Checking email configuration...")
    
    # Check if email config is valid
    try:
        from notification_config import validate_configuration
        if not validate_configuration():
            print("❌ Email configuration is incomplete!")
            print("   Please set up your .env file first")
            return False
        print("✅ Email configuration is valid")
    except Exception as e:
        print(f"❌ Error checking configuration: {e}")
        return False
    
    print("\n🚀 Starting Celery Beat Scheduler...")
    print("   This will enable automatic quiz emails:")
    print("   - Daily reminders (every 24 hours)")
    print("   - Monthly reports (every 30 days)")
    print("   - Export notifications (on demand)")
    
    try:
        # Start Celery beat scheduler
        beat_process = subprocess.Popen([
            sys.executable, '-m', 'celery', '-A', 'celery_app',
            'beat', '--loglevel=info', '--scheduler=celery.beat.PersistentScheduler'
        ])
        
        print(f"✅ Celery Beat started with PID: {beat_process.pid}")
        print("\n📧 Email System is now active!")
        print("\n📋 Scheduled Tasks:")
        print("   • Daily Quiz Reminders: Every 24 hours")
        print("   • Monthly Performance Reports: Every 30 days")
        print("   • Data Cleanup: Every 12 hours")
        
        print("\n💡 To stop the email system:")
        print("   Press Ctrl+C or kill the process")
        
        # Wait for the process
        beat_process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Email system stopped by user")
        if 'beat_process' in locals():
            beat_process.terminate()
    except Exception as e:
        print(f"❌ Failed to start email system: {e}")
        return False
    
    return True

def show_email_status():
    """Show current email system status"""
    print("📧 Email System Status")
    print("=" * 30)
    
    # Check if Celery beat is running
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        if 'celery' in result.stdout.lower():
            print("✅ Celery Beat is running")
        else:
            print("❌ Celery Beat is not running")
    except:
        print("⚠️  Could not check Celery status")
    
    # Check email configuration
    try:
        from notification_config import validate_configuration
        if validate_configuration():
            print("✅ Email configuration is valid")
        else:
            print("❌ Email configuration is incomplete")
    except Exception as e:
        print(f"❌ Error checking configuration: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        show_email_status()
    else:
        start_email_system() 