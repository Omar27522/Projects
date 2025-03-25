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
│   │   ├── google_sheets_dialog.py
│   │   ├── label_window.py
│   │   └── window_state.py
│   └── utils/         # Utility functions
│       ├── ui_components.py
│       ├── returns_operations.py
│       ├── sheets_operations.py
│       ├── settings_operations.py
│       └── logger.py
├── main.pyw           # Application entry point
├── label_maker_settings.json  # Application settings
├── GOOGLE_SHEETS_SETUP.md     # Google Sheets setup guide
└── requirements.txt   # Dependencies
```

## Features
- Modular application structure
- Centralized configuration management
- Comprehensive logging
- Window state tracking
- Welcome screen with interactive buttons
- Integration with Label Maker application
- Google Sheets integration for tracking
- Returns Data management with scrollable edit interface
- Dynamic label count display in the title section

## Dependencies
- Python 3.6+
- pywin32
- pyautogui
- gspread
- oauth2client
- Pillow

## Installation
1. Clone or download this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. For Google Sheets integration, follow the instructions in `GOOGLE_SHEETS_SETUP.md`

## Usage
Run the application by executing `main.pyw`:
```
python main.pyw
```

### Main Functions
- **User**: Quick access to user-related functions
- **Labels**: Access Returns Data and label management features
- **Management**: Open the Label Maker file viewer for the selected labels directory
- **Settings**: Configure application settings including Google Sheets integration

## Returns Data Management
The application includes a robust Returns Data management system:
- View and edit shipping records
- Scrollable interface for editing records
- Form validation for required fields
- Success/error messages for user feedback

## Google Sheets Integration
The application can connect to Google Sheets for tracking:
- Configure connection in Settings
- Test connection status
- Automatically update tracking information

## Development
The application is designed to be easily extended with new features:
- Add new UI components in the `src/ui/` directory
- Extend configuration options in `src/config/config_manager.py`
- Add utility functions in `src/utils/`
- Use the standardized UI components in `src/utils/ui_components.py` for consistent UI design

## UI Components
The application uses standardized UI components for a consistent look and feel:
- Title sections
- Colored buttons with hover effects
- Button grids
- Form field groups
- Status displays

## Integration with Label Maker
The application integrates with the Label Maker application by:
1. Detecting the Label Maker installation directory
2. Launching Label Maker with appropriate parameters
3. Managing window focus between applications
4. Displaying the number of labels in the configured directory
