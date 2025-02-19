# Label Maker Version 1.0.1 LabelsV3

A streamlined label printing application designed for warehouse returns department operations.

## Overview

This application facilitates efficient label printing in a warehouse environment with the following key features:
- Label generation with product information and barcodes
- Label search functionality by SKU or name
- Batch label creation from CSV files
- Configurable label settings

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

## Dependencies

The application requires Python 3.7+ with the following packages:

### Core Dependencies
- **Pillow (>=10.0.0)**: Image processing library used for:
  - Label image generation
  - Image resizing and manipulation
  - Loading and saving image files

- **pywin32 (>=306)**: Windows integration library for:
  - System-level window management
  - Windows-specific UI features
  - File system operations

- **pandas (>=2.0.0)**: Data manipulation library used for:
  - CSV file processing
  - Batch label data handling
  - Data validation and cleaning

- **pyautogui (>=0.9.54)**: GUI automation library for:
  - Screen interaction
  - Window positioning
  - Automated UI testing

- **python-barcode (>=0.14.0)**: Barcode generation library for:
  - Creating product barcodes
  - Supporting multiple barcode formats
  - Barcode validation

### Utility Dependencies
- **dataclasses (>=0.6)**: Data structure library for:
  - Type-safe data containers
  - Configuration settings
  - Label data models

- **typing (>=3.7.4)**: Type hinting support for:
  - Code documentation
  - Type checking
  - IDE support

- **json5 (>=0.9.14)**: JSON parsing library for:
  - Configuration file handling
  - Settings management
  - Data serialization

### Built-in Dependencies
- **tkinter**: GUI framework (comes with Python) used for:
  - Main application interface
  - Window management
  - User input handling

All required package versions are specified in `requirements.txt`. Install them using:
```bash
pip install -r requirements.txt
```

For permission-restricted environments, use:
```bash
pip install --user -r requirements.txt
```

## File Structure

```
Labels V3/
├── assets/          # Application icons and UI elements
├── fonts/           # Required font files (arial.ttf, arialbd.ttf)
├── src/             # Source code
│   ├── ui/         # User interface components
│   ├── utils/      # Utility functions
│   ├── barcode_generator.py
│   └── config.py
└── main.pyw        # Application entry point
```

## Configuration

The application uses `label_maker_settings.json` for user preferences:
- Font sizes (large and medium)
- Barcode dimensions (width and height)
- Window settings (transparency, always on top)
- Last used directory

Default settings work well for most users, but can be adjusted through the UI if needed.

## Required Assets

The application requires:
- Font files in `/fonts`:
  - arial.ttf
  - arialbd.ttf
- UI icons in `/assets`:
  - Various application icons
  - Settings and view files icons

## Code Style

Keep code legible and well-documented for easy collaboration between developers.

## Support

For any issues or questions, please contact the Baby Manager from the support team.
