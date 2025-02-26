# User Interface Guide

## Table of Contents

- [Main Window](#main-window)
  - [Input Fields](#input-fields)
  - [Control Buttons](#control-buttons)
  - [Preview Area](#preview-area)
- [View Files Window](#view-files-window)
  - [Search and File List](#search-and-file-list)
  - [Toggle Controls](#toggle-controls)
  - [Preview Panel](#preview-panel)
- [Window Management](#window-management)
  - [Pinning Windows](#pinning-windows)
  - [Transparency Control](#transparency-control)
  - [Auto-Switch Behavior](#auto-switch-behavior)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Visual Feedback](#visual-feedback)
- [Tooltips](#tooltips)

## Main Window

The Main Window is the primary interface for creating new labels.

```
┌───────────────────────────────────────────────────────────────────────┐
│ Label Maker                                                 _ □ X     │
├───────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐  ┌─────────────┐  ┌───────────┐                       │
│ │ Always on   │  │  Settings   │  │ Labels:   │                       │
│ │    Top      │  │             │  │    42     │                       │
│ └─────────────┘  └─────────────┘  └───────────┘                       │
│ ┌─────────────┐                                                       │
│ │    Reset    │                                                       │
│ └─────────────┘                                                       │
│                                                                       │
│ Product Name Line 1: ┌───────────────────────────────────────────┐    │
│                      │ Quantum Flux Capacitor                    │    │
│                      └───────────────────────────────────────────┘    │
│                                                                       │
│ Line 2 (optional):   ┌───────────────────────────────────────────┐    │
│                      │ Time Travel Edition                       │    │
│                      └───────────────────────────────────────────┘    │
│                                                                       │
│ Variant:             ┌───────────────────────────────────────────┐    │
│                      │ PLUTONIUM_FREE                            │    │
│                      └───────────────────────────────────────────┘    │
│                                                                       │
│ UPC Code (12 digits):┌───────────────────────────────────────────┐    │
│                      │ 314159265358                              │    │
│                      └───────────────────────────────────────────┘    │
│                                                                       │
│ ┌─────────────┐       ┌─────────────┐                                 │
│ │   Preview   │       │  View Files │                                 │
│ └─────────────┘       └─────────────┘                                 │
└───────────────────────────────────────────────────────────────────────┘
```

### Input Fields

1. **Product Name Line 1**
   - Main product name or description
   - Required field

2. **Line 2 (optional)**
   - Secondary product information
   - Optional field

3. **Variant**
   - Product variant information
   - Optional field

4. **UPC Code (12 digits)**
   - 12-digit UPC barcode number
   - Required field
   - Auto-validates for correct format

### Control Buttons

1. **Always on Top**
   - Toggles the window to stay on top of other windows
   - Green button indicates when active

2. **Settings**
   - Opens the Settings window
   - Configure font sizes, barcode dimensions, and more

3. **Labels Counter**
   - Shows the number of saved labels (42 in the example)
   - Also serves as a button to view saved labels

4. **Reset**
   - Clears all input fields
   - Starts a new label

5. **Preview**
   - Shows a preview of the current label
   - Opens the Label Preview window

6. **View Files**
   - Opens the View Files window
   - Browse and manage saved labels

## View Files Window

The View Files window allows you to search, view, and manage existing labels.

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│ View Files                                                           _ □ X        │
├───────────────────────────────────────────────────────────────────────────────────┤
│ Labels: 42   ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐                                  │
│              │ 🔍 │ │ + │ │ 🖨️ │ │ ⚡ │ │ 📄 │ │ 📋 │                                  │
│              └───┘ └───┘ └───┘ └───┘ └───┘ └───┘                                  │
│                                                                                   │
│ Find: ┌─────────────────────────────────────────────────────────────────────┐     │
│       │ flux                                                                │     │
│       └─────────────────────────────────────────────────────────────────────┘     │
│                                                                                   │
│ ┌───────────────────────────────────┐ ┌───────────────────────────────────────┐   │
│ │ Quantum Flux Capacitor            │ │  Quantum Flux                         │   │
│ │ Banana Phone_YELLOW               │ │  Capacitor                            │   │
│ │ Invisible Paint_CLEAR             │ │                                       │   │
│ │ Moon Cheese_BLEU                  │ │  PLUTONIUM_FREE                       │   │
│ │ Unicorn Kibble_RAINBOW            │ │                                       │   │
│ │ Gravity Boots_ORBITER             │ │ ┌─────────────────────────────────┐   │   │
│ │ Perpetual Motion_STATIC           │ │ │ ███ █ ███ █ ███ █ ███ █ ███ █ █ │   │   │
│ │ Schrödinger's Catnip              │ │ │ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ │   │   │
│ │ Warp Drive_LIGHTSPEED             │ │ │ ███ █ ███ █ ███ █ ███ █ ███ █ █ │   │   │
│ │ Teleportation Socks               │ │ │ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ │   │   │
│ │ Babel Fish_UNIVERSAL              │ │ │ ███ █ ███ █ ███ █ ███ █ ███ █ █ │   │   │
│ │ Memory Foam_FORGETFUL             │ │ │ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ │   │   │
│ │ Pocket Dimension_TARDIS           │ │ └─────────────────────────────────┘   │   │
│ │ Sonic Screwdriver_GREEN           │ │                                       │   │
│ │ Infinity Gauntlet_SNAP            │ │   314159265358                        │   │
│ │ Lightsaber_BLUE                   │ │                                       │   │
│ └───────────────────────────────────┘ └───────────────────────────────────────┘   │
│                                                                                   │
│ ┌─────────────┐    ┌─────────────┐                                                │
│ │     Open    │    │    Print    │  Last Label Printed 3m ago                     │
│ └─────────────┘    └─────────────┘                                                │
└───────────────────────────────────────────────────────────────────────────────────┘
```

### Search and File List

- **Labels Counter**: Shows the total number of saved labels (42 in the example)
- **Find Bar**: Filter labels by name or content
- **File List**: Shows all saved labels matching the search criteria

### Toggle Controls

1. **Search** (🔍 button)
   - Activate search functionality

2. **Add New Label** (+ button)
   - Creates a new label

3. **Print Label** (🖨️ button)
   - Prints the selected label

4. **Quick Action** (⚡ button)
   - Fast processing of selected label

5. **File Management** (📄 button)
   - File operations like export/import

6. **Clipboard** (📋 button)
   - Copy label information to clipboard

### Label Preview

- Right panel shows a preview of the selected label
- Displays product name, variant, and barcode
- "Last Label Printed" timestamp shows when the label was last printed

### Action Buttons

- **Open**: Opens the selected label for editing
- **Print**: Prints the selected label

## Settings Window

The Settings window allows you to customize various aspects of the application.

```
┌─────────────────────────────────────────────────┐
│ Settings                             _ □ X      │
├─────────────────────────────────────────────────┤
│ Font Settings                                   │
│ ┌─────────────────────────────────────────────┐ │
│ │ Large Font Size:  ┌────────────────────┐    │ │
│ │                   │        42          │    │ │
│ │                   └────────────────────┘    │ │
│ │                                             │ │
│ │ Medium Font Size: ┌────────────────────┐    │ │
│ │                   │        42          │    │ │
│ │                   └────────────────────┘    │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ Barcode Settings                                │
│ ┌─────────────────────────────────────────────┐ │
│ │ Barcode Width:    ┌────────────────────┐    │ │
│ │                   │       600          │    │ │
│ │                   └────────────────────┘    │ │
│ │                                             │ │
│ │ Barcode Height:   ┌────────────────────┐    │ │
│ │                   │       314          │    │ │
│ │                   └────────────────────┘    │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ Batch Import                                    │
│ ┌─────────────────────────────────────────────┐ │
│ │ Import multiple labels from a CSV file.      │ │
│ │ Required columns: 'Goods Name', 'Goods'      │ │
│ │                                             │ │
│ │ ┌─────────────────┐                         │ │
│ │ │ Upload CSV File │                         │ │
│ │ └─────────────────┘                         │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ Window Settings                                 │
│ ┌─────────────────────────────────────────────┐ │
│ │ □ Always on Top                             │ │
│ │                                             │ │
│ │ Transparency: ┌───────────[■]──────────┐    │ │
│ │                                             │ │
│ │ ┌─────────────────┐                         │ │
│ │ │  Save Settings  │                         │ │
│ │ └─────────────────┘                         │ │
│ └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### Font Settings

- **Large Font Size**: Adjust the size of large text on labels (default: 42)
- **Medium Font Size**: Adjust the size of medium text on labels (default: 42)

### Barcode Settings

- **Barcode Width**: Set the width of barcodes (default: 600)
- **Barcode Height**: Set the height of barcodes (default: 314)

### Batch Import

- Import multiple labels from a CSV file
- Required columns: 'Goods Name', 'Goods'
- **Upload CSV File** button to select and import CSV data

### Window Settings

- **Always on Top**: Keep windows on top of other applications
- **Transparency**: Adjust window transparency with the slider
- **Save Settings** button to apply and save changes

## Label Preview Window

The Label Preview window shows how the label will look when printed.

```
┌─────────────────────────────────────────────────┐
│ Label Preview                        _ □ X      │
├─────────────────────────────────────────────────┤
│                                                 │
│ QUANTUM FLUX CAPACITOR                          │
│ Time Travel Edition                             │
│                                                 │
│ PLUTONIUM_FREE                                  │
│                                                 │
│ ┌─────────────────────────────────────────────┐ │
│ │ ███ █ ███ █ ███ █ ███ █ ███ █ ███ █ ███ █ █ │ │
│ │ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ │ │
│ │ ███ █ ███ █ ███ █ ███ █ ███ █ ███ █ ███ █ █ │ │
│ │ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ │ │
│ │ ███ █ ███ █ ███ █ ███ █ ███ █ ███ █ ███ █ █ │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ 314159265358                                    │
│                                                 │
│                ┌─────────────────┐              │
│                │   Save Label    │              │
│                └─────────────────┘              │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Preview Features

- Displays the formatted label with all entered information
- Shows product name, variant, and barcode
- **Save Label** button to save the current label

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+P | Print current label |
| Ctrl+F | Open View Files window |
| Ctrl+O | Open selected file (in View Files window) |
| Ctrl+P | Print selected file (in View Files window) |
| Ctrl+Z | Undo text changes (in text fields) |
| Ctrl+Y | Redo text changes (in text fields) |
| Ctrl+Backspace | Delete word before cursor (in text fields) |
