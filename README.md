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

These are set during the setup process and stored in the `.env` file.

## Security Considerations

- Only specific IP addresses can access the proxy
- All connections use SSL/TLS
- SSH tunnels are used for secure communication

## License

This project is created by Sadeq N. Yazdi and published under the MIT License without any warranty.

See the [LICENSE](LICENSE) file for details or visit the [Open Source Initiative MIT License page](https://opensource.org/licenses/MIT) for more information.