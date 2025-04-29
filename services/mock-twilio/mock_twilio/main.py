"""Main application module for the mock Twilio API."""

import random
from datetime import datetime
from typing import Dict, List, Optional, Union

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from mock_twilio.config import settings
from mock_twilio.models import (
    LogEntry,
    SMSMessage,
    SMSMessageResponse,
    message_store,
)

app = FastAPI(
    title="Mock Twilio API",
    description="A mock implementation of the Twilio API for testing",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


def check_auth(request: Request) -> bool:
    """Validate basic auth credentials against configured values."""
    auth = request.headers.get("Authorization")
    
    if not auth or not auth.startswith("Basic "):
        return False
    
    import base64
    
    try:
        credentials = base64.b64decode(auth[6:]).decode("utf-8")
        account_sid, auth_token = credentials.split(":")
        return account_sid == settings.ACCOUNT_SID and auth_token == settings.AUTH_TOKEN
    except Exception:
        return False


@app.get("/", response_class=HTMLResponse)
async def root():
    """Display a simple homepage."""
    return """
    <html>
        <head>
            <title>Mock Twilio API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #F22F46; }
                h2 { color: #0D122B; }
                pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>Mock Twilio API</h1>
            <p>This is a mock implementation of the Twilio API for testing purposes.</p>
            
            <h2>Endpoints</h2>
            <ul>
                <li><strong>POST /v1/Accounts/{AccountSid}/Messages</strong> - Send SMS messages</li>
                <li><strong>GET /logs</strong> - View logs of sent messages</li>
            </ul>
            
            <h2>Example cURL</h2>
            <pre>curl -X POST https://twilio-mock.example.com/v1/Accounts/ACxxxxxxxxxxxxxxxx/Messages \\
    -u ACxxxxxxxxxxxxxxxx:your_auth_token \\
    -d "To=+15551234567" \\
    -d "From=+15557654321" \\
    -d "Body=Hello from mock Twilio!"</pre>
        </body>
    </html>
    """


@app.post("/v1/Accounts/{account_sid}/Messages", response_model=SMSMessageResponse)
async def send_message(
    account_sid: str,
    request: Request,
    To: str = Form(...),
    From: str = Form(...),
    Body: str = Form(...),
):
    """Send an SMS message (mocked)."""
    # Authenticate the request
    if not check_auth(request):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authentication",
        )
    
    # Check if account SID in path matches the authenticated one
    if account_sid != settings.ACCOUNT_SID:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The requested resource /v1/Accounts/{account_sid}/Messages was not found",
        )
    
    # Random failure based on configured rate
    if random.random() < settings.FAILURE_RATE:
        error_message = SMSMessage(
            account_sid=account_sid,
            to=To,
            from_=From,
            body=Body,
            status="failed",
            error_code=30001,
            error_message="Queue overflow",
        )
        message_store.add_message(error_message)
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "code": 30001,
                "message": "Queue overflow",
                "status": 400,
            },
        )
    
    # Create a successful message
    message = SMSMessage(
        account_sid=account_sid,
        to=To,
        from_=From,
        body=Body,
    )
    message_store.add_message(message)
    
    # Convert to response model
    now = datetime.utcnow().isoformat()
    return SMSMessageResponse(
        sid=message.sid,
        date_created=message.date_created,
        date_updated=now,
        date_sent=now,
        account_sid=message.account_sid,
        to=message.to,
        from_=message.from_,
        body=message.body,
        status=message.status,
        direction=message.direction,
        uri=f"/v1/Accounts/{account_sid}/Messages/{message.sid}",
    )


@app.get("/logs")
async def get_logs() -> List[Dict]:
    """Return logs of all messages sent."""
    logs = message_store.get_logs()
    return [log.model_dump(by_alias=True) for log in logs]


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "mock_twilio.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )