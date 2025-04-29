from flask import Flask, request, jsonify
import random
import string
import datetime
import re
import os

app = Flask(__name__)

# Store last 50 verification logs
verification_logs = []

def generate_random_sid(prefix):
    """Generate a random Twilio-like SID with the given prefix"""
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    return f"{prefix}{random_part}"

@app.route("/v1/Accounts/<account_sid>/Verify/Services/<service_sid>/Verifications", methods=["POST"])
def send_verification(account_sid, service_sid):
    """Handle verification request (start verification)"""
    data = request.json or request.form
    to = data.get("To")
    channel = data.get("Channel", "sms")
    
    # Generate a random verification code (4-10 digits)
    code = ''.join(random.choices(string.digits, k=random.randint(4, 6)))
    
    # Create log entry
    log_entry = {
        "time": datetime.datetime.now().isoformat(),
        "to": to,
        "channel": channel,
        "code": code,
        "status": "pending",
        "sid": generate_random_sid("VE"),
        "account_sid": account_sid,
        "service_sid": service_sid
    }
    
    # Add to logs, keeping only the last 50
    verification_logs.insert(0, log_entry)
    if len(verification_logs) > 50:
        verification_logs.pop()
    
    return jsonify({
        "sid": log_entry["sid"],
        "service_sid": service_sid,
        "account_sid": account_sid,
        "to": to,
        "channel": channel,
        "status": "pending",
        "valid": False,
        "date_created": log_entry["time"],
        "date_updated": log_entry["time"]
    })

@app.route("/v1/Accounts/<account_sid>/Verify/Services/<service_sid>/VerificationCheck", methods=["POST"])
def check_verification(account_sid, service_sid):
    """Handle verification check"""
    data = request.json or request.form
    to = data.get("To")
    code = data.get("Code")
    
    # Find the most recent verification for this recipient
    matching_verification = None
    for log in verification_logs:
        if log["to"] == to:
            matching_verification = log
            break
    
    # For mock purposes, any code is considered valid
    is_valid = True
    
    if matching_verification:
        matching_verification["status"] = "approved"
    
    return jsonify({
        "sid": generate_random_sid("VC"),
        "service_sid": service_sid,
        "account_sid": account_sid,
        "to": to,
        "channel": "sms",
        "status": "approved",
        "valid": is_valid,
        "date_created": datetime.datetime.now().isoformat(),
        "date_updated": datetime.datetime.now().isoformat()
    })

@app.route("/v1/Accounts/<account_sid>/Messages.json", methods=["POST"])
def send_sms(account_sid):
    """Legacy SMS API for compatibility"""
    data = request.json or request.form
    to = data.get("To")
    from_number = data.get("From")
    body = data.get("Body", "")
    
    # Try to extract code from message body
    code_match = re.search(r'\d+', body)
    code = code_match.group(0) if code_match else "0000"
    
    # Create log entry
    log_entry = {
        "time": datetime.datetime.now().isoformat(),
        "to": to,
        "from": from_number,
        "body": body,
        "code": code,
        "status": "delivered",
        "sid": generate_random_sid("SM")
    }
    
    # Add to logs, keeping only the last 50
    verification_logs.insert(0, log_entry)
    if len(verification_logs) > 50:
        verification_logs.pop()
    
    return jsonify({
        "sid": log_entry["sid"],
        "date_created": log_entry["time"],
        "date_updated": log_entry["time"],
        "date_sent": log_entry["time"],
        "account_sid": account_sid,
        "to": to,
        "from": from_number,
        "body": body,
        "status": "queued",
        "num_segments": "1",
        "num_media": "0",
        "direction": "outbound-api",
        "api_version": "2010-04-01",
        "price": "0.00",
        "price_unit": "USD",
        "error_code": None,
        "error_message": None
    })

@app.route("/logs", methods=["GET"])
def get_logs():
    """Get the last 50 verification logs"""
    return jsonify(verification_logs)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port, debug=False)