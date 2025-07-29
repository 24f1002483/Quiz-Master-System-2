from app import create_app
from models.model import db, User, Role, Subject, Chapter, Quiz, Question
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    print("Creating sample data...")
    
    # Create admin user if not exists
    admin = User.query.filter_by(role=Role.ADMIN).first()
    if not admin:
        admin = User(
            username='admin@quizmaster.com',
            email='admin@quizmaster.com',
            full_name='Admin User',
            qualification='Administrator',
            role=Role.ADMIN
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Created admin user")
    
    # Create subjects
    subjects_data = [
        {'name': 'Mathematics', 'description': 'Advanced mathematics topics'},
        {'name': 'Science', 'description': 'General science concepts'},
        {'name': 'English', 'description': 'English language and literature'}
    ]
    
    subjects = []
    for subj_data in subjects_data:
        subject = Subject.query.filter_by(name=subj_data['name']).first()
        if not subject:
            subject = Subject(
                name=subj_data['name'],
                description=subj_data['description'],
                admin_id=admin.id
            )
            db.session.add(subject)
            subjects.append(subject)
        else:
            subjects.append(subject)
    
    db.session.commit()
    print(f"Created {len(subjects)} subjects")
    
    # Create chapters
    chapters_data = [
        {'name': 'Algebra', 'subject': 'Mathematics', 'sequence': 1},
        {'name': 'Geometry', 'subject': 'Mathematics', 'sequence': 2},
        {'name': 'Physics', 'subject': 'Science', 'sequence': 1},
        {'name': 'Chemistry', 'subject': 'Science', 'sequence': 2},
        {'name': 'Grammar', 'subject': 'English', 'sequence': 1},
        {'name': 'Literature', 'subject': 'English', 'sequence': 2}
    ]
    
    chapters = []
    for chap_data in chapters_data:
        subject = Subject.query.filter_by(name=chap_data['subject']).first()
        if subject:
            chapter = Chapter.query.filter_by(name=chap_data['name'], subject_id=subject.id).first()
            if not chapter:
                chapter = Chapter(
                    name=chap_data['name'],
                    description=f"Chapter about {chap_data['name']}",
                    sequence=chap_data['sequence'],
                    subject_id=subject.id
                )
                db.session.add(chapter)
                chapters.append(chapter)
            else:
                chapters.append(chapter)
    
    db.session.commit()
    print(f"Created {len(chapters)} chapters")
    
    # Create quizzes with current dates
    now = datetime.utcnow()
    start_date = now - timedelta(hours=1)  # Started 1 hour ago
    end_date = now + timedelta(days=7)     # Ends in 7 days
    
    quizzes_data = [
        {'title': 'Basic Algebra Quiz', 'chapter': 'Algebra', 'duration': 30},
        {'title': 'Geometry Fundamentals', 'chapter': 'Geometry', 'duration': 45},
        {'title': 'Physics Basics', 'chapter': 'Physics', 'duration': 60},
        {'title': 'Chemistry Introduction', 'chapter': 'Chemistry', 'duration': 30},
        {'title': 'English Grammar Test', 'chapter': 'Grammar', 'duration': 45},
        {'title': 'Literature Quiz', 'chapter': 'Literature', 'duration': 60}
    ]
    
    quizzes = []
    for quiz_data in quizzes_data:
        chapter = Chapter.query.filter_by(name=quiz_data['chapter']).first()
        if chapter:
            quiz = Quiz.query.filter_by(title=quiz_data['title']).first()
            if not quiz:
                quiz = Quiz(
                    title=quiz_data['title'],
                    description=f"Quiz on {quiz_data['chapter']}",
                    chapter_id=chapter.id,
                    start_date=start_date,
                    end_date=end_date,
                    time_duration=quiz_data['duration'],  # Store in minutes
                    is_active=True
                )
                db.session.add(quiz)
                quizzes.append(quiz)
            else:
                quizzes.append(quiz)
    
    db.session.commit()
    print(f"Created {len(quizzes)} quizzes")
    
    # Create questions for each quiz
    for quiz in quizzes:
        if len(quiz.questions) == 0:  # Only add questions if quiz doesn't have any
            questions_data = [
                {
                    'question_title': f'Question 1 - {quiz.title}',
                    'question_statement': f'What is the main topic of {quiz.title}?',
                    'option1': 'Option A',
                    'option2': 'Option B', 
                    'option3': 'Option C',
                    'option4': 'Option D',
                    'correct_answer': 1
                },
                {
                    'question_title': f'Question 2 - {quiz.title}',
                    'question_statement': f'Which concept is most important in {quiz.title}?',
                    'option1': 'Concept A',
                    'option2': 'Concept B',
                    'option3': 'Concept C', 
                    'option4': 'Concept D',
                    'correct_answer': 2
                },
                {
                    'question_title': f'Question 3 - {quiz.title}',
                    'question_statement': f'How would you apply knowledge from {quiz.title}?',
                    'option1': 'Method A',
                    'option2': 'Method B',
                    'option3': 'Method C',
                    'option4': 'Method D', 
                    'correct_answer': 3
                }
            ]
            
            for q_data in questions_data:
                question = Question(
                    quiz_id=quiz.id,
                    question_title=q_data['question_title'],
                    question_statement=q_data['question_statement'],
                    option1=q_data['option1'],
                    option2=q_data['option2'],
                    option3=q_data['option3'],
                    option4=q_data['option4'],
                    correct_answer=q_data['correct_answer'],
                    explanation=f"This is the correct answer for {q_data['question_title']}"
                )
                db.session.add(question)
    
    db.session.commit()
    print("Created questions for all quizzes")
    
    print("Sample data creation completed!")
    print(f"Total subjects: {Subject.query.count()}")
    print(f"Total chapters: {Chapter.query.count()}")
    print(f"Total quizzes: {Quiz.query.count()}")
    print(f"Total questions: {Question.query.count()}") 