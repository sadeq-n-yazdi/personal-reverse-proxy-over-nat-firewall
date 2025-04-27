#!/bin/bash
set -e

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

# Load environment variables
if [ -f .env ]; then
  # Use set -a to export all variables automatically
  set -a
  . .env || { echo "Error: Failed to load .env file, check for syntax errors"; exit 1; }
  set +a
  
  # Verify required environment variables are set
  if [ -z "$SERVER_USER" ] || [ -z "$SERVER_IP" ]; then
    echo "Error: Required environment variables (SERVER_USER, SERVER_IP) not found in .env file"
    exit 1
  fi
else
  echo "Error: .env file not found. Run setup.sh first"
  exit 1
fi

# Check parameters
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <local_port> <remote_port>"
  exit 1
fi

LOCAL_PORT=$1
REMOTE_PORT=$2

# Create SSH tunnel
echo "Creating SSH tunnel from local port $LOCAL_PORT to remote port $REMOTE_PORT"
ssh -R $REMOTE_PORT:localhost:$LOCAL_PORT $SERVER_USER@$SERVER_IP