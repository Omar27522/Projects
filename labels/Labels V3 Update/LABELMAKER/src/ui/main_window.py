import tkinter as tk
from typing import Optional, Dict, Any
import os

from ..config import ConfigManager
from ..utils.logger import setup_logger
from .window_manager import WindowManager
from ..barcode_generator import BarcodeGenerator, LabelData

from .main_win.components.tooltip import ToolTip
from .main_win.components.file_viewer import FileViewer
from .main_win.components.input_fields import InputFieldManager
from .main_win.components.settings import SettingsWindow
from .main_win.components.buttons import ButtonManager
from .main_win.components.preview import PreviewWindow

from .main_win.utils.fonts import FontManager
from .main_win.utils.icons import IconManager
from .main_win.utils.variables import VariableManager

# Get logger instance
logger = setup_logger()

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Initialize window tracking
        self.app_windows = []  # Track all windows
        self.app_windows.append(self)  # Include main window
        
        # Initialize managers
        self.config_manager = ConfigManager()
        self.window_manager = WindowManager()
        self.barcode_generator = BarcodeGenerator(self.config_manager.settings)
        
        # Initialize utility managers
        self.icon_manager = IconManager()
        self.font_manager = FontManager(self)
        self.variable_manager = VariableManager(self.config_manager)
        
        # Initialize component managers
        self.button_manager = ButtonManager(self)
        self.input_field_manager = InputFieldManager(self, self.variable_manager)
        self.input_field_manager.always_on_top = self.variable_manager.always_on_top
        self.settings_window = SettingsWindow(self, self.config_manager, self.variable_manager, self.icon_manager)
        self.file_viewer = FileViewer(self, self.config_manager, self.icon_manager)
        self.preview_window = PreviewWindow(self, self.barcode_generator)
        
        # Set initial transparency
        self.attributes('-alpha', self.config_manager.settings.transparency_level)
        
        # Create main window
        self._create_main_window()
        
        # Bind focus event to main window
        self.bind("<FocusIn>", lambda e: self._on_window_focus(self))
        
        # Bind UPC set event from file viewer
        self.bind('<<SetUPC>>', self._on_upc_set)

    def _create_main_window(self):
        """Create and setup the main application window"""
        self.title("Label Maker")
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Set window icon
        self.icon_manager.set_window_icon(self)
        
        # Create top control frame
        self.button_manager.create_top_control_frame(self, {
            'toggle_always_on_top': self.toggle_always_on_top,
            'show_settings': self.settings_window.show
        })
        
        # Create input fields
        self.input_field_manager.create_input_fields(self)
        
        # Create control frame
        self.button_manager.create_control_frame(self, {
            'clear_inputs': self.clear_inputs
        })
        
        # Create action buttons
        self._create_action_buttons()

    def _create_action_buttons(self):
        """Create action buttons frame"""
        frame = tk.Frame(self)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Preview button
        self.button_manager.create_styled_button(
            frame, "Preview", self.preview_label,
            tooltip_text="Preview the label",
            color_scheme={'bg': '#e3f2fd', 'activebackground': '#bbdefb', 'hoverbg': '#90caf9'}
        ).pack(side=tk.LEFT, padx=2)
        
        # View Files button
        self.button_manager.create_styled_button(
            frame, "View Files", self.file_viewer.show,
            tooltip_text="View existing labels",
            color_scheme={'bg': '#f5f5f5', 'activebackground': '#e0e0e0', 'hoverbg': '#bdbdbd'}
        ).pack(side=tk.LEFT, padx=2)

    def toggle_always_on_top(self):
        """Toggle the always on top state"""
        current = self.variable_manager.always_on_top.get()
        self.variable_manager.always_on_top.set(not current)
        self.attributes('-topmost', not current)

    def clear_inputs(self):
        """Clear all input fields"""
        for var in self.variable_manager.input_vars.values():
            var.set('')

    def preview_label(self):
        """Show label preview"""
        label_data = LabelData(
            name_line1=self.variable_manager.input_vars['name_line1'].get(),
            name_line2=self.variable_manager.input_vars['name_line2'].get(),
            variant=self.variable_manager.input_vars['variant'].get(),
            upc_code=self.variable_manager.input_vars['upc_code'].get()
        )
        self.preview_window.show(label_data)

    def _on_window_focus(self, focused_window):
        """Handle window focus to manage stacking order"""
        # Bring the focused window to the front of our windows
        if focused_window in self.app_windows:
            focused_window.lift()
            
            # If always on top is enabled, make sure it stays on top
            if self.variable_manager.always_on_top.get():
                focused_window.attributes('-topmost', True)

    def _on_upc_set(self, event):
        """Handle UPC set event from file viewer"""
        upc = event.data
        self.variable_manager.input_vars['upc_code'].set(upc)
        self.input_field_manager.inputs['upc_code'].focus_set()
        self.input_field_manager.inputs['upc_code'].select_range(0, tk.END)

    def run(self):
        """Start the application"""
        self.mainloop()
