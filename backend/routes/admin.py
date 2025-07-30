from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.model import db, User, Subject, Chapter, Quiz, Question, Role
from functools import wraps

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
    return jsonify(new_quiz.serialize()), 201

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
    
    quiz.title = data.get('title', quiz.title)
    quiz.time_duration = data.get('duration', quiz.time_duration)
    quiz.is_active = data.get('is_active', quiz.is_active)
    db.session.commit()
    return jsonify(quiz.serialize()), 200

@admin_bp.route('/quizzes/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_quiz(id):
    try:
        quiz = Quiz.query.get_or_404(id)
        
        # Delete all user quiz attempts associated with this quiz first
        # (this will cascade delete UserAnswer records)
        from models.model import UserQuizAttempt
        attempts = UserQuizAttempt.query.filter_by(quiz_id=id).all()
        for attempt in attempts:
            db.session.delete(attempt)
        
        # Delete all scores associated with this quiz
        from models.model import Score
        scores = Score.query.filter_by(quiz_id=id).all()
        for score in scores:
            db.session.delete(score)
        
        # Delete all questions associated with this quiz
        questions = Question.query.filter_by(quiz_id=id).all()
        for question in questions:
            db.session.delete(question)
        
        # Now delete the quiz
        db.session.delete(quiz)
        db.session.commit()
        
        return jsonify({"message": "Quiz and all associated data deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error deleting quiz: {str(e)}"}), 500

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