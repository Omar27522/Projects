# Command-Line Arguments Guide

## Table of Contents

- [Overview](#overview)
- [Available Arguments](#available-arguments)
- [Usage Examples](#usage-examples)
- [Automation Scenarios](#automation-scenarios)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

## Overview

Label Maker supports command-line arguments that allow you to automate various tasks and integrate the application with other systems. This guide explains the available command-line options and provides examples of how to use them effectively.

## Available Arguments

### Basic Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--help` or `-h` | Display help information | `label_maker.exe --help` |
| `--version` or `-v` | Display application version | `label_maker.exe --version` |

### File and Directory Operations

| Argument | Description | Example |
|----------|-------------|---------|
| `--csv-file=PATH` or `-c PATH` | Process a CSV file on startup | `label_maker.exe --csv-file="C:\path\to\file.csv"` |
| `--output-dir=PATH` or `-o PATH` | Specify output directory for labels | `label_maker.exe --output-dir="C:\Labels\Output"` |
| `--open-dir=PATH` | Open a specific directory in View Files window | `label_maker.exe --open-dir="C:\Labels\Output"` |

### Label Generation

| Argument | Description | Example |
|----------|-------------|---------|
| `--product-name=NAME` | Set product name for single label | `label_maker.exe --product-name="Widget Pro - Blue"` |
| `--upc=CODE` | Set UPC code for single label | `label_maker.exe --upc=123456789012` |
| `--save-label=PATH` | Generate and save a single label | `label_maker.exe --product-name="Widget" --upc=123456789012 --save-label="C:\output.png"` |

### Print Options

| Argument | Description | Example |
|----------|-------------|---------|
| `--print` | Print generated label(s) immediately | `label_maker.exe --csv-file="products.csv" --print` |
| `--mirror-print` | Enable mirror printing | `label_maker.exe --csv-file="products.csv" --print --mirror-print` |
| `--printer=NAME` | Specify printer to use | `label_maker.exe --printer="DYMO LabelWriter 450"` |

### Application Behavior

| Argument | Description | Example |
|----------|-------------|---------|
| `--silent` | Run in silent mode (no UI) | `label_maker.exe --csv-file="products.csv" --silent` |
| `--log-level=LEVEL` | Set logging level (DEBUG, INFO, WARNING, ERROR) | `label_maker.exe --log-level=DEBUG` |
| `--config=PATH` | Use alternative config file | `label_maker.exe --config="C:\custom_config.json"` |

## Usage Examples

### Process a CSV File

```
label_maker.exe --csv-file="C:\Inventory\products.csv" --output-dir="C:\Labels\Output"
```

This command:
1. Launches Label Maker
2. Automatically processes the specified CSV file
3. Saves the generated labels to the specified output directory
4. Opens the main application window

### Generate and Print a Single Label

```
label_maker.exe --product-name="Widget Pro - Blue" --upc=123456789012 --print
```

This command:
1. Launches Label Maker
2. Creates a label with the specified product name and UPC code
3. Sends the label to the default printer
4. Opens the main application window

### Batch Processing in Silent Mode

```
label_maker.exe --csv-file="C:\Inventory\products.csv" --output-dir="C:\Labels\Output" --print --silent
```

This command:
1. Launches Label Maker in silent mode (no UI)
2. Processes the specified CSV file
3. Saves the generated labels to the specified output directory
4. Prints all generated labels
5. Exits the application when complete

### Open View Files Window with Specific Directory

```
label_maker.exe --open-dir="C:\Labels\Output"
```

This command:
1. Launches Label Maker
2. Opens the View Files window
3. Navigates to the specified directory

## Automation Scenarios

### Integration with Inventory Systems

You can integrate Label Maker with inventory management systems by having the inventory system export a CSV file and then call Label Maker with the appropriate command-line arguments:

```
label_maker.exe --csv-file="%EXPORT_PATH%" --output-dir="%LABEL_DIR%" --print --silent
```

### Scheduled Batch Processing

Use Windows Task Scheduler to automate label generation at specific times:

1. Create a new task in Task Scheduler
2. Set the program/script to the path of `label_maker.exe`
3. Add arguments like `--csv-file="C:\daily_export.csv" --print --silent`
4. Set the schedule as needed

### Integration with Barcode Scanners

For workstations with barcode scanners, you can create shortcuts that launch Label Maker with pre-filled UPC codes:

```
label_maker.exe --upc=%SCANNED_CODE%
```

The `%SCANNED_CODE%` would be replaced by the barcode scanner input.

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "File not found" error | Ensure file paths are correct and enclosed in quotes if they contain spaces |
| Silent mode not exiting | Check the CSV file format for errors that might be causing the process to wait for user input |
| Print command not working | Verify printer name if specified, or check default printer settings |

### Exit Codes

Label Maker returns the following exit codes that can be used in scripts to determine if the operation was successful:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid command-line arguments |
| 3 | File not found or inaccessible |
| 4 | CSV processing error |
| 5 | Printing error |

### Logging

When using command-line arguments, especially in silent mode, it's helpful to enable detailed logging:

```
label_maker.exe --csv-file="products.csv" --silent --log-level=DEBUG
```

This will write detailed information to the log file, which can be helpful for troubleshooting.

## Advanced Usage

### Combining Multiple Operations

You can combine multiple arguments to perform complex operations:

```
label_maker.exe --csv-file="weekly.csv" --output-dir="C:\Labels\Weekly" --printer="DYMO LabelWriter" --mirror-print --log-level=INFO --silent
```

### Using Environment Variables

In batch scripts, you can use environment variables with Label Maker:

```batch
@echo off
set TODAY=%date:~10,4%%date:~4,2%%date:~7,2%
label_maker.exe --csv-file="daily_%TODAY%.csv" --output-dir="C:\Labels\%TODAY%"
```

### Creating Desktop Shortcuts

Create desktop shortcuts with different command-line arguments for quick access to common tasks:

1. Right-click on the desktop and select New > Shortcut
2. Enter the path to `label_maker.exe` followed by the desired arguments
3. Name the shortcut appropriately

For example:
```
"C:\Program Files\Label Maker\label_maker.exe" --open-dir="C:\Labels\Output"
```

This creates a shortcut that opens Label Maker with the View Files window showing a specific directory.
