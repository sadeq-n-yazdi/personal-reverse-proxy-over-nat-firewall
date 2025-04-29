import requests
import json
import time
from pprint import pprint

# Base configuration
BASE_URL = "http://localhost:3000"
ACCOUNT_SID = "AC123456789"
SERVICE_SID = "VA123456789"
PHONE_NUMBER = "+1234567890"
TEST_CODE = "123456"

def test_verify_service():
    """Test the Twilio Verify API workflow"""
    print("\n=== Testing Twilio Verify API ===")
    
    # Step 1: Start a verification
    print("\n1. Starting verification:")
    start_url = f"{BASE_URL}/v1/Accounts/{ACCOUNT_SID}/Verify/Services/{SERVICE_SID}/Verifications"
    start_data = {
        "To": PHONE_NUMBER,
        "Channel": "sms"
    }
    
    start_response = requests.post(start_url, json=start_data)
    
    if start_response.status_code == 200:
        start_result = start_response.json()
        print("✅ Verification started successfully")
        pprint(start_result)
    else:
        print(f"❌ Failed to start verification: {start_response.status_code}")
        print(start_response.text)
        return False
    
    # Step 2: Check a verification code
    print("\n2. Checking verification code:")
    check_url = f"{BASE_URL}/v1/Accounts/{ACCOUNT_SID}/Verify/Services/{SERVICE_SID}/VerificationCheck"
    check_data = {
        "To": PHONE_NUMBER,
        "Code": TEST_CODE
    }
    
    check_response = requests.post(check_url, json=check_data)
    
    if check_response.status_code == 200:
        check_result = check_response.json()
        if check_result.get("valid"):
            print("✅ Verification code check successful")
            pprint(check_result)
        else:
            print("❌ Verification code was not valid")
            pprint(check_result)
            return False
    else:
        print(f"❌ Failed to check verification: {check_response.status_code}")
        print(check_response.text)
        return False
    
    return True

def test_legacy_sms():
    """Test the legacy SMS API"""
    print("\n=== Testing Legacy SMS API ===")
    
    # Send an SMS
    print("\n1. Sending SMS:")
    sms_url = f"{BASE_URL}/v1/Accounts/{ACCOUNT_SID}/Messages.json"
    sms_data = {
        "To": PHONE_NUMBER,
        "From": "+19876543210",
        "Body": f"Your verification code is {TEST_CODE}"
    }
    
    sms_response = requests.post(sms_url, json=sms_data)
    
    if sms_response.status_code == 200:
        sms_result = sms_response.json()
        print("✅ SMS sent successfully")
        pprint(sms_result)
        return True
    else:
        print(f"❌ Failed to send SMS: {sms_response.status_code}")
        print(sms_response.text)
        return False

def test_logs_endpoint():
    """Test the logs endpoint"""
    print("\n=== Testing Logs Endpoint ===")
    
    logs_url = f"{BASE_URL}/logs"
    logs_response = requests.get(logs_url)
    
    if logs_response.status_code == 200:
        logs = logs_response.json()
        print(f"✅ Retrieved {len(logs)} log entries")
        if logs:
            print("\nMost recent log entry:")
            pprint(logs[0])
        return True
    else:
        print(f"❌ Failed to retrieve logs: {logs_response.status_code}")
        print(logs_response.text)
        return False

if __name__ == "__main__":
    # Wait for service to be ready
    print("Waiting for mock-twilio service to be ready...")
    time.sleep(5)
    
    # Run tests
    verify_result = test_verify_service()
    sms_result = test_legacy_sms()
    logs_result = test_logs_endpoint()
    
    # Show final result
    print("\n=== Test Results ===")
    print(f"Verify API Test: {'✅ PASSED' if verify_result else '❌ FAILED'}")
    print(f"Legacy SMS Test: {'✅ PASSED' if sms_result else '❌ FAILED'}")
    print(f"Logs Endpoint Test: {'✅ PASSED' if logs_result else '❌ FAILED'}")
    
    overall = verify_result and sms_result and logs_result
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall else '❌ SOME TESTS FAILED'}")