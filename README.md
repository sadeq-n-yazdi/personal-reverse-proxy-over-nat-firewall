# Personal Reverse Proxy Over Firewall

A service application that runs on a Debian VPS and allows you to manage an Nginx reverse proxy for exposing local services behind NAT.

## Features

- Docker-based Nginx reverse proxy
- Automatic SSL certificate management with Certbot
- IP address restriction for security
- Cloudflare API integration for subdomain management
- CLI tool for easy management
- SSH tunnel creation similar to `ssh -R`

## Overview

This tool consists of two main components:

1. **Server Component**: Runs on your Debian VPS and manages the Nginx reverse proxy
2. **Client Component**: Runs on your local machine where your services are hosted

## Server Setup (VPS)

### Requirements

- Debian-based VPS (Ubuntu/Debian)
- Root access
- Ports 80, 443, and SSH port open

### Installation Steps

1. Clone this repository to your Debian VPS:

```bash
git clone https://github.com/yourusername/personal-reverse-proxy-over-firewall.git
cd personal-reverse-proxy-over-firewall
```

2. Run the setup script:

```bash
sudo bash scripts/setup.sh
```

The setup script will:
- Install necessary dependencies (Docker, Docker Compose, Python3)
- Set up Python virtual environment with uv package manager
- Install SSL certificates via Certbot
- Configure Nginx as a reverse proxy
- Set up environment variables
- Start the Docker services

3. During setup, you'll be prompted to enter:
   - Cloudflare API Token
   - Cloudflare Zone ID
   - Cloudflare Email
   - Base Domain
   - Server IP
   - Server SSH User

These values are stored in a `.env` file for future use.

### Verifying Server Setup

```bash
# Check if Docker services are running
docker ps

# Verify Nginx is running
curl -I http://localhost

# Check that the proxy-manager command is available
which proxy-manager

# Test the proxy-manager command
proxy-manager --help
```

## Client Setup (Local Machine)

### Requirements

- Python 3.8+
- SSH client
- Local service you want to expose

### Installation Steps

1. Clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/personal-reverse-proxy-over-firewall.git
cd personal-reverse-proxy-over-firewall
```

2. Set up SSH key authentication:

```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy key to VPS
ssh-copy-id user@your-vps-ip
```

3. Create a local configuration file:

```bash
cp config.sample.yaml config.yaml
```

4. Edit the configuration with your details:

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

## Usage

### Setting Up a New Proxy (VPS)

```bash
# On your VPS
proxy-manager setup --subdomain myapp --local-port 3000 --allowed-ip 203.0.113.1
```

This will:
1. Create a new subdomain (myapp.yourdomain.com) using Cloudflare API
2. Generate an SSL certificate for the subdomain
3. Create an Nginx configuration with IP restrictions
4. Restart Nginx to apply the changes

### Creating a Tunnel from Your Local Machine

```bash
# On your local machine
proxy-manager tunnel --local-port 3000 --remote-port 8080
```

Or use the included script:

```bash
# On your local machine
bash scripts/tunnel.sh 3000 8080
```

This will create an SSH tunnel between your local machine and the VPS, exposing your local service (running on port 3000) through the VPS.

### Accessing Your Service

After setting up both the proxy and the tunnel, your service will be accessible at:

```
https://myapp.yourdomain.com
```

The traffic flow works as follows:
1. Client makes request to `https://myapp.yourdomain.com`
2. Request reaches your VPS
3. Nginx on VPS forwards the request through the SSH tunnel
4. Your local service receives the request and responds
5. Response travels back through the same path to the client

## Advanced Usage

### Managing Multiple Services

You can set up multiple proxies and tunnels for different services:

```bash
# On VPS: Set up multiple proxies
proxy-manager setup --subdomain app1 --local-port 3000 --allowed-ip 203.0.113.1
proxy-manager setup --subdomain app2 --local-port 3001 --allowed-ip 203.0.113.1

# On local machine: Create tunnels for each service
bash scripts/tunnel.sh 3000 8080
bash scripts/tunnel.sh 3001 8081
```

### Using Different Local and Remote Ports

The local port (on your development machine) and remote port (on the VPS) can be different:

```bash
# Example: Local service on port 5000, tunnel using port 8080 on VPS
bash scripts/tunnel.sh 5000 8080
```

### Persistent Tunnels

For long-running tunnels, you can use tools like `autossh` or `systemd` service:

```bash
# Install autossh
sudo apt-get install autossh

# Create persistent tunnel
autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -R 8080:localhost:3000 user@your-vps-ip -N
```

## Configuration

### Environment Variables

The following environment variables are used:

- `CF_API_TOKEN`: Cloudflare API token
- `CF_ZONE_ID`: Cloudflare Zone ID for your domain
- `CF_EMAIL`: Email associated with your Cloudflare account
- `BASE_DOMAIN`: Your base domain (e.g., example.com)
- `SERVER_IP`: Your VPS IP address
- `SERVER_USER`: SSH user for your VPS (default: root)

These are set during the setup process and stored in the `.env` file.

### Sample Configuration Files

The project includes several sample configuration files:

- `config.sample.yaml`: Example configuration for multiple domains
- `.env.sample`: Example environment variables file
- `nginx/sample.conf`: Sample Nginx configuration with SSL and security settings

### Getting Required API Keys and IDs

#### Cloudflare API Token

1. Log in to your [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Go to "My Profile" (click your profile icon in the top right)
3. Select "API Tokens" from the left menu
4. Click "Create Token"
5. Select "Create Custom Token"
6. Give it a name (e.g., "Personal-Reverse-Proxy-Over-Firewall")
7. Under "Permissions":
   - Zone - DNS - Edit
   - Zone - SSL and Certificates - Edit
8. Under "Zone Resources":
   - Include - Specific zone - select your domain
9. Set a TTL (time to live) for the token (or leave as is)
10. Click "Continue to summary" and then "Create Token"
11. Copy the token immediately (it won't be shown again)

#### Cloudflare Zone ID

1. Log in to your [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Select the domain you want to use
3. On the "Overview" page, scroll down to the "API" section
4. Your Zone ID is displayed there
5. Copy this ID for use in the setup

## Security Considerations

### IP Restrictions

By default, the proxy requires IP address restrictions. This means only specified IP addresses can access your services.

```bash
# Restrict access to specific IPs
proxy-manager setup --subdomain myapp --local-port 3000 --allowed-ip 203.0.113.1,198.51.100.1
```

### SSL/TLS

All connections use SSL/TLS encryption through Let's Encrypt certificates.

### SSH Security

For better security:
1. Use key-based authentication (disable password authentication)
2. Use a non-root user with appropriate permissions
3. Consider changing the default SSH port

```bash
# On VPS: Edit SSH config
sudo nano /etc/ssh/sshd_config

# Set the following:
PasswordAuthentication no
PermitRootLogin prohibit-password
Port 2222  # Change to a non-standard port

# Restart SSH
sudo systemctl restart sshd
```

### Firewall Configuration

Configure your firewall to only allow necessary ports:

```bash
# On VPS: Set up UFW firewall
sudo apt-get install ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 2222/tcp  # If you changed SSH port
sudo ufw enable
```

## Troubleshooting

### Common Issues

#### SSH Tunnel Not Working

```bash
# Check if SSH tunnel is active
ps aux | grep ssh

# If not active, restart the tunnel
bash scripts/tunnel.sh 3000 8080
```

#### Nginx Configuration Issues

```bash
# Check Nginx configuration
docker exec nginx nginx -t

# Restart Nginx
docker exec nginx nginx -s reload
```

#### Certificate Issues

```bash
# Request new certificates
docker exec certbot certbot renew --force-renewal
```

## License

This project is created by Sadeq N. Yazdi and published under the MIT License without any warranty.

See the [LICENSE](LICENSE) file for details or visit the [Open Source Initiative MIT License page](https://opensource.org/licenses/MIT) for more information.