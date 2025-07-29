# Simple script to fix total_questions issue
# Run this in your Python console or as a script

import sqlite3
import os

def fix_total_questions():
    # Find the database file
    db_paths = [
        'quiz.db',
        'instance/quiz.db',
        '../instance/quiz.db',
        '../../instance/quiz.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ Database file not found!")
        print("Searched in:", db_paths)
        return
    
    print(f"✅ Found database at: {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all quiz attempts
    cursor.execute("SELECT id, quiz_id, total_questions, score FROM user_quiz_attempts")
    attempts = cursor.fetchall()
    
    print(f"Found {len(attempts)} quiz attempts")
    
    # Get quiz question counts
    cursor.execute("SELECT id, title FROM quizzes")
    quizzes = cursor.fetchall()
    quiz_question_counts = {}
    
    for quiz_id, quiz_title in quizzes:
        cursor.execute("SELECT COUNT(*) FROM questions WHERE quiz_id = ?", (quiz_id,))
        question_count = cursor.fetchone()[0]
        quiz_question_counts[quiz_id] = question_count
        print(f"Quiz {quiz_id} ({quiz_title}): {question_count} questions")
    
    # Fix attempts with missing total_questions
    fixed_count = 0
    for attempt_id, quiz_id, total_questions, score in attempts:
        if total_questions is None or total_questions == 0:
            if quiz_id in quiz_question_counts:
                new_total = quiz_question_counts[quiz_id]
                cursor.execute(
                    "UPDATE user_quiz_attempts SET total_questions = ? WHERE id = ?",
                    (new_total, attempt_id)
                )
                print(f"Fixed attempt {attempt_id}: set total_questions to {new_total}")
                fixed_count += 1
            else:
                print(f"Warning: Quiz {quiz_id} not found for attempt {attempt_id}")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"✅ Successfully fixed {fixed_count} attempts")
    
    # Show final summary
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, quiz_id, total_questions, score, status FROM user_quiz_attempts")
    final_attempts = cursor.fetchall()
    
    print("\n📊 Final Summary:")
    for attempt_id, quiz_id, total_questions, score, status in final_attempts:
        quiz_title = "Unknown"
        for qid, qtitle in quizzes:
            if qid == quiz_id:
                quiz_title = qtitle
                break
        print(f"Attempt {attempt_id}: {quiz_title} - Score: {score}/{total_questions} - Status: {status}")
    
    conn.close()

if __name__ == "__main__":
    fix_total_questions() 