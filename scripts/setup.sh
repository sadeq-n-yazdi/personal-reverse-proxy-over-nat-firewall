#!/bin/bash
set -e

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Install dependencies
apt-get update
apt-get install -y docker.io docker-compose python3 python3-pip

# Create required directories
mkdir -p logs
mkdir -p certs

# Set up environment variables
read -p "Enter Cloudflare API Token: " CF_API_TOKEN
read -p "Enter Cloudflare Zone ID: " CF_ZONE_ID
read -p "Enter Cloudflare Email: " CF_EMAIL
read -p "Enter Base Domain: " BASE_DOMAIN
read -p "Enter Server IP: " SERVER_IP
read -p "Enter Server SSH User (default: root): " SERVER_USER
SERVER_USER=${SERVER_USER:-root}

# Create .env file
cat > .env << EOF
CF_API_TOKEN=$CF_API_TOKEN
CF_ZONE_ID=$CF_ZONE_ID
CF_EMAIL=$CF_EMAIL
BASE_DOMAIN=$BASE_DOMAIN
SERVER_IP=$SERVER_IP
SERVER_USER=$SERVER_USER
EOF

# Install Python dependencies
pip3 install requests

# Make scripts executable
chmod +x cli/cli.py
chmod +x scripts/tunnel.sh

# Create symbolic link
ln -sf $(pwd)/cli/cli.py /usr/local/bin/proxy-manager

# Start services
docker-compose up -d

echo "Setup complete!"
echo "Use 'proxy-manager setup --subdomain example --local-port 3000 --allowed-ip 1.2.3.4' to create a new proxy"