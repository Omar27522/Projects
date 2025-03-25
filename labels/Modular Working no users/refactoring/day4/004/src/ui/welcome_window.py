import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import utility modules
from src.config.config_manager import ConfigManager
from src.utils.file_utils import directory_exists, count_files_in_directory, get_project_root, file_exists
from src.utils.ui_utils import center_window
from src.utils.ui_components import (
    create_title_section, create_colored_button, create_button_grid, 
    create_version_label, create_form_field_group, create_status_bar, 
    create_sheets_status_display
)
from src.utils.barcode_operations import find_or_create_barcode, print_barcode, process_barcode
from src.utils.sheets_operations import write_to_google_sheet, create_google_sheets_dialog
from src.utils.returns_operations import load_returns_data, update_log_file, create_returns_dialog, create_edit_dialog
from src.utils.settings_operations import create_settings_dialog, update_sheets_status_display
from src.utils.dialog_handlers import (
    create_label_dialog, create_labels_dialog, 
    create_settings_dialog_handler, create_google_sheets_dialog_handler
)

# Third-party imports
import pyautogui
import barcode
from barcode.writer import ImageWriter
from PIL import Image
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import logging
import subprocess
import time

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
        try:
            # Check if labels directory is set and exists
            if not self.config_manager.settings.last_directory or not directory_exists(self.config_manager.settings.last_directory):
                messagebox.showinfo("Labels Required", 
                    "Please select a Labels directory before creating labels.\n\n"
                    "Click the 'Settings' button to set your Labels directory.")
                return
            
            # Get the path to the dialog launcher script
            project_root = get_project_root()
            launcher_script = os.path.join(project_root, 'launch_dialog.py')
            
            # Create the launcher script if it doesn't exist
            if not file_exists(launcher_script):
                with open(launcher_script, 'w') as f:
                    f.write("""
import os
import sys
import tkinter as tk
from PIL import Image, ImageTk
import ctypes

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Set DPI awareness before creating any windows
try:
    awareness = ctypes.c_int(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    ctypes.windll.shcore.SetProcessDpiAwareness(awareness)
except AttributeError:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception as e:
    print(f"Failed to set DPI awareness: {e}")

def set_taskbar_icon(dialog, icon_name):
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "assets", icon_name)
        
        if os.path.exists(icon_path):
            # Load and set the icon using PhotoImage for the window icon
            icon = tk.PhotoImage(file=icon_path)
            dialog.iconphoto(True, icon)
            
            # Keep reference to prevent garbage collection
            dialog._icon = icon
            
            # Set unique AppUserModelID for Windows taskbar
            app_id = f'LabelMaker.{icon_name.split("_")[0]}'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        else:
            print(f"Icon file not found at {icon_path}")
    except Exception as e:
        print(f"Failed to set taskbar icon: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python launch_dialog.py <dialog_type>")
        sys.exit(1)
        
    dialog_type = sys.argv[1]
    
    if dialog_type == "create_label":
        from src.utils.dialog_handlers import create_label_dialog
        from src.config.config_manager import ConfigManager
        
        # Create a dummy root window to avoid errors
        root = tk.Tk()
        root.withdraw()
        
        # Set the taskbar icon
        set_taskbar_icon(root, "createlabels_64.png")
        
        # Create the dialog
        config_manager = ConfigManager()
        dialog = create_label_dialog(root, config_manager, lambda: None)
        
        # Run the dialog
        root.mainloop()
        
    elif dialog_type == "returns_data":
        from src.utils.dialog_handlers import create_labels_dialog
        from src.config.config_manager import ConfigManager
        
        # Create a dummy root window to avoid errors
        root = tk.Tk()
        root.withdraw()
        
        # Set the taskbar icon
        set_taskbar_icon(root, "returnsdata_64.png")
        
        # Create the dialog
        dialog, _ = create_labels_dialog(root)
        
        # Run the dialog
        root.mainloop()
        
    elif dialog_type == "settings":
        from src.utils.dialog_handlers import create_settings_dialog_handler
        from src.config.config_manager import ConfigManager
        
        # Create a dummy root window to avoid errors
        root = tk.Tk()
        root.withdraw()
        
        # Set the taskbar icon
        set_taskbar_icon(root, "settings_64.png")
        
        # Create the dialog
        config_manager = ConfigManager()
        dialog = create_settings_dialog_handler(root, config_manager, lambda dir=None: None)
        
        # Run the dialog
        root.mainloop()
    elif dialog_type == "google_sheets":
        from src.utils.dialog_handlers import create_google_sheets_dialog_handler
        from src.config.config_manager import ConfigManager
        
        # Create a dummy root window to avoid errors
        root = tk.Tk()
        root.withdraw()
        
        # Set the taskbar icon
        set_taskbar_icon(root, "settings_64.png")
        
        # Create the dialog
        config_manager = ConfigManager()
        dialog = create_google_sheets_dialog_handler(root, config_manager, None)
        
        # Run the dialog
        root.mainloop()
    else:
        print(f"Unknown dialog type: {dialog_type}")
        sys.exit(1)
""")
            
            # Run the launcher script with the create_label argument
            subprocess.Popen([sys.executable, launcher_script, "create_label"])
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Create Label dialog: {str(e)}")

    def user_action(self):
        """Handler for User button click"""
        # Call the create_label_action method to open the Create Label dialog
        self.create_label_action()

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
                else:
                    # Process still running, check again after 1 second
                    self.after(1000, check_process)
            
            # Start checking the process
            self.after(1000, check_process)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Label Maker: {str(e)}")
            self.deiconify()  # Show welcome window again

    def labels_action(self):
        """Handler for Labels button click - Display and edit returns data"""
        try:
            # Get the path to the dialog launcher script
            project_root = get_project_root()
            launcher_script = os.path.join(project_root, 'launch_dialog.py')
            
            # Run the launcher script with the returns_data argument
            subprocess.Popen([sys.executable, launcher_script, "returns_data"])
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Returns Data dialog: {str(e)}")

    def settings_action(self):
        """Open settings dialog"""
        try:
            # Get the path to the dialog launcher script
            project_root = get_project_root()
            launcher_script = os.path.join(project_root, 'launch_dialog.py')
            
            # Run the launcher script with the settings argument
            subprocess.Popen([sys.executable, launcher_script, "settings"])
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Settings dialog: {str(e)}")
    
    def open_sheets_dialog(self):
        """Open the Google Sheets configuration dialog"""
        try:
            # Get the path to the dialog launcher script
            project_root = get_project_root()
            launcher_script = os.path.join(project_root, 'launch_dialog.py')
            
            # Update the launcher script to include Google Sheets dialog
            with open(launcher_script, 'r') as f:
                content = f.read()
            
            if "google_sheets" not in content:
                # Add Google Sheets dialog handling to the launcher script
                with open(launcher_script, 'w') as f:
                    # Find the position to insert the new code
                    insert_pos = content.find("else:")
                    if insert_pos != -1:
                        new_content = content[:insert_pos] + """    elif dialog_type == "google_sheets":
        from src.utils.dialog_handlers import create_google_sheets_dialog_handler
        from src.config.config_manager import ConfigManager
        
        # Create a dummy root window to avoid errors
        root = tk.Tk()
        root.withdraw()
        
        # Set the taskbar icon
        set_taskbar_icon(root, "settings_64.png")
        
        # Create the dialog
        config_manager = ConfigManager()
        dialog = create_google_sheets_dialog_handler(root, config_manager, None)
        
        # Run the dialog
        root.mainloop()
        
""" + content[insert_pos:]
                        f.write(new_content)
            
            # Run the launcher script with the google_sheets argument
            subprocess.Popen([sys.executable, launcher_script, "google_sheets"])
            
            # Reload config manager after a delay to get updated settings
            def reload_config():
                self.config_manager = ConfigManager()
                self._update_sheets_status_display()
            
            # Schedule the config reload after a few seconds
            self.after(5000, reload_config)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Google Sheets dialog: {str(e)}")
    
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

    def _update_sheets_status_display(self):
        """Update the Google Sheets status display in the welcome window"""
        if hasattr(self, 'sheets_status_label'):
            # Reload config manager to get the latest settings
            self.config_manager = ConfigManager()
            
            # Get Google Sheets configuration
            sheets_config = self.config_manager.settings
            
            # Default status
            status_text = "Not Connected"
            status_color = "red"
            on_click = None
            
            # Check if Google Sheets is configured and connected
            if (hasattr(sheets_config, 'google_sheets_connection_status') and 
                sheets_config.google_sheets_connection_status == "Connected"):
                
                status_text = "Connected"
                status_color = "green"
            # Fallback to checking if configuration exists
            elif (hasattr(sheets_config, 'google_sheet_url') and 
                sheets_config.google_sheet_url and 
                hasattr(sheets_config, 'google_sheet_name') and 
                sheets_config.google_sheet_name):
                
                status_text = "Configured (Not Tested)"
                status_color = "orange"
                on_click = self.test_sheets_connection
            
            # Update the status label
            self.sheets_status_label.config(text=status_text, fg=status_color, font=("Arial", 8))
            
            # Make the label clickable if it's the orange "Configured (Not Tested)" status
            if status_text == "Configured (Not Tested)" and on_click:
                self.sheets_status_label.bind("<Button-1>", lambda e: on_click())
                self.sheets_status_label.bind("<Enter>", lambda e: self.sheets_status_label.config(cursor="hand2", font=("Arial", 8, "underline")))
                self.sheets_status_label.bind("<Leave>", lambda e: self.sheets_status_label.config(cursor="", font=("Arial", 8)))
    
    def test_sheets_connection(self):
        """Test the connection to Google Sheets without opening the full dialog"""
        from src.utils.sheets_utils import validate_sheet_url, test_sheet_connection
        from src.utils.file_utils import get_credentials_file_path, file_exists
        from tkinter import messagebox
        
        try:
            # Get Google Sheets configuration
            sheets_config = self.config_manager.settings
            
            # Check if Google Sheets is configured
            if not (sheets_config.google_sheet_url and sheets_config.google_sheet_name):
                messagebox.showerror("Error", "Google Sheets is not fully configured. Please open the settings to configure it.")
                return
            
            # Check for credentials file
            creds_file = get_credentials_file_path()
            if not file_exists(creds_file):
                messagebox.showerror("Error", f"Credentials file not found at:\n{creds_file}\n\nPlease create a service account and download the credentials file.")
                return
            
            # Validate the sheet URL
            is_valid, result = validate_sheet_url(sheets_config.google_sheet_url)
            if not is_valid:
                messagebox.showerror("Error", result)
                return
            
            # Test connection
            success, message = test_sheet_connection(result, sheets_config.google_sheet_name)
            
            if success:
                # Update connection status
                self.config_manager.settings.google_sheets_connection_status = "Connected"
                self.config_manager.save_settings()
                
                # Update the display
                self._update_sheets_status_display()
                
                messagebox.showinfo("Success", "Connected to Google Sheet successfully!")
            else:
                # Update connection status
                self.config_manager.settings.google_sheets_connection_status = "Connection Failed"
                self.config_manager.save_settings()
                
                # Update the display
                self._update_sheets_status_display()
                
                messagebox.showerror("Error", f"Could not connect to Google Sheet.\n\nError: {message}")
                
        except ImportError:
            messagebox.showerror("Error", "Required libraries not installed. Please install gspread and oauth2client to connect to Google Sheets.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n\n{str(e)}")
