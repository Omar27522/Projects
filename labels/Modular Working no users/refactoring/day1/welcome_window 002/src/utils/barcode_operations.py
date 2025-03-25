"""
Utility functions for barcode operations specific to the Label Maker application.
"""

import os
import datetime
from PIL import Image
import barcode
from barcode.writer import ImageWriter
from src.utils.file_utils import ensure_directory_exists, file_exists, find_files_by_sku, log_shipping_record, directory_exists

def create_barcode_for_tracking(tracking_number, directory, mirror_print=False, status_callback=None):
    """
    Create a barcode image for the given tracking number and save it to the specified directory.
    
    Args:
        tracking_number: The tracking number to encode in the barcode
        directory: The directory to save the barcode image to
        mirror_print: Whether to create a mirrored version of the barcode
        status_callback: Optional callback function to update status messages
        
    Returns:
        tuple: (success, barcode_path, message)
    """
    try:
        # Check if the directory exists
        if not directory_exists(directory):
            if status_callback:
                status_callback(f"Error: Directory not found: {directory}", 'red')
            return False, None, f"Error: Directory not found: {directory}"
        
        # Create barcode
        code128 = barcode.get_barcode_class('code128')
        barcode_image = code128(tracking_number, writer=ImageWriter())
        
        # Save barcode to the configured labels directory
        # Use a simple filename without special characters
        barcode_filename = f'barcode_{tracking_number.replace("/", "_").replace("\\", "_").replace(":", "_")}.png'
        barcode_path = os.path.join(directory, barcode_filename)
        
        # Log the path for debugging
        print(f"Saving barcode to: {barcode_path}")
        
        barcode_image.save(barcode_path)
        
        # Verify the file was created
        if not file_exists(barcode_path):
            if status_callback:
                status_callback(f"Error: Failed to create barcode file at {barcode_path}", 'red')
            return False, None, f"Error: Failed to create barcode file at {barcode_path}"
        
        return True, barcode_path, "Barcode created successfully"
        
    except Exception as e:
        error_msg = str(e)
        if status_callback:
            status_callback(f"Error creating barcode: {error_msg}", 'red')
        return False, None, f"Error creating barcode: {error_msg}"

def print_barcode(barcode_path, mirror_print=False, status_callback=None):
    """
    Print a barcode image.
    
    Args:
        barcode_path: The path to the barcode image
        mirror_print: Whether to create a mirrored version of the barcode before printing
        status_callback: Optional callback function to update status messages
        
    Returns:
        tuple: (success, message)
    """
    try:
        # If mirror print is enabled, create a mirrored temporary copy
        print_path = barcode_path
        if mirror_print:
            try:
                img = Image.open(barcode_path)
                mirrored_img = img.transpose(Image.FLIP_LEFT_RIGHT)
                temp_dir = os.path.join(os.environ.get('TEMP', os.getcwd()), 'labelmaker_temp')
                ensure_directory_exists(temp_dir)
                temp_path = os.path.join(temp_dir, f'mirror_{os.path.basename(barcode_path)}')
                mirrored_img.save(temp_path)
                print_path = temp_path
                if status_callback:
                    status_callback("Created mirrored label for printing", 'blue')
            except Exception as e:
                if status_callback:
                    status_callback(f"Error creating mirrored image: {str(e)}", 'red')
                # Continue with original image if mirroring fails
                print_path = barcode_path
        
        # Use the default Windows print pictures functionality
        os.startfile(print_path, "print")
        
        # Return success
        if status_callback:
            status_callback("Label sent to printer. Ready for next label.", 'green')
        return True, "Label sent to printer"
        
    except Exception as e:
        error_msg = str(e)
        if status_callback:
            status_callback(f"Error printing barcode: {error_msg}", 'red')
        print(f"Error printing barcode: {error_msg}")
        
        # Fallback to opening the file if printing fails
        try:
            os.startfile(barcode_path)
            if status_callback:
                status_callback("Printing failed. Opened image for manual printing.", 'orange')
            return False, "Printing failed. Opened image for manual printing."
        except Exception as e2:
            if status_callback:
                status_callback(f"Error opening barcode: {str(e2)}", 'red')
            return False, f"Error opening barcode: {str(e2)}"

def find_or_create_barcode(tracking_number, sku, directory, mirror_print=False, status_callback=None):
    """
    Find an existing barcode file for the given SKU or create a new one for the tracking number.
    
    Args:
        tracking_number: The tracking number to encode in the barcode
        sku: The SKU to search for existing barcodes
        directory: The directory to save the barcode image to
        mirror_print: Whether to create a mirrored version of the barcode
        status_callback: Optional callback function to update status messages
        
    Returns:
        tuple: (success, barcode_path, is_new, message)
    """
    # Check if a file with this SKU already exists
    existing_file = None
    if sku:
        # Search for files containing the SKU in the filename
        matching_files = find_files_by_sku(directory, sku)
        if matching_files:
            existing_file = matching_files[0]  # Use the first matching file
            if status_callback:
                status_callback(f"Found existing label file for SKU: {sku}", 'blue')
            print(f"Using existing label file: {existing_file}")
            return True, existing_file, False, f"Found existing label file for SKU: {sku}"
    
    # Create a new barcode if no existing file was found
    success, barcode_path, message = create_barcode_for_tracking(tracking_number, directory, mirror_print, status_callback)
    return success, barcode_path, True, message
