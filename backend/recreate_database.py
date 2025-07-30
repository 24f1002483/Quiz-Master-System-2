#!/usr/bin/env python3
"""
Script to recreate database with correct schema
"""

from app import create_app
from models.model import db, User, Role
import os

def recreate_database():
    app = create_app()
    
    with app.app_context():
        try:
            print("Recreating database...")
            
            # Drop all tables
            db.drop_all()
            print("Dropped all tables")
            
            # Create all tables with new schema
            db.create_all()
            print("Created all tables with new schema")
            
            # Create default admin user
            admin_username = 'admin@quizmaster.com'
            admin_password = 'admin123'
            
            admin = User(
                username=admin_username,
                full_name='Admin',
                qualification='Admin',
                dob=None,
                role=Role.ADMIN,
                notification_preference='email',
                phone=None
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print("Created admin user successfully!")
            
            # Test the database
            users = User.query.all()
            print(f"Found {len(users)} users in database")
            
            # Test creating a regular user
            test_user = User(
                username='test@example.com',
                full_name='Test User',
                qualification='Student',
                notification_preference='email',
                phone='+1234567890'
            )
            db.session.add(test_user)
            db.session.commit()
            print("Created test user successfully!")
            
            print("Database recreation completed successfully!")
            
        except Exception as e:
            print(f"Error recreating database: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    recreate_database()