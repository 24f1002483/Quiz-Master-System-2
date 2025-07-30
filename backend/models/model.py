
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, time, timedelta
from enum import Enum
from sqlalchemy import or_, and_

# Initialize db only once
# (Assume db is initialized elsewhere in the app, or uncomment below if needed)
db = SQLAlchemy()

# --- ENUMS ---
class Role(Enum):
    USER = 'user'
    ADMIN = 'admin'

# --- ASSOCIATION TABLES ---
# Removed quiz_questions association table - questions now have direct quiz_id foreign key

# --- MODELS ---
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)  # email as username
    password_hash = db.Column(db.String(128))
    full_name = db.Column(db.String(120))
    qualification = db.Column(db.String(120))
    dob = db.Column(db.Date)
    role = db.Column(db.Enum(Role), default=Role.USER)
    is_active = db.Column(db.Boolean, default=True)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    notification_preference = db.Column(db.String(20), default='email')  # email, sms, gchat
    phone = db.Column(db.String(20))  # phone number for SMS notifications
    scores = db.relationship('Score', backref='user', lazy=True)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'qualification': self.qualification,
            'dob': self.dob.isoformat() if self.dob else None,
            'role': self.role.value,
            'is_active': self.is_active,
            'date_joined': self.date_joined.isoformat() if self.date_joined else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'notification_preference': self.notification_preference,
            'phone': self.phone
        }

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chapters = db.relationship('Chapter', backref='subject', lazy=True)
    creator = db.relationship('User', backref='created_subjects')
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'admin_id': self.admin_id,
            'chapters': [
                {
                    'id': chapter.id,
                    'name': chapter.name,
                    'description': chapter.description,
                    'sequence': chapter.sequence,
                    'questionCount': sum(len(quiz.questions) for quiz in chapter.quizzes) if chapter.quizzes else 0
                }
                for chapter in self.chapters
            ]
        }

class Chapter(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    sequence = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True)
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'sequence': self.sequence,
            'subject_id': self.subject_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    time_duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    questions = db.relationship('Question', backref='quiz', lazy=True)

    def is_available(self):
        now = datetime.utcnow()
        return self.is_active and self.start_date <= now <= self.end_date
    def time_remaining(self):
        if not self.is_available():
            return 0
        end_time = min(
            datetime.utcnow() + timedelta(minutes=self.time_duration),
            self.end_date
        )
        return (end_time - datetime.utcnow()).total_seconds()
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'chapter_id': self.chapter_id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'time_duration': self.time_duration,
            'is_active': self.is_active,
            'is_available': self.is_available(),
            'time_remaining': self.time_remaining(),
            'created_at': self.created_at.isoformat(),
            'questions': [question.serialize() for question in self.questions]
        }

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_title = db.Column(db.String(200), nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(255), nullable=False)
    option2 = db.Column(db.String(255), nullable=False)
    option3 = db.Column(db.String(255))
    option4 = db.Column(db.String(255))
    correct_answer = db.Column(db.Integer, nullable=False)
    explanation = db.Column(db.Text)
    difficulty = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def serialize(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'question_title': self.question_title,
            'question_statement': self.question_statement,
            'option1': self.option1,
            'option2': self.option2,
            'option3': self.option3,
            'option4': self.option4,
            'correct_answer': self.correct_answer,
            'explanation': self.explanation,
            'difficulty': self.difficulty,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    time_taken = db.Column(db.Integer)
    attempt_number = db.Column(db.Integer, default=1)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    passed = db.Column(db.Boolean)
    detailed_results = db.Column(db.JSON)
    def serialize(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'user_id': self.user_id,
            'score': self.score,
            'total_questions': self.total_questions,
            'percentage': self.percentage,
            'time_taken': self.time_taken,
            'attempt_number': self.attempt_number,
            'timestamp': self.timestamp.isoformat(),
            'passed': self.passed
        }

# --- SEARCH MIXINS ---
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

# --- QUIZ ATTEMPT & USER ANSWER ---
class UserQuizAttempt(db.Model):
    __tablename__ = 'user_quiz_attempts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    total_questions = db.Column(db.Integer)
    score = db.Column(db.Integer)
    status = db.Column(db.String(32), default='in_progress')
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    user = db.relationship('User', backref='quiz_attempts', lazy=True)
    quiz = db.relationship('Quiz', backref='user_attempts', lazy=True)
    answers = db.relationship('UserAnswer', backref='user_quiz_attempt', cascade='all, delete-orphan')
    
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'quiz_id': self.quiz_id,
            'total_questions': self.total_questions,
            'score': self.score,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }

class UserAnswer(db.Model):
    __tablename__ = 'user_answers'
    id = db.Column(db.Integer, primary_key=True)
    user_quiz_attempt_id = db.Column(
        db.Integer,
        db.ForeignKey('user_quiz_attempts.id', name='fk_user_answer_user_quiz_attempt_id'),
        nullable=False
    )
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    selected_option = db.Column(db.Integer)  # 1-4
    is_correct = db.Column(db.Boolean)
    time_spent = db.Column(db.Integer)  # in seconds
    question = db.relationship('Question', lazy=True)
    
    def serialize(self):
        return {
            'question_id': self.question_id,
            'question_content': getattr(self.question, 'question_statement', None),
            'selected_option': self.selected_option,
            'is_correct': self.is_correct,
            'time_spent': self.time_spent,
            'correct_answer': getattr(self.question, 'correct_answer', None),
            'options': [
                getattr(self.question, 'option1', None),
                getattr(self.question, 'option2', None),
                getattr(self.question, 'option3', None),
                getattr(self.question, 'option4', None)
            ]
        } 