"""
Configuration settings for the Label Manager application.
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Application settings
APP_NAME = os.getenv('APP_NAME', 'Label Manager')
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Window settings
WINDOW_TITLE = APP_NAME
WINDOW_SIZE = os.getenv('WINDOW_SIZE', '1024x768')

# UI Theme
THEME = {
    'background_color': "#f5f6fa",
    'header_background': "#2c3e50",
    'header_foreground': "#ecf0f1",
    'button_background': "#3498db",
    'button_foreground': "#ffffff",
    'error_color': "#e74c3c",
    'success_color': "#2ecc71",
    'warning_color': "#f1c40f",
    'listbox_background': "#ffffff",
    'listbox_foreground': "#2c3e50",
    'listbox_selected_background': "#3498db",
    'listbox_selected_foreground': "#ffffff",
    'listbox_font_size': 11
}

# File storage settings
APP_DATA = os.getenv('APPDATA')
APP_DIR = Path(APP_DATA) / APP_NAME if APP_DATA else Path.home() / APP_NAME
LABELS_DIR = APP_DIR / "labels"
CACHE_DIR = APP_DIR / "cache"
LOG_DIR = APP_DIR / "logs"
TEMP_DIR = APP_DIR / "temp"
CONFIG_FILE = APP_DIR / "config.json"

# Default directories
DEFAULT_LABELS_DIR = r"C:\Users\Justin\Documents\Labels"

# Create necessary directories
for directory in [LABELS_DIR, CACHE_DIR, LOG_DIR, TEMP_DIR]:
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logging.error(f"Failed to create directory {directory}: {e}")

# File settings
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024))  # Default 10MB
ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS', '.png,.PNG').split(',')
ALLOWED_IMAGE_EXTENSIONS = os.getenv('ALLOWED_IMAGE_EXTENSIONS', '.png,.PNG').split(',')

SUPPORTED_EXTENSIONS = {
    'labels': ALLOWED_EXTENSIONS,
    'images': ALLOWED_IMAGE_EXTENSIONS
}

# Logging configuration
LOG_LEVEL = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
MAX_LOG_SIZE = int(os.getenv('MAX_LOG_SIZE', 5 * 1024 * 1024))  # Default 5MB
MAX_LOG_BACKUPS = int(os.getenv('MAX_LOG_BACKUPS', 5))

LOG_CONFIG = {
    'filename': Path(__file__).parent / 'logs' / f"{APP_NAME.lower().replace(' ', '_')}.log",
    'level': LOG_LEVEL,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'max_bytes': MAX_LOG_SIZE,
    'backup_count': MAX_LOG_BACKUPS
}

# External dependencies
TESSERACT_PATH = os.getenv('TESSERACT_PATH', r"C:\Program Files\Tesseract-OCR\tesseract.exe")

# Cache settings
CACHE_ENABLED = True
CACHE_TTL = 3600  # 1 hour in seconds
MAX_CACHE_SIZE = 100 * 1024 * 1024  # 100MB

# Performance settings
BATCH_SIZE = 100
THREAD_POOL_SIZE = 4
IO_BUFFER_SIZE = 8192  # 8KB

# Feature flags
FEATURES = {
    'ocr_enabled': True,
    'auto_rename': True,
    'duplicate_detection': True,
    'image_preview': True,
    'batch_operations': True
}
