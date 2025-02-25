import tkinter as tk
from tkinter import ttk
from ..utils.icons import IconManager

class SettingsWindow:
    """Manages the settings window and related functionality"""
    def __init__(self, parent, config_manager, variable_manager, icon_manager):
        self.parent = parent
        self.config_manager = config_manager
        self.variable_manager = variable_manager
        self.icon_manager = icon_manager
        self.settings_window = None

    def show(self):
        """Show settings window"""
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.focus_force()
            return

        self.settings_window = tk.Toplevel(self.parent)
        self.settings_window.title("Settings")
        self.settings_window.geometry("400x500")
        self.settings_window.resizable(False, False)
        self.settings_window.transient(self.parent)
        
        # Set window icon
        self.icon_manager.set_window_icon(self.settings_window, '32', 'settings')
        
        self._create_settings_content()

    def _create_settings_content(self):
        """Create settings window content"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Font Settings Tab
        font_frame = ttk.Frame(notebook)
        notebook.add(font_frame, text='Font')

        ttk.Label(font_frame, text="Large Font Size:").pack(pady=5)
        ttk.Scale(font_frame, from_=20, to=72, 
                 variable=self.variable_manager.font_size_large, 
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5)

        ttk.Label(font_frame, text="Medium Font Size:").pack(pady=5)
        ttk.Scale(font_frame, from_=14, to=48, 
                 variable=self.variable_manager.font_size_medium, 
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5)

        # Barcode Settings Tab
        barcode_frame = ttk.Frame(notebook)
        notebook.add(barcode_frame, text='Barcode')

        ttk.Label(barcode_frame, text="Barcode Width:").pack(pady=5)
        ttk.Scale(barcode_frame, from_=1, to=3, 
                 variable=self.variable_manager.barcode_width, 
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5)

        ttk.Label(barcode_frame, text="Barcode Height:").pack(pady=5)
        ttk.Scale(barcode_frame, from_=15, to=50, 
                 variable=self.variable_manager.barcode_height, 
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5)

        # Window Settings Tab
        window_frame = ttk.Frame(notebook)
        notebook.add(window_frame, text='Window')

        ttk.Checkbutton(window_frame, text="Always on Top", 
                       variable=self.variable_manager.always_on_top).pack(pady=5)

        ttk.Label(window_frame, text="Window Transparency:").pack(pady=5)
        transparency_scale = ttk.Scale(window_frame, from_=0.3, to=1.0, 
                                     variable=self.variable_manager.transparency_level, 
                                     orient=tk.HORIZONTAL)
        transparency_scale.pack(fill=tk.X, padx=5)
        
        # Bind transparency update
        self.variable_manager.transparency_level.trace('w', self.update_transparency)

        # Save Button
        save_button = ttk.Button(self.settings_window, text="Save", command=self.save_settings)
        save_button.pack(pady=10)

    def update_transparency(self, *args):
        """Update window transparency"""
        self.parent.attributes('-alpha', self.variable_manager.transparency_level.get())
        if self.settings_window:
            self.settings_window.attributes('-alpha', self.variable_manager.transparency_level.get())

    def save_settings(self):
        """Save settings to config"""
        self.config_manager.settings.font_size_large = self.variable_manager.font_size_large.get()
        self.config_manager.settings.font_size_medium = self.variable_manager.font_size_medium.get()
        self.config_manager.settings.barcode_width = self.variable_manager.barcode_width.get()
        self.config_manager.settings.barcode_height = self.variable_manager.barcode_height.get()
        self.config_manager.settings.always_on_top = self.variable_manager.always_on_top.get()
        self.config_manager.settings.transparency_level = self.variable_manager.transparency_level.get()
        
        self.config_manager.save_settings()
        self.settings_window.destroy()
