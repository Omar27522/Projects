"""
File utility functions for the Label Maker application.
"""
import os
import sys
import datetime

def get_project_root():
    """
    Get the absolute path to the project root directory.
    
    Returns:
        str: Absolute path to the project root directory
    """
    # Assuming this file is in src/utils
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def file_exists(file_path):
    """
    Check if a file exists.
    
    Args:
        file_path (str): Path to the file to check
        
    Returns:
        bool: True if the file exists, False otherwise
    """
    return file_path and os.path.exists(file_path) and os.path.isfile(file_path)

def directory_exists(directory_path):
    """
    Check if a directory exists without creating it.
    
    Args:
        directory_path (str): Path to the directory to check
        
    Returns:
        bool: True if the directory exists, False otherwise
    """
    return directory_path and os.path.exists(directory_path) and os.path.isdir(directory_path)

def ensure_directory_exists(directory_path):
    """
    Create a directory if it doesn't exist.
    
    Args:
        directory_path (str): Path to the directory to create
        
    Returns:
        bool: True if the directory exists or was created successfully, False otherwise
    """
    if not directory_exists(directory_path):
        try:
            os.makedirs(directory_path)
            return True
        except Exception as e:
            print(f"Error creating directory {directory_path}: {e}")
            return False
    return True

def count_files_in_directory(directory_path):
    """
    Count the number of files in a directory.
    
    Args:
        directory_path (str): Path to the directory
        
    Returns:
        int: Number of files in the directory, or 0 if the directory doesn't exist
    """
    if directory_path and os.path.exists(directory_path):
        return len([f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))])
    return 0

def find_files_with_extension(directory_path, extension):
    """
    Find all files with a specific extension in a directory.
    
    Args:
        directory_path (str): Path to the directory
        extension (str): File extension to search for (e.g., '.png')
        
    Returns:
        list: List of file paths matching the extension
    """
    if not directory_path or not os.path.exists(directory_path):
        return []
    
    return [os.path.join(directory_path, f) for f in os.listdir(directory_path) 
            if os.path.isfile(os.path.join(directory_path, f)) and f.endswith(extension)]

def find_file_by_content(directory_path, content_str):
    """
    Find files containing a specific string in their filename.
    
    Args:
        directory_path (str): Path to the directory
        content_str (str): String to search for in filenames
        
    Returns:
        list: List of file paths containing the string
    """
    if not directory_path or not os.path.exists(directory_path):
        return []
    
    return [os.path.join(directory_path, f) for f in os.listdir(directory_path) 
            if os.path.isfile(os.path.join(directory_path, f)) and content_str in f]

def find_files_by_sku(directory_path, sku, extension='.png'):
    """
    Find files containing a specific SKU in their filename with the given extension.
    
    Args:
        directory_path (str): Path to the directory
        sku (str): SKU to search for in filenames
        extension (str): File extension to filter by (default: '.png')
        
    Returns:
        list: List of file paths containing the SKU and matching the extension
    """
    if not directory_path or not directory_exists(directory_path) or not sku:
        return []
    
    return [os.path.join(directory_path, f) for f in os.listdir(directory_path) 
            if os.path.isfile(os.path.join(directory_path, f)) and 
            sku in f and f.endswith(extension)]

def get_central_log_file_path():
    """
    Get the path to the central shipping records log file.
    
    Returns:
        tuple: (log_dir, log_file_path) - Paths to the log directory and log file
    """
    project_root = get_project_root()
    log_dir = os.path.join(project_root, 'logs')
    log_file = os.path.join(log_dir, 'shipping_records.txt')
    return log_dir, log_file

def log_shipping_record(tracking_number, sku, label_filename):
    """
    Log a shipping record to the central log file.
    
    Args:
        tracking_number (str): Tracking number
        sku (str): SKU
        label_filename (str): Label filename
        
    Returns:
        bool: True if logging was successful, False otherwise
    """
    log_dir, log_file = get_central_log_file_path()
    
    # Create logs directory if it doesn't exist
    if not ensure_directory_exists(log_dir):
        return False
    
    try:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(log_file, 'a') as f:
            f.write(f"{timestamp} | Tracking: {tracking_number} | SKU: {sku} | Label: {label_filename}\n")
        return True
    except Exception as e:
        print(f"Error logging shipping record: {e}")
        return False

def get_credentials_file_path():
    """
    Get the path to the Google Sheets credentials file.
    
    Returns:
        str: Path to the credentials file
    """
    return os.path.join(get_project_root(), 'credentials.json')
