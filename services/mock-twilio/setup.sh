#!/bin/bash

# Setup script for mock-twilio service

set -e  # Exit on error

# ANSI color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up mock-twilio service...${NC}"

# Create virtual environment using uv
echo -e "${YELLOW}Creating virtual environment with uv...${NC}"
uv venv || { echo -e "${RED}Failed to create virtual environment!${NC}"; exit 1; }

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate || { echo -e "${RED}Failed to activate virtual environment!${NC}"; exit 1; }

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
uv pip install -e ".[dev]" || { echo -e "${RED}Failed to install dependencies!${NC}"; exit 1; }

# Set up pre-commit hooks
echo -e "${YELLOW}Setting up pre-commit hooks...${NC}"
pre-commit install || { echo -e "${RED}Failed to install pre-commit hooks!${NC}"; exit 1; }

# Create .env file from sample if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from sample...${NC}"
    cp .env.sample .env
fi

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${BLUE}Run the service locally with:${NC}"
echo -e "source .venv/bin/activate"
echo -e "uvicorn mock_twilio.main:app --reload --port 3000"
echo -e "${BLUE}Or use Docker:${NC}"
echo -e "docker-compose up -d"

# Make the script executable
chmod +x setup.sh