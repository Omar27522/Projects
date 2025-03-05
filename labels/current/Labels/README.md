# Label Maker Management Application

## Overview
This application provides a modular interface for managing the Label Maker application. It has been designed with a focus on modularity, maintainability, and extensibility.

## Project Structure
```
work/
├── assets/            # Application assets
├── logs/              # Log files
├── src/               # Source code
│   ├── config/        # Configuration management
│   │   └── config_manager.py
│   ├── ui/            # User interface components
│   │   ├── welcome_window.py
│   │   └── window_state.py
│   └── utils/         # Utility functions
│       └── logger.py
├── main.pyw           # Application entry point
└── requirements.txt   # Dependencies
```

## Features
- Modular application structure
- Centralized configuration management
- Comprehensive logging
- Window state tracking
- Welcome screen with interactive buttons
- Integration with Label Maker application

## Dependencies
- Python 3.x
- pywin32
- pyautogui

## Installation
1. Clone or download this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
Run the application by executing `main.pyw`:
```
python main.pyw
```

### Main Functions
- **Labels**: Select a directory containing label files
- **Management**: Open the Label Maker file viewer for the selected labels directory
- **Settings**: Configure application settings

## Development
The application is designed to be easily extended with new features:
- Add new UI components in the `src/ui/` directory
- Extend configuration options in `src/config/config_manager.py`
- Add utility functions in `src/utils/`

## Integration with Label Maker
The application integrates with the Label Maker application by:
1. Detecting the Label Maker installation directory
2. Launching Label Maker with appropriate parameters
3. Managing window focus between applications
