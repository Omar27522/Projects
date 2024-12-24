import os
import win32print
import win32ui
import win32con
from PIL import Image, ImageWin

def get_default_printer():
    """Get the default printer name."""
    return win32print.GetDefaultPrinter()

def print_image(image_path, printer_name=None):
    """Print an image using the specified or default printer.
    
    Args:
        image_path (str): Path to the image file
        printer_name (str, optional): Name of printer to use. Defaults to system default.
    
    Returns:
        bool: True if printing successful, False otherwise
    """
    try:
        # Get printer name
        if not printer_name:
            printer_name = get_default_printer()
            
        # Open the printer
        hprinter = win32print.OpenPrinter(printer_name)
        printer_info = win32print.GetPrinter(hprinter, 2)
        
        # Create the DC for printing
        hdc = win32ui.CreateDC()
        hdc.CreatePrinterDC(printer_name)
        
        # Open and prepare the image
        img = Image.open(image_path)
        
        # Get printer resolution
        printer_dpi_x = int(GetDeviceCaps(hdc, win32con.LOGPIXELSX))
        printer_dpi_y = int(GetDeviceCaps(hdc, win32con.LOGPIXELSY))
        
        # Get printer page size (in pixels at printer DPI)
        printer_width = int(GetDeviceCaps(hdc, win32con.PHYSICALWIDTH))
        printer_height = int(GetDeviceCaps(hdc, win32con.PHYSICALHEIGHT))
        
        # Scale image to fit printer width while maintaining aspect ratio
        aspect_ratio = img.size[1] / img.size[0]
        new_width = printer_width
        new_height = int(printer_width * aspect_ratio)
        
        # If height is too large, scale based on height instead
        if new_height > printer_height:
            new_height = printer_height
            new_width = int(printer_height / aspect_ratio)
        
        # Center the image
        x = int((printer_width - new_width) / 2)
        y = int((printer_height - new_height) / 2)
        
        # Start the print job
        hdc.StartDoc(os.path.basename(image_path))
        hdc.StartPage()
        
        # Draw the image
        dib = ImageWin.Dib(img)
        dib.draw(hdc.GetHandleOutput(), (x, y, x + new_width, y + new_height))
        
        # End the print job
        hdc.EndPage()
        hdc.EndDoc()
        
        # Clean up
        hdc.DeleteDC()
        win32print.ClosePrinter(hprinter)
        
        return True
        
    except Exception as e:
        print(f"Error printing {image_path}: {e}")
        return False

def print_multiple(image_paths, printer_name=None):
    """Print multiple images.
    
    Args:
        image_paths (list): List of paths to image files
        printer_name (str, optional): Name of printer to use. Defaults to system default.
    
    Returns:
        tuple: (success_count, failed_paths)
    """
    success_count = 0
    failed_paths = []
    
    for path in image_paths:
        if print_image(path, printer_name):
            success_count += 1
        else:
            failed_paths.append(path)
    
    return success_count, failed_paths
