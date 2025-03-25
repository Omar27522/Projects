"""
Dialog handling utilities for the Label Maker application.
Contains functions for creating and managing various dialogs.
"""

import tkinter as tk
from tkinter import messagebox
import os
import datetime
import logging

# Import utility functions
from src.utils.file_utils import file_exists, get_credentials_file_path, directory_exists
from src.utils.ui_components import create_title_section, create_colored_button, create_form_field_group, create_status_bar
from src.utils.barcode_operations import process_barcode
from src.utils.sheets_operations import write_to_google_sheet, create_google_sheets_dialog
from src.utils.ui_utils import center_window
from src.utils.returns_operations import load_returns_data, update_log_file, create_returns_dialog, create_edit_dialog
from src.utils.settings_operations import create_settings_dialog
from src.config.config_manager import ConfigManager

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
    dialog.transient(parent)  # Make dialog modal
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
    Handle the creation of the settings dialog and related operations
    
    Args:
        parent: Parent window
        config_manager: Configuration manager instance
        update_label_count_callback: Callback to update label count after settings changes
        
    Returns:
        None
    """
    # Function to open Google Sheets dialog
    def open_sheets_dialog():
        nonlocal config_manager
        
        # Create Google Sheets dialog
        sheets_dialog = create_google_sheets_dialog_handler(parent, config_manager)
        
        # Wait for the dialog to be closed
        parent.wait_window(sheets_dialog)
        
        # Reload config manager to get updated settings
        config_manager = ConfigManager()
        
        # Update the Google Sheets status in the settings dialog
        if hasattr(sheets_status_label, 'config'):
            # Check if Google Sheets is configured and connected
            sheets_config = config_manager.settings
            
            # Default status
            status_text = "Not Connected"
            status_color = 'red'
            
            # Check if Google Sheets is configured and connected
            if (hasattr(sheets_config, 'google_sheets_connection_status') and 
                sheets_config.google_sheets_connection_status == "Connected"):
                
                status_text = "Connected"
                status_color = 'green'
            # Fallback to checking if configuration exists
            elif (hasattr(sheets_config, 'google_sheet_url') and 
                sheets_config.google_sheet_url and 
                hasattr(sheets_config, 'google_sheet_name') and 
                sheets_config.google_sheet_name):
                
                status_text = "Configured (Not Tested)"
                status_color = 'orange'
            
            # Update the status label
            sheets_status_label.config(text=status_text, fg=status_color)
    
    # Function to save settings
    def save_settings(dialog, directory):
        # Validate directory
        if not directory:
            messagebox.showerror("Error", "Please select a labels directory.")
            return
        
        # Check if directory exists
        if not directory_exists(directory):
            # Ask if we should create the directory
            create_dir = messagebox.askyesno(
                "Directory Not Found", 
                f"The directory '{directory}' does not exist. Would you like to create it?"
            )
            
            if create_dir:
                try:
                    os.makedirs(directory)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create directory: {str(e)}")
                    return
            else:
                return
        
        # Save settings
        config_manager.settings.last_directory = directory
        config_manager.save_settings()
        
        # Update label count
        update_label_count_callback(directory)
        
        # Close dialog
        dialog.destroy()
    
    # Create settings dialog
    settings_dialog, directory_var, label_count_var = create_settings_dialog(
        parent, 
        config_manager, 
        update_label_count_callback, 
        open_sheets_dialog,
        save_settings
    )
    
    # Get reference to sheets status label
    for widget in settings_dialog.winfo_children():
        if isinstance(widget, tk.Frame):
            for child in widget.winfo_children():
                if isinstance(child, tk.LabelFrame) and child.cget('text') == "Google Sheets Integration":
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, tk.Frame):
                            for great_grandchild in grandchild.winfo_children():
                                if isinstance(great_grandchild, tk.Label) and great_grandchild.cget('text') != "Status:":
                                    sheets_status_label = great_grandchild
                                    break
    
    return settings_dialog

def create_google_sheets_dialog_handler(parent, config_manager, update_callback=None):
    """
    Handle the creation of the Google Sheets configuration dialog
    
    Args:
        parent: Parent window
        config_manager: Configuration manager instance
        update_callback: Optional callback to update the status display after dialog closes
        
    Returns:
        The created Google Sheets dialog
    """
    # Create Google Sheets dialog
    sheets_dialog = create_google_sheets_dialog(parent, config_manager, update_callback)
    
    return sheets_dialog
