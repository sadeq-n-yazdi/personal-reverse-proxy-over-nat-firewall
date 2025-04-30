#!/bin/bash

# Test runner script for mock-twilio service

set -e  # Exit on error

# ANSI color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Running tests for mock-twilio service...${NC}"

# Activate virtual environment
if [ -d ".venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source .venv/bin/activate || { echo -e "${RED}Failed to activate virtual environment!${NC}"; exit 1; }
else
    echo -e "${RED}Virtual environment not found. Run setup.sh first.${NC}"
    exit 1
fi

# Run ruff linting
echo -e "${YELLOW}Running ruff linting...${NC}"
ruff check . || { echo -e "${RED}Linting failed!${NC}"; exit 1; }

# Run ruff formatting check
echo -e "${YELLOW}Checking code formatting...${NC}"
ruff format --check . || { echo -e "${YELLOW}Formatting issues found, running formatter...${NC}"; ruff format .; }

# Run pytest
echo -e "${YELLOW}Running tests...${NC}"
pytest -vv || { echo -e "${RED}Tests failed!${NC}"; exit 1; }

echo -e "${GREEN}All tests passed!${NC}"