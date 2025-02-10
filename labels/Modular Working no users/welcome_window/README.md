# Label Maker V3 - Welcome Window

A modern, user-friendly welcome window interface for the Label Maker V3 application built with Python and Tkinter.

## Overview

The Welcome Window serves as the main entry point for the Label Maker V3 application. It provides a clean, intuitive interface with quick access to various functionalities including user operations, management tools, label creation, and settings.

## Project Structure

```
welcome_window/
├── src/
│   ├── button_factory.py    # Factory class for creating styled buttons
│   ├── config.py           # Configuration and action handlers
│   └── styles.py           # UI styling constants and configurations
├── welcome_window.py       # Main window implementation
├── __init__.py            # Package initialization
└── README.md              # Project documentation
```

## Features

- **User Section**: Quick access to user-related operations
- **Management Tools**: Administrative and management functionalities
- **Labels**: Direct access to label creation and management
- **Settings**: Application configuration and preferences
- **Modern UI**: Clean, responsive interface with consistent styling
- **Non-resizable Window**: Maintains layout integrity
- **Version Display**: Shows current application version

## Technical Details

### Dependencies
- Python 3.x
- Tkinter (included in standard Python distribution)

### Key Components

1. **WelcomeWindow Class**
   - Main window implementation
   - Handles window configuration and UI component creation
   - Manages layout and styling

2. **ButtonFactory**
   - Creates consistently styled buttons
   - Manages button appearance and behavior

3. **Configuration**
   - Window settings
   - Color schemes
   - Action handlers

## Usage

To run the welcome window:

```python
from welcome_window import WelcomeWindow

app = WelcomeWindow()
app.mainloop()
```

## Styling

The application uses a consistent color scheme and styling defined in `styles.py`. Buttons are color-coded based on their functionality:
- User section
- Management tools
- Labels section
- Settings

## Contributing

When contributing to this project, please maintain:
- Consistent code style
- Proper documentation for new features
- Separation of concerns (UI, logic, configuration)
- Use of the ButtonFactory for new buttons
- Adherence to the established styling guidelines
