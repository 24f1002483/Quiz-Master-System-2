#!/usr/bin/env python3
"""
Email Monitoring Dashboard
Comprehensive tool to monitor email delivery status and troubleshoot issues
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import re

def setup_logging():
    """Setup logging for the monitor"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

logger = setup_logging()

class EmailMonitor:
    def __init__(self):
        self.log_files = [
            'daily_reminders.log',
            'notification_logs.log'
        ]
        self.stats = {
            'total_attempts': 0,
            'successful_sends': 0,
            'failed_sends': 0,
            'recent_errors': [],
            'user_stats': defaultdict(int),
            'hourly_stats': defaultdict(int)
        }
    
    def parse_log_files(self):
        """Parse log files to extract email statistics"""
        logger.info("Analyzing email logs...")
        
        for log_file in self.log_files:
            if not os.path.exists(log_file):
                logger.warning(f"Log file not found: {log_file}")
                continue
                
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line in lines:
                    self._parse_log_line(line.strip())
                    
            except Exception as e:
                logger.error(f"Error reading {log_file}: {e}")
    
    def _parse_log_line(self, line):
        """Parse individual log line"""
        if not line:
            return
            
        # Extract timestamp
        timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
        if timestamp_match:
            timestamp_str = timestamp_match.group(1)
            try:
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                hour_key = timestamp.strftime('%Y-%m-%d %H:00')
                self.stats['hourly_stats'][hour_key] += 1
            except:
                pass
        
        # Check for email success
        if 'Email sent successfully' in line:
            self.stats['successful_sends'] += 1
            self.stats['total_attempts'] += 1
            
            # Extract recipient
            recipient_match = re.search(r'Email sent successfully to (.+)', line)
            if recipient_match:
                recipient = recipient_match.group(1)
                self.stats['user_stats'][recipient] += 1
        
        # Check for email failures
        elif 'Failed to send' in line or 'ERROR' in line:
            self.stats['failed_sends'] += 1
            self.stats['total_attempts'] += 1
            
            # Store recent errors
            if len(self.stats['recent_errors']) < 10:
                self.stats['recent_errors'].append(line)
    
    def check_email_configuration(self):
        """Check email configuration status"""
        logger.info("Checking email configuration...")
        
        required_vars = [
            'EMAIL_FROM', 'SMTP_HOST', 'SMTP_PORT',
            'SMTP_USERNAME', 'SMTP_PASSWORD'
        ]
        
        config_status = {}
        for var in required_vars:
            value = os.getenv(var)
            config_status[var] = {
                'configured': bool(value),
                'value': value[:10] + '...' if value and len(value) > 10 else value
            }
        
        return config_status
    
    def test_email_connection(self):
        """Test email connection"""
        logger.info("Testing email connection...")
        
        try:
            from notification_services import send_email_internal
            
            # Test with a simple email
            result = send_email_internal(
                recipient=os.getenv('EMAIL_FROM'),
                subject="Quiz Master 2 - Connection Test",
                body="Email connection test successful!"
            )
            
            return True, "Connection successful"
            
        except Exception as e:
            return False, str(e)
    
    def get_user_email_addresses(self):
        """Get user email addresses from database"""
        try:
            from app import create_app
            from models.model import db, User, Role
            
            app = create_app()
            with app.app_context():
                users = User.query.filter_by(role=Role.USER, is_active=True).all()
                
                user_emails = []
                for user in users:
                    # Check if user has email field or use username
                    email = getattr(user, 'email', None) or user.username
                    user_emails.append({
                        'id': user.id,
                        'username': user.username,
                        'email': email,
                        'full_name': getattr(user, 'full_name', 'N/A'),
                        'last_login': user.last_login.isoformat() if user.last_login else 'Never'
                    })
                
                return user_emails
                
        except Exception as e:
            logger.error(f"Error getting user emails: {e}")
            return []
    
    def generate_report(self):
        """Generate comprehensive email monitoring report"""
        logger.info("Generating Email Monitoring Report")
        logger.info("=" * 50)
        
        # Parse logs
        self.parse_log_files()
        
        # Configuration status
        logger.info("\nEmail Configuration:")
        config_status = self.check_email_configuration()
        for var, status in config_status.items():
            logger.info(f"   {var}: {'Configured' if status['configured'] else 'Missing'}")
        
        # Connection test
        logger.info("\nConnection Test:")
        test_success, test_message = self.test_email_connection()
        logger.info(f"   {test_message}")
        
        # Email statistics
        logger.info("\nEmail Statistics:")
        logger.info(f"   Total Attempts: {self.stats['total_attempts']}")
        logger.info(f"   Successful Sends: {self.stats['successful_sends']}")
        logger.info(f"   Failed Sends: {self.stats['failed_sends']}")
        
        if self.stats['total_attempts'] > 0:
            success_rate = (self.stats['successful_sends'] / self.stats['total_attempts']) * 100
            logger.info(f"   Success Rate: {success_rate:.1f}%")
        
        # User statistics
        if self.stats['user_stats']:
            logger.info("\nEmails by User:")
            for user, count in sorted(self.stats['user_stats'].items()):
                logger.info(f"   {user}: {count} emails")
        
        # Recent errors
        if self.stats['recent_errors']:
            logger.info("\nRecent Errors:")
            for error in self.stats['recent_errors'][-5:]:  # Show last 5 errors
                logger.info(f"   {error}")
        
        # Active users
        logger.info("\nActive Users:")
        users = self.get_user_email_addresses()
        if users:
            for user in users[:10]:  # Show first 10 users
                logger.info(f"   {user['username']} ({user['email']}) - Last login: {user['last_login']}")
            if len(users) > 10:
                logger.info(f"   ... and {len(users) - 10} more users")
        else:
            logger.info("   No active users found")
        
        # Recommendations
        logger.info("\nRecommendations:")
        if not test_success:
            logger.info("   • Fix email configuration issues")
        if self.stats['failed_sends'] > 0:
            logger.info("   • Check recent error logs for specific issues")
        if not users:
            logger.info("   • Add active users to the system")
        if self.stats['total_attempts'] == 0:
            logger.info("   • Run a test reminder to verify email system")
    
    def monitor_real_time(self):
        """Monitor email system in real-time"""
        logger.info("Starting real-time email monitoring...")
        logger.info("   Press Ctrl+C to stop")
        
        import time
        import subprocess
        
        try:
            while True:
                # Clear screen (optional)
                os.system('cls' if os.name == 'nt' else 'clear')
                
                # Generate fresh report
                self.generate_report()
                
                logger.info(f"\nLast updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info("   Refreshing in 30 seconds...")
                
                time.sleep(30)
                
        except KeyboardInterrupt:
            logger.info("\nReal-time monitoring stopped")
    
    def send_test_email(self, recipient=None):
        """Send a test email"""
        if not recipient:
            recipient = os.getenv('EMAIL_FROM')
        
        logger.info(f"Sending test email to {recipient}...")
        
        try:
            from notification_services import send_email_internal
            
            result = send_email_internal(
                recipient=recipient,
                subject="Quiz Master 2 - Test Email",
                body=f"""
Hello!

This is a test email from Quiz Master 2 Email Monitoring System.

Test Details:
- Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Recipient: {recipient}
- System: Email Monitoring Dashboard

If you receive this email, your email configuration is working correctly!

Best regards,
Quiz Master 2 Team
                """.strip()
            )
            
            logger.info("Test email sent successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Test email failed: {e}")
            return False

def main():
    """Main entry point"""
    monitor = EmailMonitor()
    
    if len(sys.argv) < 2:
        command = "report"
    else:
        command = sys.argv[1]
    
    if command == "report":
        monitor.generate_report()
    elif command == "monitor":
        monitor.monitor_real_time()
    elif command == "test":
        recipient = sys.argv[2] if len(sys.argv) > 2 else None
        monitor.send_test_email(recipient)
    elif command == "config":
        config_status = monitor.check_email_configuration()
        logger.info("Email Configuration Status:")
        for var, status in config_status.items():
            logger.info(f"   {var}: {status['value'] if status['configured'] else 'Not set'}")
    else:
        logger.info("Available commands:")
        logger.info("  report  - Generate email monitoring report (default)")
        logger.info("  monitor - Start real-time monitoring")
        logger.info("  test    - Send test email")
        logger.info("  config  - Show configuration status")

if __name__ == "__main__":
    main()