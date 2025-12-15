#!/usr/bin/env python3
"""
Test script to verify the landing page and login flow
"""
import requests
import time

FRONTEND_URL = "https://app.triboka.com"

def test_landing_page():
    """Test that the landing page loads correctly"""
    print("🧪 Testing landing page...")

    try:
        response = requests.get(FRONTEND_URL + "/")
        if response.status_code == 200:
            content = response.text

            # Check for key elements
            checks = [
                ("TribokaChain" in content, "TribokaChain title"),
                ("Trazabilidad Blockchain" in content, "Blockchain subtitle"),
                ("Acceder al Sistema" in content, "Login button"),
                ("¿Qué es TribokaChain?" in content, "Features section"),
                ("href=\"/login\"" in content, "Login link")
            ]

            passed = 0
            for check, description in checks:
                if check:
                    print(f"  ✅ {description}")
                    passed += 1
                else:
                    print(f"  ❌ {description}")

            if passed == len(checks):
                print("🎉 Landing page test PASSED")
                return True
            else:
                print(f"❌ Landing page test FAILED ({passed}/{len(checks)} checks passed)")
                return False
        else:
            print(f"❌ Landing page returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing landing page: {e}")
        return False

def test_login_page():
    """Test that the login page loads correctly"""
    print("\n🧪 Testing login page...")

    try:
        response = requests.get(FRONTEND_URL + "/login")
        if response.status_code == 200:
            content = response.text

            # Check for login form elements
            checks = [
                ("Login" in content, "Login title"),
                ("email" in content, "Email field"),
                ("password" in content, "Password field"),
                ("form" in content, "Login form")
            ]

            passed = 0
            for check, description in checks:
                if check:
                    print(f"  ✅ {description}")
                    passed += 1
                else:
                    print(f"  ❌ {description}")

            if passed == len(checks):
                print("🎉 Login page test PASSED")
                return True
            else:
                print(f"❌ Login page test FAILED ({passed}/{len(checks)} checks passed)")
                return False
        else:
            print(f"❌ Login page returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing login page: {e}")
        return False

def test_login_flow():
    """Test the complete login flow"""
    print("\n🧪 Testing login flow...")

    # Create a session to maintain cookies
    session = requests.Session()

    # First visit landing page
    try:
        response = session.get(FRONTEND_URL + "/")
        if response.status_code != 200:
            print(f"❌ Could not access landing page: {response.status_code}")
            return False
        print("  ✅ Landing page accessible")
    except Exception as e:
        print(f"❌ Error accessing landing page: {e}")
        return False

    # Login with test credentials
    login_data = {
        "email": "admin@triboka.com",
        "password": "admin123"
    }

    try:
        response = session.post(FRONTEND_URL + "/login", data=login_data, allow_redirects=False)
        if response.status_code == 302:
            print("  ✅ Login successful - redirect to dashboard")
        else:
            print(f"❌ Login failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return False

    # Check if we can access dashboard
    try:
        response = session.get(FRONTEND_URL + "/dashboard")
        if response.status_code == 200:
            print("  ✅ Dashboard accessible after login")
            print("🎉 Login flow test PASSED")
            return True
        else:
            print(f"❌ Could not access dashboard: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing dashboard: {e}")
        return False

def main():
    print("🚀 Starting TribokaChain landing page tests...\n")

    tests = [
        test_landing_page,
        test_login_page,
        test_login_flow
    ]

    passed = 0
    for test in tests:
        if test():
            passed += 1
        time.sleep(0.5)  # Small delay between tests

    print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 All tests PASSED! Landing page is working correctly.")
        return True
    else:
        print("❌ Some tests FAILED. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)