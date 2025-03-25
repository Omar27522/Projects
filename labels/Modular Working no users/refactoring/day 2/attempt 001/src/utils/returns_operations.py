"""
Utility functions for handling returns data operations.
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox

from src.utils.file_utils import get_central_log_file_path, file_exists
from src.utils.ui_utils import center_window, create_button, make_window_modal
from src.utils.ui_components import create_title_section, create_colored_button, create_button_grid, create_form_field_group

def load_returns_data(tree):
    """
    Load returns data from the log file into the treeview.
    
    Args:
        tree: The treeview widget to populate with data
        
    Returns:
        bool: True if data was loaded successfully, False otherwise
    """
    # Clear existing items
    for item in tree.get_children():
        tree.delete(item)
        
    # Get path to log file using our utility function
    log_dir, log_file = get_central_log_file_path()
    
    if not os.path.exists(log_file):
        # No records yet
        tree.insert("", "end", values=("No records found", "", "", ""))
        return False
        
    # Read and parse log file
    with open(log_file, 'r') as f:
        lines = f.readlines()
        
    # Add each record to the treeview
    for line in lines:
        try:
            # Parse line
            parts = line.strip().split(" | ")
            if len(parts) >= 4:
                timestamp = parts[0]
                tracking = parts[1].replace("Tracking: ", "")
                sku = parts[2].replace("SKU: ", "")
                label_full = parts[3].replace("Label: ", "")
                
                # Extract just the filename from the full path
                label_filename = os.path.basename(label_full)
                
                # Use the filename as the display value
                label_display = label_filename
                
                # Insert into treeview with full label stored in hidden column
                tree.insert("", "end", values=(tracking, sku, label_display, timestamp, label_full))
        except Exception as e:
            print(f"Error parsing log line: {str(e)}")
    
    return True

def update_log_file(tree):
    """
    Update the log file with the current contents of the treeview.
    
    Args:
        tree: The treeview widget containing the data
        
    Returns:
        bool: True if the log file was updated successfully, False otherwise
    """
    try:
        # Path to log file
        log_dir, log_file = get_central_log_file_path()
        
        # Get all items from treeview
        all_items = tree.get_children()
        
        # Create logs directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Write to log file
        with open(log_file, 'w') as f:
            for item_id in all_items:
                item_values = tree.item(item_id, "values")
                if item_values and item_values[0] != "No records found":
                    timestamp = item_values[3]
                    tracking = item_values[0]
                    sku = item_values[1]
                    
                    # Get the full label path from the hidden column
                    full_label_path = item_values[4] if len(item_values) > 4 else ""
                    
                    # Write to log file in the format: timestamp | Tracking: tracking | SKU: sku | Label: full_label_path
                    f.write(f"{timestamp} | Tracking: {tracking} | SKU: {sku} | Label: {full_label_path}\n")
        
        return True
    except Exception as e:
        print(f"Error updating log file: {str(e)}")
        return False

def create_returns_dialog(parent):
    """
    Create a dialog for viewing and editing returns data.
    
    Args:
        parent: The parent window
        
    Returns:
        tuple: (dialog, tree) - The dialog window and the treeview widget
    """
    # Create a dialog window for viewing and editing returns data
    dialog = tk.Toplevel(parent)
    dialog.title("Returns Data")
    dialog.geometry("800x500")
    dialog.resizable(True, True)
    dialog.configure(bg='white')
    dialog.transient(parent)  # Make dialog modal
    dialog.grab_set()  # Make dialog modal
    
    # Center the dialog
    center_window(dialog)
    
    # Create a frame for the content
    content_frame = tk.Frame(dialog, bg='white', padx=20, pady=20)
    content_frame.pack(fill='both', expand=True)
    
    # Create title section
    title_frame, _, _ = create_title_section(content_frame, "Returns Data")
    title_frame.pack(pady=(0, 20))
    
    # Create a frame for the treeview with scrollbars
    tree_frame = tk.Frame(content_frame, bg='white')
    tree_frame.pack(fill='both', expand=True, pady=(0, 10))
    
    # Create vertical scrollbar
    vsb = tk.Scrollbar(tree_frame, orient="vertical")
    vsb.pack(side='right', fill='y')
    
    # Create horizontal scrollbar
    hsb = tk.Scrollbar(tree_frame, orient="horizontal")
    hsb.pack(side='bottom', fill='x')
    
    # Create treeview
    columns = ("tracking", "sku", "label", "timestamp", "full_label")
    tree = ttk.Treeview(
        tree_frame, 
        columns=columns,
        show='headings',
        yscrollcommand=vsb.set,
        xscrollcommand=hsb.set
    )
    
    # Configure scrollbars
    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)
    
    # Define column headings
    tree.heading("tracking", text="Tracking Number")
    tree.heading("sku", text="SKU")
    tree.heading("label", text="Label")
    tree.heading("timestamp", text="Timestamp")
    tree.heading("full_label", text="Full Label")  # Hidden column
    
    # Define column widths
    tree.column("tracking", width=200, minwidth=150)
    tree.column("sku", width=150, minwidth=100)
    tree.column("label", width=250, minwidth=150)
    tree.column("timestamp", width=150, minwidth=150)
    tree.column("full_label", width=0, stretch=False)  # Hidden column
    
    tree.pack(fill='both', expand=True)
    
    # Style the treeview
    style = ttk.Style()
    style.configure("Treeview", 
                    background="white",
                    foreground="black",
                    rowheight=25,
                    fieldbackground="white")
    style.map('Treeview', background=[('selected', '#4CAF50')])
    
    return dialog, tree, content_frame

def create_edit_dialog(parent, tree, selected_item):
    """
    Create a dialog for editing a returns data record.
    
    Args:
        parent: The parent window
        tree: The treeview widget containing the data
        selected_item: The selected item in the treeview
        
    Returns:
        bool: True if the record was edited successfully, False otherwise
    """
    # Get values of selected item
    item_values = tree.item(selected_item[0], "values")
    if not item_values or item_values[0] == "No records found":
        return False
        
    # Get the full label path from the hidden column
    full_label_path = item_values[4]
    
    # Check if the file exists
    if not file_exists(full_label_path):
        messagebox.showerror("File Not Found", f"The label file could not be found at:\n{full_label_path}")
        return False
    
    # Create edit dialog
    edit_dialog = tk.Toplevel(parent)
    edit_dialog.title("Edit Record")
    edit_dialog.geometry("500x300")
    edit_dialog.resizable(False, False)
    edit_dialog.configure(bg='white')
    edit_dialog.transient(parent)
    edit_dialog.grab_set()
    
    # Center the dialog
    center_window(edit_dialog)
    
    # Create a frame for the content
    edit_frame = tk.Frame(edit_dialog, bg='white', padx=20, pady=20)
    edit_frame.pack(fill='both', expand=True)
    
    # Create title section
    title_frame, _, _ = create_title_section(edit_frame, "Edit Record")
    title_frame.pack(pady=(0, 20))
    
    # Define form fields
    fields = [
        {
            'label': 'Timestamp:',
            'var_type': 'string',
            'default': item_values[3],
            'width': 30,
            'required': True
        },
        {
            'label': 'Tracking Number:',
            'var_type': 'string',
            'default': item_values[0],
            'width': 30,
            'required': True
        },
        {
            'label': 'SKU:',
            'var_type': 'string',
            'default': item_values[1],
            'width': 30,
            'required': True
        },
        {
            'label': 'Label:',
            'var_type': 'string',
            'default': item_values[2],
            'width': 30,
            'required': False,
            'readonly': True
        }
    ]
    
    # Create form fields
    form_frame = tk.Frame(edit_frame, bg='white')
    form_frame.pack(fill='x', expand=True)
    
    field_widgets = create_form_field_group(form_frame, fields)
    
    # Make the label field readonly
    label_widget = field_widgets['Label:']['widget']
    label_widget.config(state='readonly')
    
    # Store the full label path
    full_label_path_var = tk.StringVar(value=full_label_path)
    
    # Create a frame for the buttons
    button_frame = tk.Frame(edit_frame, bg='white')
    button_frame.pack(fill='x', expand=True, pady=(20, 0))
    
    # Function to save changes
    def save_changes():
        # Get updated values
        new_timestamp = field_widgets['Timestamp:']['var'].get()
        new_tracking = field_widgets['Tracking Number:']['var'].get()
        new_sku = field_widgets['SKU:']['var'].get()
        
        # Get the full label path
        full_label_path = full_label_path_var.get()
        
        # Update treeview with display values
        tree.item(selected_item[0], values=(new_tracking, new_sku, item_values[2], new_timestamp, full_label_path))
        
        # Update log file
        update_log_file(tree)
        
        # Close dialog
        edit_dialog.destroy()
    
    # Function to delete record
    def delete_record():
        # Confirm deletion
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
            # Delete from treeview
            tree.delete(selected_item[0])
            
            # Update log file
            update_log_file(tree)
            
            # Close dialog
            edit_dialog.destroy()
    
    # Save Button
    save_button = create_colored_button(
        button_frame,
        "Save",
        '#4CAF50',  # Green
        '#A5D6A7',  # Light Green
        save_changes
    )
    save_button.pack(side='left', padx=(10, 0))
    
    # Delete Button
    delete_button = create_colored_button(
        button_frame,
        "Delete",
        '#f44336',  # Red
        '#EF9A9A',  # Light Red
        delete_record
    )
    delete_button.pack(side='left', padx=(10, 0))
    
    # Cancel Button
    cancel_button = create_colored_button(
        button_frame,
        "Cancel",
        '#9E9E9E',  # Gray
        '#E0E0E0',  # Light Gray
        edit_dialog.destroy
    )
    cancel_button.pack(side='left', padx=(10, 0))
    
    # Wait for the dialog to be closed
    parent.wait_window(edit_dialog)
    return True
