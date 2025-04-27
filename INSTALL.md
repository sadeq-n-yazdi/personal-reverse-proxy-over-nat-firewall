# Installation Guide

This guide provides detailed step-by-step instructions for setting up the Personal Reverse Proxy Over Firewall on both your VPS and local machine.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Installation (VPS)](#server-installation-vps)
3. [Client Installation (Local Machine)](#client-installation-local-machine)
4. [Configuration](#configuration)
5. [First-Time Setup](#first-time-setup)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### VPS Requirements
- Debian-based Linux distribution (Debian 10+, Ubuntu 20.04+)
- Root access or sudo privileges
- Open ports: 22 (SSH), 80 (HTTP), 443 (HTTPS)
- Minimum resources: 1GB RAM, 1 CPU core, 10GB storage
- Public IP address

### Local Machine Requirements
- Any operating system with SSH client
- Python 3.8+
- Network connectivity to your VPS
- Local service to expose (web app, API, etc.)

### Accounts Required
- Cloudflare account with a domain registered
- SSH access to your VPS

## Server Installation (VPS)

### Step 1: Update System Packages

```bash
apt-get update && apt-get upgrade -y
```

### Step 2: Install Git

```bash
apt-get install -y git
```

### Step 3: Clone Repository

```bash
git clone https://github.com/yourusername/personal-reverse-proxy-over-firewall.git
cd personal-reverse-proxy-over-firewall
```

### Step 4: Run Setup Script

```bash
# Make the setup script executable
chmod +x scripts/setup.sh

# Run the setup script
sudo bash scripts/setup.sh
```

During the setup, you'll be prompted to enter:
- Cloudflare API Token
- Cloudflare Zone ID
- Cloudflare Email
- Base Domain
- Server IP
- Server SSH User

These values are stored in a `.env` file for future use.

### Step 5: Verify Installation

```bash
# Check if Docker services are running
docker ps

# Verify Nginx is running
curl -I http://localhost

# Check if proxy-manager command is available
which proxy-manager
```

## Client Installation (Local Machine)

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/personal-reverse-proxy-over-firewall.git
cd personal-reverse-proxy-over-firewall
```

### Step 2: Set Up SSH Keys (if not already done)

```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy key to VPS
ssh-copy-id user@your-vps-ip
```

### Step 3: Create Configuration File

```bash
cp config.sample.yaml config.yaml
```

### Step 4: Edit Configuration

Open `config.yaml` in your text editor and update with your details:

```yaml
server:
  host: your-vps-ip
  user: your-ssh-user
  port: 22  # SSH port, usually 22

domains:
  - subdomain: myapp
    local_port: 3000
    remote_port: 8080
    allowed_ips:
      - 192.168.1.1
      - 203.0.113.1
```

## Configuration

### Cloudflare API Setup

1. Log in to your [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Go to "My Profile" > "API Tokens"
3. Click "Create Token"
4. Select "Create Custom Token"
5. Set permissions:
   - Zone > DNS > Edit
   - Zone > SSL and Certificates > Edit
6. Set Zone Resources to your specific domain
7. Create the token and copy it

### Nginx Configuration (Advanced)

If you need to customize the Nginx configuration beyond the defaults:

1. Copy the template:
   ```bash
   cp nginx/template.conf nginx/custom.conf
   ```

2. Edit the custom configuration:
   ```bash
   nano nginx/custom.conf
   ```

3. Use your custom configuration when setting up a proxy:
   ```bash
   proxy-manager setup --subdomain myapp --local-port 3000 --allowed-ip 203.0.113.1 --template custom.conf
   ```

## First-Time Setup

### Setting Up a Proxy

On your VPS, run:

```bash
proxy-manager setup --subdomain myapp --local-port 3000 --allowed-ip 203.0.113.1
```

This will:
1. Create the subdomain in Cloudflare
2. Generate SSL certificates
3. Create Nginx configuration
4. Restart Nginx to apply changes

### Creating Your First Tunnel

On your local machine, run:

```bash
bash scripts/tunnel.sh 3000 8080
```

This creates an SSH tunnel from your local port 3000 to the VPS port 8080.

## Verification

### Check Subdomain in Cloudflare

1. Log in to your Cloudflare dashboard
2. Go to your domain
3. Verify the subdomain is created with the correct A record

### Test the Connection

1. Start your local service on the configured port
2. Create the tunnel
3. Visit `https://myapp.yourdomain.com` in your browser
4. Verify the request reaches your local service

### Check Logs

```bash
# On VPS: Check Nginx logs
docker logs nginx

# On VPS: Check Certbot logs
docker logs certbot

# On local machine: Check SSH tunnel
ps aux | grep ssh
```

## Troubleshooting

### Common Issues

#### SSH Connection Failures

If you see "Permission denied":
```bash
# Check SSH key permissions
chmod 600 ~/.ssh/id_ed25519
chmod 700 ~/.ssh

# Verify connection
ssh -v user@your-vps-ip
```

#### Certificate Generation Failures

```bash
# Check if ports 80 and 443 are open
sudo netstat -tulpn | grep -E ':(80|443)'

# Manually request certificate
docker exec certbot certbot certonly --webroot -w /var/www/certbot -d myapp.yourdomain.com
```

#### Nginx Configuration Errors

```bash
# Check Nginx configuration
docker exec nginx nginx -t

# See detailed Nginx logs
docker logs nginx
```

#### Environment Variable Issues

If you see ".env file not found" or similar errors:
```bash
# Check if .env file exists
ls -la .env

# Verify it has the right permissions
chmod 600 .env
```

### Getting Help

If you continue to experience issues, please:
1. Check the README.md for additional documentation
2. Search existing GitHub issues
3. Open a new issue with details about your problem

## Next Steps

After successful installation:
- Set up multiple proxies for different services
- Create persistent tunnels with autossh or systemd
- Configure monitoring and alerting
- Implement IP restrictions for enhanced security

For advanced usage, refer to the README.md file.