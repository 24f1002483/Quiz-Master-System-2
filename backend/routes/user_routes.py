from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.model import db, Quiz, Question, UserQuizAttempt, UserAnswer, User
from datetime import datetime

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/count', methods=['GET'])
@jwt_required()
def get_user_count():
    """Get total user count for analytics"""
    try:
        user_count = User.query.count()
        return jsonify({'count': user_count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/quizzes/upcoming', methods=['GET'])
@jwt_required()
def get_upcoming_quizzes():
    quizzes = Quiz.query.filter(Quiz.start_date >= datetime.utcnow()).all()
    quiz_list = []
    for q in quizzes:
        try:
            chapter_name = q.chapter.name if q.chapter else "Unknown Chapter"
            subject_name = q.chapter.subject.name if q.chapter and q.chapter.subject else "Unknown Subject"
            
            quiz_list.append({
                'id': q.id,
                'title': q.title,
                'chapter_name': chapter_name,
                'subject_name': subject_name,
                'date': q.start_date.isoformat() if q.start_date else None,
                'duration': q.time_duration * 60 if q.time_duration else None,  # Convert minutes to seconds
                'question_count': len(q.questions)
            })
        except Exception as e:
            print(f"Error processing quiz {q.id}: {e}")
            # Add quiz with fallback values
            quiz_list.append({
                'id': q.id,
                'title': q.title,
                'chapter_name': "Unknown Chapter",
                'subject_name': "Unknown Subject",
                'date': q.start_date.isoformat() if q.start_date else None,
                'duration': q.time_duration * 60 if q.time_duration else None,
                'question_count': len(q.questions)
            })
    
    return jsonify(quiz_list)

@user_bp.route('/quizzes/scores', methods=['GET'])
@jwt_required()
def get_user_scores():
    user_id = get_jwt_identity()
    attempts = UserQuizAttempt.query.filter_by(
        user_id=user_id, 
        status='completed'
    ).order_by(UserQuizAttempt.end_time.desc()).all()
    
    scores = []
    for a in attempts:
        try:
            # Handle missing quiz relationship
            quiz_title = a.quiz.title if a.quiz else "Unknown Quiz"
            
            # Handle missing end_time
            date_str = a.end_time.isoformat() if a.end_time else None
            
            # Handle division by zero for percentage calculation
            percentage = 0
            if a.total_questions and a.total_questions > 0:
                percentage = round((a.score / a.total_questions) * 100, 2)
            
            scores.append({
                'quiz_id': a.quiz_id,
                'quiz_title': quiz_title,
                'date': date_str,
                'score': a.score or 0,
                'total_questions': a.total_questions or 0,
                'percentage': percentage
            })
        except Exception as e:
            # Log the error but continue processing other attempts
            print(f"Error processing attempt {a.id}: {e}")
            continue
    
    return jsonify(scores)

@user_bp.route('/quiz/<int:quiz_id>/attempts', methods=['GET'])
@jwt_required()
def get_quiz_attempt_history(quiz_id):
    """Get all attempts for a specific quiz by the current user"""
    user_id = get_jwt_identity()
    
    attempts = UserQuizAttempt.query.filter_by(
        user_id=user_id,
        quiz_id=quiz_id
    ).order_by(UserQuizAttempt.start_time.desc()).all()
    
    attempt_history = []
    for a in attempts:
        try:
            # Handle missing end_time
            date_str = a.end_time.isoformat() if a.end_time else None
            
            # Handle division by zero for percentage calculation
            percentage = 0
            if a.total_questions and a.total_questions > 0:
                percentage = round((a.score / a.total_questions) * 100, 2)
            
            attempt_history.append({
                'attempt_id': a.id,
                'quiz_id': a.quiz_id,
                'start_time': a.start_time.isoformat() if a.start_time else None,
                'end_time': date_str,
                'score': a.score or 0,
                'total_questions': a.total_questions or 0,
                'percentage': percentage,
                'status': a.status
            })
        except Exception as e:
            print(f"Error processing attempt {a.id}: {e}")
            continue
    
    return jsonify(attempt_history)


@user_bp.route('/quiz/question/<int:attempt_id>/<int:question_num>', methods=['GET'])
@jwt_required()
def get_quiz_question(attempt_id, question_num):
    attempt = UserQuizAttempt.query.get_or_404(attempt_id)
    if str(attempt.user_id) != get_jwt_identity():
        return jsonify({"message": "Unauthorized"}), 403
    
    quiz = attempt.quiz
    if question_num < 1 or question_num > len(quiz.questions):
        return jsonify({"message": "Invalid question number"}), 400
    
    question = quiz.questions[question_num - 1]
    return jsonify({
        'attempt_id': attempt_id,
        'question_number': question_num,
        'total_questions': attempt.total_questions,
        'question': {
            'id': question.id,
            'title': question.question_title,
            'content': question.question_statement,
            'options': [
                question.option1,
                question.option2,
                question.option3,
                question.option4
            ]
        }
    })

@user_bp.route('/quiz/answer', methods=['POST'])
@jwt_required()
def submit_answer():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({"message": "No data provided"}), 400
        
        required_fields = ['attempt_id', 'question_id', 'selected_option']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"message": f"Missing required fields: {missing_fields}"}), 400
        
        # Validate data types
        try:
            attempt_id = int(data['attempt_id'])
            question_id = int(data['question_id'])
            selected_option = int(data['selected_option'])
        except (ValueError, TypeError):
            return jsonify({"message": "Invalid data types for attempt_id, question_id, or selected_option"}), 400
        
        # Validate selected_option range
        if selected_option < 1 or selected_option > 4:
            return jsonify({"message": "selected_option must be between 1 and 4"}), 400
        
        # Get the attempt
        attempt = UserQuizAttempt.query.get_or_404(attempt_id)
        if str(attempt.user_id) != user_id:
            return jsonify({"message": "Unauthorized"}), 403
        
        # Get the question
        question = Question.query.get_or_404(question_id)
        
        # Save or update answer
        existing_answer = UserAnswer.query.filter_by(
            user_quiz_attempt_id=attempt.id,
            question_id=question.id
        ).first()
        
        if existing_answer:
            existing_answer.selected_option = selected_option
            existing_answer.is_correct = (selected_option == question.correct_answer)
        else:
            new_answer = UserAnswer(
                user_quiz_attempt_id=attempt.id,
                question_id=question.id,
                selected_option=selected_option,
                is_correct=(selected_option == question.correct_answer),
                time_spent=data.get('time_spent', 0)
            )
            db.session.add(new_answer)
        
        db.session.commit()
        
        return jsonify({
            'is_correct': selected_option == question.correct_answer,
            'correct_answer': question.correct_answer
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in submit_answer: {str(e)}")
        return jsonify({"message": f"Internal server error: {str(e)}"}), 500

@user_bp.route('/quiz/complete/<int:attempt_id>', methods=['POST'])
@jwt_required()
def complete_quiz(attempt_id):
    print(f"DEBUG: Completing quiz attempt {attempt_id}")
    attempt = UserQuizAttempt.query.get_or_404(attempt_id)
    current_user_id = get_jwt_identity()
    
    # Convert to int for comparison since JWT identity is stored as string
    if str(attempt.user_id) != current_user_id:
        print(f"DEBUG: User ID mismatch. JWT: {current_user_id}, Attempt: {attempt.user_id}")
        return jsonify({"message": "Unauthorized"}), 403
    
    print(f"DEBUG: Found attempt for user {attempt.user_id}")
    
    # Calculate score - use user_quiz_attempt_id instead of attempt_id
    correct_answers = UserAnswer.query.filter_by(
        user_quiz_attempt_id=attempt.id,
        is_correct=True
    ).count()
    
    total_answers = UserAnswer.query.filter_by(
        user_quiz_attempt_id=attempt.id
    ).count()
    
    # Get total questions from the quiz
    total_questions = total_answers  # Default to total answers
    try:
        if attempt.quiz and hasattr(attempt.quiz, 'questions'):
            total_questions = len(attempt.quiz.questions)
    except Exception as e:
        print(f"DEBUG: Error getting quiz questions: {e}")
        # Fallback to total answers
    
    print(f"DEBUG: Correct answers: {correct_answers}, Total answers: {total_answers}, Total questions: {total_questions}")
    
    attempt.score = correct_answers
    attempt.total_questions = total_questions  # This was missing!
    attempt.end_time = datetime.utcnow()
    attempt.status = 'completed'
    
    try:
        db.session.commit()
        print(f"DEBUG: Quiz completed successfully. Score: {correct_answers}/{total_questions}")
        return jsonify(attempt.serialize())
    except Exception as e:
        print(f"DEBUG: Error committing quiz completion: {e}")
        db.session.rollback()
        return jsonify({"message": "Error completing quiz"}), 500