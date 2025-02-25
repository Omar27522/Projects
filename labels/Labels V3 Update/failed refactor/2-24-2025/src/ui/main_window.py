import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
import os
from PIL import Image, ImageTk

from ..config import ConfigManager
from ..utils.logger import setup_logger
from .window_manager import WindowManager
from ..barcode_generator import BarcodeGenerator, LabelData
from .components.label_form import LabelForm

logger = setup_logger()

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.app_windows = [self]  # Track all windows
        self.config_manager = ConfigManager()
        self.window_manager = WindowManager()
        self.barcode_generator = BarcodeGenerator(self.config_manager.settings)
        
        # Window state
        self.is_auto_switch = tk.BooleanVar(value=True)
        self.attributes('-alpha', self.config_manager.settings.transparency_level)
        
        # Initialize UI
        self._setup_window()
        self._create_components()
        self.bind("<FocusIn>", lambda e: self._on_window_focus(self))
        
    def _setup_window(self):
        """Setup main window properties"""
        self.title("Label Maker V3")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.quit_app)
        
    def _create_components(self):
        """Create main UI components"""
        # Create main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create label form
        self.label_form = LabelForm(
            main_container,
            on_create_label=self._handle_create_label,
            config_manager=self.config_manager
        )
        self.label_form.pack(fill=tk.X, pady=5)
        
        # TODO: Add other components (preview, toolbar, etc.)
        
    def _handle_create_label(self, upc: str, name_line1: str, name_line2: str, variant: str):
        """Handle label creation request from form"""
        try:
            label_data = LabelData(
                upc_code=upc,
                name_line1=name_line1,
                name_line2=name_line2,
                variant=variant
            )
            
            # Generate and save the label
            self.barcode_generator.generate_and_save(
                label_data,
                self.config_manager.settings.save_directory
            )
            
            # Show success message
            messagebox.showinfo(
                "Success",
                f"Label created successfully!\nUPC: {upc}"
            )
            
        except Exception as e:
            logger.error(f"Error creating label: {e}")
            messagebox.showerror(
                "Error",
                f"Failed to create label: {str(e)}"
            )
    
    def _on_window_focus(self, window):
        """Handle window focus to manage stacking order"""
        for w in self.app_windows:
            if w.winfo_exists():
                if w is window:
                    w.lift()
                else:
                    w.lower()
    
    def quit_app(self):
        """Clean up and quit application"""
        try:
            self.config_manager.save_settings()
            for window in self.app_windows:
                if window.winfo_exists():
                    window.destroy()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            self.quit()
