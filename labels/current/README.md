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
4. Run `main.pyw` to start the application

## Dependencies

The application requires Python with the following packages:
- tkinter (GUI framework)
- Pillow (Image processing)
- python-barcode (Barcode generation)
- pyautogui (Screen interaction)
- pandas (CSV processing)
Note: User environments are typically pre-configured with these dependencies.

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
