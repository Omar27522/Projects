# Welcome Window Documentation

## Overview

The `welcome_window.py` file contains the implementation of the main welcome window for the Label Maker application. This window serves as the entry point for users, providing access to various features of the application through a user-friendly interface.

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

#### `_create_title_section()`

Creates the title section of the window, displaying:
- The number of labels in the configured directory
- "Label Maker V3" text

This section dynamically updates when the labels directory changes.

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

Each button has a distinct color scheme and hover effects.

#### `_create_button()`

Helper method to create styled buttons with hover effects.

Parameters:
- `parent`: Parent widget
- `text`: Button text
- `color_pair`: Tuple of (normal_color, hover_color)
- `command`: Button command
- `big`: Boolean indicating if this is a big button

#### `_create_version_label()`

Creates a version label at the bottom right of the window.

### Action Methods

#### `user_action()`

Handler for User button click:
- Checks if labels directory is set and exists
- Creates a dialog window for user input if directory is valid

#### `management_action()`

Handler for Management button click:
- Launches the management view
- Uses command-line arguments instead of PyAutoGUI

#### `labels_action()`

Handler for Labels button click:
- Opens the labels interface
- Provides access to returns data (previously "Shipping Records")

#### `settings_action()`

Handler for Settings button click:
- Opens the settings dialog
- Allows configuration of the labels directory and other settings

### Settings Dialog

The settings dialog allows users to:
- View and change the labels directory
- Configure appearance settings
- Save settings to persist between sessions

When the labels directory is changed, the label count in the title section is automatically updated.

## Dependencies

- `tkinter`: For the GUI components
- `os`, `sys`, `subprocess`: For system operations
- `src.config.config_manager`: For managing application configuration
- `src.ui.window_state`: For managing window state

## Key Features

1. **Dynamic Label Count**: Displays the number of labels in the configured directory
2. **Material Design Buttons**: Styled buttons with hover effects
3. **Responsive UI**: Updates in real-time when settings change
4. **Modal Dialogs**: For user input and settings configuration

## Usage

The WelcomeWindow is typically instantiated and run as follows:

```python
app = WelcomeWindow()
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
│   ├── _create_button()
│   ├── _create_version_label()
│   ├── user_action()
│   ├── management_action()
│   ├── labels_action()
│   └── settings_action()
```
