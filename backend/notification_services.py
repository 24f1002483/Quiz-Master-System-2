import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import requests
import os
from twilio.rest import Client
from celery import Celery
from config import Config
from models.model import User  # updated import
# Removed: from celery import current_app  # Correct spelling
celery = Celery(broker=Config.CELERY_BROKER_URL)

@celery.task(bind=True, rate_limit=Config.EMAIL_RATE_LIMIT)
def send_email(self, recipient, subject, body, attachment=None, attachment_name=None):
    """Send email with optional attachment"""
    try:
        msg = MIMEMultipart()
        msg['From'] = os.getenv('EMAIL_FROM', 'noreply@quizapp.com')
        msg['To'] = recipient
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        if attachment:
            part = MIMEApplication(attachment, Name=attachment_name)
            part['Content-Disposition'] = f'attachment; filename="{attachment_name}"'
            msg.attach(part)
        
        with smtplib.SMTP(
            os.getenv('SMTP_HOST', 'smtp.gmail.com'),
            int(os.getenv('SMTP_PORT', 587))
        ) as server:
            server.starttls()
            server.login(
                os.getenv('SMTP_USERNAME', ''),
                os.getenv('SMTP_PASSWORD', '')
            )
            server.send_message(msg)
        
        return f"Email sent to {recipient}"
    except Exception as e:
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery.task(bind=True, rate_limit=Config.SMS_RATE_LIMIT)
def send_sms(self, phone_number, message):
    """Send SMS using Twilio"""
    try:
        client = Client(
            os.getenv('TWILIO_ACCOUNT_SID', ''),
            os.getenv('TWILIO_AUTH_TOKEN', '')
        )
        
        message = client.messages.create(
            body=message,
            from_=os.getenv('TWILIO_PHONE_NUMBER', ''),
            to=phone_number
        )
        
        return f"SMS sent to {phone_number}, SID: {message.sid}"
    except Exception as e:
        raise self.retry(exc=e, countdown=60, max_retries=3)

@celery.task(bind=True)  # Fixed: Using celery.task instead of current_app.task
def send_gchat_message(self, user_id, message):
    """
    Send message to Google Chat webhook
    
    Args:
        user_id: ID of the user to send to
        message: Text message to send
        
    Returns:
        str: Status message
    """
    try:
        user = User.query.get(user_id)
        if not user or not user.gchat_webhook_url:
            return f"No Google Chat webhook for user {user_id}"
            
        response = requests.post(
            user.gchat_webhook_url,
            json={"text": message},
            timeout=10
        )
        response.raise_for_status()
        return f"Google Chat message sent to user {user_id}"
        
    except Exception as e:
        # Using self.retry for Celery task retry mechanism
        raise self.retry(exc=e, countdown=60, max_retries=3)