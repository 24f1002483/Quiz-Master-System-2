from celery import Celery
from flask import Flask
from datetime import datetime, timedelta
from models.model import db, User, Quiz, UserQuizAttempt
from notification_services import send_email
from notification_services import send_gchat_message
from notification_services import send_sms
import pandas as pd
import io

def create_celery_app(app=None):
    from app import create_app
    app = app or create_app()
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

celery = create_celery_app()

@celery.task
def send_daily_reminders():
    """Send daily quiz reminders to users"""
    try:
        # Get quizzes starting in the next 24 hours
        now = datetime.utcnow()
        tomorrow = now + timedelta(days=1)
        
        upcoming_quizzes = Quiz.query.filter(
            Quiz.start_date >= now,
            Quiz.start_date <= tomorrow,
            Quiz.is_active == True
        ).all()
        
        if not upcoming_quizzes:
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
        
        for user in users:
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
            
            # Send via preferred notification method
            if user.notification_preference == 'email':
                send_email.delay(
                    recipient=user.username,
                    subject="Daily Quiz Reminder",
                    body=message
                )
            elif user.notification_preference == 'gchat':
                send_gchat_message.delay(
                    user_id=user.id,
                    message=message
                )
            elif user.notification_preference == 'sms':
                send_sms.delay(
                    phone_number=user.phone,
                    message=message
                )
        
        return f"Sent daily reminders to {len(users)} users about {len(upcoming_quizzes)} quizzes"
    except Exception as e:
        return f"Error sending daily reminders: {str(e)}"

@celery.task
def generate_monthly_reports():
    """Generate and send monthly performance reports"""
    try:
        # Calculate date range (previous month)
        today = datetime.utcnow()
        first_day_of_month = today.replace(day=1)
        last_month_end = first_day_of_month - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        
        # Get all active users
        users = User.query.filter_by(is_active=True).all()
        
        for user in users:
            # Get user's quiz attempts from last month
            attempts = UserQuizAttempt.query.filter(
                UserQuizAttempt.user_id == user.id,
                UserQuizAttempt.end_time >= last_month_start,
                UserQuizAttempt.end_time <= last_month_end,
                UserQuizAttempt.status == 'completed'
            ).all()
            
            if not attempts:
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
        
        return f"Generated monthly reports for {len(users)} users"
    except Exception as e:
        return f"Error generating monthly reports: {str(e)}"

def generate_pdf_report(user, report_data, start_date, end_date):
    """Generate PDF report using pandas and reportlab"""
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