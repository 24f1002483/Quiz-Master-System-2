#!/usr/bin/env python3
"""
Enhanced Daily Reminders System
Implements smart daily reminders with user inactivity detection and new quiz alerts
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy import func, and_, or_
from models.model import User, Quiz, UserQuizAttempt, Subject, Chapter, Role
from notification_services import send_email_internal
import logging

logger = logging.getLogger(__name__)

def check_user_inactivity(user, days_threshold=7):
    """Check if user has been inactive for specified days"""
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_threshold)
    
    # Check last login
    if user.last_login and user.last_login < cutoff_date:
        return True
    
    # Check last quiz attempt
    last_attempt = UserQuizAttempt.query.filter_by(
        user_id=user.id, 
        status='completed'
    ).order_by(UserQuizAttempt.end_time.desc()).first()
    
    if not last_attempt or last_attempt.end_time < cutoff_date:
        return True
    
    return False

def get_new_quizzes_since_last_visit(user, days_threshold=7):
    """Get quizzes created since user's last visit"""
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_threshold)
    
    # Get user's last activity
    last_activity = user.last_login
    if not last_activity:
        last_activity = cutoff_date
    
    # Find new quizzes created after user's last activity
    new_quizzes = Quiz.query.filter(
        and_(
            Quiz.created_at > last_activity,
            Quiz.is_active == True,
            Quiz.start_date > datetime.now(timezone.utc)  # Only future quizzes
        )
    ).all()
    
    return new_quizzes

def get_upcoming_quizzes_for_user(user, days_ahead=7):
    """Get upcoming quizzes relevant to the user"""
    end_date = datetime.now(timezone.utc) + timedelta(days=days_ahead)
    
    upcoming_quizzes = Quiz.query.filter(
        and_(
            Quiz.start_date >= datetime.now(timezone.utc),
            Quiz.start_date <= end_date,
            Quiz.is_active == True
        )
    ).all()
    
    return upcoming_quizzes

def should_send_reminder(user):
    """Determine if reminder should be sent to user"""
    # Check if user is inactive
    is_inactive = check_user_inactivity(user)
    
    # Check for new quizzes
    new_quizzes = get_new_quizzes_since_last_visit(user)
    
    # Check for upcoming quizzes
    upcoming_quizzes = get_upcoming_quizzes_for_user(user)
    
    # Send reminder if any condition is met
    return is_inactive or new_quizzes or upcoming_quizzes

def generate_reminder_message(user, new_quizzes, upcoming_quizzes):
    """Generate personalized reminder message"""
    message = f"Quiz Master 2 - Daily Reminder\n\n"
    message += f"Hello {user.full_name or user.username},\n\n"
    
    # Inactivity alert
    if check_user_inactivity(user):
        message += "You haven't been active recently. Don't miss out on learning opportunities!\n\n"
    
    # New quizzes alert
    if new_quizzes:
        message += "New Quizzes Available:\n"
        for quiz in new_quizzes:
            subject = quiz.chapter.subject.name
            chapter = quiz.chapter.name
            start_time = quiz.start_date.strftime("%b %d, %Y at %H:%M")
            message += f"  • {quiz.title} ({subject} - {chapter})\n"
            message += f"    Starts: {start_time}, Duration: {quiz.time_duration} mins\n\n"
    
    # Upcoming quizzes alert
    if upcoming_quizzes:
        message += "Upcoming Quizzes:\n"
        for quiz in upcoming_quizzes:
            subject = quiz.chapter.subject.name
            chapter = quiz.chapter.name
            start_time = quiz.start_date.strftime("%b %d, %Y at %H:%M")
            message += f"  • {quiz.title} ({subject} - {chapter})\n"
            message += f"    Starts: {start_time}, Duration: {quiz.time_duration} mins\n\n"
    
    # Call to action
    message += "Ready to test your knowledge? Log in now and take a quiz!\n\n"
    message += "Best regards,\nQuiz Master 2 Team"
    
    return message

def send_reminder_to_user(user, message):
    """Send reminder using user's preferred notification method"""
    try:
        # Get user email - use email field if available, otherwise use username
        user_email = getattr(user, 'email', None) or user.username
        
        # Check if user has notification preference, default to email
        notification_pref = getattr(user, 'notification_preference', 'email')
        
        if notification_pref == 'email' or not hasattr(user, 'notification_preference'):
            # Send email
            send_email_internal(
                recipient=user_email,
                subject="Quiz Master 2 - Daily Reminder",
                body=message
            )
            logger.info(f"Email reminder sent to {user.username} ({user_email})")
            
        elif notification_pref == 'sms' and hasattr(user, 'phone') and user.phone:
            # Send SMS (placeholder for SMS integration)
            logger.info(f"SMS reminder would be sent to {user.phone}")
            # TODO: Implement SMS sending
            # For now, fallback to email
            send_email_internal(
                recipient=user_email,
                subject="Quiz Master 2 - Daily Reminder",
                body=message
            )
            logger.info(f"Fallback email reminder sent to {user.username} ({user_email})")
            
        elif notification_pref == 'gchat':
            # Send Google Chat message (placeholder for webhook integration)
            logger.info(f"Google Chat reminder would be sent to {user.username}")
            # TODO: Implement Google Chat webhook
            # For now, fallback to email
            send_email_internal(
                recipient=user_email,
                subject="Quiz Master 2 - Daily Reminder",
                body=message
            )
            logger.info(f"Fallback email reminder sent to {user.username} ({user_email})")
            
        else:
            # Fallback to email
            send_email_internal(
                recipient=user_email,
                subject="Quiz Master 2 - Daily Reminder",
                body=message
            )
            logger.info(f"Fallback email reminder sent to {user.username} ({user_email})")
            
        return True
        
    except Exception as e:
        logger.error(f"Failed to send reminder to {user.username}: {e}")
        import traceback
        logger.error(f"Error details: {traceback.format_exc()}")
        return False

def enhanced_daily_reminders_task():
    """Enhanced daily reminders task with smart logic"""
    try:
        logger.info("Starting enhanced daily reminders task")
        
        # Get all active users
        users = User.query.filter_by(is_active=True, role=Role.USER).all()
        
        successful_reminders = 0
        failed_reminders = 0
        skipped_users = 0
        
        for user in users:
            try:
                # Check if reminder should be sent
                if not should_send_reminder(user):
                    skipped_users += 1
                    continue
                
                # Get relevant quizzes
                new_quizzes = get_new_quizzes_since_last_visit(user)
                upcoming_quizzes = get_upcoming_quizzes_for_user(user)
                
                # Generate personalized message
                message = generate_reminder_message(user, new_quizzes, upcoming_quizzes)
                
                # Send reminder
                if send_reminder_to_user(user, message):
                    successful_reminders += 1
                else:
                    failed_reminders += 1
                    
            except Exception as e:
                logger.error(f"Error processing reminder for user {user.id}: {e}")
                failed_reminders += 1
        
        result = f"Enhanced daily reminders completed: {successful_reminders} sent, {failed_reminders} failed, {skipped_users} skipped"
        logger.info(result)
        return result
        
    except Exception as e:
        logger.error(f"Error in enhanced daily reminders task: {e}")
        raise

if __name__ == "__main__":
    # Set up Flask app context
    from app import create_app
    from models.model import db
    
    app = create_app()
    with app.app_context():
        # Test the enhanced reminders
        enhanced_daily_reminders_task() 
        