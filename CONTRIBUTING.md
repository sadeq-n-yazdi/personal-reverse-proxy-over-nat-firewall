# Contributing to Personal-Grok

Thank you for your interest in contributing to the Personal-Grok project! This document provides guidelines and instructions for contributing.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/sadeq-n-yazdi/personal-grok.git
   cd personal-grok
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the project in development mode:
   ```bash
   pip install uv
   uv pip install -e ".[dev]"
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Workflow

### Code Style

This project uses Ruff for linting and formatting:

- Maximum line length: 120 characters
- Python version: 3.8+
- Follow PEP 8 style guide with minor exceptions defined in pyproject.toml

To check your code:
```bash
uv run ruff check .
uv run ruff format .
```

### Commit Guidelines

- Write clear, concise commit messages
- Reference issue numbers when appropriate
- Make sure pre-commit hooks pass before committing

### Pull Request Process

1. Fork the repository and create a new branch from `master`
2. Make your changes and ensure all tests pass
3. Update documentation if necessary
4. Submit a pull request with a clear description of the changes

## Project Structure

- `docker-compose.yml`: Main service configuration
- `nginx/`: Nginx configuration templates and generated configs
- `personal_grok/`: Python package with CLI tools
- `scripts/`: Setup and utility scripts
- `certs/`: SSL certificate storage (managed by certbot)

## Testing

Run tests before submitting pull requests:

```bash
# TODO: Add testing framework
```

## Documentation

Update documentation when making changes to the code:

- README.md: For user-facing documentation
- CONTRIBUTING.md: For contributor guidelines
- Code comments: For technical details

## License

By contributing to Personal-Grok, you agree that your contributions will be licensed under the project's MIT License.