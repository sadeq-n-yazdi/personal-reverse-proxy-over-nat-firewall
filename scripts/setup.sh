#!/bin/bash
# Exit on error but allow for error handling
set -o pipefail

# Error handling function
handle_error() {
  local exit_code=$1
  local error_message=$2
  echo "ERROR: $error_message (exit code: $exit_code)"
  exit $exit_code
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  handle_error 1 "This script must be run as root"
fi

echo "Starting setup process..."

# Check and install dependencies
echo "Checking for dependencies..."

# Check for Docker
if ! command -v docker &> /dev/null; then
  echo "Docker not found, installing..."
  apt-get update || handle_error 2 "Failed to update package list"
  apt-get install -y docker.io || handle_error 3 "Failed to install Docker"
  # Verify installation
  if ! command -v docker &> /dev/null; then
    handle_error 4 "Docker installation failed"
  fi
  echo "Docker installed successfully: $(docker --version)"
else
  echo "Docker is already installed: $(docker --version)"
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
  echo "Docker Compose not found, installing..."
  apt-get update || handle_error 5 "Failed to update package list"
  apt-get install -y docker-compose || handle_error 6 "Failed to install Docker Compose"
  # Verify installation
  if ! command -v docker-compose &> /dev/null; then
    handle_error 7 "Docker Compose installation failed"
  fi
  echo "Docker Compose installed successfully: $(docker-compose --version)"
else
  echo "Docker Compose is already installed: $(docker-compose --version)"
fi

# Check for Python3
if ! command -v python3 &> /dev/null; then
  echo "Python3 not found, installing..."
  apt-get update || handle_error 8 "Failed to update package list"
  apt-get install -y python3 python3-venv || handle_error 9 "Failed to install Python3"
  # Verify installation
  if ! command -v python3 &> /dev/null; then
    handle_error 10 "Python3 installation failed"
  fi
  echo "Python3 installed successfully: $(python3 --version)"
else
  echo "Python3 is already installed: $(python3 --version)"
fi

# Check for curl
if ! command -v curl &> /dev/null; then
  echo "Curl not found, installing..."
  apt-get update || handle_error 11 "Failed to update package list"
  apt-get install -y curl || handle_error 12 "Failed to install curl"
  # Verify installation
  if ! command -v curl &> /dev/null; then
    handle_error 13 "Curl installation failed"
  fi
  echo "Curl installed successfully: $(curl --version | head -n 1)"
else
  echo "Curl is already installed: $(curl --version | head -n 1)"
fi

# Create required directories
echo "Creating required directories..."
mkdir -p logs || handle_error 14 "Failed to create logs directory"
mkdir -p certs || handle_error 15 "Failed to create certs directory"
mkdir -p venv || handle_error 16 "Failed to create venv directory"
echo "Directories created successfully"

# Check and set up Python environment with uv
echo "Setting up Python environment with UV..."
if ! command -v uv &> /dev/null; then
  echo "UV not found, installing..."
  curl -LsSf https://astral.sh/uv/install.sh | sh || handle_error 17 "Failed to download UV installer"
  # Verify installation - might need to refresh PATH
  export PATH="$HOME/.cargo/bin:$PATH"
  if ! command -v uv &> /dev/null; then
    handle_error 18 "UV installation failed"
  fi
  echo "UV installed successfully: $(uv --version)"
else
  echo "UV is already installed: $(uv --version)"
fi

echo "Syncing project dependencies..."
uv sync --all-extras || handle_error 19 "Failed to sync project dependencies with UV"
echo "Dependencies synced successfully"

# Activate virtual environment
echo "Activating virtual environment..."
if [ -f venv/bin/activate ]; then
  source venv/bin/activate || handle_error 20 "Failed to activate virtual environment"
  echo "Virtual environment activated successfully"
else
  handle_error 21 "Virtual environment activation script not found"
fi

# Set up environment variables
echo "Setting up environment variables..."
if [ -f .env ]; then
  echo "Loading existing environment variables from .env file"
  source .env || handle_error 22 "Failed to load .env file"
fi

# Ask for each value, using existing values as defaults if available
echo "Please provide the following configuration values (press Enter to use default if shown):"
read -p "Enter Cloudflare API Token [${CF_API_TOKEN:-}]: " CF_API_TOKEN_INPUT
read -p "Enter Cloudflare Zone ID [${CF_ZONE_ID:-}]: " CF_ZONE_ID_INPUT
read -p "Enter Cloudflare Email [${CF_EMAIL:-}]: " CF_EMAIL_INPUT
read -p "Enter Base Domain [${BASE_DOMAIN:-}]: " BASE_DOMAIN_INPUT
read -p "Enter Server IP [${SERVER_IP:-}]: " SERVER_IP_INPUT
read -p "Enter Server SSH User [${SERVER_USER:-root}]: " SERVER_USER_INPUT

# Use new input if provided, otherwise keep existing values
CF_API_TOKEN=${CF_API_TOKEN_INPUT:-${CF_API_TOKEN:-}}
CF_ZONE_ID=${CF_ZONE_ID_INPUT:-${CF_ZONE_ID:-}}
CF_EMAIL=${CF_EMAIL_INPUT:-${CF_EMAIL:-}}
BASE_DOMAIN=${BASE_DOMAIN_INPUT:-${BASE_DOMAIN:-}}
SERVER_IP=${SERVER_IP_INPUT:-${SERVER_IP:-}}
SERVER_USER=${SERVER_USER_INPUT:-${SERVER_USER:-root}}

# Validate required fields
if [ -z "$CF_API_TOKEN" ]; then
  handle_error 23 "Cloudflare API Token is required"
fi
if [ -z "$CF_ZONE_ID" ]; then
  handle_error 24 "Cloudflare Zone ID is required"
fi
if [ -z "$CF_EMAIL" ]; then
  handle_error 25 "Cloudflare Email is required"
fi
if [ -z "$BASE_DOMAIN" ]; then
  handle_error 26 "Base Domain is required"
fi
if [ -z "$SERVER_IP" ]; then
  handle_error 27 "Server IP is required"
fi

echo "Environment variables set successfully"

# Create .env file
echo "Creating .env file..."
cat > .env << EOF || handle_error 28 "Failed to create .env file"
CF_API_TOKEN=$CF_API_TOKEN
CF_ZONE_ID=$CF_ZONE_ID
CF_EMAIL=$CF_EMAIL
BASE_DOMAIN=$BASE_DOMAIN
SERVER_IP=$SERVER_IP
SERVER_USER=$SERVER_USER
EOF
echo ".env file created successfully"

# Make scripts executable
echo "Making scripts executable..."
chmod +x cli/cli.py || handle_error 29 "Failed to make cli.py executable"
chmod +x scripts/tunnel.sh || handle_error 30 "Failed to make tunnel.sh executable"
echo "Scripts made executable successfully"

# Add project root to environment variables
echo "Adding project root to environment variables..."
echo "PROJECT_ROOT=$(pwd)" >> .env || handle_error 31 "Failed to add PROJECT_ROOT to .env file"
echo "PROJECT_ROOT added to environment variables"

# Set up project for development
export PROJECT_ROOT=$(pwd)

# Make wrapper executable
echo "Setting up proxy-manager command..."
if [ -f /usr/local/bin/proxy-manager ]; then
  chmod +x /usr/local/bin/proxy-manager || handle_error 32 "Failed to make proxy-manager executable"
  echo "proxy-manager command set up successfully"
else
  handle_error 33 "proxy-manager command not found in /usr/local/bin"
fi

# Start services
echo "Starting Docker services..."
docker-compose up -d || handle_error 34 "Failed to start Docker services"
echo "Docker services started successfully"

echo "-----------------------------------------"
echo "✅ Setup completed successfully!"
echo "-----------------------------------------"
echo "Use 'proxy-manager setup --subdomain example --local-port 3000 --allowed-ip 1.2.3.4' to create a new proxy"
echo "-----------------------------------------"
exit 0
