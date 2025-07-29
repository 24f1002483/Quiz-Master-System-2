#!/usr/bin/env python3
"""
Debug script to identify 403 FORBIDDEN issues with quiz completion
"""

import requests
import json
from datetime import datetime

def debug_quiz_403():
    print("🔍 Debugging Quiz 403 FORBIDDEN Error")
    print("=" * 50)
    
    # Test login to get token
    print("1. Testing login...")
    login_data = {
        "username": "admin",  # Change to your username
        "password": "admin123"  # Change to your password
    }
    
    try:
        login_response = requests.post('http://localhost:5000/api/auth/login', json=login_data)
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result.get('access_token')
            user_data = login_result.get('user')
            print(f"✅ Login successful")
            print(f"👤 User ID: {user_data.get('id')}")
            print(f"👤 Username: {user_data.get('username')}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Get available quizzes
    print("\n2. Getting available quizzes...")
    try:
        quizzes_response = requests.get('http://localhost:5000/api/user/quiz/available', headers=headers)
        if quizzes_response.status_code == 200:
            quizzes = quizzes_response.json()
            print(f"✅ Found {len(quizzes)} available quizzes")
            if quizzes:
                quiz_id = quizzes[0]['id']
                print(f"🎯 Using quiz ID: {quiz_id}")
            else:
                print("❌ No available quizzes")
                return
        else:
            print(f"❌ Failed to get quizzes: {quizzes_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting quizzes: {e}")
        return
    
    # Start quiz
    print(f"\n3. Starting quiz {quiz_id}...")
    try:
        start_response = requests.post(f'http://localhost:5000/api/user/quiz/start/{quiz_id}', headers=headers)
        if start_response.status_code in [200, 201]:
            start_data = start_response.json()
            attempt_id = start_data.get('attempt_id')
            print(f"✅ Quiz started successfully")
            print(f"📝 Attempt ID: {attempt_id}")
        else:
            print(f"❌ Failed to start quiz: {start_response.status_code}")
            print(f"Response: {start_response.text}")
            return
    except Exception as e:
        print(f"❌ Error starting quiz: {e}")
        return
    
    # Check attempt details in database
    print(f"\n4. Checking attempt details...")
    try:
        # Get attempt details (if endpoint exists)
        attempt_response = requests.get(f'http://localhost:5000/api/user/quiz/attempt/{attempt_id}', headers=headers)
        if attempt_response.status_code == 200:
            attempt_data = attempt_response.json()
            print(f"✅ Attempt details retrieved")
            print(f"👤 Attempt User ID: {attempt_data.get('user_id')}")
            print(f"📊 Attempt Status: {attempt_data.get('status')}")
        else:
            print(f"⚠️ Could not get attempt details: {attempt_response.status_code}")
    except Exception as e:
        print(f"⚠️ Error getting attempt details: {e}")
    
    # Try to complete quiz
    print(f"\n5. Attempting to complete quiz...")
    try:
        complete_response = requests.post(f'http://localhost:5000/api/user/quiz/complete/{attempt_id}', headers=headers)
        print(f"📊 Complete Response Status: {complete_response.status_code}")
        print(f"📊 Complete Response Headers: {dict(complete_response.headers)}")
        
        if complete_response.status_code == 200:
            print("✅ Quiz completed successfully!")
            result = complete_response.json()
            print(f"📊 Score: {result.get('score')}")
        elif complete_response.status_code == 403:
            print("❌ 403 FORBIDDEN - Authorization issue")
            print(f"Response: {complete_response.text}")
            
            # Additional debugging
            print("\n🔍 Additional Debugging:")
            print(f"Current User ID from JWT: {user_data.get('id')}")
            print(f"Token: {token[:20]}...")
            
        else:
            print(f"❌ Unexpected status: {complete_response.status_code}")
            print(f"Response: {complete_response.text}")
            
    except Exception as e:
        print(f"❌ Error completing quiz: {e}")
    
    # Test token validity
    print(f"\n6. Testing token validity...")
    try:
        me_response = requests.get('http://localhost:5000/api/auth/me', headers=headers)
        if me_response.status_code == 200:
            me_data = me_response.json()
            print(f"✅ Token is valid")
            print(f"👤 Current user: {me_data.get('username')} (ID: {me_data.get('id')})")
        else:
            print(f"❌ Token validation failed: {me_response.status_code}")
            print(f"Response: {me_response.text}")
    except Exception as e:
        print(f"❌ Error validating token: {e}")

if __name__ == "__main__":
    debug_quiz_403() 