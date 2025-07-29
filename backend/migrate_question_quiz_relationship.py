#!/usr/bin/env python3
"""
Migration script to change question-quiz relationship from many-to-many to one-to-many:
1. Add quiz_id column to questions table
2. Migrate existing relationships from quiz_questions table
3. Remove quiz_questions association table
"""

import sqlite3
import os
from datetime import datetime

def migrate_question_quiz_relationship():
    db_path = 'instance/quiz.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Starting question-quiz relationship migration...")
        
        # Check if quiz_questions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='quiz_questions'")
        quiz_questions_exists = cursor.fetchone()
        
        # Check if quiz_id column already exists in questions table
        cursor.execute("PRAGMA table_info(questions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'quiz_id' not in columns:
            print("Adding quiz_id column to questions table...")
            cursor.execute("ALTER TABLE questions ADD COLUMN quiz_id INTEGER")
            
            # If quiz_questions table exists, migrate the relationships
            if quiz_questions_exists:
                print("Migrating existing relationships from quiz_questions table...")
                cursor.execute("SELECT quiz_id, question_id FROM quiz_questions")
                relationships = cursor.fetchall()
                
                for quiz_id, question_id in relationships:
                    cursor.execute("UPDATE questions SET quiz_id = ? WHERE id = ?", (quiz_id, question_id))
                    print(f"Migrated question {question_id} to quiz {quiz_id}")
                
                # Remove the quiz_questions table
                print("Removing quiz_questions association table...")
                cursor.execute("DROP TABLE quiz_questions")
            else:
                print("No quiz_questions table found. Setting default quiz_id for existing questions...")
                # Set a default quiz_id for existing questions (you may want to adjust this)
                cursor.execute("UPDATE questions SET quiz_id = 1 WHERE quiz_id IS NULL")
        
        # Add foreign key constraint (SQLite doesn't support adding foreign keys to existing tables easily)
        # We'll rely on the application layer to maintain referential integrity
        
        conn.commit()
        print("Migration completed successfully!")
        
        # Verify the migration
        cursor.execute("PRAGMA table_info(questions)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'quiz_id' in columns:
            print("✓ quiz_id column successfully added to questions table")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='quiz_questions'")
        if not cursor.fetchone():
            print("✓ quiz_questions association table successfully removed")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_question_quiz_relationship() 