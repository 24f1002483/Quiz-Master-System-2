from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.model import User, Question, Chapter, Quiz, Subject, Score, UserAnswer, UserQuizAttempt, db
from datetime import datetime

api_routes_bp = Blueprint('api_routes', __name__)

@api_routes_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (admin only)"""
    try:
        users = User.query.all()
        return jsonify([u.serialize() for u in users]), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching users', 'error': str(e)}), 500

@api_routes_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    """Create a new user (admin only)"""
    try:
        data = request.get_json()
        user = User(
            username=data.get('username'),
            full_name=data.get('full_name'),
            qualification=data.get('qualification'),
            role=data.get('role', 'user')
        )
        user.set_password(data.get('password'))
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User created successfully', 'user': user.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating user', 'error': str(e)}), 500

@api_routes_bp.route('/users/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    """Update a user (admin only)"""
    try:
        user = User.query.get_or_404(id)
        data = request.get_json()
        
        if 'username' in data:
            user.username = data['username']
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'qualification' in data:
            user.qualification = data['qualification']
        if 'role' in data:
            user.role = data['role']
        if 'password' in data:
            user.set_password(data['password'])
            
        db.session.commit()
        return jsonify({'message': 'User updated successfully', 'user': user.serialize()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating user', 'error': str(e)}), 500

@api_routes_bp.route('/users/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    """Delete a user (admin only)"""
    try:
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting user', 'error': str(e)}), 500

@api_routes_bp.route('/questions', methods=['GET'])
@jwt_required()
def get_questions():
    """Get all questions (admin only)"""
    try:
        questions = Question.query.all()
        return jsonify([q.serialize() for q in questions]), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching questions', 'error': str(e)}), 500

@api_routes_bp.route('/questions', methods=['POST'])
@jwt_required()
def create_question():
    """Create a new question (admin only)"""
    try:
        data = request.get_json()
        question = Question(
            text=data.get('text'),
            option_a=data.get('option_a'),
            option_b=data.get('option_b'),
            option_c=data.get('option_c'),
            option_d=data.get('option_d'),
            correct_answer=data.get('correct_answer'),
            explanation=data.get('explanation'),
            quiz_id=data.get('quiz_id')
        )
        db.session.add(question)
        db.session.commit()
        return jsonify({'message': 'Question created successfully', 'question': question.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating question', 'error': str(e)}), 500

@api_routes_bp.route('/questions/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_question(id):
    """Delete a question (admin only)"""
    try:
        question = Question.query.get_or_404(id)
        db.session.delete(question)
        db.session.commit()
        return jsonify({'message': 'Question deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting question', 'error': str(e)}), 500

@api_routes_bp.route('/chapters', methods=['GET'])
@jwt_required()
def get_chapters():
    """Get all chapters (admin only)"""
    try:
        chapters = Chapter.query.all()
        return jsonify([c.serialize() for c in chapters]), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching chapters', 'error': str(e)}), 500

@api_routes_bp.route('/chapters', methods=['POST'])
@jwt_required()
def create_chapter():
    """Create a new chapter (admin only)"""
    try:
        data = request.get_json()
        chapter = Chapter(
            name=data.get('name'),
            description=data.get('description'),
            subject_id=data.get('subject_id')
        )
        db.session.add(chapter)
        db.session.commit()
        return jsonify({'message': 'Chapter created successfully', 'chapter': chapter.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating chapter', 'error': str(e)}), 500

@api_routes_bp.route('/chapters/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_chapter(id):
    """Delete a chapter (admin only)"""
    try:
        chapter = Chapter.query.get_or_404(id)
        db.session.delete(chapter)
        db.session.commit()
        return jsonify({'message': 'Chapter deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting chapter', 'error': str(e)}), 500

@api_routes_bp.route('/quizzes', methods=['GET'])
@jwt_required()
def get_quizzes():
    """Get all quizzes (admin only)"""
    try:
        quizzes = Quiz.query.all()
        return jsonify([q.serialize() for q in quizzes]), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching quizzes', 'error': str(e)}), 500

@api_routes_bp.route('/subjects', methods=['GET'])
@jwt_required()
def get_subjects():
    """Get all subjects (admin only)"""
    try:
        subjects = Subject.query.all()
        return jsonify([s.serialize() for s in subjects]), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching subjects', 'error': str(e)}), 500

@api_routes_bp.route('/subjects', methods=['POST'])
@jwt_required()
def create_subject():
    """Create a new subject (admin only)"""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        subject = Subject(
            name=data.get('name'),
            description=data.get('description'),
            admin_id=current_user_id
        )
        db.session.add(subject)
        db.session.commit()
        return jsonify({'message': 'Subject created successfully', 'subject': subject.serialize()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating subject', 'error': str(e)}), 500

@api_routes_bp.route('/subjects/<int:id>', methods=['PUT'])
@jwt_required()
def update_subject(id):
    """Update a subject (admin only)"""
    try:
        subject = Subject.query.get_or_404(id)
        data = request.get_json()
        
        if 'name' in data:
            subject.name = data['name']
        if 'description' in data:
            subject.description = data['description']
        if 'is_active' in data:
            subject.is_active = data['is_active']
            
        db.session.commit()
        return jsonify({'message': 'Subject updated successfully', 'subject': subject.serialize()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating subject', 'error': str(e)}), 500

@api_routes_bp.route('/subjects/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_subject(id):
    """Delete a subject (admin only)"""
    try:
        subject = Subject.query.get_or_404(id)
        
        # Delete all related data in the correct order
        # First delete all questions from quizzes in this subject's chapters
        for chapter in subject.chapters:
            for quiz in chapter.quizzes:
                # Delete user answers first (for questions in this quiz)
                questions = Question.query.filter_by(quiz_id=quiz.id).all()
                for question in questions:
                    UserAnswer.query.filter_by(question_id=question.id).delete()
                # Delete user quiz attempts
                UserQuizAttempt.query.filter_by(quiz_id=quiz.id).delete()
                # Delete questions
                Question.query.filter_by(quiz_id=quiz.id).delete()
                # Delete scores
                Score.query.filter_by(quiz_id=quiz.id).delete()
            # Delete quizzes
            Quiz.query.filter_by(chapter_id=chapter.id).delete()
        # Delete chapters
        Chapter.query.filter_by(subject_id=id).delete()
        # Finally delete the subject
        db.session.delete(subject)
        db.session.commit()
        return jsonify({'message': 'Subject deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting subject', 'error': str(e)}), 500 