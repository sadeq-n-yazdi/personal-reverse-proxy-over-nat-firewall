# Code Review Style Guide

## Project Overview
Personal-Reverse-Proxy-Over-Firewall is a reverse proxy service that runs on a Debian VPS, managing Nginx configurations and creating secure tunnels for exposing services behind NAT firewalls.

## Code Style Standards
- Follow PEP 8 with 120 character line length
- Use type hints for all functions
- Write clear docstrings for all functions
- Use descriptive variable and function names
- Avoid complex nested conditions
- Keep functions focused on a single responsibility
- Ensure proper error handling

## Security Priorities
- Never expose sensitive information in logs or error messages
- Always validate and sanitize user inputs
- Use secure defaults for all configuration options
- Follow principle of least privilege
- Ensure proper SSL certificate handling
- Implement proper authentication for all endpoints
- Be cautious with file operations to prevent path traversal

## Pull Request Review Guidelines
When reviewing code, check for:
- Adherence to project code style and conventions
- Security vulnerabilities, especially in network-facing code
- Proper error handling, especially for network operations
- Input validation for all user-provided data
- Backward compatibility with existing configurations
- Code simplicity and readability
- Edge case handling
- Proper documentation
- Type hint usage

## Development Workflow
- Changes should be properly linted (ruff)
- Pre-commit hooks should be passing
- Code should maintain a clean structure
- Virtual environments should be used for Python work
- Changes must be properly documented