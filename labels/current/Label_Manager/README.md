# Label Manager

A Python-based application for managing and organizing label files with OCR capabilities.

## Features

- Load and manage label files from local directories
- Preview label contents
- OCR text extraction using Tesseract
- Automatic file organization
- Search and filter capabilities
- Batch operations (rename, delete)
- Duplicate detection

## Requirements

- Python 3.8 or higher
- Tesseract OCR engine
- Dependencies listed in requirements.txt

## Installation

1. Install Python 3.8 or higher
2. Install Tesseract OCR:
   ```
   Download from: https://github.com/UB-Mannheim/tesseract/wiki
   ```
3. Clone the repository
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Copy `.env.example` to `.env` and configure settings
6. Run the application:
   ```
   python main.py
   ```

## Configuration

The application can be configured using environment variables or a `.env` file:

- `APP_NAME`: Application name
- `APP_VERSION`: Application version
- `DEBUG`: Enable debug mode
- `WINDOW_SIZE`: Main window size
- `TESSERACT_PATH`: Path to Tesseract executable
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Project Structure

```
label_manager/
├── main.py           # Application entry point
├── config.py         # Configuration settings
├── requirements.txt  # Python dependencies
├── .env.example     # Environment variables template
├── src/
│   ├── gui/         # GUI components
│   ├── local/       # Local storage management
│   └── utils/       # Utility functions
└── logs/            # Application logs
```

## Usage

1. Start the application
2. Use the "Load Directory" button to load label files
3. Select files to preview or perform operations
4. Use the toolbar buttons for various operations:
   - 🔄 Refresh: Reload file list
   - 🗑️ Delete: Remove selected files
   - ✏️ Rename: Rename files based on content
   - 🔍 Find Duplicates: Detect duplicate files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
