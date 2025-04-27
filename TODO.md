# TODO List

This document tracks planned enhancements, pending fixes, and feature ideas for the Personal Reverse Proxy Over Firewall project.

## High Priority

- [ ] Add automated tests for CLI commands
- [ ] Improve error handling in tunnel script
- [ ] Create systemd service template for persistent tunnels
- [ ] Add validation for Cloudflare API responses
- [ ] Update documentation with troubleshooting examples

## Features

- [ ] Add multi-domain support in a single config
- [ ] Implement connection monitoring dashboard
- [ ] Add automatic reconnection for dropped tunnels
- [ ] Create configuration wizard for first-time setup
- [ ] Support for wildcard subdomains
- [ ] Add HTTP basic auth option for protected endpoints

## Security Enhancements

- [ ] Implement automatic security headers in Nginx
- [ ] Add rate limiting for proxy endpoints
- [ ] Support for client certificate authentication
- [ ] Add audit logging for connection attempts
- [ ] Implement IP geolocation restrictions

## Performance Improvements

- [ ] Optimize Nginx configuration for better performance
- [ ] Add caching options for static content
- [ ] Implement connection pooling for tunnels
- [ ] Add compression for HTTP responses
- [ ] Optimize Docker image sizes

## Bug Fixes

- [x] Fix virtual environment activation in setup script
- [x] Fix .env file handling in tunnel script
- [ ] Fix error when subdomain already exists
- [ ] Address permission issues in Docker volumes
- [ ] Fix certificate renewal failures

## Documentation

- [x] Add detailed setup instructions for VPS and local machine
- [x] Create INSTALL.md with step-by-step guide
- [ ] Add video tutorial for setup process
- [ ] Document all CLI options and arguments
- [ ] Create examples directory with sample configurations

## CI/CD

- [ ] Set up GitHub Actions for automated testing
- [ ] Implement automatic Docker image builds
- [ ] Add version tagging for releases
- [ ] Create release automation script
- [ ] Add integration tests with real-world scenarios

## Maintenance

- [ ] Update dependencies to latest versions
- [ ] Refactor CLI code for better maintainability
- [ ] Improve typing coverage in Python code
- [ ] Add proper logging throughout the application
- [ ] Implement telemetry for anonymous usage statistics (opt-in)

## Long-term Ideas

- [ ] Web UI for managing proxies and tunnels
- [ ] Support for multiple cloud providers (not just Cloudflare)
- [ ] Mobile app for monitoring and management
- [ ] Plugin system for custom extensions
- [ ] Integration with popular development tools

## Completed

- [x] Basic implementation of proxy management
- [x] SSH tunnel script implementation
- [x] Cloudflare API integration
- [x] Nginx configuration templates
- [x] Setup script for VPS
- [x] Add colorized output to scripts
- [x] Make scripts executable with proper permissions
- [x] Update documentation with detailed usage instructions