import tkinter as tk
from tkinter import ttk, messagebox
import re
import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.config.config_manager import ConfigManager

class GoogleSheetsDialog(tk.Toplevel):
    """Dialog for configuring Google Sheets integration"""
    
    def __init__(self, parent):
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
        self.config_manager = ConfigManager()
        
        # Initialize connection status
        self.connection_status = "Not Connected"
        
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
        refresh_button = tk.Button(
            sheet_selection_frame,
            text="⟳",
            font=("Arial", 10),
            bg='#2196F3',
            fg='white',
            activebackground='#1976D2',
            activeforeground='white',
            relief=tk.FLAT,
            padx=8,
            pady=2,
            command=self._fetch_sheet_names
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
        
        # Test Connection Button
        test_button = tk.Button(
            button_frame, 
            text="Test Connection", 
            font=("Arial", 10), 
            bg='#2196F3', 
            fg='white',
            activebackground='#1976D2',
            activeforeground='white',
            relief=tk.FLAT,
            padx=20,  # Increased horizontal padding
            pady=10,  # Increased vertical padding
            command=self._test_connection
        )
        test_button.pack(side='left', padx=(10, 0))  # Added left padding
        
        # Save Button
        save_button = tk.Button(
            button_frame, 
            text="Save & Connect", 
            font=("Arial", 10, "bold"), 
            bg='#4CAF50', 
            fg='white',
            activebackground='#45a049',
            activeforeground='white',
            relief=tk.FLAT,
            padx=25,  # Increased horizontal padding
            pady=10,  # Increased vertical padding
            command=self._save_settings
        )
        save_button.pack(side='right', padx=(15, 10))  # Added right padding
        
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
            padx=20,  # Increased horizontal padding
            pady=10,  # Increased vertical padding
            command=self.destroy
        )
        cancel_button.pack(side='right', padx=(0, 10))  # Added right padding
        
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
            # Get the URL and sheet name
            url = self.url_var.get().strip()
            sheet_name = self.sheet_var.get().strip()
            
            # Validate URL
            if not url:
                messagebox.showerror("Error", "Please enter a Google Sheet URL")
                return
            
            # Check if URL is valid
            sheet_id_pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)'
            match = re.match(sheet_id_pattern, url)
            if not match:
                messagebox.showerror("Error", "Invalid Google Sheet URL format.\n\nURL should be in the format:\nhttps://docs.google.com/spreadsheets/d/YOUR_SHEET_ID")
                return
            
            # Validate sheet name
            if not sheet_name:
                messagebox.showerror("Error", "Please enter a sheet name")
                return
            
            # Here we would normally test the actual connection
            # For now, we'll simulate a successful connection
            # In a real implementation, you would use gspread to connect to the sheet
            
            # Import required libraries
            try:
                import gspread
                from oauth2client.service_account import ServiceAccountCredentials
            except ImportError:
                messagebox.showerror("Error", "Required libraries not installed.\n\nPlease install gspread and oauth2client:\npip install gspread oauth2client")
                return
            
            # Check for credentials file
            creds_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'credentials.json')
            if not os.path.exists(creds_file):
                messagebox.showerror("Error", f"Credentials file not found at:\n{creds_file}\n\nPlease create a service account and download the credentials file.")
                return
            
            # Attempt to connect
            try:
                # Define the scope
                scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                
                # Add credentials to the account
                creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
                
                # Authorize the clientsheet
                client = gspread.authorize(creds)
                
                # Get the sheet
                sheet_id = match.group(1)
                spreadsheet = client.open_by_key(sheet_id)
                
                # Try to access the specified worksheet
                try:
                    worksheet = spreadsheet.worksheet(sheet_name)
                    
                    # If we get here, the connection was successful
                    self.connection_status = "Connected"
                    self._update_status()
                    messagebox.showinfo("Success", f"Successfully connected to sheet '{sheet_name}'")
                    
                except gspread.exceptions.WorksheetNotFound:
                    # Sheet not found, show available sheets
                    all_sheets = [sheet.title for sheet in spreadsheet.worksheets()]
                    sheet_list = "\n".join(all_sheets)
                    
                    # Update the dropdown with the available sheet names
                    self.sheet_dropdown['values'] = all_sheets
                    
                    self.connection_status = "Sheet Not Found"
                    self._update_status()
                    messagebox.showerror("Error", f"Sheet '{sheet_name}' not found.\n\nAvailable sheets:\n{sheet_list}")
                
            except Exception as e:
                self.connection_status = "Connection Failed"
                self._update_status()
                messagebox.showerror("Connection Error", f"Failed to connect to Google Sheet:\n\n{str(e)}")
        
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
            if not url:
                messagebox.showerror("Error", "Please enter a Google Sheet URL")
                return
            
            # Check if URL is valid
            sheet_id_pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)'
            match = re.match(sheet_id_pattern, url)
            if not match:
                messagebox.showerror("Error", "Invalid Google Sheet URL format.\n\nURL should be in the format:\nhttps://docs.google.com/spreadsheets/d/YOUR_SHEET_ID")
                return
            
            # Import required libraries
            try:
                import gspread
                from oauth2client.service_account import ServiceAccountCredentials
            except ImportError:
                messagebox.showerror("Error", "Required libraries not installed.\n\nPlease install gspread and oauth2client:\npip install gspread oauth2client")
                return
            
            # Check for credentials file
            creds_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'credentials.json')
            if not os.path.exists(creds_file):
                messagebox.showerror("Error", f"Credentials file not found at:\n{creds_file}\n\nPlease create a service account and download the credentials file.")
                return
            
            # Attempt to connect
            try:
                # Define the scope
                scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                
                # Add credentials to the account
                creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
                
                # Authorize the clientsheet
                client = gspread.authorize(creds)
                
                # Get the sheet
                sheet_id = match.group(1)
                spreadsheet = client.open_by_key(sheet_id)
                
                # Get the available sheet names
                sheet_names = [sheet.title for sheet in spreadsheet.worksheets()]
                
                # Update the dropdown with the available sheet names
                self.sheet_dropdown['values'] = sheet_names
                
                # Select the first sheet by default
                self.sheet_var.set(sheet_names[0] if sheet_names else "")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch sheet names:\n\n{str(e)}")
        
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
                
            if url and not re.match(r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)', url):
                messagebox.showerror("Error", "Invalid Google Sheet URL format.\n\nURL should be in the format:\nhttps://docs.google.com/spreadsheets/d/YOUR_SHEET_ID")
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
            if self.config_manager.save_settings():
                # Test connection before closing
                try:
                    # Import required libraries
                    try:
                        import gspread
                        from oauth2client.service_account import ServiceAccountCredentials
                    except ImportError:
                        messagebox.showinfo("Settings Saved", "Settings saved successfully, but required libraries not installed.\n\nPlease install gspread and oauth2client to connect to Google Sheets.")
                        self.destroy()
                        return
                    
                    # Check for credentials file
                    creds_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'credentials.json')
                    if not os.path.exists(creds_file):
                        messagebox.showinfo("Settings Saved", "Settings saved successfully, but credentials file not found.\n\nPlease create a service account and download the credentials file.")
                        self.destroy()
                        return
                    
                    # Check if URL is valid
                    sheet_id_pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)'
                    match = re.match(sheet_id_pattern, url)
                    if not match:
                        messagebox.showinfo("Settings Saved", "Settings saved successfully, but the URL format is invalid.")
                        self.destroy()
                        return
                        
                    # Define the scope
                    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                    
                    # Add credentials to the account
                    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
                    
                    # Authorize the clientsheet
                    client = gspread.authorize(creds)
                    
                    # Get the sheet
                    sheet_id = match.group(1)
                    spreadsheet = client.open_by_key(sheet_id)
                    
                    # Try to access the specified worksheet
                    try:
                        worksheet = spreadsheet.worksheet(sheet_name)
                        
                        # If we get here, the connection was successful
                        self.connection_status = "Connected"
                        self._update_status()
                        messagebox.showinfo("Success", f"Settings saved and successfully connected to sheet '{sheet_name}'")
                        self.destroy()
                        
                    except gspread.exceptions.WorksheetNotFound:
                        # Sheet not found, show available sheets
                        all_sheets = [sheet.title for sheet in spreadsheet.worksheets()]
                        sheet_list = "\n".join(all_sheets)
                        
                        # Update the dropdown with the available sheet names
                        self.sheet_dropdown['values'] = all_sheets
                        
                        self.connection_status = "Sheet Not Found"
                        self._update_status()
                        messagebox.showerror("Error", f"Settings saved, but sheet '{sheet_name}' not found.\n\nAvailable sheets:\n{sheet_list}")
                    
                except Exception as e:
                    # Connection failed but settings were saved
                    messagebox.showinfo("Settings Saved", f"Settings saved successfully, but could not connect to Google Sheet.\n\nError: {str(e)}")
                    self.destroy()
            else:
                messagebox.showerror("Error", "Failed to save settings")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving settings:\n\n{str(e)}")
    
    def center_window(self):
        """Center the window on the screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
