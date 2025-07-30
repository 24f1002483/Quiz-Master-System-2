from celery import Celery
from flask import Flask
from datetime import datetime, timedelta
from models.model import db, User, Quiz, UserQuizAttempt, Role
from notification_services import send_email
import pandas as pd
import io
import logging
from celery.signals import task_success, task_failure, task_revoked
from celery.utils.log import get_task_logger

# Setup logging
logger = get_task_logger(__name__)

def create_celery_app(app=None):
    if app is None:
        # Import here to avoid circular import
        from app import create_app
        app = create_app()
    
    # Import config directly to ensure we have the Celery settings
    from config import Config
    
    celery = Celery(
        app.import_name,
        broker=Config.broker_url,
        backend=Config.result_backend
    )
    
    # Update with Flask app config first
    celery.conf.update(app.config)
    
    # Then update with Celery-specific config from Config class
    celery_config = {}
    for key, value in Config.__dict__.items():
        if not key.startswith('_'):
            celery_config[key] = value
    
    celery.conf.update(celery_config)
    
    # Enhanced Celery configuration
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=30 * 60,  # 30 minutes
        task_soft_time_limit=25 * 60,  # 25 minutes
        worker_prefetch_multiplier=4,
        worker_max_tasks_per_child=1000,
        worker_disable_rate_limits=False,
        task_acks_late=True,
        worker_lost_wait=30,
        result_expires=3600,  # 1 hour
        result_persistent=True,
        task_ignore_result=False,
        task_store_errors_even_if_ignored=True,
        task_always_eager=False,
        task_eager_propagates=True,
        task_compression='gzip',
        task_routes={
            'celery_app.send_daily_reminders': {'queue': 'reminders'},
            'celery_app.generate_monthly_reports': {'queue': 'reports'},
            'notification_services.send_email': {'queue': 'notifications'},
        },
        task_default_queue='default',
        task_default_exchange='default',
        task_default_routing_key='default',
    )
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
        
        def on_failure(self, exc, task_id, args, kwargs, einfo):
            logger.error(f"Task {task_id} failed: {exc}")
            super().on_failure(exc, task_id, args, kwargs, einfo)
        
        def on_retry(self, exc, task_id, args, kwargs, einfo):
            logger.warning(f"Task {task_id} retrying: {exc}")
            super().on_retry(exc, task_id, args, kwargs, einfo)
    
    celery.Task = ContextTask
    return celery

celery = create_celery_app()

# Task monitoring signals
@task_success.connect
def task_success_handler(sender=None, **kwargs):
    logger.info(f"Task {sender} completed successfully")

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, **kwargs):
    logger.error(f"Task {sender} (ID: {task_id}) failed: {exception}")

@task_revoked.connect
def task_revoked_handler(sender=None, request=None, terminated=None, signum=None, expired=None, **kwargs):
    logger.warning(f"Task {sender} was revoked. Terminated: {terminated}, Expired: {expired}")

@celery.task(bind=True, max_retries=3, default_retry_delay=300)
def send_daily_reminders(self):
    """Send daily quiz reminders to users with enhanced error handling"""
    try:
        logger.info("Starting daily reminders task")
        
        # Get quizzes starting in the next 24 hours
        now = datetime.utcnow()
        tomorrow = now + timedelta(days=1)
        
        upcoming_quizzes = Quiz.query.filter(
            Quiz.start_date >= now,
            Quiz.start_date <= tomorrow,
            Quiz.is_active == True
        ).all()
        
        if not upcoming_quizzes:
            logger.info("No upcoming quizzes for daily reminders")
            return "No upcoming quizzes for daily reminders"
        
        # Group quizzes by subject/chapter
        quiz_groups = {}
        for quiz in upcoming_quizzes:
            key = f"{quiz.chapter.subject.name} - {quiz.chapter.name}"
            if key not in quiz_groups:
                quiz_groups[key] = []
            quiz_groups[key].append(quiz)
        
        # Get all active users
        users = User.query.filter_by(is_active=True).all()
        
        successful_notifications = 0
        failed_notifications = 0
        
        for user in users:
            try:
                # Prepare reminder message
                message = "📚 Daily Quiz Reminder:\n\n"
                message += f"Hello {user.username},\n\n"
                message += "You have upcoming quizzes:\n\n"
                
                for group, quizzes in quiz_groups.items():
                    message += f"👉 {group}:\n"
                    for quiz in quizzes:
                        start_time = quiz.start_date.strftime("%b %d, %Y at %H:%M UTC")
                        message += f"  - {quiz.title} (Starts: {start_time}, Duration: {quiz.time_duration} mins)\n"
                
                message += "\nGood luck with your preparations!"
                
                # Send notification using configured method
                # Send email notification
                send_email.delay(
                    recipient=user.email or user.username,
                    subject="Daily Quiz Reminder",
                    body=message
                )
                
                successful_notifications += 1
                
            except Exception as e:
                logger.error(f"Failed to send reminder to user {user.id}: {e}")
                failed_notifications += 1
        
        result = f"Sent daily reminders: {successful_notifications} successful, {failed_notifications} failed"
        logger.info(result)
        return result
        
    except Exception as e:
        logger.error(f"Error in daily reminders task: {str(e)}")
        raise self.retry(exc=e, countdown=600, max_retries=3)

@celery.task(bind=True, max_retries=3, default_retry_delay=600)
def generate_monthly_reports(self):
    """Generate and send monthly performance reports with enhanced error handling"""
    try:
        logger.info("Starting monthly reports generation")
        
        # Calculate date range (previous month)
        today = datetime.utcnow()
        first_day_of_month = today.replace(day=1)
        last_month_end = first_day_of_month - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        
        # Get all active users
        users = User.query.filter_by(is_active=True).all()
        
        successful_reports = 0
        failed_reports = 0
        
        for user in users:
            try:
                # Get user's quiz attempts from last month
                attempts = UserQuizAttempt.query.filter(
                    UserQuizAttempt.user_id == user.id,
                    UserQuizAttempt.end_time >= last_month_start,
                    UserQuizAttempt.end_time <= last_month_end,
                    UserQuizAttempt.status == 'completed'
                ).all()
                
                if not attempts:
                    logger.info(f"No activity for user {user.id} in {last_month_start.strftime('%B %Y')}")
                    continue  # Skip users with no activity
                
                # Prepare report data
                report_data = {
                    "Total Quizzes Attempted": len(attempts),
                    "Total Questions Answered": sum(a.total_questions for a in attempts),
                    "Correct Answers": sum(a.score for a in attempts),
                    "Overall Accuracy": f"{round((sum(a.score for a in attempts) / sum(a.total_questions for a in attempts)) * 100, 2)}%",
                    "Average Time per Quiz": f"{round(sum(a.time_taken for a in attempts) / len(attempts) / 60, 2)} mins",
                    "Quizzes by Subject": {}
                }
                
                # Group by subject
                subject_stats = {}
                for attempt in attempts:
                    subject = attempt.quiz.chapter.subject.name
                    if subject not in subject_stats:
                        subject_stats[subject] = {
                            "count": 0,
                            "total_questions": 0,
                            "correct_answers": 0
                        }
                    subject_stats[subject]["count"] += 1
                    subject_stats[subject]["total_questions"] += attempt.total_questions
                    subject_stats[subject]["correct_answers"] += attempt.score
                
                # Calculate subject-wise stats
                for subject, stats in subject_stats.items():
                    report_data["Quizzes by Subject"][subject] = {
                        "Quizzes Attempted": stats["count"],
                        "Accuracy": f"{round((stats['correct_answers'] / stats['total_questions']) * 100, 2)}%",
                        "Average Score": f"{round(stats['correct_answers'] / stats['count'], 2)}/{round(stats['total_questions'] / stats['count'], 2)}"
                    }
                
                # Generate PDF report
                pdf_buffer = generate_pdf_report(user, report_data, last_month_start, last_month_end)
                
                # Email the report
                send_email.delay(
                    recipient=user.username,
                    subject=f"Monthly Performance Report - {last_month_start.strftime('%B %Y')}",
                    body="Please find attached your monthly performance report.",
                    attachment=pdf_buffer.getvalue(),
                    attachment_name=f"quiz_report_{user.username}_{last_month_start.strftime('%Y_%m')}.pdf"
                )
                
                successful_reports += 1
                logger.info(f"Generated report for user {user.id}")
                
            except Exception as e:
                logger.error(f"Failed to generate report for user {user.id}: {e}")
                failed_reports += 1
        
        result = f"Generated monthly reports: {successful_reports} successful, {failed_reports} failed"
        logger.info(result)
        return result
        
    except Exception as e:
        logger.error(f"Error in monthly reports task: {str(e)}")
        raise self.retry(exc=e, countdown=1200, max_retries=3)

@celery.task(bind=True)
def cleanup_old_data(self):
    """Clean up old task results and temporary data"""
    try:
        from monitoring import cleanup_old_task_results
        cleaned_count = cleanup_old_task_results(days=7)
        logger.info(f"Cleaned up {cleaned_count} old task results")
        return f"Cleaned up {cleaned_count} old task results"
    except Exception as e:
        logger.error(f"Error in cleanup task: {str(e)}")
        raise self.retry(exc=e, countdown=300, max_retries=2)

@celery.task(bind=True)
def export_quiz_history_csv(self, user_id, export_format='csv'):
    """Export user's quiz history to CSV format"""
    try:
        from models.model import User, UserQuizAttempt, Quiz, Chapter, Subject
        
        # Get user
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}
        
        # Get all quiz attempts for the user
        attempts = UserQuizAttempt.query.filter_by(user_id=user_id).order_by(UserQuizAttempt.start_time.desc()).all()
        
        if not attempts:
            return {"error": "No quiz history found for this user"}
        
        # Prepare data for export
        export_data = []
        for attempt in attempts:
            quiz = attempt.quiz
            chapter = quiz.chapter
            subject = chapter.subject
            
            export_data.append({
                'Quiz Title': quiz.title,
                'Subject': subject.name,
                'Chapter': chapter.name,
                'Start Time': attempt.start_time.strftime('%Y-%m-%d %H:%M:%S') if attempt.start_time else '',
                'End Time': attempt.end_time.strftime('%Y-%m-%d %H:%M:%S') if attempt.end_time else '',
                'Status': attempt.status,
                'Total Questions': attempt.total_questions,
                'Score': attempt.score,
                'Percentage': round((attempt.score / attempt.total_questions * 100), 2) if attempt.total_questions > 0 else 0,
                'Time Taken (minutes)': round(attempt.time_taken / 60, 2) if attempt.time_taken else 0,
                'Duration': f"{quiz.time_duration} minutes"
            })
        
        # Create DataFrame and export
        df = pd.DataFrame(export_data)
        
        if export_format == 'csv':
            # Create CSV buffer
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            
            # Save to file
            filename = f"quiz_history_{user.username}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = f"exports/{filename}"
            
            # Ensure exports directory exists
            import os
            os.makedirs("exports", exist_ok=True)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                f.write(csv_buffer.getvalue())
            
            return {
                "success": True,
                "filename": filename,
                "filepath": filepath,
                "record_count": len(export_data),
                "user": user.username
            }
        
        elif export_format == 'excel':
            # Create Excel file
            filename = f"quiz_history_{user.username}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = f"exports/{filename}"
            
            # Ensure exports directory exists
            import os
            os.makedirs("exports", exist_ok=True)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Quiz History', index=False)
            
            return {
                "success": True,
                "filename": filename,
                "filepath": filepath,
                "record_count": len(export_data),
                "user": user.username
            }
    
    except Exception as e:
        logger.error(f"Export quiz history failed for user {user_id}: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"error": f"Export failed: {str(e)}"}

@celery.task(bind=True)
def export_user_performance_csv(self, admin_id, filters=None, export_format='csv'):
    """Export user performance data for admin analysis"""
    try:
        from models.model import User, UserQuizAttempt, Quiz, Chapter, Subject
        
        # Verify admin
        admin = User.query.get(admin_id)
        if not admin or admin.role != Role.ADMIN:
            return {"error": "Unauthorized access"}
        
        # Build query with filters
        query = db.session.query(
            User.username,
            User.full_name,
            User.qualification,
            User.date_joined,
            Subject.name.label('subject_name'),
            Chapter.name.label('chapter_name'),
            Quiz.title.label('quiz_title'),
            UserQuizAttempt.start_time,
            UserQuizAttempt.end_time,
            UserQuizAttempt.status,
            UserQuizAttempt.total_questions,
            UserQuizAttempt.score,
            UserQuizAttempt.time_taken
        ).join(
            UserQuizAttempt, User.id == UserQuizAttempt.user_id
        ).join(
            Quiz, UserQuizAttempt.quiz_id == Quiz.id
        ).join(
            Chapter, Quiz.chapter_id == Chapter.id
        ).join(
            Subject, Chapter.subject_id == Subject.id
        )
        
        # Apply filters
        if filters:
            if filters.get('date_from'):
                query = query.filter(UserQuizAttempt.start_time >= filters['date_from'])
            if filters.get('date_to'):
                query = query.filter(UserQuizAttempt.start_time <= filters['date_to'])
            if filters.get('subject_id'):
                query = query.filter(Subject.id == filters['subject_id'])
            if filters.get('status'):
                query = query.filter(UserQuizAttempt.status == filters['status'])
        
        # Execute query
        results = query.all()
        
        if not results:
            return {"error": "No data found for the specified filters"}
        
        # Prepare data for export
        export_data = []
        for row in results:
            percentage = round((row.score / row.total_questions * 100), 2) if row.total_questions > 0 else 0
            time_taken_minutes = round(row.time_taken / 60, 2) if row.time_taken else 0
            
            export_data.append({
                'Username': row.username,
                'Full Name': row.full_name,
                'Qualification': row.qualification,
                'Date Joined': row.date_joined.strftime('%Y-%m-%d') if row.date_joined else '',
                'Subject': row.subject_name,
                'Chapter': row.chapter_name,
                'Quiz Title': row.quiz_title,
                'Start Time': row.start_time.strftime('%Y-%m-%d %H:%M:%S') if row.start_time else '',
                'End Time': row.end_time.strftime('%Y-%m-%d %H:%M:%S') if row.end_time else '',
                'Status': row.status,
                'Total Questions': row.total_questions,
                'Score': row.score,
                'Percentage': percentage,
                'Time Taken (minutes)': time_taken_minutes,
                'Performance': 'Excellent' if percentage >= 90 else 'Good' if percentage >= 70 else 'Average' if percentage >= 50 else 'Poor'
            })
        
        # Create DataFrame and export
        df = pd.DataFrame(export_data)
        
        if export_format == 'csv':
            # Create CSV buffer
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            
            # Save to file
            filename = f"user_performance_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = f"exports/{filename}"
            
            # Ensure exports directory exists
            import os
            os.makedirs("exports", exist_ok=True)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                f.write(csv_buffer.getvalue())
            
            return {
                "success": True,
                "filename": filename,
                "filepath": filepath,
                "record_count": len(export_data),
                "admin": admin.username
            }
        
        elif export_format == 'excel':
            # Create Excel file
            filename = f"user_performance_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = f"exports/{filename}"
            
            # Ensure exports directory exists
            import os
            os.makedirs("exports", exist_ok=True)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='User Performance', index=False)
            
            return {
                "success": True,
                "filename": filename,
                "filepath": filepath,
                "record_count": len(export_data),
                "admin": admin.username
            }
    
    except Exception as e:
        return {"error": f"Export failed: {str(e)}"}

@celery.task(bind=True)
def export_quiz_analytics_csv(self, admin_id, quiz_id=None, export_format='csv'):
    """Export detailed quiz analytics for admin analysis"""
    try:
        from models.model import User, UserQuizAttempt, Quiz, Chapter, Subject, Question, UserAnswer
        
        # Verify admin
        admin = User.query.get(admin_id)
        if not admin or admin.role != Role.ADMIN:
            return {"error": "Unauthorized access"}
        
        # Build query
        if quiz_id:
            # Specific quiz analytics
            quiz = Quiz.query.get(quiz_id)
            if not quiz:
                return {"error": "Quiz not found"}
            
            # Get all attempts for this quiz
            attempts = UserQuizAttempt.query.filter_by(quiz_id=quiz_id).all()
            
            if not attempts:
                return {"error": "No attempts found for this quiz"}
            
            # Prepare detailed analytics
            export_data = []
            for attempt in attempts:
                user = attempt.user
                
                # Get detailed answers
                answers = UserAnswer.query.filter_by(user_quiz_attempt_id=attempt.id).all()
                
                for answer in answers:
                    question = answer.question
                    export_data.append({
                        'Quiz Title': quiz.title,
                        'Subject': quiz.chapter.subject.name,
                        'Chapter': quiz.chapter.name,
                        'Username': user.username,
                        'Full Name': user.full_name,
                        'Question': question.question_statement,
                        'Selected Option': answer.selected_option,
                        'Correct Answer': question.correct_answer,
                        'Is Correct': answer.is_correct,
                        'Time Spent (seconds)': answer.time_spent,
                        'Attempt Start': attempt.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'Attempt End': attempt.end_time.strftime('%Y-%m-%d %H:%M:%S') if attempt.end_time else '',
                        'Overall Score': f"{attempt.score}/{attempt.total_questions}",
                        'Overall Percentage': round((attempt.score / attempt.total_questions * 100), 2) if attempt.total_questions > 0 else 0
                    })
        else:
            # All quizzes analytics
            attempts = UserQuizAttempt.query.filter_by(status='completed').all()
            
            export_data = []
            for attempt in attempts:
                user = attempt.user
                quiz = attempt.quiz
                
                # Get question-level details
                answers = UserAnswer.query.filter_by(user_quiz_attempt_id=attempt.id).all()
                
                for answer in answers:
                    question = answer.question
                    export_data.append({
                        'Quiz Title': quiz.title,
                        'Subject': quiz.chapter.subject.name,
                        'Chapter': quiz.chapter.name,
                        'Username': user.username,
                        'Full Name': user.full_name,
                        'Question': question.question_statement,
                        'Selected Option': answer.selected_option,
                        'Correct Answer': question.correct_answer,
                        'Is Correct': answer.is_correct,
                        'Time Spent (seconds)': answer.time_spent,
                        'Attempt Start': attempt.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'Attempt End': attempt.end_time.strftime('%Y-%m-%d %H:%M:%S') if attempt.end_time else '',
                        'Overall Score': f"{attempt.score}/{attempt.total_questions}",
                        'Overall Percentage': round((attempt.score / attempt.total_questions * 100), 2) if attempt.total_questions > 0 else 0
                    })
        
        if not export_data:
            return {"error": "No data found for export"}
        
        # Create DataFrame and export
        df = pd.DataFrame(export_data)
        
        if export_format == 'csv':
            filename = f"quiz_analytics_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = f"exports/{filename}"
            
            # Ensure exports directory exists
            import os
            os.makedirs("exports", exist_ok=True)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                df.to_csv(f, index=False)
            
            return {
                "success": True,
                "filename": filename,
                "filepath": filepath,
                "record_count": len(export_data),
                "admin": admin.username
            }
        
        elif export_format == 'excel':
            filename = f"quiz_analytics_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filepath = f"exports/{filename}"
            
            # Ensure exports directory exists
            import os
            os.makedirs("exports", exist_ok=True)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Quiz Analytics', index=False)
            
            return {
                "success": True,
                "filename": filename,
                "filepath": filepath,
                "record_count": len(export_data),
                "admin": admin.username
            }
    
    except Exception as e:
        return {"error": f"Export failed: {str(e)}"}

def generate_pdf_report(user, report_data, start_date, end_date):
    """Generate PDF report using reportlab"""
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Prepare content
    content = []
    
    # Title
    title = Paragraph(
        f"Monthly Performance Report for {user.username}",
        styles['Title']
    )
    content.append(title)
    
    # Date range
    date_range = Paragraph(
        f"Period: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}",
        styles['Normal']
    )
    content.append(date_range)
    content.append(Spacer(1, 24))
    
    # Summary table
    summary_data = [
        ["Metric", "Value"],
        ["Total Quizzes Attempted", report_data["Total Quizzes Attempted"]],
        ["Total Questions Answered", report_data["Total Questions Answered"]],
        ["Correct Answers", report_data["Correct Answers"]],
        ["Overall Accuracy", report_data["Overall Accuracy"]],
        ["Average Time per Quiz", report_data["Average Time per Quiz"]]
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    content.append(summary_table)
    content.append(Spacer(1, 24))
    
    # Subject-wise performance
    if report_data["Quizzes by Subject"]:
        subject_title = Paragraph("Performance by Subject", styles['Heading2'])
        content.append(subject_title)
        
        subject_data = [["Subject", "Quizzes", "Accuracy", "Avg Score"]]
        for subject, stats in report_data["Quizzes by Subject"].items():
            subject_data.append([
                subject,
                stats["Quizzes Attempted"],
                stats["Accuracy"],
                stats["Average Score"]
            ])
        
        subject_table = Table(subject_data)
        subject_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        content.append(subject_table)
    
    # Build PDF
    doc.build(content)
    buffer.seek(0)
    return buffer