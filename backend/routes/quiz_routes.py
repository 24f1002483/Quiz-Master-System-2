from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.model import db, Subject, Chapter, Quiz, Question, User

quiz_bp = Blueprint('quiz', __name__, url_prefix='/api/quiz')

# COMMENTED OUT - Duplicate of optimized route in /api/v2/subjects
# @quiz_bp.route('/subjects', methods=['GET'])
# @jwt_required()
# def get_subjects():
#     subjects = Subject.query.all()
#     return jsonify([subject.serialize() for subject in subjects])

@quiz_bp.route('/chapters/<int:subject_id>', methods=['GET'])
@jwt_required()
def get_chapters(subject_id):
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return jsonify([chapter.serialize() for chapter in chapters])

@quiz_bp.route('/chapters', methods=['GET'])
@jwt_required()
def get_all_chapters():
    chapters = Chapter.query.all()
    return jsonify([chapter.serialize() for chapter in chapters])

@quiz_bp.route('/quizzes/chapter/<int:chapter_id>', methods=['GET'])
@jwt_required()
def get_quizzes_by_chapter(chapter_id):
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    return jsonify([quiz.serialize() for quiz in quizzes])

# COMMENTED OUT - Duplicate of optimized route in /api/v2/quizzes
# @quiz_bp.route('/quizzes', methods=['GET'])
# @jwt_required()
# def get_all_quizzes():
#     quizzes = Quiz.query.all()
#     return jsonify([quiz.serialize() for quiz in quizzes])

# COMMENTED OUT - Duplicate of optimized route in /api/v2/quizzes/<int:quiz_id>
# @quiz_bp.route('/quizzes/<int:quiz_id>', methods=['GET'])
# @jwt_required()
# def get_quiz_by_id(quiz_id):
#     quiz = Quiz.query.get_or_404(quiz_id)
#     return jsonify(quiz.serialize())

@quiz_bp.route('/questions/<int:quiz_id>', methods=['GET'])
@jwt_required()
def get_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions
    return jsonify([question.serialize() for question in questions])

@quiz_bp.route('/chapter', methods=['POST'])
@jwt_required()
def add_chapter():
    data = request.get_json()
    new_chapter = Chapter(
        name=data['name'],
        subject_id=data['subject_id']
    )
    db.session.add(new_chapter)
    db.session.commit()
    return jsonify(new_chapter.serialize()), 201

@quiz_bp.route('/quiz', methods=['POST'])
@jwt_required()
def add_quiz():
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
        time_duration=data['duration']
    )
    db.session.add(new_quiz)
    db.session.commit()
    return jsonify(new_quiz.serialize()), 201

@quiz_bp.route('/question', methods=['POST'])
@jwt_required()
def add_question():
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

# Similar DELETE and PUT endpoints for all entities