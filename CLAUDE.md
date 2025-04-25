# Instructions for Claude

## Project Overview
Personal-Grok is a reverse proxy service application that runs on a Debian VPS. It manages Nginx configurations and creates secure tunnels for exposing services behind NAT. The project provides a CLI tool for managing proxy services and secure tunnels for developers working behind firewalls.

## AI Agent Guidelines

### General Approach
When working with this codebase, follow these general guidelines:
- First understand the project architecture before suggesting changes
- Focus on security as a priority, especially for network-facing code
- Ensure backward compatibility with existing configurations
- Prefer simplicity over complexity in all solutions

### When Making Code Changes
1. First analyze the problem thoroughly before implementing
2. Break implementation into logical steps
3. For each change, verify it won't break existing functionality
4. Ensure new code follows the project's style and conventions
5. Add appropriate error handling for network operations
6. Ensure all user inputs are properly validated
7. Consider security implications of all changes

### Security Considerations
- Never expose sensitive information in logs or error messages
- Always validate and sanitize user input
- Use secure defaults for all configuration options
- Follow principle of least privilege for all operations
- Ensure proper handling of SSL certificates
- Implement proper authentication for all endpoints
- Be cautious with any file operations to prevent path traversal

### Code Quality Standards
- Follow PEP 8 with 120 character line length
- Use type hints for all new functions
- Write clear docstrings for all functions
- Use descriptive variable and function names
- Avoid complex nested conditions
- Keep functions focused on a single responsibility
- Ensure proper error handling

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
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
uv pip install -e ".[dev]"
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
- `CONTRIBUTING.md`: Guidelines for contributors
- `LICENSE`: MIT License information
- `CLAUDE.md`: Instructions for Claude AI assistant

## Development Standards
- Use ruff for linting and formatting
- Follow a 120 character line length limit
- Ensure pre-commit hooks pass before committing
- Maintain clean code structure with proper imports
- Use virtual environments for all Python work
- All changes must be properly documented

## Licensing
This project is created by Sadeq N. Yazdi and published under the MIT License without any warranty. See the LICENSE file for details.

## Pre-commit Hooks
Pre-commit hooks are set up to ensure code quality:
- Ruff for linting and formatting
- Trailing whitespace removal
- EOF fixing
- YAML/TOML validation
- Detection of large files and private keys

## Key Dependencies
- Docker and Docker Compose for containerization
- Nginx for reverse proxy
- Certbot for SSL certificate management
- Python 3.8+ with virtual environment
- Uv for Python package management

## AI Assistant Interaction Guidelines

### Effective Prompting
When requesting assistance from Claude or other AI assistants:
- Be specific about what part of the codebase you're working with
- Provide context about the issue or feature you're addressing
- Specify constraints (e.g., "maintain backward compatibility")
- Ask for explanation of any unclear recommendations

### For Security-Related Changes
When requesting changes that involve:
- Network communication
- Authentication
- Configuration management
- Certificate handling
- Domain management via Cloudflare

Always ask the AI to specifically address security implications of the changes.

### For CLI Tool Development
When enhancing the CLI tool:
- Prioritize user experience and clear error messages
- Ensure consistent command patterns
- Maintain backward compatibility
- Consider input validation and security

### For Infrastructure Changes
When modifying Docker or Nginx configurations:
- Validate changes thoroughly
- Consider production deployment implications
- Ensure proper error handling and logging
- Document any change to default behaviors