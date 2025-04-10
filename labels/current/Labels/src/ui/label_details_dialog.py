"""
Label Details Dialog for the Label Maker application.
This module provides a dialog for viewing detailed information about a label.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import webbrowser
from PIL import Image, ImageTk
import threading
import tempfile

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import utility modules
from src.utils.ui_components import create_colored_button
from src.utils.file_utils import find_files_by_sku
from src.utils.barcode_operations import print_barcode

class LabelDetailsDialog(tk.Toplevel):
    """Dialog for displaying label details"""
    
    def __init__(self, parent, record, config_manager):
        """
        Initialize the Label Details Dialog
        
        Args:
            parent: Parent widget
            record: Dictionary containing label record data
            config_manager: Configuration manager instance
        """
        super().__init__(parent)
        
        # Store references
        self.parent = parent
        self.record = record
        self.config_manager = config_manager
        self.label_files = []
        
        # Mirror print setting
        self.mirror_print = tk.BooleanVar(value=False)
        if hasattr(self.config_manager, 'settings') and hasattr(self.config_manager.settings, 'mirror_print'):
            self.mirror_print.set(self.config_manager.settings.mirror_print)
        
        # Configure dialog
        self.title(f"Label Details: {record.get('label_name', 'Unknown')}")
        self.geometry("800x600")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        # Set dialog position centered on parent
        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.geometry(f"+{x}+{y}")
        
        # Status variable
        self.status_var = tk.StringVar(value="Loading label information...")
        
        # Create UI
        self._create_ui()
        
        # Load label files in background
        self._load_label_files()
        
        # Make dialog modal
        self.focus_set()
        self.wait_window()
    
    def _create_ui(self):
        """Create the user interface elements"""
        # Create main container with padding
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title with label name
        title_label = ttk.Label(
            main_frame, 
            text=self.record.get('label_name', 'Unknown Label'),
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Create details frame
        details_frame = ttk.Frame(main_frame)
        details_frame.pack(fill='both', expand=True)
        
        # Left column - Label information
        info_frame = ttk.LabelFrame(details_frame, text="Label Information")
        info_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Create a canvas with scrollbar for the info frame
        canvas = tk.Canvas(info_frame)
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add field labels and values
        field_mappings = [
            ("Item Variant", "item_variant_number"),
            ("UPC", "upc"),
            ("Label Name", "label_name"),
            ("Department", "department"),
            ("Category", "category"),
            ("Color", "color"),
            ("Website Color", "website_color"),
            ("Website Name", "website_name")
        ]
        
        for i, (label_text, field_name) in enumerate(field_mappings):
            # Label
            label = ttk.Label(scrollable_frame, text=f"{label_text}:", font=('Arial', 10, 'bold'))
            label.grid(row=i, column=0, sticky='w', padx=5, pady=5)
            
            # Value
            value = self.record.get(field_name, "N/A")
            value_label = ttk.Label(scrollable_frame, text=value, wraplength=200)
            value_label.grid(row=i, column=1, sticky='w', padx=5, pady=5)
        
        # Right column - Label files
        files_frame = ttk.LabelFrame(details_frame, text="Label Files")
        files_frame.pack(side='right', fill='both', expand=True)
        
        # Create listbox for files
        self.files_listbox = tk.Listbox(files_frame, selectmode=tk.SINGLE)
        self.files_listbox.pack(side='left', fill='both', expand=True)
        
        # Add scrollbar to listbox
        files_scrollbar = ttk.Scrollbar(files_frame, orient="vertical", command=self.files_listbox.yview)
        files_scrollbar.pack(side="right", fill="y")
        self.files_listbox.configure(yscrollcommand=files_scrollbar.set)
        
        # Bind double-click to open file
        self.files_listbox.bind("<Double-1>", self._open_selected_file)
        
        # Add a placeholder item
        self.files_listbox.insert(tk.END, "Searching for label files...")
        
        # Separator
        ttk.Separator(main_frame).pack(fill='x', pady=15)
        
        # Bottom buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=(10, 0))
        
        # Open file button
        open_button = create_colored_button(
            buttons_frame,
            text="Open Selected File",
            color="#4CAF50",
            hover_color="#45a049",
            command=self._open_selected_file
        )
        open_button.pack(side='left', padx=(0, 5))
        
        # Print button
        print_button = create_colored_button(
            buttons_frame,
            text="Print Selected File",
            color="#2196F3",
            hover_color="#0b7dda",
            command=self._print_selected_file
        )
        print_button.pack(side='left', padx=(0, 5))
        
        # Mirror print checkbox
        mirror_frame = ttk.Frame(buttons_frame)
        mirror_frame.pack(side='left', padx=(5, 0))
        
        mirror_check = ttk.Checkbutton(
            mirror_frame,
            text="Mirror Print",
            variable=self.mirror_print,
            command=self._toggle_mirror_print
        )
        mirror_check.pack(side='left')
        
        # Close button
        close_button = ttk.Button(
            buttons_frame,
            text="Close",
            command=self.destroy
        )
        close_button.pack(side='right')
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill='x', side='bottom', pady=(10, 0))
        
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side='left')
    
    def _load_label_files(self):
        """Load label files in a background thread"""
        def find_files_thread():
            try:
                # Get SKU
                sku = self.record.get('sku', '')
                if not sku:
                    self.after(0, lambda: self._update_status("No SKU available to search for files"))
                    return
                
                # Find files
                # We need to search for label files in the last used directory
                labels_dir = self.config_manager.settings.last_directory if hasattr(self.config_manager, 'settings') and hasattr(self.config_manager.settings, 'last_directory') else None
                
                if not labels_dir or not os.path.exists(labels_dir):
                    self.after(0, lambda: self._update_status("No valid labels directory found"))
                    return
                
                # Find files in the labels directory
                try:
                    self.label_files = find_files_by_sku(labels_dir, sku)
                except Exception as e:
                    self.after(0, lambda: self._update_status(f"Error searching for files: {str(e)}"))
                    return
                
                # Update UI from main thread
                self.after(0, self._update_files_list)
            except Exception as e:
                # Handle errors
                error_message = f"Error finding files: {str(e)}"
                self.after(0, lambda msg=error_message: self._update_status(msg))
        
        # Start thread
        threading.Thread(target=find_files_thread).start()
    
    def _update_files_list(self):
        """Update the files listbox with found files"""
        # Clear listbox
        self.files_listbox.delete(0, tk.END)
        
        if not self.label_files:
            self.files_listbox.insert(tk.END, "No label files found")
            self._update_status("No label files found for this SKU")
            return
        
        # Add files to listbox
        for file_path in self.label_files:
            # Display just the filename, not the full path
            filename = os.path.basename(file_path)
            self.files_listbox.insert(tk.END, filename)
        
        # Select the first item by default
        if len(self.label_files) > 0:
            self.files_listbox.selection_set(0)
            self.files_listbox.see(0)
            self.files_listbox.activate(0)
            self.files_listbox.focus_set()
        
        self._update_status(f"Found {len(self.label_files)} label files")
    
    def _open_selected_file(self, event=None):
        """Open the selected file"""
        # Get selected index
        selected_idx = self.files_listbox.curselection()
        if not selected_idx or not self.label_files:
            messagebox.showinfo("No File Selected", "Please select a file to open")
            return
        
        # Get file path
        file_path = self.label_files[selected_idx[0]]
        
        try:
            # Open file with default application
            os.startfile(file_path)
            self._update_status(f"Opened file: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error Opening File", f"Could not open file: {str(e)}")
            
    def _print_selected_file(self):
        """Print the selected file"""
        # Get selected index
        selected_idx = self.files_listbox.curselection()
        if not selected_idx or not self.label_files:
            messagebox.showinfo("No File Selected", "Please select a file to print")
            return
        
        # Get file path
        file_path = self.label_files[selected_idx[0]]
        
        try:
            # Print the file using the barcode_operations utility
            success, message = print_barcode(
                file_path, 
                mirror_print=self.mirror_print.get(),
                status_callback=lambda msg, color: self._update_status(msg)
            )
            
            if success:
                self._update_status(f"Sent to printer: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("Error Printing File", message)
                self._update_status(f"Error printing: {message}")
        except Exception as e:
            messagebox.showerror("Error Printing File", f"Could not print file: {str(e)}")
            
    def _toggle_mirror_print(self):
        """Toggle the mirror print setting and save to config"""
        # Update the config if available
        if hasattr(self.config_manager, 'settings'):
            self.config_manager.settings.mirror_print = self.mirror_print.get()
            if hasattr(self.config_manager, 'save_settings'):
                self.config_manager.save_settings()
                
        # Update status
        if self.mirror_print.get():
            self._update_status("Mirror print enabled")
        else:
            self._update_status("Mirror print disabled")
    
    def _update_status(self, message):
        """Update the status message"""
        self.status_var.set(message)

def create_label_details_dialog(parent, record, config_manager):
    """
    Create and return a Label Details Dialog
    
    Args:
        parent: Parent widget
        record: Dictionary containing label record data
        config_manager: Configuration manager instance
        
    Returns:
        LabelDetailsDialog: The created dialog
    """
    return LabelDetailsDialog(parent, record, config_manager)
