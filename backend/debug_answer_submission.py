#!/usr/bin/env python3
"""
Debug script to test answer submission and identify 500 error
"""

import requests
import json
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_answer_submission():
    """Test the answer submission endpoint"""
    
    base_url = "http://localhost:5000"
    
    # Step 1: Login to get a token
    print("1. Logging in...")
    login_data = {
        "username": "user@example.com",  # Replace with actual user
        "password": "password123"        # Replace with actual password
    }
    
    try:
        login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return
        
        login_result = login_response.json()
        access_token = login_result.get('access_token')
        if not access_token:
            print("No access token received")
            return
        
        print("Login successful!")
        
    except Exception as e:
        print(f"Login error: {e}")
        return
    
    # Step 2: Get available quizzes
    print("\n2. Getting available quizzes...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        quizzes_response = requests.get(f"{base_url}/api/user/quiz/available", headers=headers)
        if quizzes_response.status_code != 200:
            print(f"Failed to get quizzes: {quizzes_response.status_code}")
            print(f"Response: {quizzes_response.text}")
            return
        
        quizzes = quizzes_response.json()
        if not quizzes:
            print("No quizzes available")
            return
        
        quiz = quizzes[0]  # Use first available quiz
        print(f"Found quiz: {quiz['title']} (ID: {quiz['id']})")
        
    except Exception as e:
        print(f"Error getting quizzes: {e}")
        return
    
    # Step 3: Start a quiz attempt
    print(f"\n3. Starting quiz attempt for quiz {quiz['id']}...")
    
    try:
        start_response = requests.post(f"{base_url}/api/user/quiz/start/{quiz['id']}", headers=headers)
        if start_response.status_code not in [200, 201]:
            print(f"Failed to start quiz: {start_response.status_code}")
            print(f"Response: {start_response.text}")
            return
        
        start_result = start_response.json()
        attempt_id = start_result.get('attempt_id')
        if not attempt_id:
            print("No attempt ID received")
            return
        
        print(f"Quiz started! Attempt ID: {attempt_id}")
        
    except Exception as e:
        print(f"Error starting quiz: {e}")
        return
    
    # Step 4: Get the first question
    print(f"\n4. Getting question 1 for attempt {attempt_id}...")
    
    try:
        question_response = requests.get(f"{base_url}/api/user/quiz/question/{attempt_id}/1", headers=headers)
        if question_response.status_code != 200:
            print(f"Failed to get question: {question_response.status_code}")
            print(f"Response: {question_response.text}")
            return
        
        question_data = question_response.json()
        question = question_data.get('question')
        if not question:
            print("No question data received")
            return
        
        print(f"Got question: {question['title']} (ID: {question['id']})")
        
    except Exception as e:
        print(f"Error getting question: {e}")
        return
    
    # Step 5: Submit an answer
    print(f"\n5. Submitting answer...")
    
    answer_data = {
        "attempt_id": attempt_id,
        "question_id": question['id'],
        "selected_option": 1  # Select first option
    }
    
    print(f"Submitting data: {json.dumps(answer_data, indent=2)}")
    
    try:
        answer_response = requests.post(f"{base_url}/api/user/quiz/answer", json=answer_data, headers=headers)
        print(f"Answer submission status: {answer_response.status_code}")
        print(f"Response headers: {dict(answer_response.headers)}")
        print(f"Response body: {answer_response.text}")
        
        if answer_response.status_code == 200:
            result = answer_response.json()
            print(f"Answer submitted successfully!")
            print(f"Result: {json.dumps(result, indent=2)}")
        else:
            print(f"Answer submission failed!")
            
    except Exception as e:
        print(f"Error submitting answer: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== Answer Submission Debug Test ===")
    test_answer_submission()
    print("\n=== Test Complete ===") 