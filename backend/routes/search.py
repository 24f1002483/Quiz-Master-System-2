from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.model import db, Quiz, User, Score, Subject, Chapter, Question
from sqlalchemy import or_

search_bp = Blueprint('search', __name__)

@search_bp.route('/quizzes', methods=['GET'])
@jwt_required()
def search_quizzes():
    """Search quizzes by title, description, or ID"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    try:
        quizzes = Quiz.query.filter(
            or_(
                Quiz.title.ilike(f'%{query}%'),
                Quiz.description.ilike(f'%{query}%'),
                Quiz.id.cast(db.String).ilike(f'%{query}%')
            )
        ).limit(50).all()
        
        return jsonify([quiz.serialize() for quiz in quizzes])
    except Exception as e:
        print(f"Error searching quizzes: {e}")
        return jsonify([])

@search_bp.route('/users', methods=['GET'])
@jwt_required()
def search_users():
    """Search users by username, email, or ID (admin only)"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    try:
        # Check if current user is admin
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user or current_user.role.value != 'admin':
            return jsonify([])
        
        users = User.query.filter(
            or_(
                User.username.ilike(f'%{query}%'),
                User.full_name.ilike(f'%{query}%'),
                User.id.cast(db.String).ilike(f'%{query}%')
            )
        ).limit(50).all()
        
        return jsonify([user.serialize() for user in users])
    except Exception as e:
        print(f"Error searching users: {e}")
        return jsonify([])

@search_bp.route('/scores', methods=['GET'])
@jwt_required()
def search_scores():
    """Search scores by quiz title, user, or score values"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Build query based on user role
        if current_user.role.value == 'admin':
            # Admin can see all scores
            scores = Score.query.join(Quiz).filter(
                or_(
                    Quiz.title.ilike(f'%{query}%'),
                    Score.id.cast(db.String).ilike(f'%{query}%'),
                    Score.score.cast(db.String).ilike(f'%{query}%'),
                    Score.total_questions.cast(db.String).ilike(f'%{query}%')
                )
            ).limit(50).all()
        else:
            # Regular users can only see their own scores
            scores = Score.query.join(Quiz).filter(
                Score.user_id == current_user_id,
                or_(
                    Quiz.title.ilike(f'%{query}%'),
                    Score.id.cast(db.String).ilike(f'%{query}%'),
                    Score.score.cast(db.String).ilike(f'%{query}%'),
                    Score.total_questions.cast(db.String).ilike(f'%{query}%')
                )
            ).limit(50).all()
        
        return jsonify([score.serialize() for score in scores])
    except Exception as e:
        print(f"Error searching scores: {e}")
        return jsonify([])

@search_bp.route('/subjects', methods=['GET'])
@jwt_required()
def search_subjects():
    """Search subjects by name, code, or description"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    try:
        subjects = Subject.query.filter(
            or_(
                Subject.name.ilike(f'%{query}%'),
                Subject.description.ilike(f'%{query}%'),
                Subject.id.cast(db.String).ilike(f'%{query}%')
            )
        ).limit(50).all()
        
        return jsonify([subject.serialize() for subject in subjects])
    except Exception as e:
        print(f"Error searching subjects: {e}")
        return jsonify([])

@search_bp.route('/chapters', methods=['GET'])
@jwt_required()
def search_chapters():
    """Search chapters by title, description, or subject"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    try:
        chapters = Chapter.query.join(Subject).filter(
            or_(
                Chapter.name.ilike(f'%{query}%'),
                Chapter.description.ilike(f'%{query}%'),
                Chapter.sequence.cast(db.String).ilike(f'%{query}%'),
                Subject.name.ilike(f'%{query}%'),
                Chapter.id.cast(db.String).ilike(f'%{query}%')
            )
        ).limit(50).all()
        
        # Add subject name to each chapter
        results = []
        for chapter in chapters:
            chapter_data = chapter.serialize()
            chapter_data['subject_name'] = chapter.subject.name if chapter.subject else 'Unknown'
            results.append(chapter_data)
        
        return jsonify(results)
    except Exception as e:
        print(f"Error searching chapters: {e}")
        return jsonify([])

@search_bp.route('/questions', methods=['GET'])
@jwt_required()
def search_questions():
    """Search questions by text, type, subject, or chapter"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    try:
        questions = Question.query.join(Quiz).join(Chapter).join(Subject).filter(
            or_(
                Question.question_title.ilike(f'%{query}%'),
                Question.question_statement.ilike(f'%{query}%'),
                Question.difficulty.cast(db.String).ilike(f'%{query}%'),
                Chapter.name.ilike(f'%{query}%'),
                Subject.name.ilike(f'%{query}%'),
                Question.id.cast(db.String).ilike(f'%{query}%')
            )
        ).limit(50).all()
        
        # Add subject and chapter info to each question
        results = []
        for question in questions:
            question_data = question.serialize()
            question_data['subject_name'] = question.quiz.chapter.subject.name if question.quiz and question.quiz.chapter and question.quiz.chapter.subject else 'Unknown'
            question_data['chapter_title'] = question.quiz.chapter.name if question.quiz and question.quiz.chapter else 'Unknown'
            results.append(question_data)
        
        return jsonify(results)
    except Exception as e:
        print(f"Error searching questions: {e}")
        return jsonify([])