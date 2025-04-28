#!/bin/bash
# Exit on error but allow for error handling
set -o pipefail

# Check if terminal supports colors
if [ -t 1 ] && command -v tput > /dev/null; then
  ncolors=$(tput colors)
  if [ -n "$ncolors" ] && [ $ncolors -ge 8 ]; then
    # Terminal supports colors
    NORMAL=$(tput sgr0)
    RED=$(tput setaf 1)
    GREEN=$(tput setaf 2)
    YELLOW=$(tput setaf 3)
    BLUE=$(tput setaf 4)
    WHITE=$(tput setaf 7)
    BOLD=$(tput bold)
  fi
fi

# Colored output functions
info() {
  echo "${BLUE}INFO:${NORMAL} $1"
}

success() {
  echo "${GREEN}SUCCESS:${NORMAL} $1"
}

warning() {
  echo "${YELLOW}WARNING:${NORMAL} $1"
}

# Error handling function
handle_error() {
  local exit_code=$1
  local error_message=$2
  echo "${RED}ERROR:${NORMAL} $error_message (exit code: $exit_code)"
  exit $exit_code
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  handle_error 1 "This script must be run as root"
fi

echo "${BOLD}Starting setup process...${NORMAL}"

# Check and install dependencies
info "Checking for dependencies..."

# Check for Docker
if ! command -v docker &> /dev/null; then
  info "Docker not found, installing..."
  apt-get update || handle_error 2 "Failed to update package list"
  apt-get install -y docker.io || handle_error 3 "Failed to install Docker"
  # Verify installation
  if ! command -v docker &> /dev/null; then
    handle_error 4 "Docker installation failed"
  fi
  success "Docker installed successfully: $(docker --version)"
else
  info "Docker is already installed: $(docker --version)"
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
  info "Docker Compose not found, installing..."
  apt-get update || handle_error 5 "Failed to update package list"
  apt-get install -y docker-compose || handle_error 6 "Failed to install Docker Compose"
  # Verify installation
  if ! command -v docker-compose &> /dev/null; then
    handle_error 7 "Docker Compose installation failed"
  fi
  success "Docker Compose installed successfully: $(docker-compose --version)"
else
  info "Docker Compose is already installed: $(docker-compose --version)"
fi

# Check for Python3
if ! command -v python3 &> /dev/null; then
  info "Python3 not found, installing..."
  apt-get update || handle_error 8 "Failed to update package list"
  apt-get install -y python3 python3-venv || handle_error 9 "Failed to install Python3"
  # Verify installation
  if ! command -v python3 &> /dev/null; then
    handle_error 10 "Python3 installation failed"
  fi
  success "Python3 installed successfully: $(python3 --version)"
else
  info "Python3 is already installed: $(python3 --version)"
fi

# Check for curl
if ! command -v curl &> /dev/null; then
  info "Curl not found, installing..."
  apt-get update || handle_error 11 "Failed to update package list"
  apt-get install -y curl || handle_error 12 "Failed to install curl"
  # Verify installation
  if ! command -v curl &> /dev/null; then
    handle_error 13 "Curl installation failed"
  fi
  success "Curl installed successfully: $(curl --version | head -n 1)"
else
  info "Curl is already installed: $(curl --version | head -n 1)"
fi

# Create required directories
info "Creating required directories..."
mkdir -p logs || handle_error 14 "Failed to create logs directory"
mkdir -p certs || handle_error 15 "Failed to create certs directory"
mkdir -p nginx/available nginx/templates || handle_error 16 "Failed to create nginx directories"
mkdir -p certbot/www || handle_error 17 "Failed to create certbot directories"

# Generate a random serial number for the certificate
SERIAL=$(openssl rand -hex 8)

# Create default self-signed certificate for Nginx
info "Creating self-signed certificate for default server..."
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
  -keyout nginx/default-key.pem \
  -out nginx/default-cert.pem \
  -subj "/CN=localhost" \
  -addext "serialNumber=$SERIAL" \
  -quiet || handle_error 18 "Failed to create self-signed certificate"

success "Directories created successfully"

# Check and set up Python environment with uv
info "Setting up Python environment with UV..."
if ! command -v uv &> /dev/null; then
  info "UV not found, installing..."
  curl -LsSf https://astral.sh/uv/install.sh | sh || handle_error 17 "Failed to download UV installer"
  # Verify installation - might need to refresh PATH
  export PATH="$HOME/.cargo/bin:$PATH"
  if ! command -v uv &> /dev/null; then
    handle_error 18 "UV installation failed"
  fi
  success "UV installed successfully: $(uv --version)"
else
  info "UV is already installed: $(uv --version)"
fi

# Create Python virtual environment if it doesn't exist
info "Setting up Python virtual environment..."
if [ ! -f .venv/bin/activate ]; then
  info "Creating new virtual environment..."
  uv venv || handle_error 19 "Failed to create virtual environment with UV"
  success "Virtual environment created successfully"
fi

# Activate virtual environment
info "Activating virtual environment..."
source .venv/bin/activate || handle_error 20 "Failed to activate virtual environment"
success "Virtual environment activated successfully"

info "Syncing project dependencies..."
uv sync --all-extras || handle_error 21 "Failed to sync project dependencies with UV"
success "Dependencies synced successfully"

# Set up environment variables
info "Setting up environment variables..."
if [ -f .env ]; then
  info "Loading existing environment variables from .env file"
  # Use . instead of source for better compatibility
  . .env || warning "Failed to load .env file, proceeding with user input only"
else
  warning "No .env file found, proceeding with user input only"
fi

# Ask for each value, using existing values as defaults if available
echo "${BOLD}Please provide the following configuration values (press Enter to use default if shown):${NORMAL}"
read -p "${WHITE}Enter Cloudflare API Token [${CF_API_TOKEN:-}]: ${NORMAL}" CF_API_TOKEN_INPUT
read -p "${WHITE}Enter Cloudflare Zone ID [${CF_ZONE_ID:-}]: ${NORMAL}" CF_ZONE_ID_INPUT
read -p "${WHITE}Enter Cloudflare Email [${CF_EMAIL:-}]: ${NORMAL}" CF_EMAIL_INPUT
read -p "${WHITE}Enter Base Domain [${BASE_DOMAIN:-}]: ${NORMAL}" BASE_DOMAIN_INPUT
read -p "${WHITE}Enter Server IP [${SERVER_IP:-}]: ${NORMAL}" SERVER_IP_INPUT
read -p "${WHITE}Enter Server SSH User [${SERVER_USER:-root}]: ${NORMAL}" SERVER_USER_INPUT

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

success "Environment variables set successfully"

# Create .env file
info "Creating .env file..."
cat > .env << EOF || handle_error 28 "Failed to create .env file"
CF_API_TOKEN=$CF_API_TOKEN
CF_ZONE_ID=$CF_ZONE_ID
CF_EMAIL=$CF_EMAIL
BASE_DOMAIN=$BASE_DOMAIN
SERVER_IP=$SERVER_IP
SERVER_USER=$SERVER_USER
EOF
success ".env file created successfully"

# Make scripts executable
info "Making scripts executable..."
chmod +x cli/cli.py || handle_error 29 "Failed to make cli.py executable"
chmod +x scripts/tunnel.sh || handle_error 30 "Failed to make tunnel.sh executable"
success "Scripts made executable successfully"

# Add project root to environment variables
info "Adding project root to environment variables..."
echo "PROJECT_ROOT=$(pwd)" >> .env || handle_error 31 "Failed to add PROJECT_ROOT to .env file"
success "PROJECT_ROOT added to environment variables"

# Set up project for development
export PROJECT_ROOT=$(pwd)

# Create and install proxy-manager command wrapper
info "Setting up proxy-manager command..."
WRAPPER_PATH="/usr/local/bin/proxy-manager"
cat > $WRAPPER_PATH << 'EOFWRAPPER' || handle_error 32 "Failed to create proxy-manager wrapper"
#!/bin/bash
# Proxy Manager wrapper script

# Source environment if available
if [ -f ~/.proxy-manager-env ]; then
  source ~/.proxy-manager-env
fi

# Get the project directory
PROJECT_DIR=${PROJECT_ROOT:-$(dirname $(dirname $(readlink -f $0)))}

# Activate virtual environment if it exists
if [ -f "${PROJECT_DIR}/.venv/bin/activate" ]; then
  source "${PROJECT_DIR}/.venv/bin/activate"
fi

# Execute the CLI script
python3 "${PROJECT_DIR}/yazdi_prpon/cli.py" "$@"
EOFWRAPPER

chmod +x $WRAPPER_PATH || handle_error 33 "Failed to make proxy-manager wrapper executable"

# Store environment for the wrapper
info "Saving environment for proxy-manager wrapper..."
PROJECT_ROOT_ABS=$(realpath .)
cat > ~/.proxy-manager-env << EOF || handle_error 34 "Failed to create environment file"
PROJECT_ROOT="${PROJECT_ROOT_ABS}"
EOF

success "proxy-manager command set up successfully"

# Start services
info "Starting Docker services..."
docker-compose up -d || handle_error 35 "Failed to start Docker services"
success "Docker services started successfully"

echo "${GREEN}-----------------------------------------${NORMAL}"
echo "${BOLD}${GREEN}✅ Setup completed successfully!${NORMAL}"
echo "${GREEN}-----------------------------------------${NORMAL}"
echo "${BOLD}Use 'proxy-manager setup --subdomain example --local-port 3000 --allowed-ip 1.2.3.4' to create a new proxy${NORMAL}"
echo "${GREEN}-----------------------------------------${NORMAL}"
exit 0
