import tkinter as tk
from tkinter import ttk, messagebox
import re
import os
import sys
import json
from dataclasses import asdict

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.config.config_manager import ConfigManager
from src.utils.sheets_utils import validate_sheet_url, get_sheet_names, test_sheet_connection
from src.utils.file_utils import get_credentials_file_path, file_exists
from src.utils.ui_utils import center_window, create_button, make_window_modal
from src.utils.config_utils import save_config

class GoogleSheetsDialog(tk.Toplevel):
    """Dialog for configuring Google Sheets integration"""
    
    def __init__(self, parent, config_manager=None, update_callback=None):
        """Initialize the Google Sheets dialog"""
        super().__init__(parent)
        
        # Window setup
        self.title("Google Sheets Configuration")
        self.geometry("500x600")  # Increased height from 550 to 600
        self.resizable(False, False)
        self.configure(bg='white')
        self.transient(parent)  # Make dialog modal
        self.grab_set()  # Make dialog modal
        
        # Initialize config manager
        self.config_manager = config_manager or ConfigManager()
        
        # Store the update callback
        self.update_callback = update_callback
        
        # Initialize connection status
        self.connection_status = self.config_manager.settings.google_sheets_connection_status or "Not Connected"
        
        # Create UI
        self._create_ui()
        
        # Center the dialog
        self.center_window()
        
        # Initialize sheet dropdown if URL is already set
        if self.config_manager.settings.google_sheet_url:
            self._fetch_sheet_names()
    
    def _create_ui(self):
        """Create the user interface elements"""
        # Main content frame
        content_frame = tk.Frame(self, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            content_frame, 
            text="Google Sheets Integration", 
            font=("Arial", 14, "bold"), 
            bg='white'
        )
        title_label.pack(anchor='center', pady=(0, 20))
        
        # Description
        description_text = (
            "Connect to Google Sheets to track your shipments and inventory.\n"
            "Enter the Google Sheet URL and select the sheet name below."
        )
        description_label = tk.Label(
            content_frame, 
            text=description_text, 
            font=("Arial", 10), 
            bg='white', 
            justify='left', 
            wraplength=460
        )
        description_label.pack(fill='x', pady=(0, 20))
        
        # URL Frame
        url_frame = tk.Frame(content_frame, bg='white')
        url_frame.pack(fill='x', pady=(0, 10))
        
        url_label = tk.Label(
            url_frame, 
            text="Google Sheet URL:", 
            font=("Arial", 10), 
            bg='white'
        )
        url_label.pack(anchor='w')
        
        self.url_var = tk.StringVar(value=self.config_manager.settings.google_sheet_url or "")
        url_entry = tk.Entry(
            url_frame, 
            textvariable=self.url_var, 
            font=("Arial", 10), 
            width=50
        )
        url_entry.pack(fill='x', pady=(5, 0))
        
        # Sheet Name
        sheet_frame = tk.Frame(content_frame, bg='white')
        sheet_frame.pack(fill='x', pady=(0, 10))
        
        sheet_label = tk.Label(
            sheet_frame, 
            text="Sheet Name:", 
            font=("Arial", 10), 
            bg='white'
        )
        sheet_label.pack(anchor='w')
        
        self.sheet_var = tk.StringVar(value=self.config_manager.settings.google_sheet_name or "")
        
        # Create a frame for the sheet selection dropdown and refresh button
        sheet_selection_frame = tk.Frame(sheet_frame, bg='white')
        sheet_selection_frame.pack(fill='x', pady=(5, 0))
        
        # Create the dropdown for sheet names
        self.sheet_dropdown = ttk.Combobox(
            sheet_selection_frame,
            textvariable=self.sheet_var,
            font=("Arial", 10),
            state="readonly"
        )
        self.sheet_dropdown.pack(side='left', fill='x', expand=True)
        
        # Add a refresh button to fetch sheet names
        refresh_button = create_button(
            sheet_selection_frame,
            text="⟳",
            command=self._fetch_sheet_names,
            bg='#2196F3',
            padx=8,
            pady=2,
            font=("Arial", 10, "bold")
        )
        refresh_button.pack(side='left', padx=(5, 0))
        
        # Tracking Column
        tracking_frame = tk.Frame(content_frame, bg='white')
        tracking_frame.pack(fill='x', pady=(0, 10))
        
        tracking_label = tk.Label(
            tracking_frame, 
            text="Tracking Number Column:", 
            font=("Arial", 10), 
            bg='white'
        )
        tracking_label.pack(anchor='w')
        
        tracking_input_frame = tk.Frame(tracking_frame, bg='white')
        tracking_input_frame.pack(fill='x', pady=(5, 0))
        
        self.tracking_col_var = tk.StringVar(value=self.config_manager.settings.google_sheet_tracking_column or "D")
        tracking_col_entry = tk.Entry(
            tracking_input_frame, 
            textvariable=self.tracking_col_var, 
            font=("Arial", 10), 
            width=5
        )
        tracking_col_entry.pack(side='left')
        
        tracking_col_help = tk.Label(
            tracking_input_frame, 
            text="(e.g., A, B, C)", 
            font=("Arial", 8), 
            bg='white', 
            fg='gray'
        )
        tracking_col_help.pack(side='left', padx=(5, 20))
        
        tracking_row_label = tk.Label(
            tracking_input_frame, 
            text="Starting Row:", 
            font=("Arial", 10), 
            bg='white'
        )
        tracking_row_label.pack(side='left')
        
        self.tracking_row_var = tk.StringVar(value=str(self.config_manager.settings.google_sheet_tracking_row or 3))
        tracking_row_entry = tk.Entry(
            tracking_input_frame, 
            textvariable=self.tracking_row_var, 
            font=("Arial", 10), 
            width=5
        )
        tracking_row_entry.pack(side='left', padx=(5, 0))
        
        # SKU Column
        sku_frame = tk.Frame(content_frame, bg='white')
        sku_frame.pack(fill='x', pady=(0, 10))
        
        sku_label = tk.Label(
            sku_frame, 
            text="SKU Column:", 
            font=("Arial", 10), 
            bg='white'
        )
        sku_label.pack(anchor='w')
        
        sku_input_frame = tk.Frame(sku_frame, bg='white')
        sku_input_frame.pack(fill='x', pady=(5, 0))
        
        self.sku_col_var = tk.StringVar(value=self.config_manager.settings.google_sheet_sku_column or "F")
        sku_col_entry = tk.Entry(
            sku_input_frame, 
            textvariable=self.sku_col_var, 
            font=("Arial", 10), 
            width=5
        )
        sku_col_entry.pack(side='left')
        
        sku_col_help = tk.Label(
            sku_input_frame, 
            text="(e.g., A, B, C)", 
            font=("Arial", 8), 
            bg='white', 
            fg='gray'
        )
        sku_col_help.pack(side='left', padx=(5, 20))
        
        sku_row_label = tk.Label(
            sku_input_frame, 
            text="Starting Row:", 
            font=("Arial", 10), 
            bg='white'
        )
        sku_row_label.pack(side='left')
        
        self.sku_row_var = tk.StringVar(value=str(self.config_manager.settings.google_sheet_sku_row or 3))
        sku_row_entry = tk.Entry(
            sku_input_frame, 
            textvariable=self.sku_row_var, 
            font=("Arial", 10), 
            width=5
        )
        sku_row_entry.pack(side='left', padx=(5, 0))
        
        # Status Frame
        status_frame = tk.Frame(content_frame, bg='white')
        status_frame.pack(fill='x', pady=(10, 0))
        
        status_label_title = tk.Label(
            status_frame, 
            text="Status:", 
            font=("Arial", 10, "bold"), 
            bg='white'
        )
        status_label_title.pack(side='left')
        
        self.status_label = tk.Label(
            status_frame, 
            text=self.connection_status, 
            font=("Arial", 10), 
            bg='white', 
            fg='red'
        )
        self.status_label.pack(side='left', padx=(5, 0))
        
        # Add a separator line above the button frame
        separator = ttk.Separator(content_frame, orient='horizontal')
        separator.pack(fill='x', pady=(20, 25))
        
        # Button Frame
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill='x', pady=(0, 0), padx=20)  # Added horizontal padding
        
        # Save Button
        save_button = create_button(
            button_frame,
            text="Save",
            command=self._save_settings,
            bg='#4CAF50',
            padx=25,
            pady=10,
            font=("Arial", 10, "bold")
        )
        save_button.pack(side='right', padx=(15, 10))
        
        # Cancel Button
        cancel_button = create_button(
            button_frame,
            text="Cancel",
            command=self.destroy,
            bg='#f44336',
            padx=20,
            pady=10
        )
        cancel_button.pack(side='right', padx=(0, 10))
        
        # Initialize status
        self._update_status()
    
    def _update_status(self):
        """Update the connection status display"""
        try:
            if hasattr(self, 'status_label'):
                self.status_label.config(
                    text=self.connection_status,
                    fg='green' if self.connection_status == "Connected" else 'red'
                )
        except Exception as e:
            print(f"Error updating status: {str(e)}")
    
    def _fetch_sheet_names(self):
        """Fetch the available sheet names from the Google Sheet"""
        try:
            # Get the URL
            url = self.url_var.get().strip()
            
            # Validate URL
            is_valid, result = validate_sheet_url(url)
            if not is_valid:
                messagebox.showerror("Error", result)
                return
            
            sheet_id = result
            
            # Import required libraries
            try:
                import gspread
                from oauth2client.service_account import ServiceAccountCredentials
            except ImportError:
                messagebox.showerror("Error", "Required libraries not installed.\n\nPlease install gspread and oauth2client:\npip install gspread oauth2client")
                return
            
            # Check for credentials file
            creds_file = get_credentials_file_path()
            if not file_exists(creds_file):
                messagebox.showerror("Error", f"Credentials file not found at:\n{creds_file}\n\nPlease create a service account and download the credentials file.")
                return
            
            # Get sheet names
            success, result = get_sheet_names(sheet_id)
            if not success:
                messagebox.showerror("Error", result)
                return
            
            sheet_names = result
            
            # Update the dropdown with the available sheet names
            self.sheet_dropdown['values'] = sheet_names
            
            # Select the first sheet by default
            self.sheet_var.set(sheet_names[0] if sheet_names else "")
            
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n\n{str(e)}")
    
    def _save_settings(self):
        """Save the Google Sheets settings"""
        try:
            # Get values from UI
            url = self.url_var.get().strip()
            sheet_name = self.sheet_var.get().strip()
            tracking_col = self.tracking_col_var.get().strip().upper()
            sku_col = self.sku_col_var.get().strip().upper()
            
            # Get row values and convert to integers
            try:
                tracking_row = int(self.tracking_row_var.get().strip())
                sku_row = int(self.sku_row_var.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Row values must be numbers")
                return
            
            # Validate inputs
            if not url:
                messagebox.showerror("Error", "Please enter a Google Sheet URL")
                return
                
            if not sheet_name:
                messagebox.showerror("Error", "Please select a sheet name")
                return
            
            # Validate URL
            is_valid, result = validate_sheet_url(url)
            if not is_valid:
                messagebox.showerror("Error", result)
                return
            
            if tracking_col and not re.match(r'^[A-Z]+$', tracking_col):
                messagebox.showerror("Error", "Invalid column format. Please use letters only (A-Z).")
                return
            
            if sku_col and not re.match(r'^[A-Z]+$', sku_col):
                messagebox.showerror("Error", "Invalid column format. Please use letters only (A-Z).")
                return
            
            # Update settings
            self.config_manager.settings.google_sheet_url = url
            self.config_manager.settings.google_sheet_name = sheet_name
            self.config_manager.settings.google_sheet_tracking_column = tracking_col
            self.config_manager.settings.google_sheet_tracking_row = tracking_row
            self.config_manager.settings.google_sheet_sku_column = sku_col
            self.config_manager.settings.google_sheet_sku_row = sku_row
            
            # Save settings
            try:
                # Convert settings to dictionary
                settings_dict = asdict(self.config_manager.settings)
                
                # Save to file
                with open(self.config_manager.settings_file, 'w') as f:
                    json.dump(settings_dict, f, indent=4)
                
                # Test connection before closing
                try:
                    # Check for credentials file
                    creds_file = get_credentials_file_path()
                    if not file_exists(creds_file):
                        self.config_manager.settings.google_sheets_connection_status = "Not Connected"
                        
                        # Save settings again with updated connection status
                        settings_dict = asdict(self.config_manager.settings)
                        with open(self.config_manager.settings_file, 'w') as f:
                            json.dump(settings_dict, f, indent=4)
                            
                        # Call the update callback if it exists
                        if self.update_callback:
                            self.update_callback()
                            
                        messagebox.showinfo("Settings Saved", "Settings saved successfully, but credentials file not found.\n\nPlease create a service account and download the credentials file.")
                        self.destroy()
                        return
                    
                    # Test connection
                    success, message = test_sheet_connection(result, sheet_name)
                    
                    if success:
                        self.connection_status = "Connected"
                        self.config_manager.settings.google_sheets_connection_status = "Connected"
                        
                        # Save settings again with updated connection status
                        settings_dict = asdict(self.config_manager.settings)
                        with open(self.config_manager.settings_file, 'w') as f:
                            json.dump(settings_dict, f, indent=4)
                            
                        self._update_status()
                        
                        # Call the update callback if it exists
                        if self.update_callback:
                            self.update_callback()
                            
                        messagebox.showinfo("Success", "Settings saved and connected to Google Sheet successfully!")
                        self.destroy()
                    else:
                        self.connection_status = "Settings Saved, Connection Failed"
                        self.config_manager.settings.google_sheets_connection_status = "Connection Failed"
                        
                        # Save settings again with updated connection status
                        settings_dict = asdict(self.config_manager.settings)
                        with open(self.config_manager.settings_file, 'w') as f:
                            json.dump(settings_dict, f, indent=4)
                            
                        self._update_status()
                        
                        # Call the update callback if it exists
                        if self.update_callback:
                            self.update_callback()
                            
                        messagebox.showwarning("Warning", f"Settings saved but connection failed: {message}")
                        self.destroy()
                        
                except Exception as e:
                    self.connection_status = "Settings Saved, Connection Error"
                    self.config_manager.settings.google_sheets_connection_status = "Connection Error"
                    
                    # Save settings again with updated connection status
                    settings_dict = asdict(self.config_manager.settings)
                    with open(self.config_manager.settings_file, 'w') as f:
                        json.dump(settings_dict, f, indent=4)
                        
                    self._update_status()
                    
                    # Call the update callback if it exists
                    if self.update_callback:
                        self.update_callback()
                        
                    messagebox.showwarning("Warning", f"Settings saved but error testing connection: {str(e)}")
                    self.destroy()
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
                
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
    
    def center_window(self):
        """Center the window on the screen"""
        center_window(self)
