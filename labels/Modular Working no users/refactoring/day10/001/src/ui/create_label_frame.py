"""
Frame-based implementation of the Create Label functionality.
This module provides a frame that can be embedded in the welcome window
instead of opening a separate dialog.
"""

import os
import sys
import logging
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import utility modules
from src.utils.ui_components import create_title_section, create_colored_button, create_form_field_group
from src.utils.barcode_operations import process_barcode
from src.utils.sheets_operations import write_to_google_sheet
from src.utils.file_utils import directory_exists, file_exists, find_files_by_sku

# Configure logging
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(logs_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(logs_dir, 'label_maker.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_shipping_record(tracking_number, sku, status):
    """Log shipping record information to a separate file"""
    try:
        # Get logs directory
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Create timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format the record
        log_message = f"{timestamp} - Tracking={tracking_number}, SKU={sku}, Status={status}\n"
        
        # Write to shipping_records.txt instead of logging to the main log file
        with open(os.path.join(logs_dir, 'shipping_records.txt'), 'a', encoding='utf-8') as f:
            f.write(log_message)
            
        return True
    except Exception as e:
        # Log errors to the main log file
        logging.error(f"Error recording shipping record: {str(e)}")
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
        self.stay_on_top_var = tk.BooleanVar(value=config_manager.settings.stay_on_top if hasattr(config_manager.settings, 'stay_on_top') else False)
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface elements"""
        # Create a frame for the content with padding
        content_frame = tk.Frame(self, bg='white', padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Add a return button in the top-left corner
        return_frame = tk.Frame(content_frame, bg='white')
        return_frame.pack(fill='x', pady=(0, 5))
        
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
        return_button.pack(side='left')
        
        # Add a pin button on the right side to toggle stay-on-top
        def toggle_stay_on_top():
            current_state = self.stay_on_top_var.get()
            self.pin_btn.config(
                bg='#FFD700' if current_state else '#D3D3D3',  # Gold if on, Light Gray if off
                relief='sunken' if current_state else 'raised'
            )
            # Get the root window (Tk instance) and update its topmost state
            root = self.winfo_toplevel()
            root.attributes('-topmost', current_state)
            # Ensure window is lifted and focused when topmost is enabled
            if current_state:
                root.lift()
                root.focus_force()
            # Save the setting
            self.config_manager.settings.stay_on_top = current_state
            self.config_manager.save_settings()
        
        # Create pin button with label
        pin_frame = tk.Frame(return_frame, bg='white')
        pin_frame.pack(side='right')
        
        pin_label = tk.Label(pin_frame, text="Pin:", bg='white', font=('TkDefaultFont', 10))
        pin_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Set initial button state based on saved setting
        initial_pin_color = '#FFD700' if self.stay_on_top_var.get() else '#D3D3D3'  # Gold if on, Light Gray if off
        initial_pin_relief = 'sunken' if self.stay_on_top_var.get() else 'raised'
        
        self.pin_btn = tk.Button(pin_frame, text="📌", bg=initial_pin_color, 
                           relief=initial_pin_relief, width=3,
                           font=('TkDefaultFont', 14), anchor='center')
        
        self.pin_btn.config(
            command=lambda: [self.stay_on_top_var.set(not self.stay_on_top_var.get()),
                           toggle_stay_on_top()]
        )
        self.pin_btn.pack(side=tk.LEFT, padx=2)
        
        # Apply the initial stay-on-top state
        if self.stay_on_top_var.get():
            root = self.winfo_toplevel()
            root.attributes('-topmost', True)
        
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
        
        # Initially disable the SKU field until a valid tracking number is entered
        self.field_widgets["SKU:"]["widget"].config(state="disabled")
        
        # Add auto-copy and tab functionality for tracking number field
        def on_tracking_enter(event):
            # Get the tracking number
            tracking_number = self.tracking_var.get().strip()
            
            # Validate tracking number
            if not tracking_number:
                self._update_status("Please enter a tracking number", 'red')
                messagebox.showerror("Missing Tracking Number", "A tracking number is required.\n\nPlease enter a valid tracking number.")
                return "break"  # Prevent default Enter behavior
            
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
                
                # Enable and move focus to SKU field
                self.field_widgets["SKU:"]["widget"].config(state="normal")
                self.field_widgets["SKU:"]["widget"].focus_set()
                
                # Clear any previous error messages
                self._update_status("", 'black')
            
            return "break"  # Prevent default Enter behavior
        
        # Bind Enter key to the tracking number field
        self.field_widgets["Tracking Number:"]["widget"].bind("<Return>", on_tracking_enter)
        
        # Add functionality to print label when Enter is pressed in the SKU field
        def on_sku_enter(event):
            # Verify tracking number is present before proceeding
            tracking_number = self.tracking_var.get().strip()
            if not tracking_number:
                self._update_status("Please enter a tracking number first", 'red')
                messagebox.showerror("Missing Tracking Number", "A tracking number is required.\n\nPlease enter a valid tracking number.")
                # Move focus back to tracking number field
                self.field_widgets["Tracking Number:"]["widget"].focus_set()
                return "break"  # Prevent default Enter behavior
            
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
        # Get input values
        tracking_number = self.tracking_var.get().strip()
        sku = self.sku_var.get().strip()
        
        # Validate tracking number - now required in all cases
        if not tracking_number:
            self._update_status("Please enter a tracking number", 'red')
            messagebox.showerror("Missing Tracking Number", "A tracking number is required.\n\nPlease enter a valid tracking number.")
            # Move focus back to tracking number field
            self.field_widgets["Tracking Number:"]["widget"].focus_set()
            return False, "No tracking number provided"
        
        # Validate tracking number length
        if len(tracking_number) <= 12:
            self._update_status("Tracking number must be longer than 12 characters", 'red')
            messagebox.showerror("Invalid Tracking Number", "Tracking number must be longer than 12 characters.\n\nPlease enter a valid tracking number.")
            # Move focus back to tracking number field
            self.field_widgets["Tracking Number:"]["widget"].focus_set()
            return False, "Invalid tracking number length"
        
        # Get configuration
        mirror_print = self.mirror_print_var.get()
        print_enabled = self.print_enabled_var.get()
        
        # Get labels directory from configuration
        labels_dir = self.config_manager.settings.last_directory if hasattr(self.config_manager.settings, 'last_directory') else None
        
        # Validate labels directory
        if not labels_dir or not directory_exists(labels_dir):
            error_msg = f"Labels directory not configured or does not exist: {labels_dir}"
            self._update_status(error_msg, 'red')
            messagebox.showerror("Error", error_msg)
            return False, error_msg
        
        # Create a function to update status
        def update_status(message, color='black'):
            self._update_status(message, color)
        
        # If print is disabled, just log the information without printing
        if not print_enabled:
            # Log the shipping record
            log_shipping_record(tracking_number, sku, "No print - logging only")
            
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
                # Log the shipping record ONLY after successful printing
                log_shipping_record(tracking_number, sku, "Label printed successfully")
                
                # Write to Google Sheets ONLY after successful printing
                if (hasattr(self.config_manager.settings, 'google_sheet_url') and 
                    self.config_manager.settings.google_sheet_url and 
                    hasattr(self.config_manager.settings, 'google_sheet_name') and
                    self.config_manager.settings.google_sheet_name):
                    # Use a separate thread for Google Sheets to avoid blocking UI
                    def sheets_task():
                        try:
                            write_to_google_sheet(
                                self.config_manager, 
                                tracking_number, 
                                sku, 
                                update_status
                            )
                        except Exception as e:
                            print(f"Error writing to Google Sheets: {str(e)}")
                    
                    import threading
                    sheets_thread = threading.Thread(target=sheets_task)
                    sheets_thread.daemon = True
                    sheets_thread.start()
                
                # Show success message in the title
                self._show_success_message(f"Label for {sku or tracking_number} printed successfully!")
                
                # Clear input fields for next label
                self._clear_fields()
                
                # Update the label count
                if self.update_label_count_callback:
                    self.update_label_count_callback()
            
            # Use the simpler approach from the BAK version
            from src.utils.barcode_operations import process_barcode
            
            # Check if we have a valid tracking number or SKU
            if not tracking_number and not sku:
                error_msg = "Either tracking number or SKU is required"
                self._update_status(error_msg, 'red')
                messagebox.showerror("Error", error_msg)
                return False, error_msg
                
            # Use our utility function to process the barcode
            success, message = process_barcode(
                tracking_number,
                sku,
                labels_dir,
                mirror_print,
                update_status,
                after_print_success
            )
            
            # Use pyautogui to automatically press Enter after a shorter delay
            if success:
                try:
                    # Reduced wait time for the print dialog to appear (from 2000ms to 1000ms)
                    print("Waiting for print dialog to appear...")
                    self.after(1000, lambda: self._press_enter_for_print_dialog())
                except Exception as e:
                    print(f"Error setting up auto-press Enter: {str(e)}")
            else:
                # Show error message if process_barcode failed
                self._update_status(f"Error: {message}", 'red')
                messagebox.showerror("Error", message)
                self._clear_fields()
                
            return success, message
            
        except Exception as e:
            error_msg = str(e)
            self._update_status(f"Error processing barcode: {error_msg}", 'red')
            messagebox.showerror("Error", f"Error processing barcode: {error_msg}")
            self._clear_fields()
            return False, error_msg
    
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
        
        # Disable the SKU field until a valid tracking number is entered
        self.field_widgets["SKU:"]["widget"].config(state="disabled")
        
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
