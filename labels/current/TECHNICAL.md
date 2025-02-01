# Technical Documentation

## Architecture Overview

The application follows a modular architecture with clear separation of concerns:

### Core Components

1. **Main Application (`main.pyw`)**
   - Entry point
   - Exception handling
   - Resource cleanup
   - Window setup

2. **Barcode Generator (`src/barcode_generator.py`)**
   - Label generation
   - Image processing
   - Font management
   - Barcode creation

3. **Configuration (`src/config.py`)**
   - Settings management
   - User preferences
   - File path handling

### UI Components (`src/ui/`)

1. **Main Window**
   - Primary user interface implementation in `MainWindow` class
   - Key functions:
     - `_create_styled_button()`: Creates custom-styled buttons
     - `_create_input_fields()`: Manages label input fields
     - `_create_action_buttons()`: Creates main action buttons
     - `_create_top_control_frame()`: Creates top control buttons
     - `preview_label()`: Handles label preview functionality
     - `save_label()`: Manages label saving
     - `upload_csv()`: Handles CSV file processing

2. **Button Styling and Colors**
   - Default color scheme:
     ```python
     {
         'bg': '#3498db',        # Default blue background
         'fg': 'white',          # White text
         'hover_bg': '#2980b9',  # Darker blue on hover
         'active_bg': '#2473a6'  # Even darker blue when clicked
     }
     ```
   - Button properties:
     - Font: TkDefaultFont, 10pt, bold
     - Relief: Raised
     - Border width: 1px
     - Padding: 10px horizontal, 4px vertical
     - Hover effects: Color changes on mouse enter/leave
     - Active state: Darker background when clicked

3. **Window Manager**
   - Implemented in `WindowManager` class
   - Key functions:
     - `create_window()`: Creates new Toplevel windows
     - `make_draggable()`: Adds drag functionality to widgets
     - `set_window_on_top()`: Controls window stacking
     - `focus_window()`: Manages window focus

4. **Tooltips**
   - Custom `ToolTip` class implementation
   - Properties:
     - Background: #ffffe0 (light yellow)
     - Font: TkDefaultFont, 8pt, normal
     - Border: Solid, 1px
     - Appears on mouse hover
     - Auto-dismisses on mouse leave or button press

### Utilities (`src/utils/`)

1. **Logger**
   - Application logging
   - Error tracking
   - Debug information

2. **CSV Processor**
   - Batch label processing
   - Data validation
   - File handling

## Data Flow

1. User Input → Main Window
2. Data Validation → CSV Processor/Input Validation
3. Label Generation → Barcode Generator
4. File Output → Local Storage

## Settings Management

The `label_maker_settings.json` file stores user preferences:

```json
{
    "font_size_large": 45,
    "font_size_medium": 45,
    "barcode_width": 600,
    "barcode_height": 310,
    "always_on_top": false,
    "transparency_level": 0.9,
    "last_directory": null,
    "label_counter": 0,
    "DPI": 300,
    "LABEL_WIDTH": 600,  // DPI * 2
    "LABEL_HEIGHT": 600  // DPI * 2
}
```

Settings are managed by:
- `ConfigManager` class: Handles loading/saving settings
- `LabelSettings` class: Defines setting properties and defaults
- Settings window: Created via `show_settings()` function

## Image Processing and Label Generation

### Label Generation Process (`BarcodeGenerator` class)
1. **Font Management**
   - Uses Arial fonts (regular and bold)
   - Font paths: `fonts/arial.ttf` and `fonts/arialbd.ttf`
   - Dynamic font size configuration through settings

2. **Label Components**
   - Base canvas: RGB white background
   - Text elements:
     - Name Line 1: Position (20, 20), large font
     - Name Line 2: Dynamic position based on Line 1
     - Variant text: Centered horizontally at y=165
   - Barcode element:
     - Generated using python-barcode
     - Configurable width and height
     - Positioned below text elements

3. **File Naming Convention**
   ```
   Format: NAME Second NAME_Variant_label_123456789123.png
   - Sanitized filenames (removes invalid characters)
   - Consistent naming for batch processing
   ```

## Logging and Error Handling

### Logging System (`utils/logger.py`)
1. **Configuration**
   - Monthly rotating log files
   - Max file size: 5MB
   - Keeps 5 backup files
   - Location: `logs/label_maker_YYYYMM.log`

2. **Log Formats**
   - File logs: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
   - Console logs: `%(levelname)s: %(message)s`

3. **Error Handling Strategy**
   - Global exception handler for uncaught exceptions
   - User-friendly error messages via message boxes
   - Detailed error logging for debugging
   - Graceful cleanup on application exit

## Batch Processing

### CSV Processing (`utils/csv_processor.py`)
1. **Input Format**
   - CSV file with required columns
   - Supports multiple label generation
   - Validates barcode format

2. **Processing Features**
   - Batch label generation
   - Progress tracking
   - Error handling for invalid entries
   - Automatic directory creation

3. **Output Management**
   - Organized file structure
   - Consistent naming convention
   - Success/failure tracking
   - Label counter maintenance

## Error Handling

The application implements comprehensive error handling:
- Exception logging
- User-friendly error messages
- Resource cleanup on exit

## Performance Considerations

1. **Memory Management**
   - Efficient image processing using PIL
   - Resource cleanup after operations
   - Automatic garbage collection

2. **File Operations**
   - Asynchronous file operations where possible
   - Efficient directory scanning
   - File caching for previews

3. **UI Responsiveness**
   - Non-blocking operations for large batches
   - Progressive loading for file lists
   - Throttled preview generation

## Installation and Setup

### Dependencies
```python
# Core Dependencies
tkinter>=8.6      # GUI framework
Pillow>=9.0.0     # Image processing
python-barcode    # Barcode generation
pyautogui        # Screen interaction
pandas           # CSV processing

# Development Dependencies
pytest           # Testing
black           # Code formatting
pylint          # Code analysis
```

For exact version requirements and compatibility information, refer to `assets/dependencies/requirements.txt`.

### Required Assets
1. **Fonts**
   - Location: `/fonts/`
   - Required files:
     - `arial.ttf`: Regular text
     - `arialbd.ttf`: Bold text for headers

2. **Icons**
   - Location: `/assets/`
   - Types:
     - Application icons (multiple sizes)
     - Settings icons
     - View files icons

### Installation Steps
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Verify font files in `/fonts`
4. Verify icons in `/assets`
5. Run `main.pyw`

## Development Guidelines

### Code Organization
1. **Source Structure**
   ```
   src/
   ├── ui/           # User interface components
   │   ├── main_window.py
   │   └── window_manager.py
   ├── utils/        # Utility functions
   │   ├── logger.py
   │   └── csv_processor.py
   ├── barcode_generator.py
   └── config.py

   assets/
   ├── icons/        # Application icons
   └── dependencies/ # Project dependencies
       └── requirements.txt

   fonts/           # Required font files
   ├── arial.ttf
   └── arialbd.ttf
   ```

2. **Module Responsibilities**
   - `ui/`: All user interface components
   - `utils/`: Helper functions and utilities
   - `barcode_generator.py`: Label generation logic
   - `config.py`: Settings management

### Best Practices
1. **Code Style**
   - Follow PEP 8
   - Use type hints
   - Document classes and functions
   - Keep methods focused and small

2. **Error Handling**
   - Use try-except blocks for file operations
   - Provide user-friendly error messages
   - Log detailed error information
   - Clean up resources in finally blocks

3. **Testing**
   - Write unit tests for core functionality
   - Test error cases
   - Verify label generation accuracy
   - Test CSV processing edge cases

4. **Version Control**
   - Use meaningful commit messages
   - Keep features in separate branches
   - Review code before merging
   - Tag releases with version numbers

## User Interface Guidelines

### Window Management
1. **Main Window**
   - Always centered on startup
   - Remembers last position
   - Configurable transparency
   - Optional always-on-top

2. **Dialog Windows**
   - Modal when requiring user input
   - Non-modal for information display
   - Consistent styling with main window
   - Clear error/success messages

3. **Preview Windows**
   - Real-time label preview
   - Zoom functionality
   - Print preview
   - Quick edit capabilities

### Keyboard Navigation
1. **Global Shortcuts**
   - `Ctrl+N`: New label
   - `Ctrl+S`: Save label
   - `Ctrl+P`: Print label
   - `Ctrl+O`: Open directory
   - `F1`: Help
   - `Esc`: Close current window

2. **Input Field Navigation**
   - `Tab`: Next field
   - `Shift+Tab`: Previous field
   - `Enter`: Submit/Save
   - `Ctrl+A`: Select all

## Future Development Areas

1. User authentication system
2. Enhanced label information
3. Tracking system integration
4. Performance metrics
5. Data visualization
