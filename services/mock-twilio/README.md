# Mock Twilio Service

A simple mock service for Twilio API, designed for testing SMS verification flows without using the real Twilio service.

## Features

- Simulates Twilio SMS API endpoints
- Provides logs for sent messages
- Configurable response behavior

## Setup

This project uses uv for package management. Here's how to set up the development environment:

```bash
# Create and activate virtual environment with uv
uv venv
source .venv/bin/activate

# Install dependencies including development tools
uv pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install
```

## Running the service

```bash
# Run the service locally
uvicorn mock_twilio.main:app --reload --port 3000
```

## Configuration

The service can be configured using environment variables:

```
MOCK_TWILIO_ACCOUNT_SID=your_test_account_sid
MOCK_TWILIO_AUTH_TOKEN=your_test_auth_token
MOCK_TWILIO_FAILURE_RATE=0.0 # Set a value between 0.0 and 1.0 to simulate failures
```

## API Endpoints

### Send SMS

```
POST /v1/Accounts/{AccountSid}/Messages
```

### View Logs

```
GET /logs
```

## Docker Usage

```bash
docker build -t mock-twilio .
docker run -p 3000:3000 mock-twilio
```