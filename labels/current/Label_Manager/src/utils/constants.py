"""
Constants used throughout the Label Manager application.
"""
from enum import Enum, auto

class FileType(Enum):
    """Enumeration of file types."""
    LABEL = auto()
    IMAGE = auto()
    UNKNOWN = auto()
    
class SortOrder(Enum):
    """Enumeration of sort orders."""
    NAME_ASC = auto()
    NAME_DESC = auto()
    DATE_ASC = auto()
    DATE_DESC = auto()
    SIZE_ASC = auto()
    SIZE_DESC = auto()
    
class ViewMode(Enum):
    """Enumeration of view modes."""
    LIST = auto()
    GRID = auto()
    DETAILS = auto()
    
class ErrorCode(Enum):
    """Enumeration of error codes."""
    SUCCESS = 0
    FILE_NOT_FOUND = 1
    PERMISSION_DENIED = 2
    INVALID_FILE_TYPE = 3
    FILE_TOO_LARGE = 4
    DUPLICATE_FILE = 5
    UNKNOWN_ERROR = 999
    
# File size constants
KB = 1024
MB = KB * 1024
GB = MB * 1024

# Time constants
SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY

# UI constants
PADDING = 5
LARGE_PADDING = 10
BORDER_WIDTH = 1
BUTTON_WIDTH = 100
PREVIEW_WIDTH = 400
PREVIEW_HEIGHT = 400

# Regular expressions
PATTERNS = {
    'upc': r'^\d{12,13}$',
    'variant': r'[A-Z]{3,4}V\d(?:[A-Za-z]*)?',
    'date': r'\d{4}-\d{2}-\d{2}',
    'time': r'\d{2}:\d{2}:\d{2}'
}

# Error messages
ERRORS = {
    ErrorCode.FILE_NOT_FOUND: "File not found: {path}",
    ErrorCode.PERMISSION_DENIED: "Permission denied: {path}",
    ErrorCode.INVALID_FILE_TYPE: "Invalid file type: {type}",
    ErrorCode.FILE_TOO_LARGE: "File too large: {size}",
    ErrorCode.DUPLICATE_FILE: "Duplicate file: {name}",
    ErrorCode.UNKNOWN_ERROR: "Unknown error: {message}"
}

# Success messages
SUCCESS = {
    'file_added': "File added successfully: {name}",
    'file_deleted': "File deleted successfully: {name}",
    'file_renamed': "File renamed successfully: {old} → {new}",
    'files_loaded': "Loaded {count} files from {directory}"
}
