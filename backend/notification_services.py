import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import logging
from datetime import datetime
from celery import Celery
from config import Config
from models.model import User
from notification_config import validate_configuration

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('notification_logs.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

celery = Celery(broker=Config.broker_url)

def send_notification(recipient, subject, message, **kwargs):
    """
    Send email notification
    This is the main function that should be used throughout the project
    """
    try:
        return send_email_internal(recipient, subject, message)
    except Exception as e:
        logger.error(f"Failed to send email notification: {str(e)}")
        return f"Failed to send email notification: {str(e)}"

def send_email_internal(recipient, subject, body, attachment=None, attachment_name=None):
    """Internal email sending function"""
    try:
        # Get email configuration
        email_from = os.getenv('EMAIL_FROM')
        smtp_host = os.getenv('SMTP_HOST')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        # For MailHog and development servers, username/password might be empty
        if not email_from or not smtp_host:
            logger.error("Missing required email configuration (EMAIL_FROM, SMTP_HOST)")
            return "Missing required email configuration"
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(body, 'plain'))
        
        # Add attachment if provided
        if attachment and attachment_name:
            part = MIMEApplication(attachment, Name=attachment_name)
            part['Content-Disposition'] = f'attachment; filename="{attachment_name}"'
            msg.attach(part)
        
        # Handle different SMTP configurations
        if smtp_port == 465:
            # Use SSL connection (Gmail, etc.)
            import ssl
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context, timeout=15) as server:
                if smtp_username and smtp_password:
                    server.login(smtp_username, smtp_password)
                server.send_message(msg)
        elif smtp_port == 1025:
            # MailHog or similar development SMTP (no authentication)
            with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                # MailHog doesn't require authentication
                server.send_message(msg)
        else:
            # Standard SMTP with STARTTLS (port 587, etc.)
            with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                server.starttls()
                if smtp_username and smtp_password:
                    server.login(smtp_username, smtp_password)
                server.send_message(msg)
        
        logger.info(f"Email sent successfully to {recipient} via {smtp_host}:{smtp_port}")
        return f"Email sent successfully to {recipient}"
        
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {str(e)}")
        raise e

# Celery task for email notifications
@celery.task(bind=True, rate_limit=Config.EMAIL_RATE_LIMIT)
def send_email(self, recipient, subject, body, attachment=None, attachment_name=None):
    """Send email notification"""
    try:
        return send_email_internal(recipient, subject, body, attachment=attachment, attachment_name=attachment_name)
    except Exception as e:
        raise self.retry(exc=e, countdown=60, max_retries=3)
