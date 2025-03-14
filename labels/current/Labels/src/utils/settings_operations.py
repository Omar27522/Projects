"""
Utility functions for handling settings operations.
"""
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from src.config.config_manager import ConfigManager
from src.utils.ui_utils import center_window, create_button, make_window_modal

def create_settings_dialog(parent, config_manager, update_label_count_callback, open_sheets_dialog_callback, save_settings_callback):
    """
    Create a dialog for viewing and editing application settings.
    
    Args:
        parent: The parent window
        config_manager: The configuration manager
        update_label_count_callback: Callback for updating the label count
        open_sheets_dialog_callback: Callback for opening the Google Sheets dialog
        save_settings_callback: Callback for saving the settings
        
    Returns:
        tuple: (dialog, directory_var) - The dialog window and the directory variable
    """
    # Create settings dialog
    settings_dialog = tk.Toplevel(parent)
    settings_dialog.title("Settings")
    settings_dialog.geometry("500x400")
    settings_dialog.resizable(False, False)
    settings_dialog.configure(bg='white')
    # Remove transient and grab_set to allow separate taskbar icon
    # settings_dialog.transient(parent)  # Make dialog modal
    # settings_dialog.grab_set()  # Make dialog modal
    
    # Center the dialog
    center_window(settings_dialog)
    
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
    directory_var = tk.StringVar(value=config_manager.settings.last_directory or "")
    directory_entry = tk.Entry(directory_section, textvariable=directory_var, font=("Arial", 10), width=50)
    directory_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
    
    # Browse button
    browse_button = create_button(
        directory_section,
        text="Browse",
        command=lambda: [
            directory_var.set(filedialog.askdirectory(
                initialdir=directory_var.get() or os.path.expanduser("~"),
                title="Select Labels Directory"
            )),
            update_label_count_callback(directory_var.get())
        ],
        bg='#2196F3',
        padx=10,
        pady=5
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
    
    label_count_var = tk.StringVar(value="0")
    label_count = tk.Label(
        count_frame, 
        textvariable=label_count_var, 
        font=("Arial", 10, "bold"), 
        bg='white'
    )
    label_count.pack(side='left', padx=(5, 0))
    
    # Update label count
    update_label_count_callback(directory_var.get())
    
    # Google Sheets Section
    sheets_section = tk.LabelFrame(content_frame, text="Google Sheets Integration", font=("Arial", 12, "bold"), bg='white', padx=10, pady=10)
    sheets_section.pack(fill='x', pady=(0, 15))

    # Connection status
    status_text = "Not Connected"
    status_color = 'red'

    # Check if Google Sheets is configured
    if (config_manager.settings.google_sheet_url and 
        config_manager.settings.google_sheet_name):
        status_text = "Connected"
        status_color = 'green'

    status_frame = tk.Frame(sheets_section, bg='white')
    status_frame.pack(fill='x', pady=(5, 5))

    tk.Label(status_frame, text="Status:", font=("Arial", 10), bg='white').pack(side='left')
    sheets_status_label = tk.Label(
        status_frame,
        text=status_text,
        font=("Arial", 10, "bold"),
        fg=status_color,
        bg='white'
    )
    sheets_status_label.pack(side='left', padx=(5, 0))
    
    # Add sheet info if connected
    if status_text == "Connected":
        sheet_info = f"{config_manager.settings.google_sheet_name}"
        tk.Label(status_frame, text=" | Sheet:", font=("Arial", 10), bg='white').pack(side='left', padx=(10, 0))
        tk.Label(status_frame, text=sheet_info, font=("Arial", 10, "italic"), bg='white').pack(side='left', padx=(5, 0))
    
    # Configure button
    configure_button = create_button(
        sheets_section,
        text="Configure Google Sheets",
        command=open_sheets_dialog_callback,
        bg='#2196F3',
        padx=10,
        pady=5
    )
    configure_button.pack(pady=(5, 5))
    
    # Button Frame
    button_frame = tk.Frame(content_frame, bg='white')
    button_frame.pack(fill='x', pady=(10, 0))
    
    # Save Button
    save_button = create_button(
        button_frame,
        text="Save",
        command=lambda: save_settings_callback(settings_dialog, directory_var.get()),
        bg='#4CAF50',
        padx=15,
        pady=5
    )
    save_button.pack(side='right', padx=(10, 0))
    
    # Cancel Button
    cancel_button = create_button(
        button_frame,
        text="Cancel",
        command=settings_dialog.destroy,
        bg='#f44336',
        padx=15,
        pady=5
    )
    cancel_button.pack(side='right')
    
    return settings_dialog, directory_var, label_count_var

def update_sheets_status_display(parent, config_manager, sheets_status_label):
    """
    Update the Google Sheets status display in the welcome window.
    
    Args:
        parent: The parent window
        config_manager: The configuration manager
        sheets_status_label: The label to update
        
    Returns:
        None
    """
    # Update the Google Sheets status display
    status_text = "Not Connected"
    status_color = 'red'
    
    # Check if Google Sheets is configured
    if (config_manager.settings.google_sheet_url and 
        config_manager.settings.google_sheet_name):
        
        # Check if credentials file exists
        credentials_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'credentials.json')
        if os.path.exists(credentials_path):
            status_text = "Connected"
            status_color = 'green'
        else:
            status_text = "Missing Credentials"
            status_color = 'orange'
    
    # Update the status label
    sheets_status_label.config(text=status_text, fg=status_color)
    
    return status_text, status_color
