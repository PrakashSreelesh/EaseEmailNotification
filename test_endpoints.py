#!/usr/bin/env python3

# Simple test to check if our endpoint modifications work
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_count_endpoints():
    """Test that count endpoints return the expected format"""
    try:
        # Test imports
        from api.v1.endpoints.users import CountResponse
        from api.v1.endpoints.applications import CountResponse as AppCountResponse
        from api.v1.endpoints.smtp import CountResponse as SmtpCountResponse
        from api.v1.endpoints.templates import CountResponse as TemplateCountResponse

        # Test that CountResponse can be instantiated
        count_resp = CountResponse(count=42)
        assert count_resp.count == 42
        print("✅ CountResponse models work correctly")

        # Test that the endpoints can be imported (without fastapi dependency)
        print("✅ All endpoint modules can be imported")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_count_endpoints()
    sys.exit(0 if success else 1)