#!/usr/bin/env python3
"""
Create a formatted text file that can be easily converted to DOCX
"""

def create_formatted_report():
    """Create a formatted text report that can be copied to Word"""
    
    report_content = """
QUIZ MASTER PROJECT REPORT
==========================

STUDENT DETAILS
---------------
• Project Name: Quiz Master 2
• Project Type: Full-Stack Web Application
• Technology Stack: Python Flask (Backend) + Vue.js (Frontend)
• Database: SQLite with SQLAlchemy ORM
• Additional Technologies: Redis, Celery, Docker

PROJECT DETAILS
---------------

Problem Statement:
The Quiz Master project aims to create a comprehensive online quiz management system that allows:
• Administrators to create and manage subjects, chapters, quizzes, and questions
• Students/Users to take quizzes, view their scores, and track their progress
• Real-time quiz taking with timer functionality and automatic submission
• Score tracking and analytics for both users and administrators
• Search functionality across all content
• Session management with automatic timeout and warnings

Approach to Problem Statement:

1. Architecture Design:
   • Backend: Flask REST API with modular blueprint structure
   • Frontend: Vue.js 3 with component-based architecture
   • Database: SQLite with proper relationships and constraints
   • Caching: Redis for performance optimization
   • Background Tasks: Celery for scheduled operations

2. Key Features Implemented:
   • User Authentication & Authorization: JWT-based authentication with role-based access control
   • Quiz Management: Complete CRUD operations for subjects, chapters, quizzes, and questions
   • Real-time Quiz Taking: Timer-based quiz interface with automatic submission
   • Score Tracking: Detailed score analytics with attempt history
   • Search Functionality: Comprehensive search across all entities
   • Session Management: Automatic session timeout with user warnings
   • Admin Dashboard: Complete administrative interface for content management

3. Technical Implementation:
   • Security: Password hashing, JWT tokens, CORS configuration
   • Performance: Redis caching, rate limiting, optimized database queries
   • Scalability: Docker containerization, background task processing
   • User Experience: Responsive design, real-time updates, intuitive navigation

FRAMEWORKS AND LIBRARIES USED
-----------------------------

Backend Technologies:
• Flask: Web framework for building REST APIs
• SQLAlchemy: Object-Relational Mapping (ORM) for database operations
• Flask-JWT-Extended: JWT token management for authentication
• Flask-CORS: Cross-Origin Resource Sharing support
• Flask-Migrate: Database migration management
• Werkzeug: Security utilities for password hashing
• Redis: In-memory data structure store for caching
• Celery: Distributed task queue for background jobs
• Pickle: Python object serialization for cache storage

Frontend Technologies:
• Vue.js 3: Progressive JavaScript framework
• Vue Router: Client-side routing for single-page application
• Axios: HTTP client for API communication
• ESLint: Code linting and formatting

Development & Deployment:
• Docker: Containerization for consistent deployment
• Docker Compose: Multi-container application orchestration
• SQLite: Lightweight database for development and testing

ER DIAGRAM
----------

Database Schema Overview:

Tables and Relationships:

1. USERS Table:
   - id (Primary Key)
   - username (Unique, email format)
   - password_hash
   - full_name
   - qualification
   - dob (date of birth)
   - role (enum: user/admin)
   - is_active
   - date_joined
   - last_login

2. SUBJECTS Table:
   - id (Primary Key)
   - name
   - description
   - created_at
   - updated_at
   - is_active
   - admin_id (Foreign Key to USERS)

3. CHAPTERS Table:
   - id (Primary Key)
   - name
   - description
   - sequence
   - created_at
   - updated_at
   - subject_id (Foreign Key to SUBJECTS)

4. QUIZZES Table:
   - id (Primary Key)
   - title
   - description
   - chapter_id (Foreign Key to CHAPTERS)
   - start_date
   - end_date
   - time_duration
   - is_active
   - created_at
   - updated_at

5. QUESTIONS Table:
   - id (Primary Key)
   - quiz_id (Foreign Key to QUIZZES)
   - question_title
   - question_statement
   - option1, option2, option3, option4
   - correct_answer
   - explanation
   - difficulty
   - created_at
   - updated_at

6. SCORES Table:
   - id (Primary Key)
   - quiz_id (Foreign Key to QUIZZES)
   - user_id (Foreign Key to USERS)
   - score
   - total_questions
   - percentage
   - time_taken
   - attempt_number
   - timestamp
   - passed
   - detailed_results (JSON)

7. USER_QUIZ_ATTEMPTS Table:
   - id (Primary Key)
   - user_id (Foreign Key to USERS)
   - quiz_id (Foreign Key to QUIZZES)
   - total_questions
   - score
   - status
   - start_time
   - end_time

8. USER_ANSWERS Table:
   - id (Primary Key)
   - user_quiz_attempt_id (Foreign Key to USER_QUIZ_ATTEMPTS)
   - question_id (Foreign Key to QUESTIONS)
   - selected_option
   - is_correct
   - time_spent

Database Relationships:
1. Users can create multiple Subjects (admin role)
2. Subjects contain multiple Chapters
3. Chapters have multiple Quizzes
4. Quizzes contain multiple Questions
5. Users can take multiple Quizzes (tracked via UserQuizAttempts)
6. UserQuizAttempts contain multiple UserAnswers
7. Scores are generated when users complete quizzes

API RESOURCE ENDPOINTS
----------------------

Authentication Endpoints:
POST   /refresh                    - Refresh JWT access token
POST   /register                   - User registration
POST   /login                      - User login
POST   /logout                     - User logout
GET    /me                         - Get current user profile
GET    /session/status             - Check session status

Admin Endpoints (/api/admin):
GET    /subjects                   - Get all subjects
POST   /subjects                   - Create new subject
PUT    /subjects/<id>              - Update subject
DELETE /subjects/<id>              - Delete subject

POST   /chapters                   - Create new chapter
PUT    /chapters/<id>              - Update chapter
DELETE /chapters/<id>              - Delete chapter

GET    /quizzes                    - Get all quizzes
POST   /quizzes                    - Create new quiz
PUT    /quizzes/<id>               - Update quiz
DELETE /quizzes/<id>               - Delete quiz

POST   /questions                  - Create new question
PUT    /questions/<id>             - Update question
DELETE /questions/<id>             - Delete question

GET    /users                      - Get all users
PUT    /users/<id>                 - Update user
DELETE /users/<id>                 - Delete user

Quiz Endpoints (/api/quiz):
GET    /chapters/<subject_id>      - Get chapters by subject
GET    /chapters                   - Get all chapters
GET    /quizzes/chapter/<chapter_id> - Get quizzes by chapter
GET    /questions/<quiz_id>        - Get questions by quiz
POST   /chapter                    - Add new chapter
POST   /quiz                       - Add new quiz
POST   /question                   - Add new question

User Quiz Endpoints (/api/user-quiz):
POST   /start/<quiz_id>            - Start quiz attempt
POST   /submit/<quiz_id>           - Submit quiz answers
GET    /attempts/<quiz_id>         - Get user attempts for quiz
GET    /attempts                   - Get all user attempts

Score Endpoints (/api/scores):
GET    /user/<user_id>             - Get user scores
GET    /quiz/<quiz_id>             - Get quiz scores
GET    /history                    - Get user score history
POST   /calculate                  - Calculate and save score

Search Endpoints (/api/search):
GET    /users                      - Search users
GET    /subjects                   - Search subjects
GET    /quizzes                    - Search quizzes
GET    /questions                  - Search questions
GET    /comprehensive              - Comprehensive search

Optimized API v2 Endpoints (/api/v2):
GET    /subjects                   - Get subjects (cached)
GET    /quizzes                    - Get available quizzes (cached)
GET    /users                      - Get users (admin only, cached)
GET    /quizzes/<quiz_id>          - Get specific quiz (cached)

Rate Limiting & Caching:
• Rate Limiting: Implemented via decorators (100-150 requests per minute)
• Caching: Redis-based caching with configurable timeouts
• Session Management: Automatic timeout with warning system

KEY FEATURES & FUNCTIONALITY
----------------------------

1. User Management:
   • Registration with age validation (minimum 5 years)
   • Role-based access control (User/Admin)
   • Session management with automatic timeout
   • Profile management and activity tracking

2. Content Management:
   • Hierarchical structure: Subjects → Chapters → Quizzes → Questions
   • CRUD operations for all entities
   • Bulk operations and data validation
   • Content scheduling and availability control

3. Quiz System:
   • Real-time quiz taking with countdown timer
   • Multiple choice questions (2-4 options)
   • Automatic submission on timeout
   • Detailed answer tracking and analytics
   • Attempt history and score comparison

4. Analytics & Reporting:
   • Individual user performance tracking
   • Quiz-level analytics and statistics
   • Score history and progress monitoring
   • Detailed results with explanations

5. Search & Discovery:
   • Full-text search across all content
   • Filtered search by user role
   • Comprehensive search with multiple criteria
   • Real-time search results

6. Performance & Security:
   • Redis caching for frequently accessed data
   • Rate limiting to prevent abuse
   • JWT-based authentication
   • CORS configuration for cross-origin requests
   • Password hashing and security best practices

TECHNICAL ARCHITECTURE
----------------------

Backend Architecture:
backend/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── cache.py              # Redis caching implementation
├── celery_app.py         # Background task processing
├── models/
│   ├── model.py          # Database models and relationships
│   └── search.py         # Search functionality
├── routes/
│   ├── auth.py           # Authentication endpoints
│   ├── admin.py          # Admin management endpoints
│   ├── quiz_routes.py    # Quiz-related endpoints
│   ├── user_quiz.py      # User quiz interaction endpoints
│   ├── score_routes.py   # Score management endpoints
│   ├── search.py         # Search endpoints
│   └── optimized.py      # Optimized API v2 endpoints
└── middleware/
    ├── session_middleware.py  # Session management
    └── rate_limiter.py       # Rate limiting

Frontend Architecture:
frontend/
├── src/
│   ├── components/       # Vue.js components
│   │   ├── AdminDashboard.vue
│   │   ├── UserDashboard.vue
│   │   ├── QuizTaking.vue
│   │   ├── Login.vue
│   │   └── ... (30+ components)
│   ├── services/         # API service layer
│   │   ├── authService.js
│   │   ├── quizService.js
│   │   └── ...
│   ├── router.js         # Vue Router configuration
│   └── main.js           # Application entry point
└── dist/                 # Built application

DEPLOYMENT & INFRASTRUCTURE
---------------------------

Docker Configuration:
• Multi-container setup with Docker Compose
• Redis for caching and session storage
• Celery workers for background task processing
• Health checks and automatic restart policies

Environment Configuration:
• Development: SQLite database, debug mode enabled
• Production: PostgreSQL database, security hardening
• Testing: Isolated test database with shorter timeouts

DRIVE LINK OF PRESENTATION VIDEO
--------------------------------
[INSERT YOUR PRESENTATION VIDEO DRIVE LINK HERE]

Note: Please replace the placeholder above with the actual Google Drive link to your project presentation video.

CONCLUSION
----------

The Quiz Master project successfully implements a comprehensive online quiz management system with the following achievements:

1. Complete Feature Set: All core requirements implemented including user management, quiz creation, real-time quiz taking, and analytics
2. Scalable Architecture: Modular design with proper separation of concerns
3. Performance Optimization: Redis caching, rate limiting, and optimized database queries
4. Security Implementation: JWT authentication, password hashing, and role-based access control
5. User Experience: Intuitive interface with real-time updates and responsive design
6. Production Ready: Docker containerization and proper configuration management

The project demonstrates proficiency in full-stack development, database design, API development, and modern web technologies while providing a robust and scalable solution for online quiz management.
"""
    
    # Write to file
    with open('Quiz_Master_Project_Report_Formatted.txt', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print("✅ Formatted report created: Quiz_Master_Project_Report_Formatted.txt")
    print("📝 Instructions to convert to DOCX:")
    print("1. Open the .txt file")
    print("2. Select all content (Ctrl+A)")
    print("3. Copy (Ctrl+C)")
    print("4. Open Microsoft Word or Google Docs")
    print("5. Paste (Ctrl+V)")
    print("6. Apply formatting as needed")
    print("7. Save as .docx")

if __name__ == "__main__":
    create_formatted_report()