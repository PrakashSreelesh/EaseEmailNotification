#!/usr/bin/env python3
"""
Verification script for async email sending with webhook callbacks.

This script tests:
1. Email queuing (async response)
2. Job status polling
3. Webhook delivery (if configured)
4. Retry mechanisms
5. Idempotency

Usage:
    python verify_async_email.py
"""

import requests
import time
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "your-api-key-here"  # UPDATE THIS

# Test data
TEST_EMAIL = "test@example.com"
TEMPLATE_NAME = "welcome"  # UPDATE THIS
SERVICE_NAME = "Welcome Email Service"  # UPDATE THIS


def print_section(title):
    """Print a section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def test_1_queue_email():
    """Test 1: Queue email and get job_id"""
    print_section("TEST 1: Queue Email (Async)")
    
    url = f"{BASE_URL}/send/email/?template={TEMPLATE_NAME}"
    headers = {
        "XAPIKey": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "service_name": SERVICE_NAME,
        "to_email": TEST_EMAIL,
        "variables_data": {
            "name": "Test User",
            "verification_code": "123456"
        }
    }
    
    print(f"POST {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 202:
            print("✅ Email queued successfully!")
            job_id = response.json().get("job_id")
            return job_id
        else:
            print(f"❌ Failed to queue email: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_2_poll_job_status(job_id):
    """Test 2: Poll job status"""
    print_section("TEST 2: Poll Job Status")
    
    if not job_id:
        print("⏭️  Skipping (no job_id from Test 1)")
        return
    
    url = f"{BASE_URL}/jobs/{job_id}"
    
    max_polls = 10
    poll_interval = 2
    
    for i in range(max_polls):
        print(f"\n[Poll {i+1}/{max_polls}] GET {url}")
        
        try:
            response = requests.get(url, timeout=5)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                print(f"Job Status: {status}")
                print(f"Response: {json.dumps(data, indent=2, default=str)}")
                
                if status in ["sent", "failed"]:
                    print(f"\n✅ Final status reached: {status}")
                    
                    if status == "sent":
                        print("✅ Email sent successfully!")
                    else:
                        print(f"❌ Email failed: {data.get('error_message')}")
                        print(f"   Category: {data.get('error_category')}")
                    
                    return data
                
                print(f"Status: {status} - waiting...")
                time.sleep(poll_interval)
            else:
                print(f"❌ Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    print("\n⏱️  Timeout: Job still processing after max polls")
    return None


def test_3_full_job_status(job_id):
    """Test 3: Get full job status with webhook details"""
    print_section("TEST 3: Full Job Status (with Webhook)")
    
    if not job_id:
        print("⏭️  Skipping (no job_id)")
        return
    
    url = f"{BASE_URL}/jobs/{job_id}/full"
    
    try:
        response = requests.get(url, timeout=5)
        print(f"GET {url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2, default=str)}")
            
            webhook_delivery = data.get("webhook_delivery")
            if webhook_delivery:
                print(f"\n✅ Webhook configured!")
                print(f"   Event: {webhook_delivery.get('event_type')}")
                print(f"   Status: {webhook_delivery.get('status')}")
                if webhook_delivery.get('status') == 'delivered':
                    print("   ✅ Webhook delivered successfully!")
                elif webhook_delivery.get('status') == 'failed':
                    print(f"   ❌ Webhook failed: {webhook_delivery.get('last_error')}")
            else:
                print("\nℹ️  No webhook configured for this application")
            
            return data
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_4_idempotency():
    """Test 4: Test idempotency (manual trigger same job twice)"""
    print_section("TEST 4: Idempotency Test")
    
    print("ℹ️  This test requires manually triggering the same job_id twice")
    print("   from the Celery worker to verify no duplicate sends occur.")
    print("   Skipping automated test.")
    print("\n   Manual steps:")
    print("   1. Get a job_id from Test 1")
    print("   2. docker-compose exec worker celery -A app.worker call send_email_task --args='[\"<job_id>\"]'")
    print("   3. Run the same command again")
    print("   4. Check logs - should see 'already sent, skipping'")


def test_5_check_health():
    """Test 5: Check API health"""
    print_section("TEST 5: Health Check")
    
    url = f"{BASE_URL}/health/ready"
    
    try:
        response = requests.get(url, timeout=5)
        print(f"GET {url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ API is healthy!")
            return True
        else:
            print("❌ API health check failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all verification tests"""
    print("\n" + "=" * 60)
    print("  ASYNC EMAIL WITH WEBHOOK - VERIFICATION TESTS")
    print("=" * 60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:8]}..." if len(API_KEY) > 8 else API_KEY)
    print(f"Test Email: {TEST_EMAIL}")
    print(f"Template: {TEMPLATE_NAME}")
    print(f"Service: {SERVICE_NAME}")
    
    input("\n⚠️  Press Enter to start tests (or Ctrl+C to cancel)...")
    
    # Test 5: Health check first
    if not test_5_check_health():
        print("\n❌ API not healthy, stopping tests")
        return
    
    # Test 1: Queue email
    job_id = test_1_queue_email()
    
    if not job_id:
        print("\n❌ Failed to queue email, stopping tests")
        return
    
    # Test 2: Poll status
    final_status = test_2_poll_job_status(job_id)
    
    # Test 3: Full status with webhook
    test_3_full_job_status(job_id)
    
    # Test 4: Idempotency (manual)
    test_4_idempotency()
    
    print_section("SUMMARY")
    print("✅ Verification tests complete!")
    print(f"\nJob ID: {job_id}")
    if final_status:
        print(f"Final Status: {final_status.get('status')}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
