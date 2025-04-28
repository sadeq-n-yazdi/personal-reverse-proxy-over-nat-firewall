#!/usr/bin/env python3
import argparse
import os
import subprocess

import requests

# Cloudflare API configuration
# If running in a script, try to load .env file directly
try:
    from dotenv import load_dotenv
    
    # Try to find .env file in current directory or parent directories
    env_path = None
    current_dir = os.path.abspath(os.curdir)
    while current_dir != os.path.dirname(current_dir):  # Stop at root
        potential_env = os.path.join(current_dir, '.env')
        if os.path.isfile(potential_env):
            env_path = potential_env
            break
        current_dir = os.path.dirname(current_dir)
    
    if env_path:
        load_dotenv(env_path)
        print(f"Loaded environment from {env_path}")
except ImportError:
    print("python-dotenv not installed, using system environment variables")
except Exception as e:
    print(f"Error loading .env file: {str(e)}")

# Get environment variables
CF_API_TOKEN = os.environ.get('CF_API_TOKEN')
CF_ZONE_ID = os.environ.get('CF_ZONE_ID')
CF_EMAIL = os.environ.get('CF_EMAIL')
BASE_DOMAIN = os.environ.get('BASE_DOMAIN')

def create_subdomain(subdomain):
    """Create a subdomain using Cloudflare API"""
    # Check for required environment variables
    missing_vars = []
    for var_name, var_value in [
        ('CF_API_TOKEN', CF_API_TOKEN),
        ('CF_ZONE_ID', CF_ZONE_ID),
        ('CF_EMAIL', CF_EMAIL),
        ('BASE_DOMAIN', BASE_DOMAIN),
        ('SERVER_IP', os.environ.get('SERVER_IP'))
    ]:
        if not var_value:
            missing_vars.append(var_name)
    
    if missing_vars:
        print(f"Error: The following environment variables are not set: {', '.join(missing_vars)}")
        print("Make sure you've run the setup script and sourced the environment.")
        return False
    
    full_domain = f"{subdomain}.{BASE_DOMAIN}"
    server_ip = os.environ.get('SERVER_IP')
    
    print(f"Creating A record: {subdomain}.{BASE_DOMAIN} -> {server_ip}")
    
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "type": "A",
        "name": subdomain,
        "content": server_ip,
        "ttl": 1,
        "proxied": False
    }
    
    url = f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/dns_records"
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response_json = response.json()
        
        if response.status_code == 200 and response_json.get('success'):
            print(f"Subdomain {full_domain} created successfully")
            return True
        else:
            error_msg = response_json.get('errors', [{'message': 'Unknown error'}])[0].get('message')
            print(f"Failed to create subdomain: {error_msg}")
            print(f"Full response: {response.text}")
            return False
    except Exception as e:
        print(f"Error making request to Cloudflare API: {str(e)}")
        return False

def setup_ssl(domain):
    """Setup SSL certificate using certbot"""
    cmd = [
        "docker-compose", "run", "--rm", "certbot", "certonly",
        "--webroot", "--webroot-path=/var/www/certbot",
        "--email", CF_EMAIL, "--agree-tos", "--no-eff-email",
        "-d", domain
    ]
    
    # Verify Nginx is running and configured properly first
    print("Verifying Nginx configuration before requesting certificate...")
    verify_cmd = ["docker-compose", "exec", "nginx", "nginx", "-t"]
    verify_result = subprocess.run(verify_cmd, capture_output=True, text=True)
    if verify_result.returncode != 0:
        print(f"Nginx configuration test failed: {verify_result.stderr}")
        print("Please check your Nginx configuration before proceeding.")
        return False
    
    # Ensure .well-known directory exists in certbot webroot
    project_root = os.environ.get('PROJECT_ROOT', os.path.expanduser('~/code/personal-reverse-proxy-over-firewall'))
    webroot_dir = os.path.join(project_root, "certbot", "www", ".well-known", "acme-challenge")
    os.makedirs(webroot_dir, exist_ok=True)
    
    print(f"Running command: {' '.join(cmd)}")
    print("This may take a moment...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Command exit code: {result.returncode}")
    
    if result.returncode == 0:
        print(f"SSL certificate for {domain} created successfully")
        return True
    else:
        print(f"Failed to create SSL certificate. Error details:")
        print("---")
        print(result.stderr)
        print("---")
        
        # Provide troubleshooting tips
        print("\nTroubleshooting tips:")
        print("1. Make sure Nginx is running and accessible on port 80")
        print("2. Check that the domain points to your server's IP")
        print("3. Verify that port 80 is open in your firewall")
        print(f"4. Try accessing http://{domain}/.well-known/acme-challenge/ in your browser")
        
        return False

def create_config(domain, local_port, allowed_ip):
    """Create nginx configuration from template"""
    # Get project root directory
    project_root = os.environ.get('PROJECT_ROOT', os.path.expanduser('~/code/personal-reverse-proxy-over-firewall'))
    template_path = os.path.join(project_root, "nginx", "templates", "template.conf")
    
    print(f"Using project root: {project_root}")
    print(f"Template path: {template_path}")
    
    if not os.path.exists(template_path):
        print(f"Error: Template file not found at {template_path}")
        return False
    
    try:
        with open(template_path, 'r') as f:
            template = f.read()
        
        print("Template loaded successfully")
        print(f"Configuring for domain: {domain}, local port: {local_port}, allowed IP: {allowed_ip}")
        
        config = template.replace("{{DOMAIN}}", domain)
        config = config.replace("{{LOCAL_PORT}}", str(local_port))
        config = config.replace("{{ALLOWED_IP}}", allowed_ip)
        
        # Create directories if they don't exist
        available_dir = os.path.join(project_root, "nginx", "available")
        os.makedirs(available_dir, exist_ok=True)
        
        # Write to available directory first
        available_path = os.path.join(available_dir, f"{domain}.conf")
        print(f"Writing configuration to available: {available_path}")
        with open(available_path, 'w') as f:
            f.write(config)
        
        # Then copy to active conf.d directory
        active_path = os.path.join(project_root, "nginx", f"{domain}.conf")
        print(f"Copying configuration to active directory: {active_path}")
        with open(active_path, 'w') as f:
            f.write(config)
        
        print(f"Nginx configuration for {domain} created successfully")
        return True
    except Exception as e:
        print(f"Error creating Nginx configuration: {str(e)}")
        return False

def create_tunnel_command(local_port, remote_port):
    """Generate SSH reverse tunnel command"""
    server_ip = os.environ.get('SERVER_IP')
    server_user = os.environ.get('SERVER_USER', 'root')
    
    command = f"ssh -R {remote_port}:localhost:{local_port} {server_user}@{server_ip}"
    return command

def check_environment():
    """Check if required environment variables are set and load from .env if necessary"""
    required_vars = ['CF_API_TOKEN', 'CF_ZONE_ID', 'CF_EMAIL', 'BASE_DOMAIN', 'SERVER_IP']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("Attempting to load from .env file...")
        
        # Try to find and load .env file
        project_root = os.environ.get('PROJECT_ROOT')
        env_paths = [
            os.path.join(os.getcwd(), '.env'),                      # Current directory
            os.path.join(os.path.expanduser('~'), '.env'),          # Home directory
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')  # Project directory
        ]
        
        if project_root:
            env_paths.insert(0, os.path.join(project_root, '.env'))  # Add PROJECT_ROOT if set
        
        loaded = False
        for path in env_paths:
            if os.path.isfile(path):
                print(f"Found .env file at {path}")
                try:
                    # Manual loading as fallback
                    with open(path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if not line or line.startswith('#') or '=' not in line:
                                continue
                            key, value = line.split('=', 1)
                            os.environ[key] = value
                    loaded = True
                    print("Successfully loaded environment variables from .env file")
                    break
                except Exception as e:
                    print(f"Error loading .env file: {str(e)}")
        
        if not loaded:
            print("Could not find or load .env file")
            return False
        
        # Re-check if variables are set
        still_missing = []
        for var in required_vars:
            if not os.environ.get(var):
                still_missing.append(var)
        
        if still_missing:
            print(f"Still missing required environment variables after loading .env: {', '.join(still_missing)}")
            print("Please run the setup script or set these variables manually")
            return False
    
    # Reload global variables with new environment values
    global CF_API_TOKEN, CF_ZONE_ID, CF_EMAIL, BASE_DOMAIN
    CF_API_TOKEN = os.environ.get('CF_API_TOKEN')
    CF_ZONE_ID = os.environ.get('CF_ZONE_ID')
    CF_EMAIL = os.environ.get('CF_EMAIL')
    BASE_DOMAIN = os.environ.get('BASE_DOMAIN')
    
    return True

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
    
    # Environment check command
    env_parser = subparsers.add_parser("env", help="Check environment variables")
    
    args = parser.parse_args()
    
    if args.command == "env":
        # Print environment variable status
        if check_environment():
            print("\nEnvironment variables are set correctly:")
            print(f"CF_API_TOKEN: {'✓ Set' if CF_API_TOKEN else '✗ Not set'}")
            print(f"CF_ZONE_ID: {'✓ Set' if CF_ZONE_ID else '✗ Not set'}")
            print(f"CF_EMAIL: {'✓ Set' if CF_EMAIL else '✗ Not set'}")
            print(f"BASE_DOMAIN: {BASE_DOMAIN if BASE_DOMAIN else '✗ Not set'}")
            print(f"SERVER_IP: {os.environ.get('SERVER_IP') if os.environ.get('SERVER_IP') else '✗ Not set'}")
            print(f"PROJECT_ROOT: {os.environ.get('PROJECT_ROOT') if os.environ.get('PROJECT_ROOT') else '✗ Not set'}")
        return
    
    # Check environment before processing other commands
    if not check_environment():
        print("Environment check failed. Please run 'proxy-manager env' to debug.")
        return
    
    if args.command == "setup":
        full_domain = f"{args.subdomain}.{BASE_DOMAIN}"
        print(f"\n=== Setting up {full_domain} ===\n")
        
        print("Step 1: Creating subdomain...")
        subdomain_success = create_subdomain(args.subdomain)
        print(f"Subdomain creation {'successful' if subdomain_success else 'failed'}\n")
        
        if subdomain_success:
            print("Step 2: Creating Nginx configuration...")
            config_success = create_config(full_domain, args.local_port, args.allowed_ip)
            print(f"Configuration creation {'successful' if config_success else 'failed'}\n")
            
            if config_success:
                print("Step 3: Setting up SSL certificate...")
                ssl_success = setup_ssl(full_domain)
                print(f"SSL setup {'successful' if ssl_success else 'failed'}\n")
                
                if ssl_success:
                    print("Step 4: Restarting Nginx...")
                    restart_result = subprocess.run(["docker-compose", "restart", "nginx"], capture_output=True, text=True)
                    if restart_result.returncode == 0:
                        print("Nginx restarted successfully\n")
                    else:
                        print(f"Nginx restart failed: {restart_result.stderr}\n")
                    
                    print(f"\n=== Setup complete for {full_domain} ===")
                    print(f"To create a tunnel, run: proxy-manager tunnel --local-port {args.local_port} "
                          "--remote-port <remote_port>")
    
    elif args.command == "tunnel":
        command = create_tunnel_command(args.local_port, args.remote_port)
        print("Run the following command to create the tunnel:")
        print(f"\n{command}\n")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()