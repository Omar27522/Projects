import tkinter as tk
from tkinter import ttk, messagebox
import re
import os
import sys

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
        # Create a main frame
        main_frame = tk.Frame(self, bg='white')
        main_frame.pack(fill='both', expand=True)
        
        # Create a canvas with scrollbar
        canvas = tk.Canvas(main_frame, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        
        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Create a frame inside the canvas for the content
        content_frame = tk.Frame(canvas, bg='white', padx=30, pady=30)
        
        # Add the content frame to the canvas
        canvas_frame = canvas.create_window((0, 0), window=content_frame, anchor='nw')
        
        # Configure canvas to resize with window
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Update the width of the canvas window
            canvas.itemconfig(canvas_frame, width=event.width)
        
        # Bind events
        canvas.bind('<Configure>', configure_canvas)
        content_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Title
        title_label = tk.Label(
            content_frame, 
            text="Google Sheets Configuration", 
            font=("Arial", 14, "bold"), 
            bg='white'
        )
        title_label.pack(pady=(0, 20))
        
        # Google Sheet URL
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
            font=("Arial", 10)
        )
        refresh_button.pack(side='left', padx=(5, 0))
        
        # Column and Row Configuration
        config_frame = tk.LabelFrame(content_frame, text="Data Configuration", font=("Arial", 10, "bold"), bg='white', padx=10, pady=10)
        config_frame.pack(fill='x', pady=(10, 10))
        
        # Tracking Number Column
        tracking_col_label = tk.Label(
            config_frame, 
            text="Tracking Number Column:", 
            font=("Arial", 10), 
            bg='white'
        )
        tracking_col_label.grid(row=0, column=0, sticky='w', pady=(10, 5))
        
        self.tracking_col_var = tk.StringVar(value=self.config_manager.settings.google_sheet_tracking_column or "D")
        tracking_col_entry = tk.Entry(
            config_frame, 
            textvariable=self.tracking_col_var, 
            font=("Arial", 10), 
            width=5
        )
        tracking_col_entry.grid(row=0, column=1, sticky='w', pady=(10, 5))
        
        # Tracking Number Row
        tracking_row_label = tk.Label(
            config_frame, 
            text="Tracking Number Row:", 
            font=("Arial", 10), 
            bg='white'
        )
        tracking_row_label.grid(row=1, column=0, sticky='w', pady=(0, 5))
        
        self.tracking_row_var = tk.StringVar(value=str(self.config_manager.settings.google_sheet_tracking_row or 3))
        tracking_row_entry = tk.Entry(
            config_frame, 
            textvariable=self.tracking_row_var, 
            font=("Arial", 10), 
            width=5
        )
        tracking_row_entry.grid(row=1, column=1, sticky='w', pady=(0, 5))
        
        # SKU Column
        sku_col_label = tk.Label(
            config_frame, 
            text="SKU Column:", 
            font=("Arial", 10), 
            bg='white'
        )
        sku_col_label.grid(row=2, column=0, sticky='w', pady=(10, 5))
        
        self.sku_col_var = tk.StringVar(value=self.config_manager.settings.google_sheet_sku_column or "F")
        sku_col_entry = tk.Entry(
            config_frame, 
            textvariable=self.sku_col_var, 
            font=("Arial", 10), 
            width=5
        )
        sku_col_entry.grid(row=2, column=1, sticky='w', pady=(10, 5))
        
        # SKU Row
        sku_row_label = tk.Label(
            config_frame, 
            text="SKU Row:", 
            font=("Arial", 10), 
            bg='white'
        )
        sku_row_label.grid(row=3, column=0, sticky='w', pady=(0, 5))
        
        self.sku_row_var = tk.StringVar(value=str(self.config_manager.settings.google_sheet_sku_row or 3))
        sku_row_entry = tk.Entry(
            config_frame, 
            textvariable=self.sku_row_var, 
            font=("Arial", 10), 
            width=5
        )
        sku_row_entry.grid(row=3, column=1, sticky='w', pady=(0, 5))
        
        # Connection Status
        status_frame = tk.Frame(content_frame, bg='white')
        status_frame.pack(fill='x', pady=(10, 10))
        
        status_label = tk.Label(
            status_frame, 
            text="Connection Status:", 
            font=("Arial", 10), 
            bg='white'
        )
        status_label.pack(side='left')
        
        self.status_label = tk.Label(
            status_frame, 
            text=self.connection_status, 
            font=("Arial", 10, "bold"), 
            fg='red' if self.connection_status != "Connected" else 'green',
            bg='white'
        )
        self.status_label.pack(side='left', padx=(5, 0))
        
        # Add instruction label above buttons
        instruction_label = tk.Label(
            content_frame,
            text="Click 'Test Connection' to verify settings, then 'Save & Connect' to apply changes",
            font=("Arial", 9, "italic"),
            bg='white',
            fg='#555555'
        )
        instruction_label.pack(fill='x', pady=(5, 10))
        
        # Add a separator line above the button frame
        separator = ttk.Separator(content_frame, orient='horizontal')
        separator.pack(fill='x', pady=(20, 25))
        
        # Button Frame
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill='x', pady=(0, 0), padx=20)  # Added horizontal padding
        
        # Fetch Sheets Button
        fetch_button = create_button(
            button_frame,
            text="Fetch Sheets",
            command=self._fetch_sheet_names,
            bg='#2196F3',
            padx=20,
            pady=10
        )
        fetch_button.pack(side='left', padx=(10, 5))
        
        # Test Connection Button
        test_button = create_button(
            button_frame,
            text="Test Connection",
            command=self._test_connection,
            bg='#FF9800',
            padx=20,
            pady=10
        )
        test_button.pack(side='left', padx=5)
        
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
    
    def _test_connection(self):
        """Test the connection to the Google Sheet"""
        try:
            # Get values from UI
            url = self.url_var.get().strip()
            sheet_name = self.sheet_var.get().strip()
            
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
                self.connection_status = "Invalid URL"
                self._update_status()
                return
            
            sheet_id = result
            
            # Import required libraries
            try:
                import gspread
                from oauth2client.service_account import ServiceAccountCredentials
            except ImportError:
                messagebox.showerror("Error", "Required libraries not installed.\n\nPlease install gspread and oauth2client:\npip install gspread oauth2client")
                self.connection_status = "Libraries Missing"
                self._update_status()
                return
            
            # Test connection
            from src.utils.sheets_utils import test_sheet_connection
            success, message = test_sheet_connection(sheet_id, sheet_name)
            
            if success:
                self.connection_status = "Connected"
                self._update_status()
                messagebox.showinfo("Success", "Successfully connected to Google Sheet!")
            else:
                self.connection_status = "Connection Failed"
                self._update_status()
                messagebox.showerror("Error", message)
        
        except Exception as e:
            self.connection_status = "Error"
            self._update_status()
            messagebox.showerror("Error", f"An unexpected error occurred:\n\n{str(e)}")
    
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
        """Save the settings to the config file"""
        try:
            # Get values from UI
            url = self.url_var.get().strip()
            sheet_name = self.sheet_var.get().strip()
            tracking_col = self.tracking_col_var.get().strip().upper()
            tracking_row = int(self.tracking_row_var.get())
            sku_col = self.sku_col_var.get().strip().upper()
            sku_row = int(self.sku_row_var.get())
            
            # Validate inputs
            if not url:
                messagebox.showerror("Error", "Please enter a Google Sheet URL")
                return
                
            if not sheet_name:
                messagebox.showerror("Error", "Please select a sheet name")
                return
                
            # Validate URL format
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
            if save_config(self.config_manager.settings):
                # Test connection before closing
                try:
                    # Check for credentials file
                    creds_file = get_credentials_file_path()
                    if not file_exists(creds_file):
                        self.config_manager.settings.google_sheets_connection_status = "Not Connected"
                        self.config_manager.save_settings()
                        messagebox.showinfo("Settings Saved", "Settings saved successfully, but credentials file not found.\n\nPlease create a service account and download the credentials file.")
                        # Call the update callback if it exists
                        if self.update_callback:
                            self.update_callback()
                        self.destroy()
                        return
                    
                    # Test connection
                    success, message = test_sheet_connection(result, sheet_name)
                    
                    if success:
                        self.connection_status = "Connected"
                        self.config_manager.settings.google_sheets_connection_status = "Connected"
                        self.config_manager.save_settings()
                        self._update_status()
                        messagebox.showinfo("Success", "Settings saved and connected to Google Sheet successfully!")
                        # Call the update callback if it exists
                        if self.update_callback:
                            self.update_callback()
                        self.destroy()
                    else:
                        self.connection_status = "Settings Saved, Connection Failed"
                        self.config_manager.settings.google_sheets_connection_status = "Connection Failed"
                        self.config_manager.save_settings()
                        self._update_status()
                        messagebox.showinfo("Settings Saved", f"Settings saved successfully, but could not connect to Google Sheet.\n\nError: {message}")
                        # Call the update callback if it exists
                        if self.update_callback:
                            self.update_callback()
                        self.destroy()
                        
                except ImportError:
                    self.config_manager.settings.google_sheets_connection_status = "Not Connected"
                    self.config_manager.save_settings()
                    messagebox.showinfo("Settings Saved", "Settings saved successfully, but required libraries not installed.\n\nPlease install gspread and oauth2client to connect to Google Sheets.")
                    # Call the update callback if it exists
                    if self.update_callback:
                        self.update_callback()
                    self.destroy()
                except Exception as e:
                    self.config_manager.settings.google_sheets_connection_status = "Connection Failed"
                    self.config_manager.save_settings()
                    messagebox.showinfo("Settings Saved", f"Settings saved successfully, but an error occurred while testing the connection:\n\n{str(e)}")
                    # Call the update callback if it exists
                    if self.update_callback:
                        self.update_callback()
                    self.destroy()
            else:
                messagebox.showerror("Error", "Failed to save settings.")
        except ValueError:
            messagebox.showerror("Error", "Invalid row number. Please enter a valid integer.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n\n{str(e)}")
    
    def center_window(self):
        """Center the window on the screen"""
        center_window(self)
