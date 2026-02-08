#!/usr/bin/env python3
"""
Test script to verify the database reset works
"""
import requests
import time

def test_reset():
    print("Testing database reset...")

    # Call the reset endpoint
    try:
        response = requests.post("http://localhost:8000/api/v1/reset-db")
        if response.status_code == 200:
            print("✅ Database reset successful!")
            print(response.json())

            # Wait a moment for database operations
            time.sleep(2)

            # Test the email-services endpoint
            response2 = requests.get("http://localhost:8000/api/v1/email-services/?skip=0&limit=30")
            if response2.status_code == 200:
                data = response2.json()
                print(f"✅ Email services endpoint now works! Returned {len(data)} services")
                if data:
                    print(f"Sample service: {data[0].get('name')} - from_email: {data[0].get('from_email')}")
                return True
            else:
                print(f"❌ Email services still failing: {response2.status_code}")
                return False
        else:
            print(f"❌ Reset failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_reset()
    exit(0 if success else 1)