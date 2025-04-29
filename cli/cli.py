#!/usr/bin/env python3
# This script runs inside the virtual environment created in setup.sh
import argparse
import os
import subprocess

import requests

# Cloudflare API configuration
CF_API_TOKEN = os.environ.get('CF_API_TOKEN')
CF_ZONE_ID = os.environ.get('CF_ZONE_ID')
CF_EMAIL = os.environ.get('CF_EMAIL')
BASE_DOMAIN = os.environ.get('BASE_DOMAIN')

def create_subdomain(subdomain):
    """Create a subdomain using Cloudflare API"""
    if not all([CF_API_TOKEN, CF_ZONE_ID, CF_EMAIL, BASE_DOMAIN]):
        print("Error: Cloudflare environment variables not set")
        return False
    
    full_domain = f"{subdomain}.{BASE_DOMAIN}"
    
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "type": "A",
        "name": subdomain,
        "content": os.environ.get('SERVER_IP'),
        "ttl": 1,
        "proxied": False
    }
    
    url = f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/dns_records"
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"Subdomain {full_domain} created successfully")
        return True
    else:
        print(f"Failed to create subdomain: {response.text}")
        return False

def setup_ssl(domain):
    """Setup SSL certificate using certbot"""
    cmd = [
        "docker-compose", "run", "--rm", "certbot", "certonly",
        "--webroot", "--webroot-path=/var/www/certbot",
        "--email", CF_EMAIL, "--agree-tos", "--no-eff-email",
        "-d", domain
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"SSL certificate for {domain} created successfully")
        return True
    else:
        print(f"Failed to create SSL certificate: {result.stderr}")
        return False

def create_config(domain, local_port, allowed_ip):
    """Create nginx configuration from template"""
    template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "nginx", "template.conf")
    
    with open(template_path, 'r') as f:
        template = f.read()
    
    config = template.replace("{{DOMAIN}}", domain)
    config = config.replace("{{LOCAL_PORT}}", str(local_port))
    config = config.replace("{{ALLOWED_IP}}", allowed_ip)
    
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "nginx", f"{domain}.conf")
    
    with open(config_path, 'w') as f:
        f.write(config)
    
    print(f"Nginx configuration for {domain} created")
    return True

def create_tunnel_command(local_port, remote_port):
    """Generate SSH reverse tunnel command"""
    server_ip = os.environ.get('SERVER_IP')
    server_user = os.environ.get('SERVER_USER', 'root')
    
    command = f"ssh -R {remote_port}:localhost:{local_port} {server_user}@{server_ip}"
    return command

def main():
    parser = argparse.ArgumentParser(description="Reverse proxy manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Setup a new reverse proxy")
    setup_parser.add_argument("--subdomain", required=True, help="Subdomain to create")
    setup_parser.add_argument("--local-port", type=int, required=True, help="Local port to forward")
    setup_parser.add_argument("--allowed-ip", required=True, help="IP allowed to access the proxy")
    
    # Tunnel command
    tunnel_parser = subparsers.add_parser("tunnel", help="Create SSH tunnel")
    tunnel_parser.add_argument("--local-port", type=int, required=True, help="Local port to forward")
    tunnel_parser.add_argument("--remote-port", type=int, required=True, help="Remote port on server")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        full_domain = f"{args.subdomain}.{BASE_DOMAIN}"
        if create_subdomain(args.subdomain):
            if create_config(full_domain, args.local_port, args.allowed_ip):
                if setup_ssl(full_domain):
                    print("Restarting nginx...")
                    subprocess.run(["docker-compose", "restart", "nginx"])
                    print(f"\nSetup complete for {full_domain}")
                    print(f"To create a tunnel, run: ./cli.py tunnel --local-port {args.local_port} --remote-port <remote_port>")
    
    elif args.command == "tunnel":
        command = create_tunnel_command(args.local_port, args.remote_port)
        print("Run the following command to create the tunnel:")
        print(f"\n{command}\n")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()