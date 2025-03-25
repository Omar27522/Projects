# Label Maker Codebase Map

## Core Architecture

```
Label Maker/
├── src/
│   ├── ui/                 # User interface components
│   │   ├── welcome_window.py     # Main welcome window
│   │   ├── create_label_frame.py # Frame-based label creation
│   │   ├── no_record_label_frame.py # No-record label creation
│   │   ├── label_window.py       # Label preview window
│   │   └── google_sheets_dialog.py # Google Sheets configuration
│   ├── utils/              # Utility functions
│   │   ├── barcode_operations.py # Barcode generation and printing
│   │   ├── dialog_handlers.py    # Dialog creation functions
│   │   ├── file_utils.py         # File system operations
│   │   ├── returns_operations.py # Returns data management
│   │   ├── sheets_operations.py  # Google Sheets operations
│   │   └── ui_components.py      # Reusable UI components
│   └── config/             # Configuration management
│       └── config_manager.py     # Settings handling
├── main.pyw               # Application entry point
└── start_label_maker.pyw  # Launcher script
```

## Key Workflows

### 1. Create Label Workflow

1. User clicks "User" or "Create Label" button in welcome_window.py
2. `create_label_action()` in welcome_window.py calls `create_label_frame()` from create_label_frame.py
3. User enters tracking number and presses Enter:
   - Tracking number is copied to clipboard
   - Focus moves to SKU field
4. User enters SKU and clicks "Print Label"
5. `process_barcode()` in barcode_operations.py:
   - Creates barcode image
   - Updates Google Sheets if configured
   - Prints the label
   - Updates label count

### 2. Google Sheets Integration

1. User configures Google Sheets in Settings
2. Connection status is displayed in welcome window
3. When labels are created, data is written to the configured sheet

## Important Classes and Functions

### WelcomeWindow (welcome_window.py)
- Main application window
- Provides access to all features
- Displays label count and Google Sheets status
- Manages stay-on-top window state

### CreateLabelFrame (create_label_frame.py)
- Frame-based implementation of label creation
- Includes Pin toggle for stay-on-top functionality
- Handles tracking number validation and auto-copy

### NoRecordLabelFrame (no_record_label_frame.py)
- Frame for creating labels without logging
- Includes Pin toggle for stay-on-top functionality

### LabelWindow (label_window.py)
- Displays label preview
- Handles label printing

### ConfigManager (config_manager.py)
- Manages application settings
- Persists configuration between sessions

### Key Functions

- `create_label_dialog()` - Creates the dialog for label creation
- `process_barcode()` - Handles barcode creation and printing
- `write_to_google_sheet()` - Updates Google Sheets with label data
- `update_label_count()` - Updates the label count display

## Recent Enhancements

1. **Auto-copy and Tab in Create Label Window**
   - When user presses Enter after typing tracking number:
     - Number is automatically copied to clipboard
     - Focus moves to SKU field
   - Implemented in dialog_handlers.py

2. **Single Instance Mechanism**
   - Prevents multiple instances of the application
   - Shows notification when another instance is detected

3. **Google Sheets Status Updates**
   - Real-time status updates without requiring app restart
   - Clickable status indicator for quick connection testing

4. **Frame-based UI Implementation**
   - Replaced dialog-based UI with embedded frames
   - Improved navigation between different views
   - Enhanced user experience with consistent styling

5. **Stay-on-Top Feature**
   - Pin toggle button in all frames (except welcome window)
   - Keeps application window on top of other programs
   - Remembers user preference in settings
   - Implemented using tkinter's topmost attribute with lift() and focus_force()
