#!/usr/bin/env python3
"""
Email Notification Configuration - Email-only notification system
"""

import os

# Email notification method (fixed)
NOTIFICATION_METHOD = 'email'

def get_notification_method():
    """Get the configured notification method"""
    return NOTIFICATION_METHOD

def is_email_enabled():
    """Check if email notifications are enabled"""
    return True

def get_required_env_vars():
    """Get required environment variables for email notifications"""
    return [
        'EMAIL_FROM',
        'SMTP_HOST', 
        'SMTP_PORT',
        'SMTP_USERNAME',
        'SMTP_PASSWORD'
    ]

def validate_configuration():
    """Validate that all required environment variables are set"""
    required_vars = get_required_env_vars()
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing configuration for EMAIL notifications:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print(f"✅ EMAIL notification configuration is complete")
    return True

def get_notification_info():
    """Get information about the current notification configuration"""
    info = {
        'method': NOTIFICATION_METHOD,
        'enabled': True,
        'required_vars': get_required_env_vars(),
        'configured_vars': []
    }
    
    for var in info['required_vars']:
        value = os.getenv(var)
        if value:
            info['configured_vars'].append(var)
    
    return info 