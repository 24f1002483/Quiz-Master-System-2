#!/usr/bin/env python3
"""
Check if admin user exists in the database
"""

from app import create_app
from models.model import User, Role

def check_admin_user():
    app = create_app()
    with app.app_context():
        # Check if admin user exists
        admin = User.query.filter_by(role=Role.ADMIN).first()
        
        if admin:
            print(f"Admin user found:")
            print(f"  ID: {admin.id}")
            print(f"  Username: {admin.username}")
            print(f"  Full Name: {admin.full_name}")
            print(f"  Role: {admin.role}")
            print(f"  Is active: {admin.is_active}")
            
            # Test password
            if admin.check_password('admin123'):
                print("  Password check: ✅ admin123 is correct")
            else:
                print("  Password check: ❌ admin123 is incorrect")
        else:
            print("No admin user found!")
            
            # Create admin user
            print("Creating admin user...")
            admin = User(
                username='admin@quizmaster.com',
                full_name='Admin',
                qualification='Admin',
                dob=None,
                role=Role.ADMIN
            )
            admin.set_password('admin123')
            
            from models.model import db
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")

if __name__ == '__main__':
    check_admin_user() 