#!/usr/bin/env python3
"""
Migration script to update the questions table:
1. Add question_title column
2. Remove admin_id column
3. Preserve existing data
"""

import sqlite3
import os
from datetime import datetime

def migrate_questions():
    db_path = 'instance/quiz.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Starting questions table migration...")
        
        # Check if questions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions'")
        if not cursor.fetchone():
            print("Questions table does not exist. Creating new table...")
            create_new_questions_table(cursor)
        else:
            print("Questions table exists. Migrating existing data...")
            migrate_existing_questions_table(cursor)
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

def create_new_questions_table(cursor):
    """Create a new questions table with the updated schema"""
    cursor.execute("""
        CREATE TABLE questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_title VARCHAR(200) NOT NULL,
            question_statement TEXT NOT NULL,
            option1 VARCHAR(255) NOT NULL,
            option2 VARCHAR(255) NOT NULL,
            option3 VARCHAR(255),
            option4 VARCHAR(255),
            correct_answer INTEGER NOT NULL,
            explanation TEXT,
            difficulty INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME
        )
    """)
    print("New questions table created.")

def migrate_existing_questions_table(cursor):
    """Migrate existing questions table by adding question_title and removing admin_id"""
    
    # Check if question_title column already exists
    cursor.execute("PRAGMA table_info(questions)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'question_title' not in columns:
        print("Adding question_title column...")
        cursor.execute("ALTER TABLE questions ADD COLUMN question_title VARCHAR(200)")
        
        # Update existing questions to have a default title based on question_statement
        cursor.execute("""
            UPDATE questions 
            SET question_title = CASE 
                WHEN LENGTH(question_statement) > 50 
                THEN SUBSTR(question_statement, 1, 50) || '...'
                ELSE question_statement 
            END
            WHERE question_title IS NULL OR question_title = ''
        """)
        print("Updated existing questions with default titles.")
    
    # Check if admin_id column exists and remove it
    if 'admin_id' in columns:
        print("Removing admin_id column...")
        # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
        
        # Get all data from the current table
        cursor.execute("SELECT id, question_title, question_statement, option1, option2, option3, option4, correct_answer, explanation, difficulty, created_at, updated_at FROM questions")
        questions_data = cursor.fetchall()
        
        # Drop the old table
        cursor.execute("DROP TABLE questions")
        
        # Create new table without admin_id
        cursor.execute("""
            CREATE TABLE questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_title VARCHAR(200) NOT NULL,
                question_statement TEXT NOT NULL,
                option1 VARCHAR(255) NOT NULL,
                option2 VARCHAR(255) NOT NULL,
                option3 VARCHAR(255),
                option4 VARCHAR(255),
                correct_answer INTEGER NOT NULL,
                explanation TEXT,
                difficulty INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME
            )
        """)
        
        # Reinsert the data
        cursor.executemany("""
            INSERT INTO questions (id, question_title, question_statement, option1, option2, option3, option4, correct_answer, explanation, difficulty, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, questions_data)
        
        print("Recreated questions table without admin_id column.")
    
    # Update the quiz_questions association table if it exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='quiz_questions'")
    if cursor.fetchone():
        print("quiz_questions association table exists - no changes needed.")
    
    print("Migration of existing questions table completed.")

if __name__ == "__main__":
    migrate_questions() 