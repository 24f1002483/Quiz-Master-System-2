#!/usr/bin/env python3
"""
Comprehensive fix for quiz attempts - addresses total_questions and date issues
"""

import sqlite3
import os
from datetime import datetime

def comprehensive_fix():
    print("🔧 Running comprehensive fix for quiz attempts...")
    
    # Find database
    db_path = 'instance/quiz.db'
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    print(f"✅ Found database at: {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Fix total_questions for all attempts
        print("\n1. Fixing total_questions...")
        
        # Get all quiz attempts
        cursor.execute("SELECT id, quiz_id, total_questions, score, end_time FROM user_quiz_attempts")
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
            print(f"  Quiz {quiz_id} ({quiz_title}): {question_count} questions")
        
        # Fix attempts with missing total_questions
        fixed_count = 0
        for attempt_id, quiz_id, total_questions, score, end_time in attempts:
            if total_questions is None or total_questions == 0:
                if quiz_id in quiz_question_counts:
                    new_total = quiz_question_counts[quiz_id]
                    cursor.execute(
                        "UPDATE user_quiz_attempts SET total_questions = ? WHERE id = ?",
                        (new_total, attempt_id)
                    )
                    print(f"  Fixed attempt {attempt_id}: set total_questions to {new_total}")
                    fixed_count += 1
                else:
                    print(f"  Warning: Quiz {quiz_id} not found for attempt {attempt_id}")
        
        print(f"✅ Fixed {fixed_count} attempts with missing total_questions")
        
        # 2. Fix date formatting issues
        print("\n2. Fixing date formatting...")
        
        # Check for attempts with invalid dates
        cursor.execute("SELECT id, end_time FROM user_quiz_attempts WHERE end_time IS NOT NULL")
        date_attempts = cursor.fetchall()
        
        date_fixed_count = 0
        for attempt_id, end_time in date_attempts:
            try:
                # Try to parse the date
                if end_time:
                    # If it's already a valid datetime string, leave it
                    datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                else:
                    # Set a default date if null
                    cursor.execute(
                        "UPDATE user_quiz_attempts SET end_time = ? WHERE id = ?",
                        (datetime.utcnow().isoformat(), attempt_id)
                    )
                    date_fixed_count += 1
            except ValueError:
                # Invalid date format, fix it
                cursor.execute(
                    "UPDATE user_quiz_attempts SET end_time = ? WHERE id = ?",
                    (datetime.utcnow().isoformat(), attempt_id)
                )
                print(f"  Fixed invalid date for attempt {attempt_id}")
                date_fixed_count += 1
        
        print(f"✅ Fixed {date_fixed_count} attempts with date issues")
        
        # 3. Update quiz titles if they're corrupted
        print("\n3. Checking quiz titles...")
        
        cursor.execute("SELECT id, title FROM quizzes")
        all_quizzes = cursor.fetchall()
        
        for quiz_id, title in all_quizzes:
            if title and ('\\' in title or title.startswith('qui')):
                # Fix corrupted titles
                new_title = f"Quiz {quiz_id}"
                cursor.execute(
                    "UPDATE quizzes SET title = ? WHERE id = ?",
                    (new_title, quiz_id)
                )
                print(f"  Fixed quiz {quiz_id} title from '{title}' to '{new_title}'")
        
        # Commit all changes
        conn.commit()
        print("\n✅ All changes committed successfully!")
        
        # 4. Show final summary
        print("\n📊 Final Summary:")
        cursor.execute("""
            SELECT ua.id, ua.quiz_id, q.title, ua.total_questions, ua.score, ua.status, ua.end_time 
            FROM user_quiz_attempts ua 
            LEFT JOIN quizzes q ON ua.quiz_id = q.id
            ORDER BY ua.id
        """)
        final_attempts = cursor.fetchall()
        
        for attempt_id, quiz_id, quiz_title, total_questions, score, status, end_time in final_attempts:
            quiz_title = quiz_title or f"Quiz {quiz_id}"
            date_str = "No date" if not end_time else end_time[:10]  # Just the date part
            print(f"  Attempt {attempt_id}: {quiz_title} - Score: {score}/{total_questions} - Status: {status} - Date: {date_str}")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    comprehensive_fix() 