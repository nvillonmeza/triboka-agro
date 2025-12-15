#!/usr/bin/env python3
"""
Test script to verify JWT authentication and user management functionality
"""
import requests
import json
import sys

# Configuration
FRONTEND_URL = "http://localhost:5004"
BACKEND_URL = "http://localhost:5003"

def test_login():
    """Test login and get JWT token"""
    print("🔐 Testing login...")
    login_data = {
        "email": "admin@triboka.com",
        "password": "admin123"
    }

    try:
        response = requests.post(f"{FRONTEND_URL}/login", data=login_data, allow_redirects=False)
        print(f"Login response status: {response.status_code}")

        if response.status_code == 302:
            print("✅ Login successful - redirect to dashboard")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

def test_backend_login():
    """Test direct backend login to get JWT token"""
    print("\n🔑 Testing backend login for JWT token...")
    login_data = {
        "email": "admin@triboka.com",
        "password": "admin123"
    }

    try:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
        print(f"Backend login response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                token = data['access_token']
                print("✅ JWT token obtained successfully")
                return token
            else:
                print(f"❌ No access_token in response: {data}")
                return None
        else:
            print(f"❌ Backend login failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Backend login error: {e}")
        return None

def test_user_operations(token):
    """Test user CRUD operations"""
    print("\n👥 Testing user operations...")

    headers = {'Authorization': f'Bearer {token}'}

    # Test GET users
    print("📋 Getting users list...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/users", headers=headers)
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Retrieved {len(users)} users")
        else:
            print(f"❌ Failed to get users: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error getting users: {e}")
        return False

    # Test CREATE user
    print("➕ Creating new user...")
    new_user = {
        "first_name": "Test",
        "last_name": "User",
        "email": f"test_{int(time.time())}@example.com",
        "password": "test123",
        "role": "user",
        "is_active": True
    }

    try:
        response = requests.post(f"{BACKEND_URL}/api/users", json=new_user, headers=headers)
        if response.status_code == 201:
            created_user = response.json()
            user_id = created_user['user']['id']
            print(f"✅ User created with ID: {user_id}")
        else:
            print(f"❌ Failed to create user: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False

    # Test UPDATE user
    print("✏️ Updating user...")
    update_data = {
        "first_name": "Test",
        "last_name": "User Updated",
        "email": new_user["email"],
        "role": "user",
        "is_active": True
    }

    try:
        response = requests.put(f"{BACKEND_URL}/api/users/{user_id}", json=update_data, headers=headers)
        if response.status_code == 200:
            print("✅ User updated successfully")
        else:
            print(f"❌ Failed to update user: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error updating user: {e}")
        return False

    # Test DELETE user
    print("🗑️ Deleting user...")
    try:
        response = requests.delete(f"{BACKEND_URL}/api/users/{user_id}", headers=headers)
        if response.status_code == 200:
            print("✅ User deleted successfully")
        else:
            print(f"❌ Failed to delete user: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error deleting user: {e}")
        return False

    return True

def test_frontend_users_page():
    """Test accessing users page through frontend"""
    print("\n🌐 Testing frontend users page access...")

    # Create a session to maintain cookies
    session = requests.Session()

    # Login first
    login_data = {
        "email": "admin@triboka.com",
        "password": "admin123"
    }

    try:
        response = session.post(f"{FRONTEND_URL}/login", data=login_data, allow_redirects=False)
        if response.status_code != 302:
            print(f"❌ Frontend login failed: {response.status_code}")
            return False

        # Now access users page
        response = session.get(f"{FRONTEND_URL}/users")
        if response.status_code == 200:
            print("✅ Users page accessed successfully")
            # Check if the page contains expected content
            if "Gestión de Usuarios" in response.text:
                print("✅ Users page content loaded correctly")
                return True
            else:
                print("❌ Users page content not found")
                return False
        else:
            print(f"❌ Failed to access users page: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing frontend: {e}")
        return False

def main():
    print("🚀 Starting comprehensive JWT authentication test...\n")

    # Test 1: Frontend login
    if not test_login():
        print("❌ Frontend login test failed")
        return False

    # Test 2: Backend JWT token
    token = test_backend_login()
    if not token:
        print("❌ Backend JWT token test failed")
        return False

    # Test 3: User operations
    if not test_user_operations(token):
        print("❌ User operations test failed")
        return False

    # Test 4: Frontend users page
    if not test_frontend_users_page():
        print("❌ Frontend users page test failed")
        return False

    print("\n🎉 All tests passed! JWT authentication is working correctly.")
    return True

if __name__ == "__main__":
    import time
    success = main()
    sys.exit(0 if success else 1)