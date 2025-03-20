from tkinter import messagebox
import os
import sys
import tkinter as tk
from PIL import Image, ImageTk

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils.barcode_utils import generate_barcode, print_barcode, get_barcode_path
from src.utils.ui_utils import center_window, create_button, make_window_modal

class LabelWindow(tk.Toplevel):
    """Window for displaying and printing labels"""
    
    def __init__(self, parent, tracking_number, sku, barcode_width, barcode_height, 
                 font_size_large, font_size_medium, mirror_print, print_quality):
        """Initialize the label window"""
        super().__init__(parent)
        
        # Store parameters
        self.tracking_number = tracking_number
        self.sku = sku
        self.barcode_width = barcode_width
        self.barcode_height = barcode_height
        self.font_size_large = font_size_large
        self.font_size_medium = font_size_medium
        self.mirror_print = mirror_print
        self.print_quality = print_quality
        
        # Window setup
        self.title("Label Preview")
        self.geometry("600x400")
        self.resizable(False, False)
        self.configure(bg='white')
        
        # Make window modal
        make_window_modal(self, parent)
        
        # Create UI
        self._create_ui()
        
        # Center the window
        center_window(self)
    
    def _create_ui(self):
        """Create the user interface elements"""
        # Create a frame for the content
        content_frame = tk.Frame(self, bg='white', padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(
            content_frame, 
            text="Label Preview", 
            font=("Arial", self.font_size_large, "bold"), 
            bg='white'
        )
        title_label.pack(pady=(0, 20))
        
        # Label preview frame
        preview_frame = tk.Frame(content_frame, bg='white', bd=1, relief=tk.SOLID)
        preview_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Generate barcode
        success, result = generate_barcode(
            self.tracking_number, 
            self.barcode_width, 
            self.barcode_height, 
            self.mirror_print
        )
        
        if success:
            # Load the barcode image
            barcode_path = result
            img = Image.open(barcode_path)
            
            # Convert to PhotoImage
            self.barcode_img = ImageTk.PhotoImage(img)
            
            # Display barcode
            barcode_label = tk.Label(preview_frame, image=self.barcode_img, bg='white')
            barcode_label.pack(pady=10)
            
            # Display tracking number
            tracking_label = tk.Label(
                preview_frame, 
                text=f"Tracking: {self.tracking_number}", 
                font=("Arial", self.font_size_medium), 
                bg='white'
            )
            tracking_label.pack(pady=(0, 5))
            
            # Display SKU if provided
            if self.sku:
                sku_label = tk.Label(
                    preview_frame, 
                    text=f"SKU: {self.sku}", 
                    font=("Arial", self.font_size_medium), 
                    bg='white'
                )
                sku_label.pack(pady=(0, 5))
        else:
            # Display error message
            error_label = tk.Label(
                preview_frame, 
                text=result, 
                font=("Arial", self.font_size_medium), 
                bg='white', 
                fg='red'
            )
            error_label.pack(pady=20)
        
        # Button Frame
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Print Button
        print_button = create_button(
            button_frame, 
            text="Print Label", 
            bg='#4CAF50',
            command=self._print_label
        )
        print_button.pack(side='right', padx=(10, 0))
        
        # Close Button
        close_button = create_button(
            button_frame, 
            text="Close", 
            bg='#f44336',
            command=self.destroy
        )
        close_button.pack(side='right')
    
    def _print_label(self):
        """Print the label"""
        barcode_path = get_barcode_path(self.tracking_number)
        success, message = print_barcode(barcode_path)
        
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)
