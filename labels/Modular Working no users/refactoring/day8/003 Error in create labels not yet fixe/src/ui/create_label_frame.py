"""
Frame-based implementation of the Create Label functionality.
This module provides a frame that can be embedded in the welcome window
instead of opening a separate dialog.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import datetime
import pyautogui
import logging

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import utility modules
from src.utils.ui_components import create_title_section, create_colored_button, create_form_field_group
from src.utils.barcode_operations import process_barcode
from src.utils.sheets_operations import write_to_google_sheet
from src.utils.file_utils import directory_exists, file_exists, find_files_by_sku

# Configure logging
logging.basicConfig(
    filename=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'label_maker.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_shipping_record(tracking_number, sku, status):
    """Log shipping record information to a file"""
    try:
        log_message = f"SHIPPING RECORD: Tracking={tracking_number}, SKU={sku}, Status={status}"
        logging.info(log_message)
        return True
    except Exception as e:
        logging.error(f"Error logging shipping record: {str(e)}")
        return False

class CreateLabelFrame(tk.Frame):
    """Frame-based implementation of the Create Label functionality"""
    
    def __init__(self, parent, config_manager, update_label_count_callback, return_to_welcome_callback):
        """
        Initialize the Create Label frame
        
        Args:
            parent: Parent widget
            config_manager: Configuration manager instance
            update_label_count_callback: Callback to update label count after successful label creation
            return_to_welcome_callback: Callback to return to the welcome screen
        """
        super().__init__(parent, bg='white')
        
        # Store references
        self.parent = parent
        self.config_manager = config_manager
        self.update_label_count_callback = update_label_count_callback
        self.return_to_welcome_callback = return_to_welcome_callback
        
        # Initialize variables
        self.tracking_var = tk.StringVar()
        self.sku_var = tk.StringVar()
        self.mirror_print_var = tk.BooleanVar(value=config_manager.settings.mirror_print if hasattr(config_manager.settings, 'mirror_print') else False)
        self.print_enabled_var = tk.BooleanVar(value=True)  # Print enabled by default
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface elements"""
        # Create a frame for the content with padding
        content_frame = tk.Frame(self, bg='white', padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Add a return button in the top-left corner
        return_frame = tk.Frame(content_frame, bg='white')
        return_frame.pack(anchor='nw', pady=(0, 10))
        
        return_button = create_colored_button(
            return_frame,
            text="← Return",
            color="#4CAF50",  # Green
            hover_color="#A5D6A7",  # Light Green
            command=self.return_to_welcome_callback,
            big=False
        )
        return_button.config(
            width=10,
            height=1,
            font=("Arial", 10, "bold")
        )
        return_button.pack()
        
        # Title
        self.title_frame = tk.Frame(content_frame, bg='white')
        self.title_frame.pack(pady=(0, 20))
        
        self.title_label = tk.Label(
            self.title_frame,
            text="Create New Label",
            font=("Arial", 16, "bold"),
            bg='white',
            fg='#333333'
        )
        self.title_label.pack()
        
        # Create form fields
        fields = [
            {
                "label": "Tracking Number:",
                "var_type": "string",
                "default": "",
                "width": 30,
                "required": False
            },
            {
                "label": "SKU:",
                "var_type": "string",
                "default": "",
                "width": 30,
                "required": True
            }
        ]
        
        form_frame = tk.Frame(content_frame, bg='white')
        form_frame.pack(fill='x', pady=10)
        
        self.field_widgets = create_form_field_group(form_frame, fields)
        
        # Store references to the variables
        self.tracking_var = self.field_widgets["Tracking Number:"]["var"]
        self.sku_var = self.field_widgets["SKU:"]["var"]
        
        # Add focus to tracking number field
        self.field_widgets["Tracking Number:"]["widget"].focus_set()
        
        # Add auto-copy and tab functionality for tracking number field
        def on_tracking_enter(event):
            # Get the tracking number
            tracking_number = self.tracking_var.get().strip()
            
            # Validate tracking number length
            if tracking_number and len(tracking_number) <= 12:
                self._update_status("Tracking number must be longer than 12 characters", 'red')
                messagebox.showerror("Invalid Tracking Number", "Tracking number must be longer than 12 characters.\n\nPlease enter a valid tracking number.")
                return "break"  # Prevent default Enter behavior
            
            # Check if printing is disabled and warn the user early
            if tracking_number and not self.print_enabled_var.get():
                if not messagebox.askyesno("Print Disabled", 
                                         "The Print toggle button is disabled. The label information will be logged but no label will be printed.\n\nDo you want to continue?"):
                    # User canceled, clear the tracking number field
                    self.tracking_var.set("")
                    self._update_status("Operation cancelled by user", 'red')
                    return "break"
            
            # Copy to clipboard
            if tracking_number:
                self.clipboard_clear()
                self.clipboard_append(tracking_number)
                
                # Move focus to SKU field
                self.field_widgets["SKU:"]["widget"].focus_set()
                
                # Clear any previous error messages
                self._update_status("", 'black')
            
            return "break"  # Prevent default Enter behavior
        
        # Bind Enter key to the tracking number field
        self.field_widgets["Tracking Number:"]["widget"].bind("<Return>", on_tracking_enter)
        
        # Add functionality to print label when Enter is pressed in the SKU field
        def on_sku_enter(event):
            # Print the label
            self._print_label()
            return "break"  # Prevent default Enter behavior
        
        # Bind Enter key to the SKU field
        self.field_widgets["SKU:"]["widget"].bind("<Return>", on_sku_enter)
        
        # Options frame
        options_frame = tk.Frame(content_frame, bg='white')
        options_frame.pack(fill='x', pady=10)
        
        # Mirror print toggle
        def toggle_mirror_print():
            current_state = self.mirror_print_var.get()
            self.mirror_btn.config(
                bg='#90EE90' if current_state else '#C71585',  # Green if on, Pink if off
                relief='sunken' if current_state else 'raised'
            )
            # Save the mirror print state
            self.config_manager.settings.mirror_print = current_state
            self.config_manager.save_settings()
        
        # Set initial button state based on saved setting
        initial_color = '#90EE90' if self.mirror_print_var.get() else '#C71585'
        initial_relief = 'sunken' if self.mirror_print_var.get() else 'raised'
        
        # Create mirror button with label
        mirror_label = tk.Label(options_frame, text="M P:", bg='white', font=('TkDefaultFont', 10))
        mirror_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.mirror_btn = tk.Button(options_frame, text=" ", bg=initial_color, 
                               relief=initial_relief, width=3,
                               font=('TkDefaultFont', 14), anchor='center')
        
        self.mirror_btn.config(
            command=lambda: [self.mirror_print_var.set(not self.mirror_print_var.get()),
                           toggle_mirror_print()]
        )
        self.mirror_btn.pack(side=tk.LEFT, padx=2)
        
        # Add a spacer
        spacer = tk.Frame(options_frame, width=20, bg='white')
        spacer.pack(side=tk.LEFT)
        
        # Print toggle
        def toggle_print_enabled():
            current_state = self.print_enabled_var.get()
            self.print_btn.config(
                bg='#90EE90' if current_state else '#C71585',  # Green if on, Pink if off
                relief='sunken' if current_state else 'raised'
            )
        
        # Create print button with label
        print_label = tk.Label(options_frame, text="Print:", bg='white', font=('TkDefaultFont', 10))
        print_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.print_btn = tk.Button(options_frame, text=" ", bg='#90EE90', 
                               relief='sunken', width=3,
                               font=('TkDefaultFont', 14), anchor='center')
        
        self.print_btn.config(
            command=lambda: [self.print_enabled_var.set(not self.print_enabled_var.get()),
                           toggle_print_enabled()]
        )
        self.print_btn.pack(side=tk.LEFT, padx=2)
        
        # Create button frame
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill='x', pady=(20, 0))
        
        # Create Print Button
        print_button = create_colored_button(
            button_frame,
            text="Print Label",
            color="#4CAF50",  # Green
            hover_color="#A5D6A7",  # Light Green
            command=self._print_label,
            big=True
        )
        print_button.pack(side='left', padx=(0, 10))
        
        # Create Clear Button
        clear_button = create_colored_button(
            button_frame,
            text="Clear",
            color="#9E9E9E",  # Gray
            hover_color="#E0E0E0",  # Light Gray
            command=self._clear_fields,
            big=False
        )
        clear_button.config(width=10, height=2)
        clear_button.pack(side='left')
        
        # Status frame
        status_frame = tk.Frame(content_frame, bg='white')
        status_frame.pack(fill='x', pady=(20, 0))
        
        self.status_var = tk.StringVar(value="")
        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Arial", 10),
            bg='white',
            fg='black'
        )
        self.status_label.pack(anchor='w')
    
    def _print_label(self):
        """Handle the print label button click"""
        # Get values from form
        tracking_number = self.tracking_var.get().strip()
        sku = self.sku_var.get().strip()
        
        # Validate tracking number
        if tracking_number and len(tracking_number) <= 12:
            self._update_status("Tracking number must be longer than 12 characters", 'red')
            self.field_widgets["Tracking Number:"]["widget"].focus_set()
            return
        
        # Validate SKU
        if not sku:
            self._update_status("Please enter an SKU", 'red')
            self.field_widgets["SKU:"]["widget"].focus_set()
            return
        
        # Check if labels directory exists
        labels_dir = self.config_manager.settings.last_directory
        if not directory_exists(labels_dir):
            self._update_status(f"Labels directory not found: {labels_dir}", 'red')
            return
        
        # Define a status callback function to update the status label
        def update_status(message, color):
            self._update_status(message, color)
            self.update()
        
        # Early validation - Check if the label file exists before proceeding
        label_exists = False
        
        # First check if a file with this SKU exists directly
        sku_file = os.path.join(labels_dir, f"{sku}.txt")
        if file_exists(sku_file):
            label_exists = True
        else:
            # If no direct SKU file, check if it exists in the database
            matching_files = find_files_by_sku(labels_dir, sku, extension='.txt')
            if matching_files:
                label_exists = True
        
        # If we don't have a tracking number and the label doesn't exist, show error and don't log
        if not tracking_number and not label_exists:
            error_message = f"Could not find a label for SKU: {sku}"
            self._update_status(f"Error: {error_message}", 'red')
            messagebox.showerror("Error", error_message)
            return
        
        # Create a unique filename based on tracking number and date (but don't create the actual file)
        date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{tracking_number}_{date_str}.txt"
        filepath = os.path.join(labels_dir, filename)
        
        # Get mirror print setting from the toggle button
        mirror_print = self.mirror_print_var.get()
        
        # Check if printing is disabled
        print_enabled = self.print_enabled_var.get()
        
        if not print_enabled:
            # We already warned the user when they entered the tracking number, so no need for another warning here
            # Skip the printing process but still log the info
            log_shipping_record(tracking_number, sku, "NO_PRINT")
            
            # Write to Google Sheets if configured
            if (hasattr(self.config_manager.settings, 'google_sheet_url') and 
                self.config_manager.settings.google_sheet_url and 
                hasattr(self.config_manager.settings, 'google_sheet_name') and
                self.config_manager.settings.google_sheet_name):
                write_to_google_sheet(
                    self.config_manager, 
                    tracking_number, 
                    sku, 
                    update_status
                )
            
            # Show success message
            self._show_success_message(f"Info for {sku} recorded (no print)")
            
            # Clear input fields for next label
            self._clear_fields()
            
            # Update the label count
            if self.update_label_count_callback:
                self.update_label_count_callback()
                
            return True, "Info recorded without printing"
        
        # Use our utility function to process the barcode
        try:
            # Define a function to run after successful printing
            def after_print_success():
                # Show success message in the title
                self._show_success_message(f"Label for {sku} printed successfully!")
                
                # Clear input fields for next label
                self._clear_fields()
                
                # Update the label count
                if self.update_label_count_callback:
                    self.update_label_count_callback()
            
            # Use our utility function to process the barcode
            success, message = process_barcode(
                tracking_number,
                sku,
                labels_dir,
                mirror_print,
                update_status,
                after_print_success
            )
            
            # Use pyautogui to automatically press Enter after a short delay
            if success:
                try:
                    # Wait a moment for the print dialog to appear (longer delay)
                    print("Waiting for print dialog to appear...")
                    self.after(2000, lambda: self._press_enter_for_print_dialog())
                except Exception as e:
                    print(f"Error setting up auto-press Enter: {str(e)}")
            
        except Exception as e:
            error_msg = str(e)
            self._update_status(f"Error processing barcode: {error_msg}", 'red')
    
    def _press_enter_for_print_dialog(self):
        """Press Enter key to confirm print dialog"""
        try:
            print("Pressing Enter to confirm print dialog...")
            pyautogui.press('enter')
            print("Enter key pressed")
        except Exception as e:
            print(f"Error pressing Enter: {str(e)}")
    
    def _clear_fields(self):
        """Clear all form fields"""
        self.tracking_var.set("")
        self.sku_var.set("")
        
        # Set focus to tracking number field
        self.field_widgets["Tracking Number:"]["widget"].focus_set()
    
    def _update_status(self, message, color='black'):
        """Update the status message"""
        self.status_var.set(message)
        self.status_label.config(fg=color)
    
    def _show_success_message(self, message):
        """Show a success message in the title and revert back after a delay"""
        # Save the original text
        original_text = self.title_label.cget("text")
        
        # Change the title to the success message with green color
        self.title_label.config(text=message, fg='#4CAF50')
        
        # Schedule to revert back to original title after 3 seconds
        self.after(3000, lambda: self.title_label.config(text=original_text, fg='#333333'))
