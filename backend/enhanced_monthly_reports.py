#!/usr/bin/env python3
"""
Enhanced Monthly Activity Report System
Generates comprehensive HTML monthly reports with quiz details, scores, and rankings
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy import func, desc, and_
from models.model import User, Quiz, UserQuizAttempt, Subject, Chapter, Role
from notification_services import send_email_internal
import logging
import os

logger = logging.getLogger(__name__)

def calculate_user_rankings(month_start, month_end):
    """Calculate user rankings based on average scores"""
    rankings = User.query.join(UserQuizAttempt).filter(
        and_(
            UserQuizAttempt.end_time >= month_start,
            UserQuizAttempt.end_time <= month_end,
            UserQuizAttempt.status == 'completed',
            User.role == Role.USER
        )
    ).with_entities(
        User.id,
        User.username,
        User.full_name,
        func.avg(UserQuizAttempt.score * 100.0 / UserQuizAttempt.total_questions).label('avg_score'),
        func.count(UserQuizAttempt.id).label('attempt_count')
    ).group_by(User.id, User.username, User.full_name).order_by(
        desc('avg_score')
    ).all()
    
    return rankings

def get_user_monthly_stats(user, month_start, month_end):
    """Get comprehensive monthly statistics for a user"""
    attempts = UserQuizAttempt.query.filter(
        and_(
            UserQuizAttempt.user_id == user.id,
            UserQuizAttempt.end_time >= month_start,
            UserQuizAttempt.end_time <= month_end,
            UserQuizAttempt.status == 'completed'
        )
    ).all()
    
    if not attempts:
        return None
    
    # Basic stats
    total_quizzes = len(attempts)
    total_questions = sum(a.total_questions for a in attempts)
    total_correct = sum(a.score for a in attempts)
    total_time = sum(a.time_taken for a in attempts if a.time_taken)
    
    # Calculate averages
    avg_score = (total_correct / total_questions) * 100 if total_questions > 0 else 0
    avg_time = total_time / total_quizzes if total_quizzes > 0 else 0
    
    # Subject-wise breakdown
    subject_stats = {}
    for attempt in attempts:
        subject_name = attempt.quiz.chapter.subject.name
        if subject_name not in subject_stats:
            subject_stats[subject_name] = {
                'quizzes': 0,
                'questions': 0,
                'correct': 0,
                'time': 0
            }
        
        subject_stats[subject_name]['quizzes'] += 1
        subject_stats[subject_name]['questions'] += attempt.total_questions
        subject_stats[subject_name]['correct'] += attempt.score
        if attempt.time_taken:
            subject_stats[subject_name]['time'] += attempt.time_taken
    
    # Calculate subject averages
    for subject, stats in subject_stats.items():
        stats['avg_score'] = (stats['correct'] / stats['questions']) * 100 if stats['questions'] > 0 else 0
        stats['avg_time'] = stats['time'] / stats['quizzes'] if stats['quizzes'] > 0 else 0
    
    # Get user ranking
    rankings = calculate_user_rankings(month_start, month_end)
    user_rank = None
    total_users = len(rankings)
    
    for i, rank_data in enumerate(rankings, 1):
        if rank_data.id == user.id:
            user_rank = i
            break
    
    return {
        'total_quizzes': total_quizzes,
        'total_questions': total_questions,
        'total_correct': total_correct,
        'avg_score': round(avg_score, 2),
        'avg_time': round(avg_time / 60, 2),  # Convert to minutes
        'subject_stats': subject_stats,
        'rank': user_rank,
        'total_users': total_users,
        'attempts': attempts
    }

def generate_html_report(user, stats, month_start, month_end):
    """Generate HTML monthly report"""
    month_name = month_start.strftime("%B %Y")
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Quiz Master 2 - Monthly Report</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 3px solid #007bff;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                color: #007bff;
                margin: 0;
                font-size: 2.5em;
            }}
            .header p {{
                color: #666;
                margin: 10px 0 0 0;
                font-size: 1.2em;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }}
            .stat-card h3 {{
                margin: 0 0 10px 0;
                font-size: 1.1em;
                opacity: 0.9;
            }}
            .stat-card .value {{
                font-size: 2em;
                font-weight: bold;
                margin: 0;
            }}
            .ranking-card {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 30px;
            }}
            .subject-section {{
                margin-bottom: 30px;
            }}
            .subject-section h3 {{
                color: #007bff;
                border-bottom: 2px solid #007bff;
                padding-bottom: 10px;
            }}
            .subject-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }}
            .subject-table th, .subject-table td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            .subject-table th {{
                background-color: #f8f9fa;
                font-weight: bold;
            }}
            .subject-table tr:hover {{
                background-color: #f5f5f5;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                color: #666;
            }}
            .highlight {{
                background-color: #fff3cd;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #ffc107;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Monthly Activity Report</h1>
                <p>{month_name}</p>
                <p>Generated for: {user.full_name or user.username}</p>
            </div>
            
            <div class="highlight">
                <strong>🎯 Your Performance Summary:</strong> You completed {stats['total_quizzes']} quizzes with an average score of {stats['avg_score']}%
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total Quizzes</h3>
                    <div class="value">{stats['total_quizzes']}</div>
                </div>
                <div class="stat-card">
                    <h3>Average Score</h3>
                    <div class="value">{stats['avg_score']}%</div>
                </div>
                <div class="stat-card">
                    <h3>Questions Answered</h3>
                    <div class="value">{stats['total_questions']}</div>
                </div>
                <div class="stat-card">
                    <h3>Avg Time/Quiz</h3>
                    <div class="value">{stats['avg_time']}m</div>
                </div>
            </div>
            
            <div class="ranking-card">
                <h3>🏆 Your Ranking</h3>
                <div class="value">#{stats['rank']} of {stats['total_users']}</div>
                <p>You're among the top performers this month!</p>
            </div>
            
            <div class="subject-section">
                <h3>📚 Performance by Subject</h3>
                <table class="subject-table">
                    <thead>
                        <tr>
                            <th>Subject</th>
                            <th>Quizzes Taken</th>
                            <th>Average Score</th>
                            <th>Avg Time</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for subject, subject_stats in stats['subject_stats'].items():
        html += f"""
                        <tr>
                            <td><strong>{subject}</strong></td>
                            <td>{subject_stats['quizzes']}</td>
                            <td>{round(subject_stats['avg_score'], 2)}%</td>
                            <td>{round(subject_stats['avg_time'] / 60, 2)}m</td>
                        </tr>
        """
    
    html += f"""
                    </tbody>
                </table>
            </div>
            
            <div class="subject-section">
                <h3>📋 Quiz Details</h3>
                <table class="subject-table">
                    <thead>
                        <tr>
                            <th>Quiz Title</th>
                            <th>Subject</th>
                            <th>Score</th>
                            <th>Time Taken</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for attempt in stats['attempts']:
        quiz = attempt.quiz
        subject = quiz.chapter.subject.name
        score_percent = round((attempt.score / attempt.total_questions) * 100, 2)
        time_minutes = round(attempt.time_taken / 60, 2) if attempt.time_taken else 0
        date_str = attempt.end_time.strftime("%b %d, %Y")
        
        html += f"""
                        <tr>
                            <td>{quiz.title}</td>
                            <td>{subject}</td>
                            <td>{score_percent}%</td>
                            <td>{time_minutes}m</td>
                            <td>{date_str}</td>
                        </tr>
        """
    
    html += f"""
                    </tbody>
                </table>
            </div>
            
            <div class="footer">
                <p>📧 This report was automatically generated by Quiz Master 2</p>
                <p>Keep up the great work and continue learning!</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def send_monthly_report_to_user(user, month_start, month_end):
    """Generate and send monthly report to user"""
    try:
        # Get user statistics
        stats = get_user_monthly_stats(user, month_start, month_end)
        
        if not stats:
            logger.info(f"No activity for user {user.username} in {month_start.strftime('%B %Y')}")
            return False
        
        # Generate HTML report
        html_content = generate_html_report(user, stats, month_start, month_end)
        
        # Send email with HTML content
        month_name = month_start.strftime("%B %Y")
        
        send_email_internal(
            recipient=user.username,
            subject=f"📊 Quiz Master 2 - Monthly Report ({month_name})",
            body=f"""
Hello {user.full_name or user.username},

Please find attached your monthly activity report for {month_name}.

Your Performance Summary:
• Total Quizzes: {stats['total_quizzes']}
• Average Score: {stats['avg_score']}%
• Ranking: #{stats['rank']} of {stats['total_users']} users

Keep up the great work!

Best regards,
Quiz Master 2 Team
            """.strip(),
            attachment=html_content.encode('utf-8'),
            attachment_name=f"monthly_report_{user.username}_{month_start.strftime('%Y_%m')}.html"
        )
        
        logger.info(f"Monthly report sent to {user.username}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send monthly report to {user.username}: {e}")
        return False

def enhanced_monthly_reports_task():
    """Enhanced monthly reports task"""
    try:
        logger.info("Starting enhanced monthly reports task")
        
        # Calculate date range (previous month)
        today = datetime.now(timezone.utc)
        first_day_of_month = today.replace(day=1)
        last_month_end = first_day_of_month - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        
        # Get all active users
        users = User.query.filter_by(is_active=True, role=Role.USER).all()
        
        successful_reports = 0
        failed_reports = 0
        skipped_users = 0
        
        for user in users:
            try:
                # Check if user has activity in the month
                stats = get_user_monthly_stats(user, last_month_start, last_month_end)
                if not stats:
                    skipped_users += 1
                    continue
                
                # Send report
                if send_monthly_report_to_user(user, last_month_start, last_month_end):
                    successful_reports += 1
                else:
                    failed_reports += 1
                    
            except Exception as e:
                logger.error(f"Error processing monthly report for user {user.id}: {e}")
                failed_reports += 1
        
        result = f"Enhanced monthly reports completed: {successful_reports} sent, {failed_reports} failed, {skipped_users} skipped"
        logger.info(result)
        return result
        
    except Exception as e:
        logger.error(f"Error in enhanced monthly reports task: {e}")
        raise

if __name__ == "__main__":
    # Set up Flask app context
    from app import create_app
    from models.model import db
    
    app = create_app()
    with app.app_context():
        # Test the enhanced monthly reports
        enhanced_monthly_reports_task() 