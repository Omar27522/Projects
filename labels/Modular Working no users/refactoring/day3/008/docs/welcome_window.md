# Welcome Window Documentation

## Overview

The `welcome_window.py` file contains the implementation of the main welcome window for the Label Maker application. This window serves as the entry point for users, providing access to various features of the application through a user-friendly interface. The welcome window has been refactored to use standardized UI components from the `ui_components` module.

## Class: WelcomeWindow

The `WelcomeWindow` class extends `tk.Tk` and represents the main application window.

### Initialization

```python
def __init__(self):
```

- Initializes the window with a fixed size of 400x400 pixels
- Sets up window state management
- Configures the window style with a white background
- Removes maximize button but keeps minimize button
- Initializes the configuration manager
- Creates the user interface elements

### UI Creation Methods

#### `_create_ui()`

Creates the main UI elements by calling the following methods:
- `_create_title_section()`: Creates the title section
- `_create_button_section()`: Creates the button section
- `_create_version_label()`: Adds the version label
- Creates Google Sheets status display

#### `_create_title_section()`

Creates the title section of the window, displaying:
- The number of labels in the configured directory
- "Label Maker V3" text

This section dynamically updates when the labels directory changes. Now uses the `create_title_section()` function from the `ui_components` module.

#### `update_label_count()`

Updates the label count display based on the current directory:
- Retrieves the labels directory from config
- Counts files in the directory
- Updates the display with the count

#### `_create_button_section()`

Creates the button section with four main buttons:
- User (large button)
- Management
- Labels
- Settings

Each button has a distinct color scheme and hover effects. Now uses the `create_button_grid()` function from the `ui_components` module.

#### `_create_version_label()`

Creates a version label at the bottom right of the window. Now uses the `create_version_label()` function from the `ui_components` module.

#### `_update_sheets_status_display()`

Updates the Google Sheets connection status display based on the current configuration:
- Checks if Google Sheets is configured
- Updates the status label with the connection status and sheet name
- Uses color coding (green for connected, red for not connected)

### Action Methods

#### `user_action()`

Handler for User button click:
- Checks if labels directory is set and exists
- Creates a dialog window for user input if directory is valid
- Uses the `create_user_dialog()` function from the `dialog_handlers` module

#### `management_action()`

Handler for Management button click:
- Launches the management view
- Uses command-line arguments (--view-files) instead of PyAutoGUI to avoid window focus issues

#### `labels_action()`

Handler for Labels button click:
- Opens the labels interface
- Provides access to returns data (previously "Shipping Records")
- Uses the `create_returns_dialog()` function from the `returns_operations` module

#### `settings_action()`

Handler for Settings button click:
- Opens the settings dialog
- Allows configuration of the labels directory and other settings
- Provides access to Google Sheets configuration
- Uses the `create_settings_dialog()` function from the `settings_operations` module

### Google Sheets Integration

The welcome window includes integration with Google Sheets:
- Displays connection status in the main window
- Provides access to Google Sheets configuration through the settings dialog
- Updates the status display when settings change

When Google Sheets settings are changed, the status display is automatically updated.

## Dependencies

- `tkinter`: For the GUI components
- `os`, `sys`, `subprocess`: For system operations
- `src.config.config_manager`: For managing application configuration
- `src.ui.window_state`: For managing window state
- `src.utils.ui_components`: For standardized UI components
- `src.utils.returns_operations`: For returns data management
- `src.utils.sheets_operations`: For Google Sheets integration
- `src.utils.settings_operations`: For settings management
- `src.utils.dialog_handlers`: For dialog creation and management

## Key Features

1. **Dynamic Label Count**: Displays the number of labels in the configured directory
2. **Material Design Buttons**: Styled buttons with hover effects
3. **Responsive UI**: Updates in real-time when settings change
4. **Modal Dialogs**: For user input and settings configuration
5. **Google Sheets Integration**: Displays connection status and provides configuration access
6. **Returns Data Management**: Provides access to shipping records management

## Usage

The WelcomeWindow is typically instantiated and run as follows:

```python
app = WelcomeWindow()
app.center_window()  # Center the window on the screen
app.mainloop()
```

## File Structure

```
welcome_window.py
├── Class: WelcomeWindow
│   ├── __init__()
│   ├── _create_ui()
│   ├── _create_title_section()
│   ├── update_label_count()
│   ├── _create_button_section()
│   ├── _create_version_label()
│   ├── _update_sheets_status_display()
│   ├── user_action()
│   ├── management_action()
│   ├── labels_action()
│   └── settings_action()
```

## Refactoring Notes

The welcome window has been refactored to use standardized UI components from the `ui_components` module:
- Title sections are created using `create_title_section()`
- Buttons are created using `create_colored_button()`
- Button grids are created using `create_button_grid()`
- Version labels are created using `create_version_label()`
- Sheets status displays are created using `create_sheets_status_display()`

This refactoring improves code organization and maintainability by centralizing UI component creation logic.
