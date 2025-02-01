# Label Maker Version 1.0.1.1 LabelsV3

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
4. Install dependencies: `pip install -r assets/dependencies/requirements.txt`
5. Run `main.pyw` to start the application

## Dependencies

The application requires Python with the following packages:
- tkinter (GUI framework)
- Pillow (Image processing)
- python-barcode (Barcode generation)
- pyautogui (Screen interaction)
- pandas (CSV processing)

Note: User environments are typically pre-configured with these dependencies. For exact version requirements, see `assets/dependencies/requirements.txt`.

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

## Windows and Features

The Label Maker application consists of several windows, each serving a specific purpose:

### Welcome Window
The main entry point of the application featuring four main buttons:
- **User** (Green): [Coming Soon]
- **Management** (Blue): Opens the View Files window to manage and view existing labels
- **Labels** (Orange): Configure the directory where labels will be saved
- **Settings** (Gray): Access application settings and tools

### 1. User Window (Coming Soon)
A user interface that allows you to:
- Scan tracking numbers and validate them
- Manage SKUs (Stock Keeping Units)
- Transaction recording with comprehensive metadata:
  - Date and time stamps
  - User identification
  - SKU information
  - Tracking number details
- Transaction history and reporting

### 2. View Files Window (Management)
A file management interface that allows you to:
- View all generated labels organized by date
- Preview label images
- Print existing labels
- Create new labels
- Filter and search through labels
- Track recently printed labels
  ### 2.5. Label Maker Window
  The main label creation interface where you can:
  - Enter product details (name, barcode, etc.)
  - Generate and preview labels in real-time
  - Print labels directly
  - Save labels for later use
  - Access the View Files window to manage existing labels

### 4. Settings Window
Configure various application settings:
- **Font Sizes**: Adjust large and medium font sizes for labels
- **Barcode Settings**: Customize barcode width and height
- **Tools**: Access additional utilities like the Icon Maker

### 5. Icon Maker Window
A utility tool for creating icons that:
- Generates icons from text input
- Customizes icon appearance
- Saves icons in various formats
- Supports batch icon creation

## Usage Tips

1. **Starting Point**: Launch the app and use the Welcome Window to navigate to your desired task
2. **Creating Labels**:
   - Click "Management" to open View Files
   - Click "New Label" to open the Label Maker
   - Enter product details and generate labels

3. **Managing Labels**:
   - Use the View Files window to organize and find existing labels
   - Double-click labels to view or print them
   - Use filters to find specific labels quickly

4. **Configuration**:
   - Use the Labels button to set your preferred save location
   - Access Settings to customize fonts and barcode dimensions
   - Use Icon Maker for custom icon creation

## Code Style

Keep code legible and well-documented for easy collaboration between developers.

## Support

For any issues or questions, please contact the Baby Manager from the support team.
