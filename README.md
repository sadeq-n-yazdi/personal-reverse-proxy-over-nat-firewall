# Personal Grok Reverse Proxy Manager

A service application that runs on a Debian VPS and allows you to manage an Nginx reverse proxy for exposing local services behind NAT.

## Features

- Docker-based Nginx reverse proxy
- Automatic SSL certificate management with Certbot
- IP address restriction for security
- Cloudflare API integration for subdomain management
- CLI tool for easy management
- SSH tunnel creation similar to `ssh -R`

## Installation

1. Clone this repository to your Debian VPS:

```bash
git clone https://github.com/yourusername/personal-grok.git
cd personal-grok
```

2. Run the setup script:

```bash
sudo bash scripts/setup.sh
```

This will:
- Install necessary dependencies (Docker, Docker Compose, Python)
- Set up Python virtual environment with uv package manager
- Set up environment variables
- Start the Docker services

## Usage

### Setting up a new proxy

```bash
proxy-manager setup --subdomain myapp --local-port 3000 --allowed-ip 203.0.113.1
```

This will:
1. Create a new subdomain (myapp.yourdomain.com) using Cloudflare API
2. Generate an SSL certificate for the subdomain
3. Create an Nginx configuration with IP restrictions
4. Restart Nginx to apply the changes

### Creating a tunnel from your local machine

```bash
proxy-manager tunnel --local-port 3000 --remote-port 8080
```

This will output an SSH command to create a reverse tunnel:

```
ssh -R 8080:localhost:3000 user@your-vps-ip
```

Run this command on your local machine to expose your local service.

## Configuration

The following environment variables need to be set:

- `CF_API_TOKEN`: Cloudflare API token
- `CF_ZONE_ID`: Cloudflare Zone ID for your domain
- `CF_EMAIL`: Email associated with your Cloudflare account
- `BASE_DOMAIN`: Your base domain (e.g., example.com)
- `SERVER_IP`: Your VPS IP address
- `SERVER_USER`: SSH user for your VPS (default: root)

These are set during the setup process and stored in the `.env` file. A sample environment file (`.env.sample`) is provided with the project.

### Sample Configuration Files

The project includes several sample configuration files to help you get started:

- `.env.sample`: Example environment variables file
- `nginx/sample.conf`: Sample Nginx configuration with SSL and security settings
- `config.sample.yaml`: Example configuration for multiple domains and advanced settings

Copy and modify these files according to your needs:

### Getting Required API Keys and IDs

#### Cloudflare API Token

1. Log in to your [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Go to "My Profile" (click your profile icon in the top right)
3. Select "API Tokens" from the left menu
4. Click "Create Token"
5. Select "Create Custom Token"
6. Give it a name (e.g., "Personal-Grok")
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

#### Let's Encrypt / Certbot

No API key is needed for Let's Encrypt. Certbot will automatically:
1. Generate certificates
2. Verify domain ownership through HTTP challenges
3. Install certificates
4. Configure automatic renewal

Ensure port 80 is open on your VPS for the HTTP challenge to work.

#### SSH Setup for Tunneling

For the SSH tunneling to work properly:
1. Ensure your VPS has SSH access enabled
2. Configure key-based authentication for better security
3. Make sure the user has appropriate permissions
4. Configure your VPS firewall to allow the necessary ports

```bash
# Example: Generate SSH key on your local machine
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy key to VPS
ssh-copy-id user@your-vps-ip
```

## Security Considerations

- Only specific IP addresses can access the proxy
- All connections use SSL/TLS
- SSH tunnels are used for secure communication

## License

This project is created by Sadeq N. Yazdi and published under the MIT License without any warranty.

See the [LICENSE](LICENSE) file for details or visit the [Open Source Initiative MIT License page](https://opensource.org/licenses/MIT) for more information.