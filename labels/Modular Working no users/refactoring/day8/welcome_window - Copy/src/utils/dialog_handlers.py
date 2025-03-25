"""
Dialog handling utilities for the Label Maker application.
Contains functions for creating and managing various dialogs.
"""

import tkinter as tk
from tkinter import messagebox
import os
import datetime
import sys
import ctypes
from PIL import Image, ImageTk

# Import utility functions
from src.utils.file_utils import file_exists, get_credentials_file_path, directory_exists
from src.utils.ui_components import create_title_section, create_colored_button, create_form_field_group, create_status_bar
from src.utils.barcode_operations import process_barcode
from src.utils.sheets_operations import write_to_google_sheet, create_google_sheets_dialog
from src.utils.ui_utils import center_window
from src.utils.returns_operations import load_returns_data, update_log_file, create_returns_dialog, create_edit_dialog
from src.utils.settings_operations import create_settings_dialog
from src.config.config_manager import ConfigManager

def set_taskbar_icon(dialog, icon_name):
    """
    Set the window icon for a dialog without changing the taskbar icon
    
    Args:
        dialog: Dialog to set icon for
        icon_name: Name of the icon file (without path)
    """
    try:
        # Get the directory where the script is located
        if getattr(sys, 'frozen', False):
            script_dir = os.path.dirname(sys.executable)
        else:
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Path to the icon file
        icon_path = os.path.join(script_dir, "assets", icon_name)
        
        if os.path.exists(icon_path):
            # Load and set the icon using PhotoImage for the window icon
            icon = tk.PhotoImage(file=icon_path)
            dialog.iconphoto(False, icon)  # False means only set for this window
            
            # Keep reference to prevent garbage collection
            dialog._icon = icon  # Use _icon to be consistent with main window
            
            print(f"Successfully set window icon for dialog from {icon_path}")
        else:
            print(f"Icon file not found at {icon_path}")
    except Exception as e:
        print(f"Failed to set window icon: {str(e)}")

def create_label_dialog(parent, config_manager, update_label_count_callback):
    """
    Create a dialog for creating a new label
    
    Args:
        parent: Parent window
        config_manager: Configuration manager instance
        update_label_count_callback: Callback to update label count after successful label creation
    """
    # Check if labels directory is set
    if not config_manager.settings.last_directory:
        messagebox.showerror("Error", "Please set the labels directory in Settings first.")
        return
    
    # Create a dialog for user input
    dialog = tk.Toplevel(parent)
    dialog.title("Create Label")
    dialog.geometry("400x400")
    dialog.resizable(False, False)
    dialog.configure(bg='white')
    
    # Make this dialog a transient window of the parent
    dialog.transient(parent)
    
    # Set window icon (not taskbar icon)
    set_taskbar_icon(dialog, "createlabels_64.png")
    
    # Create a frame for the content
    content_frame = tk.Frame(dialog, bg='white', padx=20, pady=20)
    content_frame.pack(fill='both', expand=True)
    
    # Add a minimize button in the top-right corner
    minimize_frame = tk.Frame(dialog, bg='white')
    minimize_frame.place(x=370, y=10)
    
    def minimize_parent():
        # Minimize the parent window
        parent.iconify()
    
    minimize_button = tk.Button(
        minimize_frame,
        text="▁",  # Unicode character for a horizontal line
        font=("Arial", 8, "bold"),
        bg="#e0e0e0",
        fg="#333333",
        relief="flat",
        width=2,
        height=1,
        cursor="hand2",
        command=minimize_parent
    )
    minimize_button.pack()
    
    # Add hover effect
    def on_enter(e):
        minimize_button['bg'] = '#cccccc'
    
    def on_leave(e):
        minimize_button['bg'] = '#e0e0e0'
    
    minimize_button.bind("<Enter>", on_enter)
    minimize_button.bind("<Leave>", on_leave)
    
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
    
    # Add handler for Enter key in tracking field to copy value to clipboard and move to SKU field
    def on_tracking_enter(event):
        # Get the tracking number
        tracking_number = tracking_var.get().strip()
        if tracking_number:
            # Copy to clipboard
            dialog.clipboard_clear()
            dialog.clipboard_append(tracking_number)
            # Move to SKU field
            sku_entry.focus_set()
            return "break"  # Prevent default Enter behavior
    
    # Bind Enter key to the tracking entry field
    tracking_entry.bind('<Return>', on_tracking_enter)
    
    # Status
    _, status_label = create_status_bar(content_frame, "", "red")
    
    # Options frame
    options_frame = tk.Frame(content_frame, bg='white')
    options_frame.pack(fill='x', pady=10)
    
    # Mirror print toggle
    mirror_print_var = tk.BooleanVar(value=config_manager.settings.mirror_print)
    
    def toggle_mirror_print():
        current_state = mirror_print_var.get()
        mirror_btn.config(
            bg='#90EE90' if current_state else '#C71585',
            relief='sunken' if current_state else 'raised'
        )
        # Save the mirror print state
        config_manager.settings.mirror_print = current_state
        config_manager.save_settings()
    
    # Set initial button state based on saved setting
    initial_color = '#90EE90' if config_manager.settings.mirror_print else '#C71585'
    initial_relief = 'sunken' if config_manager.settings.mirror_print else 'raised'
    
    mirror_btn = tk.Button(options_frame, text=" ", bg=initial_color, 
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
        
        # Validate SKU (required field)
        if not sku:
            status_label.config(text="Please enter a SKU", fg='red')
            return
        
        # Create a unique filename based on tracking number and date (but don't create the actual file)
        date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{tracking_number}_{date_str}.txt"
        filepath = os.path.join(config_manager.settings.last_directory, filename)
        
        # Define a status callback function to update the status label
        def update_status(message, color):
            status_label.config(text=message, fg=color)
            dialog.update()
        
        # Write to Google Sheets if configured
        if (config_manager.settings.google_sheet_url and 
            config_manager.settings.google_sheet_name):
            success, message = write_to_google_sheet(
                config_manager, 
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
                update_label_count_callback()
            
            # Use our utility function to process the barcode
            success, message = process_barcode(
                tracking_number,
                sku,
                config_manager.settings.last_directory,
                config_manager.settings.mirror_print,
                update_status,
                after_print_success
            )
            
            # Use pyautogui to automatically press Enter after a short delay
            if success:
                try:
                    import pyautogui
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
    center_window(dialog)
    
    # Set dialog to be always on top
    dialog.attributes('-topmost', True)
    
    return dialog

def create_labels_dialog(parent):
    """
    Create a dialog for viewing and editing returns data
    
    Args:
        parent: Parent window
        
    Returns:
        None
    """
    # Create a dialog for viewing and editing returns data
    dialog, tree, content_frame = create_returns_dialog(parent)
    
    # Make this dialog a transient window of the parent
    dialog.transient(parent)
    
    # Set window icon (not taskbar icon)
    set_taskbar_icon(dialog, "returnsdata_64.png")
    
    # Load returns data
    load_returns_data(tree)
    
    # Button Frame
    button_frame = tk.Frame(content_frame, bg='white')
    button_frame.pack(fill='x', pady=(10, 0))
    
    # Add Edit button
    edit_button = create_colored_button(
        button_frame,
        "Edit",
        '#2196F3',  # Blue
        '#1976D2',  # Darker Blue
        lambda: edit_selected_record(tree)
    )
    edit_button.pack(side='right', padx=(10, 0))
    
    # Add Refresh button
    refresh_button = create_colored_button(
        button_frame,
        "Refresh",
        '#4CAF50',  # Green
        '#45a049',  # Darker Green
        lambda: load_returns_data(tree)
    )
    refresh_button.pack(side='right')
    
    # Function to edit selected record
    def edit_selected_record(tree):
        # Get selected item
        selected_item = tree.selection()
        
        # Check if an item is selected
        if not selected_item:
            messagebox.showinfo("No Selection", "Please select a record to edit.")
            return
        
        # Create edit dialog
        success = create_edit_dialog(dialog, tree, selected_item)
        
        # Refresh the treeview if record was edited
        if success:
            load_returns_data(tree)
    
    # Return the dialog and tree
    return dialog, tree

def create_settings_dialog_handler(parent, config_manager, update_label_count_callback):
    """
    Create a settings dialog with handlers for saving settings.
    
    Args:
        parent: The parent window
        config_manager: The configuration manager
        update_label_count_callback: Callback for updating the label count
        
    Returns:
        The created settings dialog
    """
    # Function to handle saving settings
    def save_settings(dialog, directory):
        # Save the directory to settings
        config_manager.settings.last_directory = directory
        config_manager.save_settings()
        
        # Close the dialog
        dialog.destroy()
    
    # Function to open Google Sheets dialog
    def open_sheets_dialog():
        # Create Google Sheets dialog
        sheets_dialog = create_google_sheets_dialog_handler(parent, config_manager)
        
        # Return the dialog so it can be managed by the settings dialog
        return sheets_dialog
    
    # Create settings dialog
    settings_dialog, _ = create_settings_dialog(
        parent, 
        config_manager, 
        update_label_count_callback, 
        open_sheets_dialog, 
        save_settings
    )
    
    # Make this dialog a transient window of the parent
    settings_dialog.transient(parent)
    
    # Set window icon (not taskbar icon)
    set_taskbar_icon(settings_dialog, "settings_64.png")
    
    return settings_dialog

def create_google_sheets_dialog_handler(parent, config_manager, update_callback=None):
    """
    Create a Google Sheets configuration dialog with handlers for saving settings.
    
    Args:
        parent: The parent window
        config_manager: The configuration manager
        update_callback: Optional callback to update the UI after settings are saved
        
    Returns:
        The created Google Sheets dialog
    """
    # Create Google Sheets dialog
    sheets_dialog = create_google_sheets_dialog(parent, config_manager, update_callback)
    
    # Make this dialog a transient window of the parent
    sheets_dialog.transient(parent)
    
    # Set window icon (not taskbar icon)
    set_taskbar_icon(sheets_dialog, "icon_64.png")
    
    return sheets_dialog
