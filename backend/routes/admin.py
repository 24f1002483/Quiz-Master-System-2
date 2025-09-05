from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.model import db, User, Subject, Chapter, Quiz, Question, Role
from functools import wraps
from notification_services import send_email_internal
import logging

# Setup logging
logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.role != Role.ADMIN:
            return jsonify({"message": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

# Subjects CRUD
@admin_bp.route('/subjects', methods=['GET'])
@jwt_required()
@admin_required
def get_subjects():
    subjects = Subject.query.all()
    return jsonify([subject.serialize() for subject in subjects]), 200

@admin_bp.route('/subjects', methods=['POST'])
@jwt_required()
@admin_required
def create_subject():
    data = request.get_json()
    new_subject = Subject(
        name=data['name'],
        description=data.get('description', ''),
        admin_id=get_jwt_identity()
    )
    db.session.add(new_subject)
    db.session.commit()
    return jsonify(new_subject.serialize()), 201

@admin_bp.route('/subjects/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_subject(id):
    subject = Subject.query.get_or_404(id)
    data = request.get_json()
    subject.name = data.get('name', subject.name)
    subject.description = data.get('description', subject.description)
    subject.is_active = data.get('is_active', subject.is_active)
    db.session.commit()
    return jsonify(subject.serialize()), 200

@admin_bp.route('/subjects/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    return jsonify({"message": "Subject deleted"}), 200

# Chapters CRUD
@admin_bp.route('/chapters', methods=['POST'])
@jwt_required()
@admin_required
def create_chapter():
    data = request.get_json()
    new_chapter = Chapter(
        name=data['name'],
        description=data.get('description', ''),
        sequence=data.get('sequence', 0),
        subject_id=data['subject_id']
    )
    db.session.add(new_chapter)
    db.session.commit()
    return jsonify(new_chapter.serialize()), 201

@admin_bp.route('/chapters/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_chapter(id):
    chapter = Chapter.query.get_or_404(id)
    data = request.get_json()
    chapter.name = data.get('name', chapter.name)
    chapter.description = data.get('description', chapter.description)
    chapter.sequence = data.get('sequence', chapter.sequence)
    db.session.commit()
    return jsonify(chapter.serialize()), 200

@admin_bp.route('/chapters/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_chapter(id):
    chapter = Chapter.query.get_or_404(id)
    db.session.delete(chapter)
    db.session.commit()
    return jsonify({"message": "Chapter deleted"}), 200

# Quizzes CRUD
@admin_bp.route('/quizzes', methods=['GET'])
@jwt_required()
@admin_required
def get_quizzes():
    quizzes = Quiz.query.all()
    return jsonify([quiz.serialize() for quiz in quizzes]), 200

@admin_bp.route('/quizzes', methods=['POST'])
@jwt_required()
@admin_required
def create_quiz():
    data = request.get_json()
    
    # Parse dates from the frontend
    from datetime import datetime
    start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
    end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
    
    new_quiz = Quiz(
        title=data['title'],
        description=data.get('description', ''),
        chapter_id=data['chapter_id'],
        start_date=start_date,
        end_date=end_date,
        time_duration=data.get('duration', 60)
    )
    db.session.add(new_quiz)
    db.session.commit()
    
    # Send immediate notifications to users about the new quiz
    try:
        send_new_quiz_notifications(new_quiz)
        logger.info(f"New quiz notifications sent for quiz: {new_quiz.title}")
    except Exception as e:
        logger.error(f"Failed to send new quiz notifications: {e}")
        # Don't fail the quiz creation if notifications fail
    
    return jsonify(new_quiz.serialize()), 201

def send_new_quiz_notifications(quiz):
    """Send immediate notifications to users about a new quiz"""
    try:
        # Get all active users
        users = User.query.filter_by(is_active=True, role=Role.USER).all()
        
        # Get quiz details
        subject = quiz.chapter.subject.name
        chapter = quiz.chapter.name
        start_time = quiz.start_date.strftime("%b %d, %Y at %H:%M")
        
        successful_notifications = 0
        failed_notifications = 0
        
        for user in users:
            try:
                # Generate personalized message
                message = f"""🎉 New Quiz Available!

Hello {user.full_name or user.username},

A new quiz has just been created and is now available for you to take!

📚 Quiz Details:
• Title: {quiz.title}
• Subject: {subject}
• Chapter: {chapter}
• Start Date: {start_time}
• Duration: {quiz.time_duration} minutes
• Description: {quiz.description or 'No description provided'}

🎯 Ready to test your knowledge? Log in now and take the quiz!

Best regards,
Quiz Master 2 Team"""

                # Send notification based on user preference
                if user.notification_preference == 'email':
                    send_email_internal(
                        recipient=user.username,
                        subject=f"🆕 New Quiz: {quiz.title}",
                        body=message
                    )
                    successful_notifications += 1
                    
                elif user.notification_preference == 'sms' and user.phone:
                    # TODO: Implement SMS sending
                    logger.info(f"SMS notification would be sent to {user.phone}")
                    successful_notifications += 1
                    
                elif user.notification_preference == 'gchat':
                    # TODO: Implement Google Chat webhook
                    logger.info(f"Google Chat notification would be sent to {user.username}")
                    successful_notifications += 1
                    
                else:
                    # Fallback to email
                    send_email_internal(
                        recipient=user.username,
                        subject=f"🆕 New Quiz: {quiz.title}",
                        body=message
                    )
                    successful_notifications += 1
                    
            except Exception as e:
                logger.error(f"Failed to send notification to {user.username}: {e}")
                failed_notifications += 1
        
        logger.info(f"New quiz notifications: {successful_notifications} sent, {failed_notifications} failed")
        
    except Exception as e:
        logger.error(f"Error in send_new_quiz_notifications: {e}")
        raise

@admin_bp.route('/quizzes/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_quiz(id):
    quiz = Quiz.query.get_or_404(id)
    data = request.get_json()
    
    # Parse dates if provided
    from datetime import datetime
    if 'start_date' in data:
        quiz.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
    if 'end_date' in data:
        quiz.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
    
    # Update all fields
    quiz.title = data.get('title', quiz.title)
    quiz.description = data.get('description', quiz.description)
    quiz.chapter_id = data.get('chapter_id', quiz.chapter_id)
    quiz.time_duration = data.get('time_duration', data.get('duration', quiz.time_duration))
    quiz.is_active = data.get('is_active', quiz.is_active)
    
    db.session.commit()
    return jsonify(quiz.serialize()), 200

@admin_bp.route('/quizzes/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_quiz(id):
    try:
        quiz = Quiz.query.get_or_404(id)
        quiz_title = quiz.title  # Store for logging
        
        logger.info(f"Starting deletion of quiz: {quiz_title} (ID: {id})")
        
        # Import all related models
        from models.model import UserQuizAttempt, UserAnswer, Score
        
        # Step 1: Delete all UserAnswer records for this quiz
        # Get all user quiz attempts for this quiz first
        attempts = UserQuizAttempt.query.filter_by(quiz_id=id).all()
        attempt_ids = [attempt.id for attempt in attempts]
        
        if attempt_ids:
            # Delete all user answers for these attempts
            user_answers = UserAnswer.query.filter(UserAnswer.user_quiz_attempt_id.in_(attempt_ids)).all()
            logger.info(f"Deleting {len(user_answers)} user answers")
            for answer in user_answers:
                db.session.delete(answer)
            db.session.flush()  # Flush to ensure answers are deleted before attempts
        
        # Step 2: Delete all user quiz attempts for this quiz
        logger.info(f"Deleting {len(attempts)} quiz attempts")
        for attempt in attempts:
            db.session.delete(attempt)
        db.session.flush()  # Flush to ensure attempts are deleted
        
        # Step 3: Delete all scores associated with this quiz
        scores = Score.query.filter_by(quiz_id=id).all()
        logger.info(f"Deleting {len(scores)} score records")
        for score in scores:
            db.session.delete(score)
        db.session.flush()  # Flush to ensure scores are deleted
        
        # Step 4: Delete all questions associated with this quiz
        questions = Question.query.filter_by(quiz_id=id).all()
        logger.info(f"Deleting {len(questions)} questions")
        for question in questions:
            db.session.delete(question)
        db.session.flush()  # Flush to ensure questions are deleted
        
        # Step 5: Finally delete the quiz itself
        logger.info(f"Deleting quiz: {quiz_title}")
        db.session.delete(quiz)
        
        # Commit all changes
        db.session.commit()
        
        logger.info(f"Successfully deleted quiz: {quiz_title} and all associated data")
        return jsonify({
            "message": f"Quiz '{quiz_title}' and all associated data deleted successfully",
            "deleted_items": {
                "quiz": 1,
                "questions": len(questions),
                "attempts": len(attempts),
                "answers": len(user_answers) if attempt_ids else 0,
                "scores": len(scores)
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error deleting quiz: {str(e)}"
        logger.error(error_msg)
        logger.error(f"Exception type: {type(e).__name__}")
        
        # Provide more specific error messages
        if "foreign key constraint" in str(e).lower():
            error_msg = "Cannot delete quiz: There are related records that prevent deletion. Please contact administrator."
        elif "not found" in str(e).lower():
            error_msg = "Quiz not found or already deleted."
        
        return jsonify({"message": error_msg, "error_details": str(e)}), 500

# Questions CRUD
@admin_bp.route('/questions', methods=['POST'])
@jwt_required()
@admin_required
def create_question():
    data = request.get_json()
    new_question = Question(
        quiz_id=data['quiz_id'],  # quiz_id is now required
        question_title=data['question_title'],
        question_statement=data['question_statement'],
        option1=data['option1'],
        option2=data['option2'],
        option3=data.get('option3'),
        option4=data.get('option4'),
        correct_answer=data['correct_answer'],
        explanation=data.get('explanation', ''),
        difficulty=data.get('difficulty', 3)
    )
    db.session.add(new_question)
    db.session.commit()
    
    return jsonify(new_question.serialize()), 201

@admin_bp.route('/questions/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_question(id):
    question = Question.query.get_or_404(id)
    data = request.get_json()
    question.question_title = data.get('question_title', question.question_title)
    question.question_statement = data.get('question_statement', question.question_statement)
    question.option1 = data.get('option1', question.option1)
    question.option2 = data.get('option2', question.option2)
    question.option3 = data.get('option3', question.option3)
    question.option4 = data.get('option4', question.option4)
    question.correct_answer = data.get('correct_answer', question.correct_answer)
    question.explanation = data.get('explanation', question.explanation)
    question.difficulty = data.get('difficulty', question.difficulty)
    db.session.commit()
    return jsonify(question.serialize()), 200

@admin_bp.route('/questions/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_question(id):
    question = Question.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()
    return jsonify({"message": "Question deleted"}), 200

# User Management
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@admin_bp.route('/users/count', methods=['GET'])
@jwt_required()
@admin_required
def get_users_count():
    """Get user count for admin dashboard analytics"""
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(role=Role.ADMIN).count()
        regular_users = User.query.filter_by(role=Role.USER).count()
        
        # Return both detailed stats and simple count for compatibility
        return jsonify({
            'count': total_users,  # Simple count for frontend compatibility
            'total_users': total_users,
            'active_users': active_users,
            'admin_users': admin_users,
            'regular_users': regular_users
        }), 200
    except Exception as e:
        logger.error(f"Error getting user count: {e}")
        return jsonify({'error': 'Failed to get user count'}), 500

@admin_bp.route('/analytics/overview', methods=['GET'])
@jwt_required()
@admin_required
def get_analytics_overview():
    """Get comprehensive analytics overview for admin dashboard"""
    try:
        from models.model import UserQuizAttempt, Score
        
        # User statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(role=Role.ADMIN).count()
        regular_users = User.query.filter_by(role=Role.USER).count()
        
        # Quiz statistics
        total_quizzes = Quiz.query.count()
        active_quizzes = Quiz.query.filter_by(is_active=True).count()
        
        # Subject and chapter statistics
        total_subjects = Subject.query.count()
        total_chapters = Chapter.query.count()
        
        # Quiz attempt statistics
        total_attempts = UserQuizAttempt.query.count()
        completed_attempts = UserQuizAttempt.query.filter_by(status='completed').count()
        
        # Score statistics
        total_scores = Score.query.count()
        if total_scores > 0:
            avg_score = db.session.query(db.func.avg(Score.percentage)).scalar()
            avg_score = round(float(avg_score), 2) if avg_score else 0
        else:
            avg_score = 0
        
        return jsonify({
            'users': {
                'total': total_users,
                'active': active_users,
                'admins': admin_users,
                'regular': regular_users
            },
            'quizzes': {
                'total': total_quizzes,
                'active': active_quizzes
            },
            'content': {
                'subjects': total_subjects,
                'chapters': total_chapters
            },
            'attempts': {
                'total': total_attempts,
                'completed': completed_attempts
            },
            'scores': {
                'total': total_scores,
                'average_percentage': avg_score
            }
        }), 200
    except Exception as e:
        logger.error(f"Error getting analytics overview: {e}")
        return jsonify({'error': 'Failed to get analytics overview'}), 500

@admin_bp.route('/users/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json()
    user.username = data.get('username', user.username)
    user.full_name = data.get('full_name', user.full_name)
    user.is_active = data.get('is_active', user.is_active)
    if 'password' in data:
        user.set_password(data['password'])
    db.session.commit()
    return jsonify(user.serialize()), 200

@admin_bp.route('/users/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(id):
    if id == get_jwt_identity():
        return jsonify({"message": "Cannot delete yourself"}), 400
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200