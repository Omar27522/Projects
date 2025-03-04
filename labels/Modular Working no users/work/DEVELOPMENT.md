# Development Guide

This document provides guidelines and instructions for developing the Label Maker Management Application.

## Setting Up the Development Environment

1. Run the setup script to create a virtual environment and install dependencies:

```powershell
.\setup_dev.ps1
```

This script will:
- Create a virtual environment in the `venv` directory
- Install project dependencies from `requirements.txt`
- Install development dependencies (pylint, pytest, autopep8, black)
- Create a basic test structure
- Generate a pylint configuration file

## Development Workflow

### Code Style

This project follows PEP 8 style guidelines. You can format your code using:

```
black src
```

### Linting

Run linting checks with:

```
pylint src
```

### Testing

Run tests with:

```
pytest tests
```

## Git Hooks

This project includes Git hooks to ensure code quality:

1. Set up Git to use the hooks directory:

```
git config core.hooksPath .githooks
```

2. Make the hooks executable:

```
chmod +x .githooks/pre-commit
```

The pre-commit hook will run linting and tests before allowing commits.

## Debugging

The project is configured with debug configurations in the `.windsurf` file. You can:

1. Debug the current file
2. Debug the main application

## Environments

The project supports two environments:

1. **Development**: Enables debug mode and verbose logging
2. **Production**: Disables debug mode and reduces logging verbosity

## Project Structure

```
work/
├── assets/            # Application assets
├── logs/              # Log files
├── src/               # Source code
│   ├── config/        # Configuration management
│   ├── ui/            # User interface components
│   └── utils/         # Utility functions
├── tests/             # Test files
├── .githooks/         # Git hooks
├── .windsurf          # Windsurf IDE configuration
├── main.pyw           # Application entry point
├── requirements.txt   # Dependencies
└── setup_dev.ps1      # Development setup script
```

## Adding New Features

When adding new features:

1. Create appropriate test cases in the `tests` directory
2. Follow the modular structure of the application
3. Update documentation as needed
4. Run linting and tests before committing

## Releasing

To prepare a release:

1. Update version information
2. Run all tests
3. Create a release branch
4. Tag the release with the version number
