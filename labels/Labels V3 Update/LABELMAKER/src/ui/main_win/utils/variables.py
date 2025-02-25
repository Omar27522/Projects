import tkinter as tk

class VariableManager:
    """Manages Tkinter variables for the application"""
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.input_vars = {}
        self.undo_stacks = {}
        self.redo_stacks = {}
        self.setup_variables()

    def setup_variables(self):
        """Initialize tkinter variables"""
        # Initialize variables for each input field
        self.input_vars = {
            'name_line1': tk.StringVar(),
            'name_line2': tk.StringVar(),
            'variant': tk.StringVar(),
            'upc_code': tk.StringVar()
        }

        # Initialize settings variables
        self.font_size_large = tk.IntVar(value=self.config_manager.settings.font_size_large)
        self.font_size_medium = tk.IntVar(value=self.config_manager.settings.font_size_medium)
        self.barcode_width = tk.IntVar(value=self.config_manager.settings.barcode_width)
        self.barcode_height = tk.IntVar(value=self.config_manager.settings.barcode_height)
        self.always_on_top = tk.BooleanVar(value=self.config_manager.settings.always_on_top)
        self.transparency_level = tk.DoubleVar(value=self.config_manager.settings.transparency_level)
        self.png_count = tk.StringVar(value=f"Labels: {self.config_manager.settings.label_counter}")
        self.is_auto_switch = tk.BooleanVar(value=True)  # Default to auto-switch enabled
