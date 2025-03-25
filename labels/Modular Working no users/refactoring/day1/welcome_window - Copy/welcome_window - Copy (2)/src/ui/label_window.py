import tkinter as tk
from tkinter import messagebox
import os
import sys
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageTk, ImageOps

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

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
        self.transient(parent)  # Make dialog modal
        self.grab_set()  # Make dialog modal
        
        # Create UI
        self._create_ui()
        
        # Center the window
        self.center_window()
        
        # Make sure window appears on top
        self.lift()
        self.focus_force()
        self.attributes('-topmost', True)
        self.after_idle(self.attributes, '-topmost', False)
    
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
        try:
            # Create barcode
            code128 = barcode.get_barcode_class('code128')
            barcode_image = code128(self.tracking_number, writer=ImageWriter())
            
            # Save barcode to temporary file
            temp_dir = os.path.join(os.environ.get('TEMP', os.getcwd()), 'labelmaker_temp')
            os.makedirs(temp_dir, exist_ok=True)
            barcode_path = os.path.join(temp_dir, f'barcode_{self.tracking_number}.png')
            barcode_image.save(barcode_path)
            
            # Load and resize barcode image
            img = Image.open(barcode_path)
            img = img.resize((self.barcode_width, self.barcode_height), Image.LANCZOS)
            
            # Mirror image if needed
            if self.mirror_print:
                img = ImageOps.mirror(img)
            
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
            
        except Exception as e:
            error_label = tk.Label(
                preview_frame, 
                text=f"Error generating barcode: {str(e)}", 
                font=("Arial", self.font_size_medium), 
                bg='white', 
                fg='red'
            )
            error_label.pack(pady=20)
        
        # Button Frame
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Print Button
        print_button = tk.Button(
            button_frame, 
            text="Print Label", 
            font=("Arial", 10), 
            bg='#4CAF50', 
            fg='white',
            activebackground='#45a049',
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self._print_label
        )
        print_button.pack(side='right', padx=(10, 0))
        
        # Close Button
        close_button = tk.Button(
            button_frame, 
            text="Close", 
            font=("Arial", 10), 
            bg='#f44336', 
            fg='white',
            activebackground='#d32f2f',
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.destroy
        )
        close_button.pack(side='right')
    
    def _print_label(self):
        """Print the label"""
        try:
            # Get the barcode image path
            temp_dir = os.path.join(os.environ.get('TEMP', os.getcwd()), 'labelmaker_temp')
            barcode_path = os.path.join(temp_dir, f'barcode_{self.tracking_number}.png')
            
            # Check if the file exists
            if not os.path.exists(barcode_path):
                messagebox.showerror("Error", "Barcode image not found")
                return
            
            # Use ShellExecute to open the print dialog
            try:
                import win32api
                win32api.ShellExecute(
                    0,          # Handle to parent window
                    "print",    # Operation to perform
                    barcode_path, # File to print
                    None,       # Parameters
                    ".",        # Working directory
                    0           # Show command
                )
                
                # Show success message
                messagebox.showinfo("Success", "Label sent to printer")
            except ImportError:
                # Fallback to os.startfile for printing if win32api is not available
                os.startfile(barcode_path, "print")
                messagebox.showinfo("Success", "Label sent to printer")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error printing label: {str(e)}")
    
    def center_window(self):
        """Center the window on the screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
