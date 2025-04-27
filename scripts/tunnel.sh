#!/bin/bash
set -e

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

# Load environment variables
if [ -f .env ]; then
  export $(cat .env | xargs)
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