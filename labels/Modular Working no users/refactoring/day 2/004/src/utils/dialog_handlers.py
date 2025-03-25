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
from src.utils.file_utils import file_exists, get_credentials_file_path
from src.utils.ui_components import create_title_section, create_colored_button, create_form_field_group, create_status_bar
from src.utils.barcode_operations import process_barcode
from src.utils.sheets_operations import write_to_google_sheet
from src.utils.ui_utils import center_window
from src.utils.returns_operations import load_returns_data, update_log_file, create_returns_dialog, create_edit_dialog

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
        
        # Create a unique filename based on tracking number and date (but don't create the actual file)
        date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{tracking_number}_{date_str}.txt"
        filepath = os.path.join(config_manager.settings.last_directory, filename)
        
        # Write to Google Sheets if configured
        if (config_manager.settings.google_sheet_url and 
            config_manager.settings.google_sheet_name):
            try:
                # Import required libraries
                import gspread
                from oauth2client.service_account import ServiceAccountCredentials
                
                # Check for credentials file
                creds_file = get_credentials_file_path()
                if not file_exists(creds_file):
                    status_label.config(text="Google Sheets credentials file not found", fg='red')
                    dialog.update()
                else:
                    # Define the scope
                    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                    
                    # Add credentials to the account
                    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
                    
                    # Authorize the clientsheet
                    client = gspread.authorize(creds)
                    
                    # Extract sheet ID from URL
                    import re
                    match = re.match(r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)', config_manager.settings.google_sheet_url)
                    if match:
                        sheet_id = match.group(1)
                        
                        # Open the spreadsheet
                        spreadsheet = client.open_by_key(sheet_id)
                        
                        # Get the worksheet
                        worksheet = spreadsheet.worksheet(config_manager.settings.google_sheet_name)
                        
                        # Get the next empty row or use the configured row
                        tracking_col = config_manager.settings.google_sheet_tracking_column
                        tracking_row = config_manager.settings.google_sheet_tracking_row
                        sku_col = config_manager.settings.google_sheet_sku_column
                        sku_row = config_manager.settings.google_sheet_sku_row
                        
                        # Write tracking number
                        worksheet.update_acell(f"{tracking_col}{tracking_row}", tracking_number)
                        
                        # Write SKU
                        worksheet.update_acell(f"{sku_col}{sku_row}", sku)
                        
                        # Increment row numbers for next entry
                        config_manager.settings.google_sheet_tracking_row += 1
                        config_manager.settings.google_sheet_sku_row += 1
                        config_manager.save_settings()
                        
                        status_label.config(text="Data written to Google Sheets", fg='green')
                        dialog.update()
                    else:
                        status_label.config(text="Invalid Google Sheet URL format", fg='red')
                        dialog.update()
            except ImportError:
                status_label.config(text="Google Sheets libraries not installed", fg='red')
                dialog.update()
            except Exception as e:
                status_label.config(text=f"Error writing to Google Sheets: {str(e)}", fg='red')
                dialog.update()
        
        # Generate and print the barcode directly without showing preview window
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
            lambda msg, color: [status_label.config(text=msg, fg=color), dialog.update()],
            after_print_success
        )
        
        # If using pyautogui to auto-press Enter after printing
        if success:
            try:
                import pyautogui
                # Wait a moment for the print dialog to appear
                dialog.after(1000, lambda: pyautogui.press('enter'))
            except ImportError:
                print("pyautogui not installed, cannot auto-press Enter")
        
        # Update the label count
        update_label_count_callback()
    
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
    
    return dialog

def create_user_dialog(parent, config_manager, update_label_count_callback):
    """
    Create a dialog for user input with SKU validation
    
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
    
    return dialog, tree
