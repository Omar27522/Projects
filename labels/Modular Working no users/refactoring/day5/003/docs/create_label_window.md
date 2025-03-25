# Create Label Window Documentation

## Overview

The Create Label window provides a user interface for creating and printing barcode labels. It allows users to enter tracking numbers and SKUs, configure printing options, and send labels directly to the printer.

## Implementation

The Create Label window is implemented in the `dialog_handlers.py` file through the `create_label_dialog()` function. This function creates a modal dialog with input fields for tracking number and SKU, along with buttons for printing and canceling.

### Key Features

1. **Input Fields**: 
   - Tracking Number field
   - SKU field
   - Auto-focus on the Tracking Number field when the dialog opens

2. **Automatic Copy and Tab**:
   - When the user presses Enter after typing a tracking number, it is automatically copied to the clipboard
   - Focus automatically moves to the SKU field
   - This streamlines the workflow when the tracking number needs to be pasted into the SKU field

3. **Mirror Print Toggle**:
   - Button to toggle mirror printing on/off
   - Visual indication of the current state (green for on, pink for off)
   - State is saved in the configuration

4. **Status Display**:
   - Real-time feedback on operations
   - Color-coded status messages (green for success, red for errors)

5. **Google Sheets Integration**:
   - Automatically writes tracking numbers and SKUs to Google Sheets if configured
   - Updates row numbers for the next entry

6. **Auto-Print**:
   - Uses PyAutoGUI to automatically press Enter after sending to the printer
   - Fallback to opening the image if printing fails

## Usage Flow

1. User opens the Create Label window from the welcome screen
2. User enters a tracking number and presses Enter
   - The tracking number is copied to the clipboard
   - Focus moves to the SKU field
3. User enters an SKU (optionally pasting the tracking number)
4. User clicks "Print Label" or presses Enter
5. The application:
   - Validates inputs
   - Updates Google Sheets if configured
   - Creates and prints the barcode
   - Updates the label count
   - Clears the form for the next label

## Code Structure

```python
def create_label_dialog(parent, config_manager, update_label_count_callback):
    # Dialog creation and setup
    
    # Form fields creation
    
    # Enter key handler for tracking field
    def on_tracking_enter(event):
        # Copy tracking number to clipboard
        # Move focus to SKU field
    
    # Mirror print toggle functionality
    
    # Print label function
    def print_label():
        # Get and validate input
        # Update Google Sheets
        # Generate and print barcode
        # Update label count
    
    # Button creation and event binding
```

## Dependencies

- `tkinter`: For the GUI components
- `PIL` (Pillow): For image manipulation
- `barcode`: For barcode generation
- `pyautogui`: For auto-pressing Enter in the print dialog
- `gspread` and `oauth2client`: For Google Sheets integration

## Related Components

- **Welcome Window**: Entry point that opens the Create Label dialog
- **Barcode Operations**: Utility functions for barcode generation and printing
- **Google Sheets Integration**: Functions for writing data to Google Sheets
- **Configuration Manager**: For storing and retrieving settings
