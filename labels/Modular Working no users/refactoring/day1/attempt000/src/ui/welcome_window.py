import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import datetime
import logging
import subprocess
import time
from src.utils.file_utils import ensure_directory_exists, count_files_in_directory, log_shipping_record, directory_exists, file_exists, get_project_root, find_files_by_sku
from src.utils.ui_utils import center_window, create_button, make_window_modal
from src.utils.window_utils import open_file_explorer, view_files_in_directory, restart_application
from src.utils.config_utils import get_config_directory, get_config_file_path, load_config, save_config, update_config
import pyautogui
import barcode
from barcode.writer import ImageWriter
from PIL import Image
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.config.config_manager import ConfigManager
from src.ui.label_window import LabelWindow
from src.ui.google_sheets_dialog import GoogleSheetsDialog

class WindowState:
    """Class to track and manage window state across the application"""
    
    def __init__(self):
        """Initialize the window state"""
        self.windows = []
        self.active_window = None
    
    def add_window(self, window):
        """Add a window to the state tracker"""
        self.windows.append(window)
        self.active_window = window
    
    def remove_window(self, window):
        """Remove a window from the state tracker"""
        if window in self.windows:
            self.windows.remove(window)
            
        # Update active window
        if self.windows:
            self.active_window = self.windows[-1]
        else:
            self.active_window = None
    
    def get_active_window(self):
        """Get the currently active window"""
        return self.active_window

class WelcomeWindow(tk.Tk):
    """Main welcome window for the Label Maker application"""
    
    def __init__(self):
        """Initialize the welcome window"""
        super().__init__()

        # Initialize window state
        self.window_state = WindowState()
        self.window_state.add_window(self)

        # Initialize config manager
        self.config_manager = ConfigManager()

        # Window setup
        self.title("Welcome")
        self.geometry("400x400")  # Window size
        self.resizable(False, False)  # Prevent resizing
        
        # Configure window style
        self.configure(bg='white')
        
        # Remove maximize button but keep minimize
        self.attributes('-toolwindow', 1)  # Remove minimize/maximize buttons
        self.attributes('-toolwindow', 0)  # Restore minimize button
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface elements"""
        # Add title
        self._create_title_section()
        
        # Create buttons
        self._create_button_section()
        
        # Add version label
        self._create_version_label()
        
        # Initialize the Google Sheets status display
        self._update_sheets_status_display()
    
    def _create_title_section(self):
        """Create the title section of the window"""
        title_frame = tk.Frame(self, bg='white')
        title_frame.pack(pady=20)
        
        # Get the labels directory from config
        labels_dir = self.config_manager.settings.last_directory
        
        # Count labels if directory exists
        label_count = 0
        if labels_dir and os.path.exists(labels_dir):
            # Count files in the directory (assuming all files are labels)
            label_count = count_files_in_directory(labels_dir)
        
        # Display the label count
        self.label_count_label = tk.Label(title_frame, text=f"{label_count} Labels", font=("Arial", 16, "bold"), bg='white')
        self.label_count_label.pack()
        tk.Label(title_frame, text="Label Maker V3", font=("Arial", 14), bg='white').pack()
    
    def _create_button_section(self):
        """Create the button section of the window"""
        # Button frame
        button_frame = tk.Frame(self, bg='white')
        button_frame.pack(expand=True, padx=20)  # Added horizontal padding
        
        # Button colors (Material Design)
        colors = {
            'user': ('#4CAF50', '#A5D6A7'),        # Green, Light Green
            'management': ('#2196F3', '#90CAF9'),   # Blue, Light Blue
            'labels': ('#FF9800', '#FFCC80'),       # Orange, Light Orange
            'settings': ('#9E9E9E', '#E0E0E0')      # Gray, Light Gray
        }
        
        # Buttons with their respective styles
        self.user_btn = self._create_button(
            button_frame, "User", colors['user'], 
            self.user_action, big=True
        )
        
        self.management_btn = self._create_button(
            button_frame, "Management", colors['management'],
            self.management_action
        )
        
        self.labels_btn = self._create_button(
            button_frame, "Labels", colors['labels'],
            self.labels_action
        )
        
        self.settings_btn = self._create_button(
            button_frame, "Settings", colors['settings'],
            self.settings_action
        )
        
        # Grid layout for buttons
        button_frame.grid_columnconfigure(0, weight=3)  # Even more weight to User button column
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)
        button_frame.grid_rowconfigure(2, weight=1)
        
        # Place User button spanning both rows with more padding
        self.user_btn.grid(row=0, column=0, rowspan=2, padx=15, pady=10, sticky="nsew")
        
        # Place other buttons in the second column
        self.management_btn.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        self.labels_btn.grid(row=1, column=1, padx=(10, 10), pady=5, sticky="nsew")
        
        # Move settings to bottom, spanning both columns
        self.settings_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
    
    def _create_button(self, parent, text, color_pair, command, big=False):
        """
        Create a colored button with hover effect
        
        Args:
            parent: Parent widget
            text (str): Button text
            color_pair (tuple): Tuple of (normal_color, hover_color)
            command: Button command
            big (bool): Whether this is a big button
            
        Returns:
            tk.Button: The created button
        """
        color, light_color = color_pair
        btn = tk.Button(
            parent, 
            text=text,
            font=('Arial', 18 if big else 12, 'bold' if big else 'normal'),
            fg='white',
            bg=color,
            activeforeground='black',
            activebackground='white',
            relief='flat',
            borderwidth=0,
            width=20 if big else 15,
            height=4 if big else 2,
            cursor='hand2',
            command=command
        )
        
        # Add hover effect with delay
        hover_timer = None
        
        def apply_hover():
            btn['bg'] = light_color
            btn['fg'] = 'black'
        
        def remove_hover():
            btn['bg'] = color
            btn['fg'] = 'white'
        
        def on_enter(e):
            nonlocal hover_timer
            # Cancel any existing timer
            if hover_timer is not None:
                btn.after_cancel(hover_timer)
            # Start new timer for hover effect
            hover_timer = btn.after(25, apply_hover)  # 25ms delay
        
        def on_leave(e):
            nonlocal hover_timer
            # Cancel any pending hover effect
            if hover_timer is not None:
                btn.after_cancel(hover_timer)
                hover_timer = None
            remove_hover()
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def _create_version_label(self):
        """Create the version label at the bottom right"""
        version_label = tk.Label(
            self,
            text="Ver. 1.0.1.1",
            font=("Arial", 8),
            bg='white',
            fg='gray'
        )
        version_label.pack(side='bottom', anchor='se', padx=10, pady=5)
    
    def create_label_action(self):
        """Handler for Create Label button click"""
        # Check if labels directory is set
        if not self.config_manager.settings.last_directory:
            messagebox.showerror("Error", "Please set the labels directory in Settings first.")
            return
        
        # Create a dialog for user input
        dialog = tk.Toplevel(self)
        dialog.title("Create Label")
        dialog.geometry("400x400")
        dialog.resizable(False, False)
        dialog.configure(bg='white')
        dialog.transient(self)  # Make dialog modal
        dialog.grab_set()  # Make dialog modal
        
        # Create a frame for the content
        content_frame = tk.Frame(dialog, bg='white', padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(
            content_frame, 
            text="Create New Label", 
            font=("Arial", 14, "bold"), 
            bg='white'
        )
        title_label.pack(pady=(0, 20))
        
        # Tracking Number
        tracking_frame = tk.Frame(content_frame, bg='white')
        tracking_frame.pack(fill='x', pady=(0, 10))
        
        tracking_label = tk.Label(
            tracking_frame, 
            text="Tracking Number:", 
            font=("Arial", 10), 
            bg='white'
        )
        tracking_label.pack(anchor='w')
        
        tracking_var = tk.StringVar()
        tracking_entry = tk.Entry(
            tracking_frame, 
            textvariable=tracking_var, 
            font=("Arial", 10), 
            width=30
        )
        tracking_entry.pack(fill='x', pady=(5, 0))
        tracking_entry.focus()  # Set focus to this field
        
        # SKU
        sku_frame = tk.Frame(content_frame, bg='white')
        sku_frame.pack(fill='x', pady=(0, 10))
        
        sku_label = tk.Label(
            sku_frame, 
            text="SKU:", 
            font=("Arial", 10), 
            bg='white'
        )
        sku_label.pack(anchor='w')
        
        sku_var = tk.StringVar()
        sku_entry = tk.Entry(
            sku_frame, 
            textvariable=sku_var, 
            font=("Arial", 10), 
            width=30
        )
        sku_entry.pack(fill='x', pady=(5, 0))
        
        # Status
        status_frame = tk.Frame(content_frame, bg='white')
        status_frame.pack(fill='x', pady=(10, 0))
        
        status_label = tk.Label(
            status_frame, 
            text="", 
            font=("Arial", 10), 
            bg='white',
            fg='red'
        )
        status_label.pack(anchor='w')
        
        # Options frame
        options_frame = tk.Frame(content_frame, bg='white')
        options_frame.pack(fill='x', pady=10)
        
        # Mirror print toggle
        mirror_print_var = tk.BooleanVar(value=self.config_manager.settings.mirror_print)
        
        def toggle_mirror_print():
            current_state = mirror_print_var.get()
            mirror_btn.config(
                bg='#90EE90' if current_state else '#C71585',
                relief='sunken' if current_state else 'raised'
            )
            # Save the mirror print state
            self.config_manager.settings.mirror_print = current_state
            self.config_manager.save_settings()
        
        # Set initial button state based on saved setting
        initial_color = '#90EE90' if self.config_manager.settings.mirror_print else '#C71585'
        initial_relief = 'sunken' if self.config_manager.settings.mirror_print else 'raised'
        
        mirror_btn = tk.Button(options_frame, text=" 🖨️ ", bg=initial_color, 
                               relief=initial_relief, width=3,
                               font=('TkDefaultFont', 14), anchor='center')
        
        mirror_btn.config(
            command=lambda: [mirror_print_var.set(not mirror_print_var.get()),
                           toggle_mirror_print()]
        )
        mirror_btn.pack(side=tk.LEFT, padx=2)
        
        # Button Frame
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill='x', pady=(20, 0))
        
        def print_label():
            # Get tracking number and SKU
            tracking_number = tracking_var.get().strip()
            sku = sku_var.get().strip()
            
            # Validate input
            if not tracking_number:
                status_label.config(text="Please enter a tracking number", fg='red')
                return
            
            # Create a unique filename based on tracking number and date (but don't create the actual file)
            date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{tracking_number}_{date_str}.txt"
            filepath = os.path.join(self.config_manager.settings.last_directory, filename)
            
            # Write to Google Sheets if configured
            if (self.config_manager.settings.google_sheet_url and 
                self.config_manager.settings.google_sheet_name):
                try:
                    # Import required libraries
                    import gspread
                    from oauth2client.service_account import ServiceAccountCredentials
                    
                    # Check for credentials file
                    creds_file = get_credentials_file_path()
                    if not file_exists(creds_file):
                        status_label.config(text="Google Sheets credentials file not found", fg='red')
                        dialog.update()
                    else:
                        # Define the scope
                        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                        
                        # Add credentials to the account
                        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
                        
                        # Authorize the clientsheet
                        client = gspread.authorize(creds)
                        
                        # Extract sheet ID from URL
                        import re
                        match = re.match(r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)', self.config_manager.settings.google_sheet_url)
                        if match:
                            sheet_id = match.group(1)
                            
                            # Open the spreadsheet
                            spreadsheet = client.open_by_key(sheet_id)
                            
                            # Get the worksheet
                            worksheet = spreadsheet.worksheet(self.config_manager.settings.google_sheet_name)
                            
                            # Get the next empty row or use the configured row
                            tracking_col = self.config_manager.settings.google_sheet_tracking_column
                            tracking_row = self.config_manager.settings.google_sheet_tracking_row
                            sku_col = self.config_manager.settings.google_sheet_sku_column
                            sku_row = self.config_manager.settings.google_sheet_sku_row
                            
                            # Write tracking number
                            worksheet.update_acell(f"{tracking_col}{tracking_row}", tracking_number)
                            
                            # Write SKU
                            worksheet.update_acell(f"{sku_col}{sku_row}", sku)
                            
                            # Increment row numbers for next entry
                            self.config_manager.settings.google_sheet_tracking_row += 1
                            self.config_manager.settings.google_sheet_sku_row += 1
                            self.config_manager.save_settings()
                            
                            status_label.config(text="Data written to Google Sheets", fg='green')
                            dialog.update()
                        else:
                            status_label.config(text="Invalid Google Sheet URL format", fg='red')
                            dialog.update()
                except ImportError:
                    status_label.config(text="Google Sheets libraries not installed", fg='red')
                    dialog.update()
                except Exception as e:
                    status_label.config(text=f"Error writing to Google Sheets: {str(e)}", fg='red')
                    dialog.update()
            
            # Generate and print the barcode directly without showing preview window
            try:
                # Check if the directory exists
                if not directory_exists(self.config_manager.settings.last_directory):
                    status_label.config(text=f"Error: Directory not found: {self.config_manager.settings.last_directory}", fg='red')
                    dialog.update()
                    return
                
                # Check if a file with this SKU already exists
                existing_file = None
                if sku:
                    # Search for files containing the SKU in the filename
                    matching_files = find_files_by_sku(self.config_manager.settings.last_directory, sku)
                    if matching_files:
                        existing_file = matching_files[0]  # Use the first matching file
                        status_label.config(text=f"Found existing label file for SKU: {sku}", fg='blue')
                        dialog.update()
                        print(f"Using existing label file: {existing_file}")
                
                barcode_path = None
                barcode_filename = None
                
                # If an existing file was found, use it
                if existing_file:
                    barcode_path = existing_file
                    barcode_filename = os.path.basename(existing_file)
                else:
                    # Create barcode if no existing file was found
                    import barcode
                    from barcode.writer import ImageWriter
                    
                    code128 = barcode.get_barcode_class('code128')
                    barcode_image = code128(tracking_number, writer=ImageWriter())
                    
                    # Save barcode to the configured labels directory
                    # Use a simple filename without special characters
                    barcode_filename = f'barcode_{tracking_number.replace("/", "_").replace("\\", "_").replace(":", "_")}.png'
                    barcode_path = os.path.join(self.config_manager.settings.last_directory, barcode_filename)
                    
                    # Log the path for debugging
                    print(f"Saving barcode to: {barcode_path}")
                    
                    barcode_image.save(barcode_path)
                    
                    # Verify the file was created
                    if not file_exists(barcode_path):
                        status_label.config(text=f"Error: Failed to create barcode file at {barcode_path}", fg='red')
                        dialog.update()
                        return
                
                # Now that we have the actual barcode filename, log it to the central file
                log_shipping_record(tracking_number, sku, barcode_path)
                
                # Print the barcode directly
                try:
                    # If mirror print is enabled, create a mirrored temporary copy
                    print_path = barcode_path
                    if self.config_manager.settings.mirror_print:
                        from PIL import Image
                        img = Image.open(barcode_path)
                        mirrored_img = img.transpose(Image.FLIP_LEFT_RIGHT)
                        temp_dir = os.path.join(os.environ.get('TEMP', os.getcwd()), 'labelmaker_temp')
                        ensure_directory_exists(temp_dir)
                        temp_path = os.path.join(temp_dir, f'mirror_{os.path.basename(barcode_path)}')
                        mirrored_img.save(temp_path)
                        print_path = temp_path
                        status_label.config(text="Created mirrored label for printing", fg='blue')
                        dialog.update()
                    
                    # Use the default Windows print pictures functionality
                    os.startfile(print_path, "print")
                    
                    # Use pyautogui to automatically press Enter after a short delay
                    try:
                        import pyautogui
                        # Wait a moment for the print dialog to appear
                        dialog.after(1000, lambda: pyautogui.press('enter'))
                    except ImportError:
                        print("pyautogui not installed, cannot auto-press Enter")
                    
                    # Show success message
                    status_label.config(text="Label sent to printer. Ready for next label.", fg='green')
                    dialog.update()
                    
                    # Clear input fields for next label
                    tracking_var.set("")
                    sku_var.set("")
                    tracking_entry.focus_set()
                    
                except Exception as e:
                    error_msg = str(e)
                    status_label.config(text=f"Error printing barcode: {error_msg}", fg='red')
                    dialog.update()
                    print(f"Error printing barcode: {error_msg}")
                    
                    # Fallback to opening the file if printing fails
                    try:
                        os.startfile(barcode_path)
                        status_label.config(text="Printing failed. Opened image for manual printing.", fg='orange')
                        dialog.update()
                    except Exception as e2:
                        status_label.config(text=f"Error opening barcode: {str(e2)}", fg='red')
                        dialog.update()
                
                # Update the label count
                self.update_label_count()
                
            except Exception as e:
                error_msg = str(e)
                status_label.config(text=f"Error creating barcode: {error_msg}", fg='red')
                print(f"Error creating barcode: {error_msg}")
        
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
            command=print_label
        )
        print_button.pack(side='right', padx=(10, 0))
        
        # Cancel Button
        cancel_button = tk.Button(
            button_frame, 
            text="Cancel", 
            font=("Arial", 10), 
            bg='#f44336', 
            fg='white',
            activebackground='#d32f2f',
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=dialog.destroy
        )
        cancel_button.pack(side='right')
        
        # Center the dialog
        self.center_window(dialog)
    
    def user_action(self):
        """Handler for User button click"""
        # Check if labels directory is set
        if not self.config_manager.settings.last_directory:
            messagebox.showerror("Error", "Please set the labels directory in Settings first.")
            return
        
        # Create a dialog for user input
        dialog = tk.Toplevel(self)
        dialog.title("Create Label")
        dialog.geometry("400x400")
        dialog.resizable(False, False)
        dialog.configure(bg='white')
        dialog.transient(self)  # Make dialog modal
        dialog.grab_set()  # Make dialog modal
        
        # Create a frame for the content
        content_frame = tk.Frame(dialog, bg='white', padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(
            content_frame, 
            text="Create New Label", 
            font=("Arial", 14, "bold"), 
            bg='white'
        )
        title_label.pack(pady=(0, 20))
        
        # Tracking Number
        tracking_frame = tk.Frame(content_frame, bg='white')
        tracking_frame.pack(fill='x', pady=(0, 10))
        
        tracking_label = tk.Label(
            tracking_frame, 
            text="Tracking Number:", 
            font=("Arial", 10), 
            bg='white'
        )
        tracking_label.pack(anchor='w')
        
        tracking_var = tk.StringVar()
        tracking_entry = tk.Entry(
            tracking_frame, 
            textvariable=tracking_var, 
            font=("Arial", 10), 
            width=30
        )
        tracking_entry.pack(fill='x', pady=(5, 0))
        tracking_entry.focus()  # Set focus to this field
        
        # SKU
        sku_frame = tk.Frame(content_frame, bg='white')
        sku_frame.pack(fill='x', pady=(0, 10))
        
        sku_label = tk.Label(
            sku_frame, 
            text="SKU:", 
            font=("Arial", 10), 
            bg='white'
        )
        sku_label.pack(anchor='w')
        
        sku_var = tk.StringVar()
        sku_entry = tk.Entry(
            sku_frame, 
            textvariable=sku_var, 
            font=("Arial", 10), 
            width=30
        )
        sku_entry.pack(fill='x', pady=(5, 0))
        
        # Status
        status_frame = tk.Frame(content_frame, bg='white')
        status_frame.pack(fill='x', pady=(10, 0))
        
        status_label = tk.Label(
            status_frame, 
            text="", 
            font=("Arial", 10), 
            bg='white',
            fg='red'
        )
        status_label.pack(anchor='w')
        
        # Options frame
        options_frame = tk.Frame(content_frame, bg='white')
        options_frame.pack(fill='x', pady=10)
        
        # Mirror print toggle
        mirror_print_var = tk.BooleanVar(value=self.config_manager.settings.mirror_print)
        
        def toggle_mirror_print():
            current_state = mirror_print_var.get()
            mirror_btn.config(
                bg='#90EE90' if current_state else '#C71585',
                relief='sunken' if current_state else 'raised'
            )
            # Save the mirror print state
            self.config_manager.settings.mirror_print = current_state
            self.config_manager.save_settings()
        
        # Set initial button state based on saved setting
        initial_color = '#90EE90' if self.config_manager.settings.mirror_print else '#C71585'
        initial_relief = 'sunken' if self.config_manager.settings.mirror_print else 'raised'
        
        mirror_btn = tk.Button(options_frame, text=" 🖨️ ", bg=initial_color, 
                               relief=initial_relief, width=3,
                               font=('TkDefaultFont', 14), anchor='center')
        
        mirror_btn.config(
            command=lambda: [mirror_print_var.set(not mirror_print_var.get()),
                           toggle_mirror_print()]
        )
        mirror_btn.pack(side=tk.LEFT, padx=2)
        
        # Button Frame
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill='x', pady=(20, 0))
        
        def print_label():
            # Get tracking number and SKU
            tracking_number = tracking_var.get().strip()
            sku = sku_var.get().strip()
            
            # Validate input
            if not tracking_number:
                status_label.config(text="Please enter a tracking number", fg='red')
                return
            
            if not sku:
                status_label.config(text="Please enter a SKU", fg='red')
                return
            
            # Create a unique filename based on tracking number and date (but don't create the actual file)
            date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{tracking_number}_{date_str}.txt"
            filepath = os.path.join(self.config_manager.settings.last_directory, filename)
            
            # Write to Google Sheets if configured
            if (self.config_manager.settings.google_sheet_url and 
                self.config_manager.settings.google_sheet_name):
                try:
                    # Import required libraries
                    import gspread
                    from oauth2client.service_account import ServiceAccountCredentials
                    
                    # Check for credentials file
                    creds_file = get_credentials_file_path()
                    if not file_exists(creds_file):
                        status_label.config(text="Google Sheets credentials file not found", fg='red')
                        dialog.update()
                    else:
                        # Define the scope
                        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                        
                        # Add credentials to the account
                        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
                        
                        # Authorize the clientsheet
                        client = gspread.authorize(creds)
                        
                        # Extract sheet ID from URL
                        import re
                        match = re.match(r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)', self.config_manager.settings.google_sheet_url)
                        if match:
                            sheet_id = match.group(1)
                            
                            # Open the spreadsheet
                            spreadsheet = client.open_by_key(sheet_id)
                            
                            # Get the worksheet
                            worksheet = spreadsheet.worksheet(self.config_manager.settings.google_sheet_name)
                            
                            # Get the next empty row or use the configured row
                            tracking_col = self.config_manager.settings.google_sheet_tracking_column
                            tracking_row = self.config_manager.settings.google_sheet_tracking_row
                            sku_col = self.config_manager.settings.google_sheet_sku_column
                            sku_row = self.config_manager.settings.google_sheet_sku_row
                            
                            # Write tracking number
                            worksheet.update_acell(f"{tracking_col}{tracking_row}", tracking_number)
                            
                            # Write SKU
                            worksheet.update_acell(f"{sku_col}{sku_row}", sku)
                            
                            # Increment row numbers for next entry
                            self.config_manager.settings.google_sheet_tracking_row += 1
                            self.config_manager.settings.google_sheet_sku_row += 1
                            self.config_manager.save_settings()
                            
                            status_label.config(text="Data written to Google Sheets", fg='green')
                            dialog.update()
                        else:
                            status_label.config(text="Invalid Google Sheet URL format", fg='red')
                            dialog.update()
                except ImportError:
                    status_label.config(text="Google Sheets libraries not installed", fg='red')
                    dialog.update()
                except Exception as e:
                    status_label.config(text=f"Error writing to Google Sheets: {str(e)}", fg='red')
                    dialog.update()
            
            # Generate and print the barcode directly without showing preview window
            try:
                # Check if the directory exists
                if not directory_exists(self.config_manager.settings.last_directory):
                    status_label.config(text=f"Error: Directory not found: {self.config_manager.settings.last_directory}", fg='red')
                    dialog.update()
                    return
                
                # Check if a file with this SKU already exists
                existing_file = None
                if sku:
                    # Search for files containing the SKU in the filename
                    matching_files = find_files_by_sku(self.config_manager.settings.last_directory, sku)
                    if matching_files:
                        existing_file = matching_files[0]  # Use the first matching file
                        status_label.config(text=f"Found existing label file for SKU: {sku}", fg='blue')
                        dialog.update()
                        print(f"Using existing label file: {existing_file}")
                
                barcode_path = None
                barcode_filename = None
                
                # If an existing file was found, use it
                if existing_file:
                    barcode_path = existing_file
                    barcode_filename = os.path.basename(existing_file)
                else:
                    # Create barcode if no existing file was found
                    import barcode
                    from barcode.writer import ImageWriter
                    
                    code128 = barcode.get_barcode_class('code128')
                    barcode_image = code128(tracking_number, writer=ImageWriter())
                    
                    # Save barcode to the configured labels directory
                    # Use a simple filename without special characters
                    barcode_filename = f'barcode_{tracking_number.replace("/", "_").replace("\\", "_").replace(":", "_")}.png'
                    barcode_path = os.path.join(self.config_manager.settings.last_directory, barcode_filename)
                    
                    # Log the path for debugging
                    print(f"Saving barcode to: {barcode_path}")
                    
                    barcode_image.save(barcode_path)
                    
                    # Verify the file was created
                    if not file_exists(barcode_path):
                        status_label.config(text=f"Error: Failed to create barcode file at {barcode_path}", fg='red')
                        dialog.update()
                        return
                
                # Now that we have the actual barcode filename, log it to the central file
                log_shipping_record(tracking_number, sku, barcode_path)
                
                # Print the barcode directly
                try:
                    # If mirror print is enabled, create a mirrored temporary copy
                    print_path = barcode_path
                    if self.config_manager.settings.mirror_print:
                        from PIL import Image
                        img = Image.open(barcode_path)
                        mirrored_img = img.transpose(Image.FLIP_LEFT_RIGHT)
                        temp_dir = os.path.join(os.environ.get('TEMP', os.getcwd()), 'labelmaker_temp')
                        ensure_directory_exists(temp_dir)
                        temp_path = os.path.join(temp_dir, f'mirror_{os.path.basename(barcode_path)}')
                        mirrored_img.save(temp_path)
                        print_path = temp_path
                        status_label.config(text="Created mirrored label for printing", fg='blue')
                        dialog.update()
                    
                    # Use the default Windows print pictures functionality
                    os.startfile(print_path, "print")
                    
                    # Use pyautogui to automatically press Enter after a short delay
                    try:
                        import pyautogui
                        # Wait a moment for the print dialog to appear
                        dialog.after(1000, lambda: pyautogui.press('enter'))
                    except ImportError:
                        print("pyautogui not installed, cannot auto-press Enter")
                    
                    # Show success message
                    status_label.config(text="Label sent to printer. Ready for next label.", fg='green')
                    dialog.update()
                    
                    # Clear input fields for next label
                    tracking_var.set("")
                    sku_var.set("")
                    tracking_entry.focus_set()
                    
                except Exception as e:
                    error_msg = str(e)
                    status_label.config(text=f"Error printing barcode: {error_msg}", fg='red')
                    dialog.update()
                    print(f"Error printing barcode: {error_msg}")
                    
                    # Fallback to opening the file if printing fails
                    try:
                        os.startfile(barcode_path)
                        status_label.config(text="Printing failed. Opened image for manual printing.", fg='orange')
                        dialog.update()
                    except Exception as e2:
                        status_label.config(text=f"Error opening barcode: {str(e2)}", fg='red')
                        dialog.update()
                
                # Update the label count
                self.update_label_count()
                
            except Exception as e:
                error_msg = str(e)
                status_label.config(text=f"Error creating barcode: {error_msg}", fg='red')
                print(f"Error creating barcode: {error_msg}")
        
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
            command=print_label
        )
        print_button.pack(side='right', padx=(10, 0))
        
        # Cancel Button
        cancel_button = tk.Button(
            button_frame, 
            text="Cancel", 
            font=("Arial", 10), 
            bg='#f44336', 
            fg='white',
            activebackground='#d32f2f',
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=dialog.destroy
        )
        cancel_button.pack(side='right')
        
        # Bind Enter key to print_label function
        dialog.bind('<Return>', lambda event: print_label())
        
        # Center the dialog
        self.center_window(dialog)
        
        # Set dialog to be always on top
        dialog.attributes('-topmost', True)
    
    def management_action(self):
        """Handler for Management button click"""
        try:
            # Check if labels directory is set and exists
            if not self.config_manager.settings.last_directory or not directory_exists(self.config_manager.settings.last_directory):
                messagebox.showinfo("Labels Required", 
                    "Please select a Labels directory before managing files.\n\n"
                    "Click the 'Settings' button to set your Labels directory.")
                return
                
            # Get the path to the Label Maker main.pyw file
            project_root = get_project_root()
            label_maker_dir = os.path.join(project_root, 'Label Maker')
            label_maker_main = os.path.join(label_maker_dir, 'main.pyw')
            
            if not file_exists(label_maker_main):
                messagebox.showerror("Error", f"Label Maker main file not found at: {label_maker_main}")
                return
            
            # Hide welcome window
            self.withdraw()
            
            # Run Label Maker with the --view-files argument
            process = subprocess.Popen([sys.executable, label_maker_main, "--view-files"])
            
            # Set up a check to monitor when the process terminates
            def check_process():
                if process.poll() is not None:
                    # Process has terminated, show welcome window again
                    self.deiconify()
                    self.lift()
                    self.focus_force()
                    return
                # Check again after 1 second
                self.after(1000, check_process)
                
            # Start monitoring the process
            self.after(1000, check_process)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Label Maker: {str(e)}")
            self.deiconify()  # Show welcome window again
    
    def labels_action(self):
        """Handler for Labels button click - Display and edit returns data"""
        # Create a dialog window for viewing and editing returns data
        dialog = tk.Toplevel(self)
        dialog.title("Returns Data")
        dialog.geometry("800x500")
        dialog.resizable(True, True)
        dialog.configure(bg='white')
        dialog.transient(self)  # Make dialog modal
        dialog.grab_set()  # Make dialog modal
        
        # Center the dialog
        self.center_window(dialog)
        
        # Create a frame for the content
        content_frame = tk.Frame(dialog, bg='white', padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(
            content_frame, 
            text="Returns Data", 
            font=("Arial", 16, "bold"), 
            bg='white'
        )
        title_label.pack(pady=(0, 20))
        
        # Create a frame for the treeview with scrollbars
        tree_frame = tk.Frame(content_frame, bg='white')
        tree_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Create vertical scrollbar
        vsb = tk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side='right', fill='y')
        
        # Create horizontal scrollbar
        hsb = tk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side='bottom', fill='x')
        
        # Create treeview
        columns = ("tracking", "sku", "label", "timestamp", "full_label")
        tree = ttk.Treeview(
            tree_frame, 
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        # Configure scrollbars
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        
        # Define column headings
        tree.heading("tracking", text="Tracking Number")
        tree.heading("sku", text="SKU")
        tree.heading("label", text="Label")
        tree.heading("timestamp", text="Timestamp")
        tree.heading("full_label", text="Full Label")  # Hidden column
        
        # Define column widths
        tree.column("tracking", width=200, minwidth=150)
        tree.column("sku", width=150, minwidth=100)
        tree.column("label", width=250, minwidth=150)
        tree.column("timestamp", width=150, minwidth=150)
        tree.column("full_label", width=0, stretch=False)  # Hidden column
        
        tree.pack(fill='both', expand=True)
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview", 
                        background="white",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="white")
        style.map('Treeview', background=[('selected', '#4CAF50')])
        
        # Function to load records from log file
        def load_records():
            # Clear existing items
            for item in tree.get_children():
                tree.delete(item)
                
            # Get path to log file using our utility function
            log_dir, log_file = get_central_log_file_path()
            
            if not os.path.exists(log_file):
                # No records yet
                tree.insert("", "end", values=("No records found", "", "", ""))
                return
                
            # Read and parse log file
            with open(log_file, 'r') as f:
                lines = f.readlines()
                
            # Add each record to the treeview
            for line in lines:
                try:
                    # Parse line
                    parts = line.strip().split(" | ")
                    if len(parts) >= 4:
                        timestamp = parts[0]
                        tracking = parts[1].replace("Tracking: ", "")
                        sku = parts[2].replace("SKU: ", "")
                        label_full = parts[3].replace("Label: ", "")
                        
                        # Extract just the filename from the full path
                        label_filename = os.path.basename(label_full)
                        
                        # Use the filename as the display value
                        label_display = label_filename
                        
                        # Insert into treeview with full label stored in hidden column
                        tree.insert("", "end", values=(tracking, sku, label_display, timestamp, label_full))
                except Exception as e:
                    print(f"Error parsing log line: {str(e)}")
        
        # Function to edit a record
        def edit_record():
            # Get selected item
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showinfo("Select Record", "Please select a record to edit.")
                return
                
            # Get values of selected item
            item_values = tree.item(selected_item[0], "values")
            if not item_values or item_values[0] == "No records found":
                return
                
            # Get the full label path from the hidden column
            full_label_path = item_values[4]
            
            # Check if the file exists
            if not file_exists(full_label_path):
                messagebox.showerror("File Not Found", f"The label file could not be found at:\n{full_label_path}")
                return
            
            # Create edit dialog
            edit_dialog = tk.Toplevel(dialog)
            edit_dialog.title("Edit Record")
            edit_dialog.geometry("500x300")
            edit_dialog.resizable(False, False)
            edit_dialog.configure(bg='white')
            edit_dialog.transient(dialog)
            edit_dialog.grab_set()
            
            # Center the dialog
            self.center_window(edit_dialog)
            
            # Create a frame for the content
            edit_frame = tk.Frame(edit_dialog, bg='white', padx=20, pady=20)
            edit_frame.pack(fill='both', expand=True)
            
            # Create form fields
            tk.Label(edit_frame, text="Timestamp:", font=("Arial", 10), bg='white').grid(row=0, column=0, sticky='w', pady=(0, 5))
            timestamp_var = tk.StringVar(value=item_values[3])
            timestamp_entry = tk.Entry(edit_frame, textvariable=timestamp_var, font=("Arial", 10), width=30)
            timestamp_entry.grid(row=0, column=1, sticky='we', pady=(0, 5))
            
            tk.Label(edit_frame, text="Tracking Number:", font=("Arial", 10), bg='white').grid(row=1, column=0, sticky='w', pady=(0, 5))
            tracking_var = tk.StringVar(value=item_values[0])
            tracking_entry = tk.Entry(edit_frame, textvariable=tracking_var, font=("Arial", 10), width=30)
            tracking_entry.grid(row=1, column=1, sticky='we', pady=(0, 5))
            
            tk.Label(edit_frame, text="SKU:", font=("Arial", 10), bg='white').grid(row=2, column=0, sticky='w', pady=(0, 5))
            sku_var = tk.StringVar(value=item_values[1])
            sku_entry = tk.Entry(edit_frame, textvariable=sku_var, font=("Arial", 10), width=30)
            sku_entry.grid(row=2, column=1, sticky='we', pady=(0, 5))
            
            tk.Label(edit_frame, text="Label:", font=("Arial", 10), bg='white').grid(row=3, column=0, sticky='w', pady=(0, 5))
            label_var = tk.StringVar(value=item_values[2])
            label_entry = tk.Entry(edit_frame, textvariable=label_var, font=("Arial", 10), width=30, state='readonly')
            label_entry.grid(row=3, column=1, sticky='we', pady=(0, 5))
            
            # Store the full label path
            full_label_path_var = tk.StringVar(value=full_label_path)
            
            # Create a frame for the buttons
            button_frame = tk.Frame(edit_frame, bg='white')
            button_frame.grid(row=4, column=0, columnspan=2, sticky='e', pady=(20, 0))
            
            # Save Button
            save_button = tk.Button(
                button_frame, 
                text="Save", 
                font=("Arial", 10), 
                bg='#4CAF50', 
                fg='white',
                activebackground='#45a049',
                activeforeground='white',
                relief=tk.FLAT,
                padx=15,
                pady=5,
                command=lambda: save_changes()
            )
            save_button.pack(side='left', padx=(10, 0))
            
            # Delete Button
            delete_button = tk.Button(
                button_frame, 
                text="Delete", 
                font=("Arial", 10), 
                bg='#f44336', 
                fg='white',
                activebackground='#d32f2f',
                activeforeground='white',
                relief=tk.FLAT,
                padx=15,
                pady=5,
                command=lambda: delete_record()
            )
            delete_button.pack(side='left', padx=(10, 0))
            
            # Cancel Button
            cancel_button = tk.Button(
                button_frame, 
                text="Cancel", 
                font=("Arial", 10), 
                bg='#9E9E9E', 
                fg='white',
                activebackground='#757575',
                activeforeground='white',
                relief=tk.FLAT,
                padx=15,
                pady=5,
                command=edit_dialog.destroy
            )
            cancel_button.pack(side='left', padx=(10, 0))
            
            # Function to save changes
            def save_changes():
                # Get updated values
                new_timestamp = timestamp_var.get()
                new_tracking = tracking_var.get()
                new_sku = sku_var.get()
                
                # Get the full label path
                full_label_path = full_label_path_var.get()
                
                # Update treeview with display values
                tree.item(selected_item[0], values=(new_tracking, new_sku, item_values[2], new_timestamp, full_label_path))
                
                # Update log file
                update_log_file()
                
                # Close dialog
                edit_dialog.destroy()
        
        # Function to delete a record
        def delete_record():
            # Get selected item
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showinfo("Select Record", "Please select a record to delete.")
                return
                
            # Get values of selected item
            item_values = tree.item(selected_item[0], "values")
            if not item_values or item_values[0] == "No records found":
                return
                
            # Confirm deletion
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
                # Delete from treeview
                tree.delete(selected_item[0])
                
                # Update log file
                update_log_file()
        
        # Function to update the log file with current treeview contents
        def update_log_file():
            # Path to log file
            log_dir, log_file = get_central_log_file_path()
            
            # Get all items from treeview
            all_items = tree.get_children()
            
            # Create logs directory if it doesn't exist
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Write to log file
            with open(log_file, 'w') as f:
                for item_id in all_items:
                    item_values = tree.item(item_id, "values")
                    if item_values and item_values[0] != "No records found":
                        timestamp = item_values[3]
                        tracking = item_values[0]
                        sku = item_values[1]
                        
                        # Get the full label path from the hidden column
                        full_label_path = item_values[4] if len(item_values) > 4 else ""
                        
                        # Write to log file in the format: timestamp | Tracking: tracking | SKU: sku | Label: full_label_path
                        f.write(f"{timestamp} | Tracking: {tracking} | SKU: {sku} | Label: {full_label_path}\n")
        
        # Create a frame for the buttons
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Refresh button
        refresh_button = tk.Button(
            button_frame, 
            text="Refresh", 
            font=("Arial", 10), 
            bg='#2196F3', 
            fg='white',
            activebackground='#1976D2',
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=load_records
        )
        refresh_button.pack(side='left')
        
        # Edit button
        edit_button = tk.Button(
            button_frame, 
            text="Edit", 
            font=("Arial", 10), 
            bg='#FF9800', 
            fg='white',
            activebackground='#F57C00',
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=edit_record
        )
        edit_button.pack(side='left', padx=(10, 0))
        
        # Delete button
        delete_button = tk.Button(
            button_frame, 
            text="Delete", 
            font=("Arial", 10), 
            bg='#f44336', 
            fg='white',
            activebackground='#d32f2f',
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=delete_record
        )
        delete_button.pack(side='left', padx=(10, 0))
        
        # Close button
        close_button = tk.Button(
            button_frame, 
            text="Close", 
            font=("Arial", 10), 
            bg='#9E9E9E', 
            fg='white',
            activebackground='#757575',
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=dialog.destroy
        )
        close_button.pack(side='right')
        
        # Load records initially
        load_records()
        
        # Wait for the dialog to be closed
        self.wait_window(dialog)
    
    def settings_action(self):
        """Open settings dialog"""
        # Create settings dialog
        settings_dialog = tk.Toplevel(self)
        settings_dialog.title("Settings")
        settings_dialog.geometry("600x400")  # Reduced height since we're removing sections
        settings_dialog.resizable(False, False)
        settings_dialog.configure(bg='white')
        settings_dialog.transient(self)  # Make dialog modal
        settings_dialog.grab_set()  # Make dialog modal
        
        # Create a frame for the content
        content_frame = tk.Frame(settings_dialog, bg='white', padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(
            content_frame, 
            text="Settings", 
            font=("Arial", 16, "bold"), 
            bg='white'
        )
        title_label.pack(pady=(0, 20))
        
        # Labels Directory Section
        directory_section = tk.LabelFrame(content_frame, text="Labels Directory", font=("Arial", 12, "bold"), bg='white', padx=10, pady=10)
        directory_section.pack(fill='x', pady=(0, 15))
        
        # Directory path
        directory_var = tk.StringVar(value=self.config_manager.settings.last_directory or "")
        directory_entry = tk.Entry(directory_section, textvariable=directory_var, font=("Arial", 10), width=50)
        directory_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        # Browse button
        browse_button = tk.Button(
            directory_section, 
            text="Browse", 
            font=("Arial", 10), 
            bg='#2196F3', 
            fg='white',
            activebackground='#1976D2',
            activeforeground='white',
            relief=tk.FLAT,
            padx=10,
            pady=5,
            command=lambda: [
                directory_var.set(filedialog.askdirectory(
                    initialdir=directory_var.get() or os.path.expanduser("~"),
                    title="Select Labels Directory"
                )),
                self.update_label_count(directory_var.get())
            ]
        )
        browse_button.pack(side='right')
        
        # Label count
        count_frame = tk.Frame(directory_section, bg='white')
        count_frame.pack(fill='x', pady=(10, 0))
        
        count_label = tk.Label(
            count_frame, 
            text="Labels in directory:", 
            font=("Arial", 10), 
            bg='white'
        )
        count_label.pack(side='left')
        
        self.label_count_var = tk.StringVar(value="0")
        label_count = tk.Label(
            count_frame, 
            textvariable=self.label_count_var, 
            font=("Arial", 10, "bold"), 
            bg='white'
        )
        label_count.pack(side='left', padx=(5, 0))
        
        # Update label count
        self.update_label_count(directory_var.get())
        
        # Google Sheets Section
        sheets_section = tk.LabelFrame(content_frame, text="Google Sheets Integration", font=("Arial", 12, "bold"), bg='white', padx=10, pady=10)
        sheets_section.pack(fill='x', pady=(0, 15))

        # Connection status
        status_text = "Not Connected"
        status_color = 'red'

        # Check if Google Sheets is configured
        if (self.config_manager.settings.google_sheet_url and 
            self.config_manager.settings.google_sheet_name):
            status_text = "Connected"
            status_color = 'green'

        status_frame = tk.Frame(sheets_section, bg='white')
        status_frame.pack(fill='x', pady=(5, 5))

        tk.Label(status_frame, text="Status:", font=("Arial", 10), bg='white').pack(side='left')
        self.sheets_status_label = tk.Label(
            status_frame,
            text=status_text,
            font=("Arial", 10, "bold"),
            fg=status_color,
            bg='white'
        )
        self.sheets_status_label.pack(side='left', padx=(5, 0))
        
        # Add sheet info if connected
        if status_text == "Connected":
            sheet_info = f"{self.config_manager.settings.google_sheet_name}"
            tk.Label(status_frame, text=" | Sheet:", font=("Arial", 10), bg='white').pack(side='left', padx=(10, 0))
            tk.Label(status_frame, text=sheet_info, font=("Arial", 10, "italic"), bg='white').pack(side='left', padx=(5, 0))
        
        # Configure button
        configure_button = tk.Button(
            sheets_section,
            text="Configure Google Sheets",
            font=("Arial", 10),
            bg='#2196F3',
            fg='white',
            activebackground='#1976D2',
            activeforeground='white',
            relief=tk.FLAT,
            padx=10,
            pady=5,
            command=self.open_sheets_dialog
        )
        configure_button.pack(pady=(5, 5))
        
        # Button Frame
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Save Button
        save_button = tk.Button(
            button_frame, 
            text="Save", 
            font=("Arial", 10), 
            bg='#4CAF50', 
            fg='white',
            activebackground='#45a049',
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=lambda: self._save_settings(
                settings_dialog,
                directory_var.get()
            )
        )
        save_button.pack(side='right', padx=(10, 0))
        
        # Cancel Button
        cancel_button = tk.Button(
            button_frame, 
            text="Cancel", 
            font=("Arial", 10), 
            bg='#f44336', 
            fg='white',
            activebackground='#d32f2f',
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=settings_dialog.destroy
        )
        cancel_button.pack(side='right')
        
        # Center the dialog
        self.center_window(settings_dialog)
    
    def open_sheets_dialog(self):
        """Open the Google Sheets configuration dialog"""
        sheets_dialog = GoogleSheetsDialog(self)
        self.wait_window(sheets_dialog)
        
        # Reload config manager to get updated settings
        self.config_manager = ConfigManager()
        
        # Update the Google Sheets status display
        self._update_sheets_status_display()
    
    def _update_sheets_status_display(self):
        """Update the Google Sheets status display in the welcome window"""
        # Update the Google Sheets status display
        status_text = "Not Connected"
        status_color = 'red'
        
        # Check if Google Sheets is configured
        if (self.config_manager.settings.google_sheet_url and 
            self.config_manager.settings.google_sheet_name):
            status_text = "Connected"
            status_color = 'green'
        
        # Update the status label
        if hasattr(self, 'sheets_status_label'):
            self.sheets_status_label.config(text=status_text, fg=status_color)
            
            # Clear any existing sheet info widgets
            status_frame = self.sheets_status_label.master
            for widget in status_frame.winfo_children():
                if widget != self.sheets_status_label and widget.winfo_class() != "Label" or \
                   (widget.winfo_class() == "Label" and widget.cget("text") not in ["Status:"]):
                    widget.destroy()
            
            # Add sheet info if connected
            if status_text == "Connected":
                sheet_info = f"{self.config_manager.settings.google_sheet_name}"
                tk.Label(status_frame, text=" | Sheet:", font=("Arial", 10), bg='white').pack(side='left', padx=(10, 0))
                tk.Label(status_frame, text=sheet_info, font=("Arial", 10, "italic"), bg='white').pack(side='left', padx=(5, 0))
            
            # Force a refresh of the main window to update the UI
            self.update_idletasks()
    
    def update_label_count(self, directory=None):
        """Update the label count display based on the current directory"""
        # Get the labels directory from config
        labels_dir = directory or self.config_manager.settings.last_directory
        
        # Count labels if directory exists using our utility function
        label_count = count_files_in_directory(labels_dir)
        
        # Update the label count display
        if hasattr(self, 'label_count_label'):
            self.label_count_label.config(text=f"{label_count} Labels")
        
        if hasattr(self, 'label_count_var'):
            self.label_count_var.set(str(label_count))
    
    def center_window(self, window=None):
        """
        Center a window on the screen
        
        Args:
            window: Window to center (defaults to self)
        """
        if window is None:
            window = self
            
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def _save_settings(self, dialog, directory):
        """
        Save settings to the config file
        
        Args:
            dialog: Settings dialog to close on success
            directory: Labels directory path
        """
        try:
            # Validate directory
            if directory and not directory_exists(directory):
                messagebox.showerror("Error", "The selected directory does not exist.")
                return
                
            # Update settings
            self.config_manager.settings.last_directory = directory
            
            # Save settings using the config manager
            if self.config_manager.save_settings():
                # Close dialog
                dialog.destroy()
                
                # Update label count
                self.update_label_count()
            else:
                messagebox.showerror("Error", "Failed to save settings.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving settings: {str(e)}")
