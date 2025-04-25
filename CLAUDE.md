# Instructions for Claude

## Project Overview
Personal-Grok is a reverse proxy service application that runs on a Debian VPS. It manages Nginx configurations and creates secure tunnels for exposing services behind NAT.

## Development Workflow

### Code Quality Checks
Before committing changes, run the following commands:

```bash
# Lint and format code with ruff
uv run ruff check .
uv run ruff format .

# Run pre-commit hooks
pre-commit run --all-files
```

### Environment Setup
Always use the virtual environment for development:

```bash
source venv/bin/activate
```

### CLI Commands
The CLI tool provides commands for managing proxies:

```bash
# Create a new proxy
proxy-manager setup --subdomain myapp --local-port 3000 --allowed-ip 203.0.113.1

# Create a tunnel
proxy-manager tunnel --local-port 3000 --remote-port 8080
```

## Project Structure
- `docker-compose.yml`: Main service configuration
- `nginx/`: Nginx configuration templates and generated configs
- `personal_grok/`: Python package with CLI tools
- `scripts/`: Setup and utility scripts
- `certs/`: SSL certificate storage (managed by certbot)

## Development Standards
- Use ruff for linting and formatting
- Follow a 120 character line length limit
- Ensure pre-commit hooks pass before committing
- Maintain clean code structure with proper imports
- Use virtual environments for all Python work