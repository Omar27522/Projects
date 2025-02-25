import tkinter as tk
from tkinter import ttk
import re

class InputFieldManager:
    """A class for managing input fields in the application"""
    def __init__(self, parent, frame, config_manager, undo_redo_manager):
        self.parent = parent
        self.frame = frame
        self.config_manager = config_manager
        self.undo_redo_manager = undo_redo_manager
        self.inputs = {}
        self.input_vars = {}
        
        # Create input fields
        self._create_input_fields()
        
    def _create_input_fields(self):
        """Create input fields"""
        # Configure row weights to distribute space
        for i in range(4):
            self.frame.grid_rowconfigure(i, weight=1)
        
        # Create fields with more padding for height
        fields = [
            ("Product Name Line1:", "name_line1", None),
            ("Line2 (optional):", "name_line2", None),
            ("Variant:", "variant", self._validate_variant),
            ("UPC Code(12 digits):", "upc_code", self._validate_upc)
        ]
        
        for i, (label_text, field_name, validator) in enumerate(fields):
            # Create frame for each row
            row_frame = tk.Frame(self.frame, bg='SystemButtonFace')
            row_frame.grid(row=i, column=0, sticky='ew', pady=10)  # Increased padding
            row_frame.grid_columnconfigure(1, weight=1)
            
            # Create label
            label = tk.Label(
                row_frame,
                text=label_text,
                anchor="e",
                width=20,
                bg='SystemButtonFace'
            )
            label.pack(side=tk.LEFT)  # Removed padx
            
            # Create StringVar for the field
            var = tk.StringVar()
            self.input_vars[field_name] = var
            
            # Create entry with custom font for height
            vcmd = (self.frame.register(validator), '%P') if validator else None
            entry = tk.Entry(
                row_frame,
                width=25,
                relief='sunken',
                bg='white',
                validate='key' if validator else 'none',
                validatecommand=vcmd,
                font=('TkDefaultFont', 12, 'bold'),  # Larger bold font for more height
                textvariable=var
            )
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=3)  # Only right padding
            
            # Store entry widget reference
            self.inputs[field_name] = entry
            
            # Add undo/redo support
            self.undo_redo_manager.add_undo_support(entry, var)
            
            # Add focus and click handlers
            entry.bind('<FocusIn>', self._on_input_focus)
            entry.bind('<Button-1>', self._on_input_click)
            
            # Add right-click context menu
            self.parent._add_context_menu(entry)
            
            # Special handling for UPC field
            if field_name == "upc_code":
                entry.bind('<Return>', lambda e: self._handle_upc_enter())
                
    def _validate_upc(self, *args):
        """Only allow integers in UPC field and ensure exactly 12 digits"""
        action = args[0] if len(args) > 0 else '1'
        value_if_allowed = args[1] if len(args) > 1 else ''
        
        if action == '0':  # This is a delete action
            return True
        if not value_if_allowed:  # Empty value
            return True
        if not value_if_allowed.isdigit():  # Not a digit
            return False
        if len(value_if_allowed) > 12:  # Too many digits
            return False
        return True
        
    def _validate_variant(self, *args):
        """Prevent numbers at the start of variant field"""
        action = args[0] if len(args) > 0 else '1'
        value_if_allowed = args[1] if len(args) > 1 else ''
        
        if action == '0':  # This is a delete action
            return True
        if not value_if_allowed:  # Empty value
            return True
        # Check if the first character is a digit
        if value_if_allowed[0].isdigit():
            return False
        return True
        
    def _on_input_focus(self, event):
        """Enable Always on Top when user focuses on any input field"""
        if not self.parent.always_on_top.get():
            self.parent.toggle_always_on_top()
            
    def _on_input_click(self, event):
        """Handle mouse click in input field"""
        # Select all text when clicking into field
        event.widget.select_range(0, tk.END)
        event.widget.icursor(tk.END)
            
    def _handle_upc_enter(self):
        """Handle enter key in UPC field"""
        upc = self.input_vars["upc_code"].get()
        if len(upc) == 12:
            # Clear other fields
            self.input_vars["name_line1"].set("")
            self.input_vars["name_line2"].set("")
            self.input_vars["variant"].set("")
            
            # Open file viewer window
            self.parent.view_directory_files()
            
    def clear_inputs(self):
        """Clear all input fields"""
        for var in self.input_vars.values():
            var.set('')
        self.inputs['name_line1'].focus_set()
