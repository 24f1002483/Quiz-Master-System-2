from app import create_app
from models.model import db

app = create_app()

with app.app_context():
    try:
        print("Testing database connection...")
        db.create_all()
        print("Database tables created successfully!")
        
        # Test basic query
        from models.model import User
        users = User.query.all()
        print(f"Found {len(users)} users in database")
        
    except Exception as e:
        print(f"Database error: {str(e)}")
        import traceback
        traceback.print_exc()