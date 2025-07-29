from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.model import db, UserQuizAttempt, UserAnswer
from datetime import datetime

score_bp = Blueprint('score', __name__, url_prefix='/api/scores')

@score_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_quiz():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate request data
    if not all(k in data for k in ['attempt_id', 'answers']):
        return jsonify({"message": "Missing required fields"}), 400
    
    try:
        # Get the attempt
        attempt = UserQuizAttempt.query.filter_by(
            id=data['attempt_id'],
            user_id=user_id
        ).first_or_404()
        
        # Calculate score
        correct_answers = 0
        total_questions = len(data['answers'])
        
        # Save answers and count correct ones
        for answer in data['answers']:
            is_correct = answer['selected_option'] == answer['correct_answer']
            if is_correct:
                correct_answers += 1
            
            user_answer = UserAnswer(
                user_quiz_attempt_id=attempt.id,
                question_id=answer['question_id'],
                selected_option=answer['selected_option'],
                is_correct=is_correct,
                time_spent=answer.get('time_spent', 0)
            )
            db.session.add(user_answer)
        
        # Update attempt with final score
        attempt.score = correct_answers
        attempt.total_questions = total_questions
        attempt.end_time = datetime.utcnow()
        attempt.status = 'completed'
        
        db.session.commit()
        
        return jsonify({
            "attempt_id": attempt.id,
            "score": correct_answers,
            "total_questions": total_questions,
            "percentage": round((correct_answers / total_questions) * 100, 2)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@score_bp.route('/history', methods=['GET'])
@jwt_required()
def get_score_history():
    user_id = get_jwt_identity()
    attempts = UserQuizAttempt.query.filter_by(
        user_id=user_id,
        status='completed'
    ).order_by(
        UserQuizAttempt.end_time.desc()
    ).all()
    
    return jsonify([attempt.serialize() for attempt in attempts])

@score_bp.route('/details/<int:attempt_id>', methods=['GET'])
@jwt_required()
def get_attempt_details(attempt_id):
    user_id = get_jwt_identity()
    
    # Verify the attempt belongs to the user
    attempt = UserQuizAttempt.query.filter_by(
        id=attempt_id,
        user_id=user_id
    ).first_or_404()
    
    # Get all answers for this attempt
    answers = UserAnswer.query.filter_by(
        user_quiz_attempt_id=attempt_id
    ).all()
    
    return jsonify({
        'attempt': attempt.serialize(),
        'answers': [answer.serialize() for answer in answers]
    })

@score_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_score_summary():
    user_id = get_jwt_identity()
    
    # Get all completed attempts
    attempts = UserQuizAttempt.query.filter_by(
        user_id=user_id,
        status='completed'
    ).all()
    
    if not attempts:
        return jsonify({"message": "No quiz attempts found"}), 404
    
    # Calculate summary statistics
    total_quizzes = len(attempts)
    total_questions = sum(attempt.total_questions or 0 for attempt in attempts)
    total_correct = sum(attempt.score or 0 for attempt in attempts)
    overall_percentage = round((total_correct / total_questions) * 100, 2) if total_questions > 0 else 0
    
    # Group by subject
    subject_stats = {}
    for attempt in attempts:
        # Get subject name safely
        subject_name = "Unknown"
        try:
            if attempt.quiz and attempt.quiz.chapter and attempt.quiz.chapter.subject:
                subject_name = attempt.quiz.chapter.subject.name
        except:
            pass
            
        if subject_name not in subject_stats:
            subject_stats[subject_name] = {
                'quiz_count': 0,
                'total_questions': 0,
                'total_correct': 0
            }
        
        subject_stats[subject_name]['quiz_count'] += 1
        subject_stats[subject_name]['total_questions'] += attempt.total_questions or 0
        subject_stats[subject_name]['total_correct'] += attempt.score or 0
    
    # Calculate percentages for each subject
    for subject in subject_stats.values():
        subject['percentage'] = round(
            (subject['total_correct'] / subject['total_questions']) * 100, 2
        ) if subject['total_questions'] > 0 else 0
    
    return jsonify({
        'total_quizzes': total_quizzes,
        'total_questions': total_questions,
        'total_correct': total_correct,
        'overall_percentage': overall_percentage,
        'by_subject': subject_stats,
        'recent_attempts': [attempt.serialize() for attempt in attempts[:5]]  # Last 5 attempts
    })