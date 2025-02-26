# Label Maker Version 1.0.2 LabelsV3

A streamlined label printing application designed for warehouse returns department operations, featuring an intuitive interface with advanced window management and printing controls.

## Overview

This application facilitates efficient label printing in a warehouse environment with the following key features:
- Label generation with product information and barcodes
- Advanced search functionality by SKU/UPC or name
- Smart window management with auto-switching
- Configurable printing options including mirror printing
- Batch label creation from CSV files
- Persistent user preferences
- Modern UI with tooltips and visual feedback

## Features

### Main Window
- **Input Fields**:
  - Product Name (Line 1 & 2)
  - Variant
  - UPC Code (12 digits)
- **Controls**:
  - Pin window toggle
  - Transparency adjustment
  - Font size control
  - Preview size cycling (3 sizes)

### View Files Window
- **Search Functionality**:
  - Real-time file filtering
  - SKU/UPC smart search
  - Auto-focus management
- **Toggle Controls**:
  - 🔄 Mirror Print: Flips label output horizontally
  - ⚡ Auto Switch: Smart window management
    - Closes window when no SKU/UPC match found
    - Switches focus to main window on match
    - Selects next item after printing
  - 📄 Print Minimize: Minimizes window after printing
- **Preview Features**:
  - Zoomable preview
  - Multiple size options
  - Real-time updates

### Label Operations
- Single label generation
- Batch processing from CSV
- Mirror printing support
- Print queue management
- File naming conventions
- Image format options

### User Experience
- Keyboard shortcuts
- Input validation
- Error reporting
- State persistence
- Comprehensive tooltips
- Visual feedback
- Window position memory

## Quick Start

1. Download the latest version (.zip file) from the GitHub repository
2. Delete any existing local version
3. Extract the new version to the same directory on your machine
4. Open Command Prompt (cmd) or PowerShell:
   - Press Windows + R
   - Type `cmd` and press Enter
5. Navigate to the application directory:
   ```
   cd path\to\your\application\LabelsV3\src
   ```
6. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   If you get permissions errors, try:
   ```
   pip install --user -r requirements.txt
   ```
7. Run `main.pyw` to start the application

## Usage Guide

### Basic Operations
1. **Starting the Application**:
   - Double-click `main.pyw`
   - Only one instance can run at a time

2. **Creating Labels**:
   - Enter product details in the main window
   - UPC code must be 12 digits
   - Preview updates in real-time

3. **Finding Labels**:
   - Click "View Files" or use keyboard shortcut
   - Search by name or SKU/UPC
   - Preview shows selected label

4. **Printing Labels**:
   - Select label in View Files window
   - Use print button or keyboard shortcut
   - Configure print settings as needed

### Advanced Features

1. **Window Management**:
   - Pin windows to keep them on top
   - Adjust transparency for better workflow
   - Use auto-switch for efficient SKU searches

2. **Print Controls**:
   - Toggle mirror printing for special media
   - Enable print minimize for batch operations
   - Use auto-switch for sequential printing

3. **Batch Processing**:
   - Prepare CSV with required columns
   - Use batch import feature
   - Monitor progress in status bar

## Dependencies

### Core Dependencies
- **Pillow (>=10.0.0)**: Image processing
- **pywin32 (>=306)**: Windows integration
- **pandas (>=2.0.0)**: Data manipulation
- **pyautogui (>=0.9.54)**: GUI automation
- **python-barcode (>=0.14.0)**: Barcode generation

### Utility Dependencies
- **dataclasses (>=0.6)**: Data structures
- **typing (>=3.7.4)**: Type hinting
- **json5 (>=0.9.14)**: Configuration handling

### Built-in Dependencies
- **tkinter**: GUI framework

## File Structure

```
Labels V3/
├── assets/          # Application icons and UI elements
├── docs/           # Documentation files
│   ├── README.md   # This file
│   ├── main.md     # Main script documentation
│   └── main_window.md  # Window class documentation
├── fonts/          # Required font files
│   ├── arial.ttf
│   └── arialbd.ttf
├── src/            # Source code
│   ├── ui/        # User interface components
│   │   └── main_window.py  # Main window implementation
│   ├── utils/     # Utility functions
│   ├── barcode_generator.py
│   └── config.py  # Configuration management
├── main.pyw       # Application entry point
└── label_maker_settings.json  # User preferences
```

## Configuration

### Settings File
The application uses `label_maker_settings.json` for user preferences:
```json
{
  "font_size_large": 12,
  "font_size_medium": 10,
  "barcode_width": 400,
  "transparency": 1.0,
  "view_files_mirror_print": false,
  "view_files_pin_window": false,
  "view_files_auto_switch": true,
  "view_files_print_minimize": false
}
```

### Customizable Options
- Font sizes (large and medium)
- Barcode dimensions
- Window transparency
- Toggle states
- Window positions
- Last used directory

## Required Assets

### Fonts
Required font files in `/fonts`:
- arial.ttf: Regular text
- arialbd.ttf: Bold text

### Icons
UI elements in `/assets`:
- Application icons
- Button icons
- Status indicators

## Code Style

The project follows these conventions:
- Clear function and variable names
- Comprehensive docstrings
- Type hints where applicable
- Consistent formatting
- Regular comments for complex logic

## Support

For any issues or questions:
1. Check the documentation
2. Contact the Baby Manager from the support team
3. Report bugs with specific details:
   - Error messages
   - Steps to reproduce
   - Expected behavior

## Version History

### 1.0.2
- Added print minimize feature
- Enhanced auto-switch behavior
- Improved window management
- Added comprehensive tooltips

### 1.0.1
- Initial release
- Basic label creation
- File management
- Batch processing
