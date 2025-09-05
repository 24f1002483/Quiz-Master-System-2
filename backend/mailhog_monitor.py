#!/usr/bin/env python3
"""
MailHog Email Monitor
Tool to check emails captured by MailHog during development
"""

import requests
import json
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

class MailHogMonitor:
    def __init__(self, mailhog_host='localhost', mailhog_api_port=8025):
        self.mailhog_host = mailhog_host
        self.mailhog_api_port = mailhog_api_port
        self.api_base = f"http://{mailhog_host}:{mailhog_api_port}/api"
    
    def check_connection(self):
        """Check if MailHog is running and accessible"""
        try:
            response = requests.get(f"{self.api_base}/v1/messages", timeout=5)
            return response.status_code == 200
        except Exception as e:
            return False
    
    def get_messages(self, limit=50):
        """Get messages from MailHog"""
        try:
            response = requests.get(f"{self.api_base}/v1/messages?limit={limit}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Error getting messages: {e}")
            return None
    
    def get_message_details(self, message_id):
        """Get detailed message content"""
        try:
            response = requests.get(f"{self.api_base}/v1/messages/{message_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Error getting message details: {e}")
            return None
    
    def delete_all_messages(self):
        """Delete all messages from MailHog"""
        try:
            response = requests.delete(f"{self.api_base}/v1/messages")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error deleting messages: {e}")
            return False
    
    def show_status(self):
        """Show MailHog status and recent emails"""
        print("📧 MailHog Email Monitor")
        print("=" * 40)
        
        # Check connection
        if not self.check_connection():
            print("❌ MailHog is not accessible")
            print(f"   Make sure MailHog is running on {self.mailhog_host}:{self.mailhog_api_port}")
            print("   Start MailHog with: mailhog")
            return False
        
        print("✅ MailHog is running")
        print(f"   Web UI: http://{self.mailhog_host}:{self.mailhog_api_port}")
        print(f"   SMTP: {self.mailhog_host}:1025")
        
        # Get messages
        data = self.get_messages()
        if not data:
            print("\n📭 No messages found")
            return True
        
        messages = data.get('messages', [])
        total = data.get('total', 0)
        
        print(f"\n📬 Found {total} messages")
        
        if messages:
            print("\n📋 Recent Messages:")
            for i, msg in enumerate(messages[:10]):  # Show last 10
                created = datetime.fromisoformat(msg['Created'].replace('Z', '+00:00'))
                from_addr = msg['From']['Mailbox'] + '@' + msg['From']['Domain']
                to_addrs = [f"{to['Mailbox']}@{to['Domain']}" for to in msg['To']]
                
                print(f"\n   {i+1}. {msg['Content']['Headers']['Subject'][0]}")
                print(f"      From: {from_addr}")
                print(f"      To: {', '.join(to_addrs)}")
                print(f"      Time: {created.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
    
    def show_quiz_master_emails(self):
        """Show only Quiz Master related emails"""
        print("📚 Quiz Master Emails")
        print("=" * 30)
        
        if not self.check_connection():
            print("❌ MailHog is not accessible")
            return False
        
        data = self.get_messages()
        if not data:
            print("📭 No messages found")
            return True
        
        messages = data.get('messages', [])
        quiz_messages = []
        
        for msg in messages:
            subject = msg['Content']['Headers'].get('Subject', [''])[0]
            if 'Quiz Master' in subject or 'quiz' in subject.lower():
                quiz_messages.append(msg)
        
        if not quiz_messages:
            print("📭 No Quiz Master emails found")
            return True
        
        print(f"📬 Found {len(quiz_messages)} Quiz Master emails")
        
        for i, msg in enumerate(quiz_messages):
            created = datetime.fromisoformat(msg['Created'].replace('Z', '+00:00'))
            from_addr = msg['From']['Mailbox'] + '@' + msg['From']['Domain']
            to_addrs = [f"{to['Mailbox']}@{to['Domain']}" for to in msg['To']]
            subject = msg['Content']['Headers']['Subject'][0]
            
            print(f"\n   {i+1}. {subject}")
            print(f"      From: {from_addr}")
            print(f"      To: {', '.join(to_addrs)}")
            print(f"      Time: {created.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Show preview of body
            body = msg['Content']['Body']
            if len(body) > 100:
                body_preview = body[:100] + "..."
            else:
                body_preview = body
            print(f"      Preview: {body_preview.replace(chr(10), ' ').replace(chr(13), ' ')}")
        
        return True
    
    def test_email_sending(self):
        """Test email sending to MailHog"""
        print("🧪 Testing Email Sending to MailHog")
        print("=" * 40)
        
        # Load environment
        load_dotenv()
        
        # Check MailHog connection
        if not self.check_connection():
            print("❌ MailHog is not accessible")
            return False
        
        # Get message count before
        data_before = self.get_messages(limit=1)
        count_before = data_before.get('total', 0) if data_before else 0
        
        print(f"📊 Messages before test: {count_before}")
        
        # Send test email
        try:
            from notification_services import send_email_internal
            
            result = send_email_internal(
                recipient="test@quizmaster.local",
                subject="MailHog Test - Quiz Master 2",
                body=f"""
Hello!

This is a test email from Quiz Master 2 to verify MailHog integration.

Test Details:
- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- SMTP Host: {os.getenv('SMTP_HOST')}
- SMTP Port: {os.getenv('SMTP_PORT')}
- From: {os.getenv('EMAIL_FROM')}

If you see this in MailHog, the email system is working correctly!

Best regards,
Quiz Master 2 Team
                """.strip()
            )
            
            print("✅ Test email sent successfully!")
            
            # Wait a moment and check for new messages
            import time
            time.sleep(1)
            
            data_after = self.get_messages(limit=1)
            count_after = data_after.get('total', 0) if data_after else 0
            
            print(f"📊 Messages after test: {count_after}")
            
            if count_after > count_before:
                print("✅ Email successfully captured by MailHog!")
                print(f"   Check MailHog web UI: http://{self.mailhog_host}:{self.mailhog_api_port}")
            else:
                print("⚠️  Email sent but not found in MailHog yet")
            
            return True
            
        except Exception as e:
            print(f"❌ Test email failed: {e}")
            return False
    
    def clear_mailbox(self):
        """Clear all messages from MailHog"""
        print("🗑️  Clearing MailHog Mailbox")
        print("=" * 30)
        
        if not self.check_connection():
            print("❌ MailHog is not accessible")
            return False
        
        # Get current count
        data = self.get_messages(limit=1)
        count = data.get('total', 0) if data else 0
        
        if count == 0:
            print("📭 Mailbox is already empty")
            return True
        
        print(f"📊 Found {count} messages")
        
        # Confirm deletion
        if len(sys.argv) > 2 and sys.argv[2] == "--confirm":
            if self.delete_all_messages():
                print("✅ All messages deleted successfully")
                return True
            else:
                print("❌ Failed to delete messages")
                return False
        else:
            print("⚠️  To actually delete messages, run:")
            print("   python mailhog_monitor.py clear --confirm")
            return True

def main():
    """Main entry point"""
    # Default MailHog configuration
    mailhog_host = os.getenv('MAILHOG_HOST', 'localhost')
    mailhog_port = int(os.getenv('MAILHOG_API_PORT', 8025))
    
    monitor = MailHogMonitor(mailhog_host, mailhog_port)
    
    if len(sys.argv) < 2:
        command = "status"
    else:
        command = sys.argv[1]
    
    if command == "status":
        monitor.show_status()
    elif command == "quiz":
        monitor.show_quiz_master_emails()
    elif command == "test":
        monitor.test_email_sending()
    elif command == "clear":
        monitor.clear_mailbox()
    else:
        print("📋 MailHog Monitor Commands:")
        print("  status - Show MailHog status and recent emails")
        print("  quiz   - Show only Quiz Master related emails")
        print("  test   - Send test email to MailHog")
        print("  clear  - Clear all messages from MailHog")
        print("")
        print("💡 Make sure MailHog is running:")
        print("   mailhog")
        print("")
        print("🌐 MailHog Web UI:")
        print(f"   http://{mailhog_host}:{mailhog_port}")

if __name__ == "__main__":
    main()