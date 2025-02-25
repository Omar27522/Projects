import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any, Callable
import re
from ...utils.csv_processor import is_valid_barcode, process_product_name
from ...utils.logger import setup_logger

logger = setup_logger()

class LabelForm(ttk.Frame):
    def __init__(self, parent, on_create_label: Callable, config_manager):
        super().__init__(parent)
        self.parent = parent
        self.on_create_label = on_create_label
        self.config_manager = config_manager
        
        self._setup_variables()
        self._create_widgets()
        self._setup_bindings()
    
    def _setup_variables(self):
        """Initialize form variables"""
        self.upc_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.variant_var = tk.StringVar()
        
    def _create_widgets(self):
        """Create form widgets"""
        # UPC Entry
        upc_frame = ttk.Frame(self)
        upc_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(upc_frame, text="UPC:").pack(side=tk.LEFT)
        self.upc_entry = ttk.Entry(upc_frame, textvariable=self.upc_var)
        self.upc_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Product Name Entry
        name_frame = ttk.Frame(self)
        name_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(name_frame, text="Product Name:").pack(side=tk.LEFT)
        self.name_entry = ttk.Entry(name_frame, textvariable=self.name_var)
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Variant Entry
        variant_frame = ttk.Frame(self)
        variant_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(variant_frame, text="Variant:").pack(side=tk.LEFT)
        self.variant_entry = ttk.Entry(variant_frame, textvariable=self.variant_var)
        self.variant_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Create Button
        self.create_button = ttk.Button(
            self, 
            text="Create Label",
            command=self._handle_create_label
        )
        self.create_button.pack(pady=5)
        
    def _setup_bindings(self):
        """Setup keyboard bindings"""
        self.upc_entry.bind('<Return>', lambda e: self.name_entry.focus())
        self.name_entry.bind('<Return>', lambda e: self.variant_entry.focus())
        self.variant_entry.bind('<Return>', lambda e: self._handle_create_label())
        
    def _handle_create_label(self):
        """Validate and create label"""
        upc = self.upc_var.get().strip()
        name = self.name_var.get().strip()
        variant = self.variant_var.get().strip()
        
        # Validate UPC
        if not is_valid_barcode(upc):
            logger.warning(f"Invalid UPC format: {upc}")
            return
            
        # Process product name
        name_line1, name_line2, variant = process_product_name(
            f"{name} {variant}".strip()
        )
        
        # Call parent handler
        self.on_create_label(upc, name_line1, name_line2, variant)
        
        # Clear form if configured
        if self.config_manager.settings.clear_after_print:
            self.clear_form()
            
    def clear_form(self):
        """Clear all form fields"""
        self.upc_var.set("")
        self.name_var.set("")
        self.variant_var.set("")
        self.upc_entry.focus()
        
    def set_values(self, upc: str = "", name: str = "", variant: str = ""):
        """Set form values"""
        self.upc_var.set(upc)
        self.name_var.set(name)
        self.variant_var.set(variant)
