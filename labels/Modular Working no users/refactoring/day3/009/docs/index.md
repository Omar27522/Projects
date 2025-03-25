# Label Maker Application Documentation

## Overview

This documentation provides detailed information about the Label Maker application, its components, and how they interact.

## Table of Contents

### Core Components

- [Welcome Window](welcome_window.md): Documentation for the main welcome window interface
- [UI Components](ui_components.md): Documentation for the standardized UI components
- [Returns Operations](returns_operations.md): Documentation for the returns data management
- [Google Sheets Integration](google_sheets_integration.md): Documentation for the Google Sheets integration

### Configuration

- [Configuration Management](configuration.md): Details about how application settings are managed and persisted
- [Settings Operations](settings_operations.md): Documentation for the settings dialog and operations

### User Interface

- [Window State Management](window_state.md): Information about how window state is tracked and managed
- [Button Styling](button_styling.md): Details about the Material Design-inspired button styling
- [Form Components](form_components.md): Documentation for form field creation and validation
- [Edit Record Window](edit_record_window.md): Documentation for the scrollable edit record interface
- [Create Label Window](create_label_window.md): Documentation for the label creation interface with auto-copy and tab functionality

### Features

- [Label Count Display](label_count.md): Information about the dynamic label count feature
- [Directory Management](directory_management.md): How label directories are selected and managed
- [Returns Data Management](returns_data.md): How shipping records are managed and edited
- [Google Sheets Tracking](sheets_tracking.md): How tracking information is synchronized with Google Sheets

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

### UI Development

- Use the standardized UI components from `src/utils/ui_components.py`
- Follow the Material Design color scheme
- Ensure all interfaces are responsive and user-friendly
- Implement proper validation for all user inputs

## Troubleshooting

### Common Issues

- **ModuleNotFoundError**: Ensure you're running the application from the correct directory or using the main.py entry point
- **Directory Access Issues**: Make sure the application has appropriate permissions to access the labels directory
- **Google Sheets Connection Issues**: Verify your credentials.json file and internet connection
- **UI Scaling Issues**: Check your system's DPI settings if UI elements appear too small or large
