#!/usr/bin/env python3
"""
Quick script to reset the database and fix the schema issue
"""
import requests

def fix_database():
    print("🔧 Fixing database schema...")
    print("📡 Sending reset request to http://localhost:8000/api/v1/reset-db")

    try:
        response = requests.post("http://localhost:8000/api/v1/reset-db", timeout=30)
        print(f"📊 Response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Database reset successful!")
            print(f"📝 Message: {result.get('message')}")
            print(f"📊 Status: {result.get('status')}")

            print("\n🔍 Testing email services endpoint...")
            test_response = requests.get("http://localhost:8000/api/v1/email-services/?skip=0&limit=30", timeout=10)
            print(f"📊 Email services status: {test_response.status_code}")

            if test_response.status_code == 200:
                data = test_response.json()
                print(f"✅ Email services working! Found {len(data)} services")
                if data:
                    print(f"📧 Sample service: {data[0].get('name')} - from_email: {data[0].get('from_email')}")
                return True
            else:
                print("❌ Email services still failing")
                return False
        else:
            print(f"❌ Reset failed: {response.status_code}")
            print(f"📝 Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = fix_database()
    if success:
        print("\n🎉 SUCCESS! Database schema fixed and all endpoints working!")
    else:
        print("\n❌ FAILED! Please check if the server is running on http://localhost:8000")
    exit(0 if success else 1)