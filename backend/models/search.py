from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_
from datetime import datetime
from .model import db

class SearchMixin:
    @classmethod
    def search(cls, query, user_role='user', filters=None):
        """
        Base search method for all models
        """
        raise NotImplementedError("Search method must be implemented")

class UserSearch(SearchMixin, db.Model):
    __tablename__ = 'users'

    @classmethod
    def search(cls, query, user_role='user', filters=None):
        if user_role != 'admin':
            return []
        
        search_conditions = []
        if query:
            search_conditions.append(
                or_(
                    cls.username.ilike(f'%{query}%'),
                    cls.full_name.ilike(f'%{query}%')
                )
            )
        
        if filters:
            if 'is_active' in filters:
                search_conditions.append(cls.is_active == filters['is_active'])
        
        return cls.query.filter(and_(*search_conditions)).limit(50).all()

class SubjectSearch(SearchMixin, db.Model):
    __tablename__ = 'subjects'

    @classmethod
    def search(cls, query, user_role='user', filters=None):
        search_conditions = []
        if query:
            search_conditions.append(
                or_(
                    cls.name.ilike(f'%{query}%'),
                    cls.description.ilike(f'%{query}%')
                )
            )
        
        if filters:
            if 'is_active' in filters:
                search_conditions.append(cls.is_active == filters['is_active'])
        
        return cls.query.filter(and_(*search_conditions)).limit(50).all()

class QuizSearch(SearchMixin, db.Model):
    __tablename__ = 'quizzes'

    @classmethod
    def search(cls, query, user_role='user', filters=None):
        search_conditions = []
        
        if query:
            search_conditions.append(
                or_(
                    cls.title.ilike(f'%{query}%'),
                    cls.description.ilike(f'%{query}%')
                )
            )
        
        if user_role == 'user':
            search_conditions.append(cls.is_active == True)
            search_conditions.append(cls.start_date <= datetime.utcnow())
            search_conditions.append(cls.end_date >= datetime.utcnow())
        
        if filters:
            if 'subject_id' in filters:
                search_conditions.append(cls.chapter.has(subject_id=filters['subject_id']))
            if 'chapter_id' in filters:
                search_conditions.append(cls.chapter_id == filters['chapter_id'])
        
        return cls.query.filter(and_(*search_conditions)).limit(50).all()

class QuestionSearch(SearchMixin, db.Model):
    __tablename__ = 'questions'

    @classmethod
    def search(cls, query, user_role='user', filters=None):
        if user_role != 'admin':
            return []
        
        search_conditions = []
        if query:
            search_conditions.append(
                or_(
                    cls.question_statement.ilike(f'%{query}%'),
                    cls.explanation.ilike(f'%{query}%')
                )
            )
        
        if filters:
            if 'quiz_id' in filters:
                search_conditions.append(cls.quiz_id == filters['quiz_id'])
            if 'difficulty' in filters:
                search_conditions.append(cls.difficulty == filters['difficulty'])
        
        return cls.query.filter(and_(*search_conditions)).limit(50).all()