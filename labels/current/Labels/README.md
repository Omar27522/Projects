# Label Maker V3

## Overview
This application provides a modular interface for managing the Label Maker application. It has been designed with a focus on modularity, maintainability, and extensibility.

## Project Structure
```
welcome_window/
├── assets/            # Application assets
├── logs/              # Log files
├── src/               # Source code
│   ├── config/        # Configuration management
│   │   └── config_manager.py
│   ├── ui/            # User interface components
│   │   ├── welcome_window.py
│   │   ├── create_label_frame.py
│   │   ├── no_record_label_frame.py
│   │   ├── google_sheets_dialog.py
│   │   ├── window_state.py
│   │   └── __init__.py
│   └── utils/         # Utility functions
│       ├── barcode_operations.py
│       ├── barcode_utils.py
│       ├── config_utils.py
│       ├── dialog_handlers.py
│       ├── file_utils.py
│       ├── logger.py
│       ├── returns_operations.py
│       ├── settings_operations.py
│       ├── sheets_operations.py
│       ├── sheets_utils.py
│       ├── ui_components.py
│       ├── ui_utils.py
│       ├── window_utils.py
│       └── __init__.py
├── main.pyw           # Application entry point
├── label_maker_settings.json  # Application settings
├── GOOGLE_SHEETS_SETUP.md     # Google Sheets setup guide
├── CODEBASE_MAP.md    # Codebase structure documentation
├── .windsurf          # Project metadata for Windsurf IDE
└── requirements.txt   # Dependencies
```

## Features
- Modular application structure
- Centralized configuration management
- Comprehensive logging
- Single-instance mechanism to prevent multiple application instances
- Welcome screen with interactive buttons
- Integration with Label Maker application
- Google Sheets integration for tracking
- Returns Data management with scrollable edit interface
- Dynamic label count display in the title section
- Auto-copy functionality for tracking numbers
- Print toggle for logging without physical printing
- Mirror Print option for label printing
- Hidden "No Record Label" mode for printing without logging
- Pin toggle button to keep windows on top of other applications

## Dependencies
- Python 3.6+
- pywin32
- pyautogui
- gspread
- oauth2client
- Pillow
- pandas

## Installation
1. Clone or download this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. For Google Sheets integration, follow the instructions in `GOOGLE_SHEETS_SETUP.md`

## Usage
Run the application by executing `main.pyw`:
```bash
python main.pyw
```

### Main Functions
- **User/Create Label**: Create and print labels with tracking numbers and SKUs
- **Labels/Returns Data**: Access Returns Data and label management features
- **Management**: Open the Label Maker file viewer for the selected labels directory
- **Settings**: Configure application settings including Google Sheets integration

## Label Creation and Printing
The application includes a robust label creation system:
- Enter tracking numbers and SKUs to create labels
- Auto-copy tracking numbers to clipboard when Enter is pressed
- Print toggle to enable/disable physical printing while maintaining data records
- Mirror Print option for special printing configurations
- Enhanced error handling for missing label files
- Clear warning messages when label files cannot be found

## Returns Data Management
The application includes a robust Returns Data management system:
- View and edit shipping records
- Scrollable interface for editing records
- Form validation for required fields
- Success/error messages for user feedback

## Google Sheets Integration
The application can connect to Google Sheets for tracking:
- Configure connection in Settings
- Test connection status with clickable status indicator
- Real-time status updates without requiring app restart
- Remembers the last selected sheet name
- Automatically update tracking information

## Hidden Features
- **No Record Label Mode**: Access by clicking the "Ver." text in the bottom-right corner
  - Print labels without recording them in logs or Google Sheets
  - Only requires an SKU (no tracking number)
  - Includes error handling for missing label files

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

## Recent Improvements
- Fixed label printing issues with better error handling
- Added a Print toggle button for logging without physical printing
- Added Mirror Print option for label orientation
- Implemented frame-based Create Label functionality
- Added Pin toggle button to keep windows on top of other applications
