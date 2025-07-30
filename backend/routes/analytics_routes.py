from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.model import db, Quiz, UserQuizAttempt, User, Question, Role
from sqlalchemy import func, desc
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api')

@analytics_bp.route('/quiz-stats', methods=['GET'])
@jwt_required()
def get_quiz_stats():
    """Get overall quiz statistics"""
    try:
        # Total quizzes
        total_quizzes = Quiz.query.count()
        
        # Active quizzes
        active_quizzes = Quiz.query.filter_by(is_active=True).count()
        
        # Total attempts
        total_attempts = UserQuizAttempt.query.filter_by(status='completed').count()
        
        # Average score
        avg_score_result = db.session.query(
            func.avg(UserQuizAttempt.score * 100.0 / UserQuizAttempt.total_questions)
        ).filter(
            UserQuizAttempt.status == 'completed',
            UserQuizAttempt.total_questions > 0
        ).scalar()
        
        avg_score = round(avg_score_result or 0, 1)
        
        return jsonify({
            'totalQuizzes': total_quizzes,
            'activeQuizzes': active_quizzes,
            'totalAttempts': total_attempts,
            'avgScore': avg_score
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/recent-activity', methods=['GET'])
@jwt_required()
def get_recent_activity():
    """Get recent quiz completion activity"""
    try:
        # Get recent completed attempts with user and quiz info (excluding admin users)
        recent_attempts = db.session.query(
            UserQuizAttempt,
            User.username,
            Quiz.title
        ).join(
            User, UserQuizAttempt.user_id == User.id
        ).join(
            Quiz, UserQuizAttempt.quiz_id == Quiz.id
        ).filter(
            UserQuizAttempt.status == 'completed',
            User.role != Role.ADMIN  # Exclude admin users from recent activity
        ).order_by(
            desc(UserQuizAttempt.start_time)
        ).limit(10).all()
        
        activity_list = []
        for attempt, username, quiz_title in recent_attempts:
            score_percentage = round(
                (attempt.score * 100.0 / attempt.total_questions) if attempt.total_questions > 0 else 0, 1
            )
            activity_list.append({
                'id': attempt.id,
                'user_name': username,
                'quiz_title': quiz_title,
                'score': score_percentage,
                'completed_at': attempt.start_time.isoformat()
            })
        
        return jsonify(activity_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/top-performers', methods=['GET'])
@jwt_required()
def get_top_performers():
    """Get top performing users"""
    try:
        # Calculate average scores for each user (excluding admin users)
        user_performance = db.session.query(
            User.id,
            User.username,
            func.avg(UserQuizAttempt.score * 100.0 / UserQuizAttempt.total_questions).label('avg_score'),
            func.count(UserQuizAttempt.id).label('attempt_count')
        ).join(
            UserQuizAttempt, User.id == UserQuizAttempt.user_id
        ).filter(
            UserQuizAttempt.status == 'completed',
            UserQuizAttempt.total_questions > 0,
            User.role != Role.ADMIN  # Exclude admin users from top performers
        ).group_by(
            User.id, User.username
        ).having(
            func.count(UserQuizAttempt.id) >= 1
        ).order_by(
            desc('avg_score')
        ).limit(10).all()
        
        performers_list = []
        for user_id, username, avg_score, attempt_count in user_performance:
            performers_list.append({
                'user_id': user_id,
                'user_name': username,
                'avg_score': round(avg_score or 0, 1),
                'attempt_count': attempt_count
            })
        
        return jsonify(performers_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/all-users-scores', methods=['GET'])
@jwt_required()
def get_all_users_scores():
    """Get all users ranked by their scores (excluding admin users)"""
    try:
        # Get all users with their scores (excluding admin users)
        all_users_scores = db.session.query(
            User.id,
            User.username,
            User.full_name,
            func.avg(UserQuizAttempt.score * 100.0 / UserQuizAttempt.total_questions).label('avg_score'),
            func.count(UserQuizAttempt.id).label('attempt_count'),
            func.sum(UserQuizAttempt.score).label('total_score'),
            func.sum(UserQuizAttempt.total_questions).label('total_questions')
        ).outerjoin(
            UserQuizAttempt, User.id == UserQuizAttempt.user_id
        ).filter(
            User.role != Role.ADMIN  # Exclude admin users
        ).group_by(
            User.id, User.username, User.full_name
        ).order_by(
            desc('avg_score')
        ).all()
        
        users_list = []
        for user_id, username, full_name, avg_score, attempt_count, total_score, total_questions in all_users_scores:
            users_list.append({
                'user_id': user_id,
                'username': username,
                'full_name': full_name or username,
                'avg_score': round(avg_score or 0, 1),
                'attempt_count': attempt_count or 0,
                'total_score': total_score or 0,
                'total_questions': total_questions or 0,
                'has_attempts': attempt_count > 0 if attempt_count else False
            })
        
        return jsonify(users_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/quiz-performance-data', methods=['GET'])
@jwt_required()
def get_quiz_performance_data():
    """Get quiz performance data for charts"""
    try:
        # Get quiz performance data
        quiz_performance = db.session.query(
            Quiz.id,
            Quiz.title,
            func.avg(UserQuizAttempt.score * 100.0 / UserQuizAttempt.total_questions).label('avg_score'),
            func.count(UserQuizAttempt.id).label('attempt_count')
        ).join(
            UserQuizAttempt, Quiz.id == UserQuizAttempt.quiz_id
        ).filter(
            UserQuizAttempt.status == 'completed',
            UserQuizAttempt.total_questions > 0
        ).group_by(
            Quiz.id, Quiz.title
        ).order_by(
            desc('avg_score')
        ).limit(20).all()
        
        performance_data = []
        for quiz_id, title, avg_score, attempt_count in quiz_performance:
            performance_data.append({
                'quiz_id': quiz_id,
                'title': title,
                'avg_score': round(avg_score or 0, 1),
                'attempt_count': attempt_count
            })
        
        return jsonify(performance_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/subject-performance', methods=['GET'])
@jwt_required()
def get_subject_performance():
    """Get performance data by subject"""
    try:
        from models.model import Subject, Chapter
        
        # Get subject performance data
        subject_performance = db.session.query(
            Subject.id,
            Subject.name,
            func.avg(UserQuizAttempt.score * 100.0 / UserQuizAttempt.total_questions).label('avg_score'),
            func.count(UserQuizAttempt.id).label('attempt_count')
        ).join(
            Chapter, Subject.id == Chapter.subject_id
        ).join(
            Quiz, Chapter.id == Quiz.chapter_id
        ).join(
            UserQuizAttempt, Quiz.id == UserQuizAttempt.quiz_id
        ).filter(
            UserQuizAttempt.status == 'completed',
            UserQuizAttempt.total_questions > 0
        ).group_by(
            Subject.id, Subject.name
        ).order_by(
            desc('avg_score')
        ).all()
        
        subject_data = []
        for subject_id, name, avg_score, attempt_count in subject_performance:
            subject_data.append({
                'subject_id': subject_id,
                'name': name,
                'avg_score': round(avg_score or 0, 1),
                'attempt_count': attempt_count
            })
        
        return jsonify(subject_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/daily-activity', methods=['GET'])
@jwt_required()
def get_daily_activity():
    """Get daily quiz completion activity for the last 30 days"""
    try:
        # Get daily activity for last 30 days
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        daily_activity = db.session.query(
            func.date(UserQuizAttempt.start_time).label('date'),
            func.count(UserQuizAttempt.id).label('count')
        ).filter(
            UserQuizAttempt.status == 'completed',
            UserQuizAttempt.start_time >= start_date,
            UserQuizAttempt.start_time <= end_date
        ).group_by(
            func.date(UserQuizAttempt.start_time)
        ).order_by(
            func.date(UserQuizAttempt.start_time)
        ).all()
        
        # Create a complete date range
        activity_dict = {str(date): count for date, count in daily_activity}
        
        activity_data = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            activity_data.append({
                'date': date_str,
                'count': activity_dict.get(date_str, 0)
            })
            current_date += timedelta(days=1)
        
        return jsonify(activity_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500 