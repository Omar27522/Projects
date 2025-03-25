# Label Maker Application Documentation

## Overview

This documentation provides detailed information about the Label Maker application, its components, and how they interact.

## Table of Contents

### Core Components

- [Welcome Window](welcome_window.md): Documentation for the main welcome window interface

### Configuration

- Configuration Management: Details about how application settings are managed and persisted

### User Interface

- Window State Management: Information about how window state is tracked and managed
- Button Styling: Details about the Material Design-inspired button styling

### Features

- Label Count Display: Information about the dynamic label count feature
- Directory Management: How label directories are selected and managed

## Development Guidelines

### Adding New Features

1. Create appropriate documentation in the `docs/` directory
2. Add comprehensive docstrings to your code
3. Update the README.md with information about the new feature
4. Follow the existing code style and structure

### Code Style

- Use descriptive variable and function names
- Add docstrings to all functions and classes
- Use type hints where appropriate
- Follow PEP 8 guidelines

## Troubleshooting

### Common Issues

- **ModuleNotFoundError**: Ensure you're running the application from the correct directory or using the main.py entry point
- **Directory Access Issues**: Make sure the application has appropriate permissions to access the labels directory
