from app import app, db
from models.model import Quiz
from datetime import datetime, timedelta

def migrate_quiz_dates():
    with app.app_context():
        # Get all existing quizzes
        quizzes = Quiz.query.all()
        
        for quiz in quizzes:
            # For existing quizzes, use the start_date as the date_of_quiz
            # This preserves the original quiz timing
            quiz.date_of_quiz = quiz.start_date
            
        # Commit the changes
        db.session.commit()
        print(f"Migrated {len(quizzes)} quizzes to use date_of_quiz")

if __name__ == "__main__":
    migrate_quiz_dates() 