import pandas as pd
import os
from typing import Tuple
import re
from tkinter import messagebox
from ..barcode_generator import LabelData
from ..utils.logger import setup_logger

# Setup logger
logger = setup_logger()

def sanitize_filename(name: str) -> str:
    """Remove invalid characters from filename"""
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*\'"'
    for char in invalid_chars:
        name = name.replace(char, '_')
    # Remove any other non-printable characters
    name = ''.join(char for char in name if char.isprintable())
    return name

def process_product_name(full_name: str) -> Tuple[str, str, str]:
    """Process product name into name_line1, name_line2, and variant"""
    # First try with spaces around double dash
    if ' -- ' in full_name:
        name_parts = full_name.split(' -- ', 1)
    # Then try without spaces
    elif '--' in full_name:
        name_parts = full_name.split('--', 1)
    # No fallback to single dash - if no double dash is found, there's no variant
    else:
        name_parts = [full_name]
        
    base_name = name_parts[0].strip()
    variant = name_parts[1].strip() if len(name_parts) > 1 else ""
    
    # Split base name into lines, respecting max lengths
    words = base_name.split()
    line1 = []
    line2 = []
    current_line1 = ""
    
    # Build first line (max 18 chars)
    for word in words:
        test_line = (current_line1 + " " + word).strip()
        if len(test_line) <= 18:
            line1.append(word)
            current_line1 = test_line
        else:
            break
    
    # Remaining words go to second line (max 20 chars)
    remaining_words = words[len(line1):]
    current_line2 = ""
    for word in remaining_words:
        test_line = (current_line2 + " " + word).strip()
        if len(test_line) <= 20:
            line2.append(word)
            current_line2 = test_line
        else:
            break
    
    name_line1 = " ".join(line1)
    name_line2 = " ".join(line2)
    
    return name_line1, name_line2, variant

def is_valid_barcode(barcode: str) -> bool:
    """Check if barcode consists of exactly 12 digits"""
    # Convert to string and remove any whitespace
    barcode = str(barcode).strip()
    
    # Handle numeric values that might be in scientific notation
    try:
        # Convert scientific notation to regular number
        if 'e' in barcode.lower():
            barcode = f"{float(barcode):.0f}"
        # Remove any decimal points and zeros after them
        elif '.' in barcode:
            barcode = barcode.split('.')[0]
    except ValueError:
        return False
    
    # Check if it's exactly 12 digits
    if len(barcode) != 12:
        return False
    
    # Check if all characters are digits
    return barcode.isdigit()

def create_batch_labels(csv_path: str, main_window):
    """Create labels in batch from a CSV file"""
    try:
        # Read the CSV file with numeric columns as strings to preserve leading zeros and prevent float conversion
        df = pd.read_csv(csv_path, dtype={'Goods Barcode': str})
        
        # Get save directory from settings or use default
        save_dir = main_window.config_manager.settings.last_directory
        if not os.path.exists(save_dir):
            save_dir = os.path.join(os.path.expanduser("~"), "Documents", "Labels")
            os.makedirs(save_dir, exist_ok=True)
        
        labels_created = 0
        skipped_labels = 0
        
        # Process each row
        for _, row in df.iterrows():
            barcode = str(row['Goods Barcode'])
            
            # Remove any decimal part (e.g., ".0") that might be present
            if '.' in barcode:
                barcode = barcode.split('.')[0]
                logger.info(f"Removed decimal part from barcode: {barcode}")
            
            # Skip if barcode is invalid
            if not is_valid_barcode(barcode):
                skipped_labels += 1
                logger.warning(f"Skipping invalid barcode: {barcode}")
                continue
                
            full_name = str(row['Goods Name'])
            
            # Process the product name
            name_line1, name_line2, variant = process_product_name(full_name)
            
            # Log the product name processing results
            logger.info(f"Full product name: {full_name}")
            logger.info(f"Extracted name_line1: {name_line1}")
            logger.info(f"Extracted name_line2: {name_line2}")
            logger.info(f"Extracted variant: {variant}")
            
            # Create label data
            label_data = LabelData(
                name_line1=name_line1,
                name_line2=name_line2,
                variant=variant,
                upc_code=barcode
            )
            
            # Generate the label
            label_image = main_window.barcode_generator.generate_label(label_data)
            if label_image:
                # Create filename in same format as manual labels
                safe_name1 = sanitize_filename(name_line1)
                safe_name2 = sanitize_filename(name_line2) if name_line2 else ""
                safe_variant = sanitize_filename(variant)
                
                # For debugging
                logger.info(f"Original variant: {variant}")
                logger.info(f"Sanitized variant: {safe_variant}")
                logger.info(f"Barcode: {barcode}")
                
                if safe_name2:
                    filename = f"{safe_name1} {safe_name2} - {safe_variant}_label_{barcode}.png"
                else:
                    filename = f"{safe_name1} - {safe_variant}_label_{barcode}.png"
                
                logger.info(f"Generated filename: {filename}")
                
                filepath = os.path.join(save_dir, filename)
                label_image.save(filepath)
                labels_created += 1
                
                # Update label counter in settings
                main_window.config_manager.settings.label_counter += 1
                main_window.png_count.set(f"Labels: {main_window.config_manager.settings.label_counter}")
            
        # Save settings
        main_window.config_manager.save_settings()
        
        # Show completion message
        message = f"Created {labels_created} labels in:\n{save_dir}"
        if skipped_labels > 0:
            message += f"\n\nSkipped {skipped_labels} invalid barcodes. Check the logs for details."
        messagebox.showinfo("Complete", message)
        
    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}")
        messagebox.showerror("Error", f"Failed to process CSV file:\n\n{str(e)}")
