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
from src.utils.sheets_operations import write_to_google_sheet
from src.utils.barcode_operations import find_or_create_barcode, print_barcode, process_barcode
from src.utils.ui_components import create_title_section, create_colored_button, create_button_grid, create_version_label, create_form_field_group, create_status_bar, create_sheets_status_display
from src.utils.dialog_handlers import create_label_dialog
import pyautogui
import barcode
from barcode.writer import ImageWriter
from PIL import Image
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
from src.utils.returns_operations import load_returns_data, update_log_file, create_returns_dialog, create_edit_dialog
from src.utils.settings_operations import create_settings_dialog, update_sheets_status_display
from src.utils.sheets_operations import create_google_sheets_dialog, write_to_google_sheet

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
        
        # Create Google Sheets status display
        sheets_status_frame, self.sheets_status_label = create_sheets_status_display(
            self,
            "Not Connected",
            "red"
        )
        sheets_status_frame.pack(side='left', anchor='sw', padx=10, pady=10)
        
        # Initialize the Google Sheets status display
        self._update_sheets_status_display()
    
    def _create_title_section(self):
        """Create the title section of the window"""
        # Get the labels directory from config
        labels_dir = self.config_manager.settings.last_directory
        
        # Count labels if directory exists
        label_count = 0
        if labels_dir and os.path.exists(labels_dir):
            # Count files in the directory (assuming all files are labels)
            label_count = count_files_in_directory(labels_dir)
        
        # Create title section with label count
        title_frame, self.label_count_label, _ = create_title_section(
            self, 
            f"{label_count} Labels", 
            "Label Maker V3"
        )
        
        title_frame.pack(pady=20)
    
    def _create_button_section(self):
        """Create the button section of the window"""
        # Button colors (Material Design)
        colors = {
            'user': ('#4CAF50', '#A5D6A7'),        # Green, Light Green
            'management': ('#2196F3', '#90CAF9'),   # Blue, Light Blue
            'labels': ('#FF9800', '#FFCC80'),       # Orange, Light Orange
            'settings': ('#9E9E9E', '#E0E0E0')      # Gray, Light Gray
        }
        
        # Define button specifications
        button_specs = [
            {
                'text': 'User',
                'colors': colors['user'],
                'command': self.user_action,
                'big': True,
                'grid': (0, 0, 2, 1),
                'padx': 15,
                'pady': 10,
                'sticky': 'nsew'
            },
            {
                'text': 'Management',
                'colors': colors['management'],
                'command': self.management_action,
                'grid': (0, 1, 1, 1),
                'padx': 10,
                'pady': 5,
                'sticky': 'nsew'
            },
            {
                'text': 'Labels',
                'colors': colors['labels'],
                'command': self.labels_action,
                'grid': (1, 1, 1, 1),
                'padx': 10,
                'pady': 5,
                'sticky': 'nsew'
            },
            {
                'text': 'Settings',
                'colors': colors['settings'],
                'command': self.settings_action,
                'grid': (2, 0, 1, 2),
                'padx': 10,
                'pady': 5,
                'sticky': 'ew'
            }
        ]
        
        # Create button grid
        button_frame, buttons = create_button_grid(self, button_specs, num_columns=2)
        
        # Configure grid weights
        button_frame.grid_columnconfigure(0, weight=3)  # More weight to User button column
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)
        button_frame.grid_rowconfigure(2, weight=1)
        
        # Store buttons for later reference
        self.user_btn = buttons['user']
        self.management_btn = buttons['management']
        self.labels_btn = buttons['labels']
        self.settings_btn = buttons['settings']
        
        # Pack the button frame
        button_frame.pack(expand=True, padx=20)
    
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
        return create_colored_button(parent, text, color, light_color, command, big)
    
    def _create_version_label(self):
        """Create the version label at the bottom right"""
        version_label = create_version_label(self, "Ver. 1.0.1.1")
        version_label.pack(side='right', anchor='se', padx=10, pady=10)
    
    def create_label_action(self):
        """Handler for Create Label button click"""
        # Call the create_label_dialog function from our dialog_handlers module
        create_label_dialog(self, self.config_manager, self.update_label_count)
    
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
        create_title_section(content_frame, "Create New Label")
        
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
                "required": False
            }
        ]
        
        # Create form fields using our utility function
        form_fields = create_form_field_group(content_frame, fields)
        
        # Get references to variables and entries for later use
        tracking_var = form_fields["Tracking Number:"]["var"]
        sku_var = form_fields["SKU:"]["var"]
        tracking_entry = form_fields["Tracking Number:"]["widget"]
        sku_entry = form_fields["SKU:"]["widget"]
        
        # Set focus to tracking entry
        tracking_entry.focus()
        
        # Status
        _, status_label = create_status_bar(content_frame, "", "red")
        
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
            
            # Define a status callback function to update the status label
            def update_status(message, color):
                status_label.config(text=message, fg=color)
                dialog.update()
            
            # Write to Google Sheets if configured
            if (self.config_manager.settings.google_sheet_url and 
                self.config_manager.settings.google_sheet_name):
                success, message = write_to_google_sheet(
                    self.config_manager, 
                    tracking_number, 
                    sku, 
                    update_status
                )
            
            # Find or create barcode
            try:
                # Define a function to run after successful printing
                def after_print_success():
                    # Clear input fields for next label
                    tracking_var.set("")
                    sku_var.set("")
                    tracking_entry.focus_set()
                    
                    # Update the label count
                    self.update_label_count()
                
                # Use our utility function to process the barcode
                success, message = process_barcode(
                    tracking_number,
                    sku,
                    self.config_manager.settings.last_directory,
                    self.config_manager.settings.mirror_print,
                    update_status,
                    after_print_success
                )
                
                # Use pyautogui to automatically press Enter after a short delay
                if success:
                    try:
                        # Wait a moment for the print dialog to appear
                        dialog.after(1000, lambda: pyautogui.press('enter'))
                    except ImportError:
                        print("pyautogui not installed, cannot auto-press Enter")
                
            except Exception as e:
                error_msg = str(e)
                status_label.config(text=f"Error processing barcode: {error_msg}", fg='red')
                dialog.update()
        
        # Print Button
        print_button = create_colored_button(
            button_frame,
            "Print Label",
            '#4CAF50',  # Green
            '#45a049',  # Darker Green
            print_label
        )
        print_button.pack(side='right', padx=(10, 0))
        
        # Cancel Button
        cancel_button = create_colored_button(
            button_frame,
            "Cancel",
            '#f44336',  # Red
            '#d32f2f',  # Darker Red
            dialog.destroy
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
        # Create a dialog for viewing and editing returns data
        dialog, tree, content_frame = create_returns_dialog(self)
        
        # Function to edit a record
        def edit_record():
            # Get selected item
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showinfo("Select Record", "Please select a record to edit.")
                return
            
            # Edit the selected record
            create_edit_dialog(dialog, tree, selected_item)
        
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
                update_log_file(tree)
        
        # Create a frame for the buttons
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Refresh button
        refresh_button = create_colored_button(
            button_frame,
            "Refresh",
            '#2196F3',  # Blue
            '#90CAF9',  # Light Blue
            lambda: load_returns_data(tree)
        )
        refresh_button.pack(side='left')
        
        # Edit button
        edit_button = create_colored_button(
            button_frame,
            "Edit",
            '#FF9800',  # Orange
            '#FFCC80',  # Light Orange
            edit_record
        )
        edit_button.pack(side='left', padx=(10, 0))
        
        # Delete button
        delete_button = create_colored_button(
            button_frame,
            "Delete",
            '#f44336',  # Red
            '#EF9A9A',  # Light Red
            delete_record
        )
        delete_button.pack(side='left', padx=(10, 0))
        
        # Close button
        close_button = create_colored_button(
            button_frame,
            "Close",
            '#9E9E9E',  # Gray
            '#E0E0E0',  # Light Gray
            dialog.destroy
        )
        close_button.pack(side='right')
        
        # Load records initially
        load_returns_data(tree)
        
        # Wait for the dialog to be closed
        self.wait_window(dialog)
    
    def settings_action(self):
        """Open settings dialog"""
        # Create settings dialog using our utility function
        settings_dialog, directory_var, label_count_var = create_settings_dialog(
            self,
            self.config_manager,
            self.update_label_count,
            self.open_sheets_dialog,
            self._save_settings
        )
        
        # Store the label count variable for updating
        self.label_count_var = label_count_var
        
        # Wait for the dialog to be closed
        self.wait_window(settings_dialog)
    
    def open_sheets_dialog(self):
        """Open the Google Sheets configuration dialog"""
        # Use our utility function to create the dialog
        sheets_dialog = create_google_sheets_dialog(self, self.config_manager)
        
        # Wait for the dialog to be closed
        self.wait_window(sheets_dialog)
        
        # Reload config manager to get updated settings
        self.config_manager = ConfigManager()
        
        # Update the Google Sheets status display
        self._update_sheets_status_display()
    
    def _update_sheets_status_display(self):
        """Update the Google Sheets status display in the welcome window"""
        if hasattr(self, 'sheets_status_label'):
            # Get Google Sheets configuration
            sheets_config = self.config_manager.settings
            
            # Default status
            status_text = "Not Connected"
            status_color = "red"
            
            # Check if Google Sheets is configured
            if (hasattr(sheets_config, 'google_sheet_url') and 
                sheets_config.google_sheet_url and 
                hasattr(sheets_config, 'google_sheet_name') and 
                sheets_config.google_sheet_name):
                
                status_text = "Connected"
                status_color = "green"
            
            # Update the status label
            self.sheets_status_label.config(text=status_text, fg=status_color)
    
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
            
        center_window(window)
    
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
