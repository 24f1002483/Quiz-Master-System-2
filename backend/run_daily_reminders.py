#!/usr/bin/env python3
"""
Daily Reminders System - Main Entry Point
Handles daily quiz reminders with comprehensive email monitoring
"""

import sys
import os
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_reminders.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Setup environment and check configuration"""
    # Load environment variables
    load_dotenv()
    
    logger.info("Daily Reminders System - Email Only")
    logger.info("=" * 50)
    
    # Check required environment variables
    required_vars = [
        'EMAIL_FROM', 'SMTP_HOST', 'SMTP_PORT', 
        'SMTP_USERNAME', 'SMTP_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please set up your email configuration in .env file:")
        logger.info("   EMAIL_FROM=your-email@gmail.com")
        logger.info("   SMTP_HOST=smtp.gmail.com")
        logger.info("   SMTP_PORT=587")
        logger.info("   SMTP_USERNAME=your-email@gmail.com")
        logger.info("   SMTP_PASSWORD=your-app-password")
        return False
    
    logger.info("Environment configuration is valid")
    return True

def test_email_connection():
    """Test email connection and configuration"""
    try:
        from notification_services import send_email_internal
        
        logger.info("Testing email connection...")
        
        # Test email
        test_result = send_email_internal(
            recipient=os.getenv('EMAIL_FROM'),  # Send to self for testing
            subject="Quiz Master 2 - Email Test",
            body="This is a test email from Quiz Master 2 Daily Reminders system.\n\nIf you receive this, your email configuration is working correctly!"
        )
        
        logger.info("Email test successful!")
        return True
        
    except Exception as e:
        logger.error(f"Email test failed: {e}")
        return False

def run_single_reminder_test():
    """Run a single reminder test"""
    try:
        from app import create_app
        from models.model import db, User, Role
        from enhanced_daily_reminders import enhanced_daily_reminders_task
        
        logger.info("Running single reminder test...")
        
        app = create_app()
        with app.app_context():
            # Get a test user
            test_user = User.query.filter_by(role=Role.USER, is_active=True).first()
            
            if not test_user:
                logger.warning("No active users found for testing")
                return False
            
            logger.info(f"Testing reminder for user: {test_user.username}")
            
            # Run enhanced reminders
            result = enhanced_daily_reminders_task()
            logger.info(f"Test completed: {result}")
            return True
            
    except Exception as e:
        logger.error(f"Single reminder test failed: {e}")
        return False

def run_continuous_monitoring():
    """Run continuous monitoring of email system"""
    logger.info("Starting continuous monitoring mode...")
    logger.info("   Press Ctrl+C to stop")
    
    try:
        import time
        from app import create_app
        from models.model import db, User, Role
        
        app = create_app()
        
        while True:
            try:
                with app.app_context():
                    # Check system status every 5 minutes
                    logger.info("System Status Check:")
                    
                    # Count active users
                    active_users = User.query.filter_by(role=Role.USER, is_active=True).count()
                    logger.info(f"Active Users: {active_users}")
                    
                    # Check email configuration
                    if not setup_environment():
                        logger.warning("Email Config: Invalid")
                    else:
                        logger.info("Email Config: Valid")
                    
                    # Test email connection every hour
                    current_time = datetime.now()
                    if current_time.minute == 0:  # Top of the hour
                        test_email_connection()
                    
                    logger.info(f"Next check in 5 minutes...")
                    
                time.sleep(300)  # Wait 5 minutes
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
                
    except Exception as e:
        logger.error(f"Continuous monitoring failed: {e}")
        return False

def show_scheduled_tasks():
    """Show information about scheduled tasks"""
    logger.info("Scheduled Tasks Information")
    logger.info("=" * 40)
    logger.info("Daily Reminders:")
    logger.info("  • Frequency: Every 24 hours")
    logger.info("  • Purpose: Send quiz reminders to inactive users")
    logger.info("  • Triggers: User inactivity, new quizzes, upcoming quizzes")
    logger.info("")
    logger.info("Monthly Reports:")
    logger.info("  • Frequency: Every 30 days")
    logger.info("  • Purpose: Send performance reports to users")
    logger.info("  • Content: Quiz statistics, progress analysis")
    logger.info("")
    logger.info("Email Monitoring:")
    logger.info("  • Logs: daily_reminders.log, notification_logs.log")
    logger.info("  • Status: Check logs for delivery confirmation")
    logger.info("  • Testing: Use 'test' command to verify email setup")

def show_email_delivery_status():
    """Show recent email delivery status"""
    logger.info("Recent Email Delivery Status")
    logger.info("=" * 40)
    
    try:
        # Read recent logs
        log_files = ['daily_reminders.log', 'notification_logs.log']
        
        for log_file in log_files:
            if os.path.exists(log_file):
                logger.info(f"\n{log_file} (last 10 lines):")
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-10:]:
                        if 'Email sent successfully' in line or 'Failed to send' in line:
                            logger.info(f"   {line.strip()}")
            else:
                logger.info(f"{log_file}: Not found")
                
    except Exception as e:
        logger.error(f"Could not read log files: {e}")

def main():
    """Main entry point"""
    # Get command from arguments
    command = sys.argv[1] if len(sys.argv) > 1 else "test"
    
    # Setup environment
    if not setup_environment():
        return 1
    
    # Execute command
    if command == "test":
        logger.info("Running single reminder test...")
        if test_email_connection() and run_single_reminder_test():
            logger.info("Test completed successfully")
            return 0
        else:
            logger.error("Test failed")
            return 1
            
    elif command == "monitor":
        run_continuous_monitoring()
        return 0
        
    elif command == "schedule":
        show_scheduled_tasks()
        return 0
        
    elif command == "status":
        show_email_delivery_status()
        return 0
        
    elif command == "email-test":
        if test_email_connection():
            logger.info("Email test successful")
            return 0
        else:
            logger.error("Email test failed")
            return 1
            
    else:
        logger.info("Available commands:")
        logger.info("  test       - Run single reminder test")
        logger.info("  monitor    - Start continuous monitoring")
        logger.info("  schedule   - Show scheduled tasks info")
        logger.info("  status     - Show email delivery status")
        logger.info("  email-test - Test email connection only")
        return 0

if __name__ == "__main__":
    sys.exit(main())