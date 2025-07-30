#!/usr/bin/env python3
"""
Configure single notification method for the entire project
"""

import os
from datetime import datetime

def show_notification_options():
    """Show available notification methods"""
    print("="*60)
    print("NOTIFICATION METHOD CONFIGURATION")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\nChoose ONE notification method for the entire project:")
    print("1. Email (SMTP) - Send reminders via email")
    print("2. SMS (Twilio) - Send reminders via SMS")
    print("3. Google Chat - Send reminders via Google Chat webhook")
    
    print("\nCurrent configuration:")
    current_method = os.getenv('NOTIFICATION_METHOD', 'email')
    print(f"   Method: {current_method.upper()}")

def configure_email():
    """Configure email notifications"""
    print("\n" + "="*60)
    print("EMAIL CONFIGURATION")
    print("="*60)
    
    env_content = """# Email Configuration (SMTP)
NOTIFICATION_METHOD=email
EMAIL_FROM=your-email@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Database Configuration
DATABASE_URL=sqlite:///instance/quiz.db

# Rate Limits
EMAIL_RATE_LIMIT=10/m
SMS_RATE_LIMIT=5/m
"""
    
    with open('.env.email', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env.email template")
    print("\nGmail Setup Instructions:")
    print("1. Go to your Google Account settings")
    print("2. Enable 2-Factor Authentication")
    print("3. Generate an App Password:")
    print("   - Go to Security > 2-Step Verification")
    print("   - Click 'App passwords'")
    print("   - Generate a new app password for 'Mail'")
    print("4. Copy .env.email to .env and fill in your credentials")

def configure_sms():
    """Configure SMS notifications"""
    print("\n" + "="*60)
    print("SMS CONFIGURATION")
    print("="*60)
    
    env_content = """# SMS Configuration (Twilio)
NOTIFICATION_METHOD=sms
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Database Configuration
DATABASE_URL=sqlite:///instance/quiz.db

# Rate Limits
EMAIL_RATE_LIMIT=10/m
SMS_RATE_LIMIT=5/m
"""
    
    with open('.env.sms', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env.sms template")
    print("\nTwilio Setup Instructions:")
    print("1. Sign up for a free Twilio account at https://www.twilio.com")
    print("2. Get your Account SID and Auth Token from the Twilio Console")
    print("3. Get a Twilio phone number (free trial includes one)")
    print("4. Copy .env.sms to .env and fill in your credentials")

def configure_gchat():
    """Configure Google Chat notifications"""
    print("\n" + "="*60)
    print("GOOGLE CHAT CONFIGURATION")
    print("="*60)
    
    env_content = """# Google Chat Configuration
NOTIFICATION_METHOD=gchat
GCHAT_WEBHOOK_URL=https://chat.googleapis.com/v1/spaces/your-space-id/messages

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Database Configuration
DATABASE_URL=sqlite:///instance/quiz.db

# Rate Limits
EMAIL_RATE_LIMIT=10/m
SMS_RATE_LIMIT=5/m
"""
    
    with open('.env.gchat', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env.gchat template")
    print("\nGoogle Chat Setup Instructions:")
    print("1. Go to your Google Chat space")
    print("2. Click on the space name > Manage webhooks")
    print("3. Create a new webhook")
    print("4. Copy the webhook URL")
    print("5. Copy .env.gchat to .env and fill in your webhook URL")

def test_configuration():
    """Test the current configuration"""
    print("\n" + "="*60)
    print("TESTING CONFIGURATION")
    print("="*60)
    
    try:
        from notification_config import get_notification_method, validate_configuration, get_notification_info
        
        method = get_notification_method()
        info = get_notification_info()
        
        print(f"✅ Notification method: {method.upper()}")
        print(f"✅ Required variables: {len(info['required_vars'])}")
        print(f"✅ Configured variables: {len(info['configured_vars'])}")
        
        if validate_configuration():
            print("✅ Configuration is valid!")
            return True
        else:
            print("❌ Configuration is incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Error testing configuration: {str(e)}")
        return False

def main():
    """Main configuration function"""
    show_notification_options()
    
    while True:
        print("\nChoose an option:")
        print("1. Configure Email notifications")
        print("2. Configure SMS notifications") 
        print("3. Configure Google Chat notifications")
        print("4. Test current configuration")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            configure_email()
        elif choice == '2':
            configure_sms()
        elif choice == '3':
            configure_gchat()
        elif choice == '4':
            test_configuration()
        elif choice == '5':
            print("\nConfiguration complete!")
            break
        else:
            print("Invalid choice. Please enter 1-5.")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("1. Copy the appropriate .env file to .env")
    print("2. Fill in your real credentials in .env")
    print("3. Test the configuration")
    print("4. Start your application")
    print("\nNote: The entire project will now use only the configured notification method!")

if __name__ == "__main__":
    main() 