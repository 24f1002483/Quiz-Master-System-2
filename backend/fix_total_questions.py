#!/usr/bin/env python3
"""
Script to fix existing quiz attempts that have null total_questions values
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.model import db, UserQuizAttempt, Quiz

# Create a minimal Flask app for the database operations
app = Flask(__name__)
# Use the correct database path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def fix_total_questions():
    print("🔧 Fixing total_questions for existing quiz attempts...")
    
    with app.app_context():
        # Get all attempts with null total_questions
        attempts = UserQuizAttempt.query.filter(
            (UserQuizAttempt.total_questions.is_(None)) | 
            (UserQuizAttempt.total_questions == 0)
        ).all()
        
        print(f"Found {len(attempts)} attempts with missing total_questions")
        
        fixed_count = 0
        for attempt in attempts:
            try:
                # Get the quiz and count its questions
                quiz = Quiz.query.get(attempt.quiz_id)
                if quiz:
                    total_questions = len(quiz.questions)
                    attempt.total_questions = total_questions
                    print(f"Fixed attempt {attempt.id}: quiz '{quiz.title}' has {total_questions} questions")
                    fixed_count += 1
                else:
                    print(f"Warning: Quiz {attempt.quiz_id} not found for attempt {attempt.id}")
            except Exception as e:
                print(f"Error fixing attempt {attempt.id}: {e}")
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"✅ Successfully fixed {fixed_count} attempts")
        except Exception as e:
            print(f"❌ Error committing changes: {e}")
            db.session.rollback()
        
        # Show summary of all attempts
        print("\n📊 Summary of all attempts:")
        all_attempts = UserQuizAttempt.query.all()
        for attempt in all_attempts:
            quiz = Quiz.query.get(attempt.quiz_id)
            quiz_title = quiz.title if quiz else "Unknown Quiz"
            print(f"Attempt {attempt.id}: {quiz_title} - Score: {attempt.score}/{attempt.total_questions} - Status: {attempt.status}")

if __name__ == "__main__":
    fix_total_questions() 