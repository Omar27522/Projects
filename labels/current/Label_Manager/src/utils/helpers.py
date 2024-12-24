"""
Helper utilities for the Label Manager application.
"""
import os
import re
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
from .constants import FileType, ErrorCode, PATTERNS, KB, MB, GB
from PIL import Image
import pytesseract

def get_file_type(file_path: str) -> FileType:
    """
    Determine the type of a file based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        FileType: Type of the file
    """
    ext = Path(file_path).suffix.lower()
    if ext in ['.txt', '.json', '.csv']:
        return FileType.LABEL
    elif ext in ['.png', '.jpg', '.jpeg', '.bmp']:
        return FileType.IMAGE
    return FileType.UNKNOWN

def format_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes < KB:
        return f"{size_bytes} B"
    elif size_bytes < MB:
        return f"{size_bytes/KB:.1f} KB"
    elif size_bytes < GB:
        return f"{size_bytes/MB:.1f} MB"
    return f"{size_bytes/GB:.1f} GB"

def format_timestamp(timestamp: float) -> str:
    """
    Format timestamp in human-readable format.
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        str: Formatted timestamp string
    """
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def extract_upc(text: str) -> Optional[str]:
    """
    Extract UPC code from text.
    
    Args:
        text: Text to search
        
    Returns:
        str or None: UPC if found, None otherwise
    """
    match = re.search(PATTERNS['upc'], text)
    return match.group() if match else None

def extract_variant(text: str) -> Optional[str]:
    """
    Extract variant code from text.
    
    Args:
        text: Text to search
        
    Returns:
        str or None: Variant code if found, None otherwise
    """
    match = re.search(PATTERNS['variant'], text)
    return match.group() if match else None

def extract_upc(text):
    """Extract UPC code from text."""
    # Look for 12-13 digit number
    match = re.search(r'(\d{12,13})', text)
    return match.group(1) if match else None

def extract_variant(text):
    """Extract variant code from text."""
    # Common variant patterns
    patterns = [
        r'[A-Z]{2,}(?:V\d)?',  # e.g., BLKV1, GRNGRY
        r'[A-Z]{2,}\d*',       # e.g., BLK1, GLNVY
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None

def extract_name(text, variant=None, upc=None):
    """Extract product name from text."""
    # Remove UPC if present
    if upc:
        text = text.replace(upc, '')
    
    # Remove variant if present
    if variant:
        text = text.replace(variant, '')
        
    # Remove common separators and cleanup
    text = re.sub(r'_+label_.*$', '', text)  # Remove _label_ and everything after
    text = re.sub(r'[_\s]+', ' ', text)      # Replace multiple spaces/underscores with single space
    text = text.strip()                       # Remove leading/trailing spaces
    text = text.replace(' ', '_')             # Replace spaces with underscores
    
    return text

def extract_label_info_from_image(image_path):
    """Extract product name, variant, and UPC from label image using OCR."""
    try:
        # Open and process image
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Increase size for better OCR if image is small
        width, height = img.size
        if width < 800 or height < 800:
            scale = max(800/width, 800/height)
            img = img.resize((int(width*scale), int(height*scale)), Image.Resampling.LANCZOS)
            
        # Extract text using OCR
        text = pytesseract.image_to_string(img)
        
        # Look for UPC (12-13 digits)
        upc_match = re.search(r'(\d{12,13})', text)
        upc = upc_match.group(1) if upc_match else None
        
        # Look for variant code (2+ uppercase letters, optional V1/numbers)
        variant_patterns = [
            r'[A-Z]{2,}(?:V\d)?',  # e.g., BLKV1, GRNGRY
            r'[A-Z]{2,}\d*',       # e.g., BLK1, GLNVY
        ]
        
        variant = None
        for pattern in variant_patterns:
            match = re.search(pattern, text)
            if match:
                variant = match.group(0)
                break
                
        # Extract name (first line, cleaned up)
        lines = text.split('\n')
        name = None
        for line in lines:
            # Skip empty lines and lines that are just the UPC/variant
            if not line.strip() or (upc and upc in line) or (variant and variant in line):
                continue
            # Clean up the name
            name = re.sub(r'[^\w\s-]', '', line).strip()
            name = re.sub(r'\s+', '_', name)
            if name:
                break
                
        return name, variant, upc
        
    except Exception as e:
        print(f"Error extracting info from {image_path}: {e}")
        return None, None, None

def standardize_filename(old_name, image_path=None):
    """Convert filename to standard format: NAME_VARIANT_label_UPC."""
    try:
        # First try to extract from image if path provided
        if image_path:
            name, variant, upc = extract_label_info_from_image(image_path)
            if name and variant and upc:
                return f"{name}_{variant}_label_{upc}.png"
        
        # Fallback to extracting from filename
        upc = extract_upc(old_name)
        if not upc:
            return old_name
            
        variant = extract_variant(old_name)
        if not variant:
            return old_name
            
        name = extract_name(old_name, variant, upc)
        if not name:
            return old_name
            
        return f"{name}_{variant}_label_{upc}.png"
        
    except Exception as e:
        print(f"Error standardizing filename: {e}")
        return old_name

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Remove control characters
    filename = "".join(char for char in filename if ord(char) >= 32)
    return filename.strip()

def get_error_message(code: ErrorCode, **kwargs) -> str:
    """
    Get a formatted error message for an error code.
    
    Args:
        code: Error code
        **kwargs: Format arguments
        
    Returns:
        str: Formatted error message
    """
    from .constants import ERRORS
    try:
        return ERRORS[code].format(**kwargs)
    except KeyError:
        return ERRORS[ErrorCode.UNKNOWN_ERROR].format(message="Invalid error code")
    except Exception as e:
        return ERRORS[ErrorCode.UNKNOWN_ERROR].format(message=str(e))

def get_success_message(key: str, **kwargs) -> str:
    """
    Get a formatted success message.
    
    Args:
        key: Message key
        **kwargs: Format arguments
        
    Returns:
        str: Formatted success message
    """
    from .constants import SUCCESS
    try:
        return SUCCESS[key].format(**kwargs)
    except KeyError:
        return f"Operation completed successfully"
    except Exception as e:
        return f"Operation completed with message: {str(e)}"
