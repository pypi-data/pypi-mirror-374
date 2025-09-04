# Contributing to Adaptive Dynamics Toolkit

Thank you for your interest in contributing to Adaptive Dynamics Toolkit! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before participating in our community.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/adaptive-dynamics-toolkit.git`
3. Install development dependencies: `pip install -e ".[dev,docs,torch,sympy]"`
4. Create a branch for your changes: `git checkout -b feature/your-feature-name`

## Development Process

### Environment Setup

We recommend using Python 3.10 or higher. Set up your development environment:

```bash
# Create and activate a virtual environment
uv venv 
# or
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all extras
pip install -e ".[dev,docs,torch,sympy]"
```

### Code Style

- We follow PEP 8 guidelines with a line length of 100 characters
- Use [ruff](https://github.com/charliermarsh/ruff) for linting
- Use [mypy](http://mypy-lang.org/) for type checking

```bash
# Run the linter
ruff check src tests

# Run type checking
mypy src
```

### Testing

We use pytest for testing:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/adaptive_dynamics
```

### Documentation

- Use Google-style docstrings
- Update documentation when adding new features
- Build and preview documentation locally:

```bash
mkdocs serve
```

## Pull Request Process

1. Ensure your code passes all tests, linting, and type checks
2. Update documentation if needed
3. Include tests for new features
4. Update CHANGELOG.md with your changes under "Unreleased"
5. Submit a pull request to the `main` branch
6. Sign the Contributor License Agreement (CLA) if prompted

## Feature Requests and Bug Reports

- Use GitHub issues to report bugs or request features
- Check existing issues before creating new ones
- Use the provided templates for bug reports and feature requests

## Community

- Join our [Discord server](https://discord.gg/YOUR_INVITE_CODE) for discussions
- Subscribe to our newsletter for updates

## License

- By contributing to this project, you agree that your contributions will be licensed under the project's [MIT License](LICENSE)
- Note that the Pro features are under a separate commercial license