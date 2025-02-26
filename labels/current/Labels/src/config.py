import os
import json
import sys
from dataclasses import dataclass
from typing import Optional

@dataclass
class LabelSettings:
    font_size_large: int = 45
    font_size_medium: int = 45
    barcode_width: int = 600
    barcode_height: int = 310
    always_on_top: bool = False
    transparency_level: float = 0.9
    last_directory: Optional[str] = None
    label_counter: int = 0
    # View files window preferences
    view_files_mirror_print: bool = False
    view_files_pin_window: bool = False
    view_files_auto_switch: bool = True
    view_files_print_minimize: bool = False  # Print minimize feature

    DPI: int = 300
    LABEL_WIDTH: int = DPI * 2
    LABEL_HEIGHT: int = DPI * 2

class ConfigManager:
    def __init__(self):
        # Get the directory where the script is located
        if getattr(sys, 'frozen', False):
            script_dir = os.path.dirname(sys.executable)
        else:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        # Save settings in the program directory
        self.settings_file = os.path.join(script_dir, 'label_maker_settings.json')
        self.settings = LabelSettings()
        self.load_settings()

    def load_settings(self) -> None:
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    last_dir = data.get('last_directory', '')
                    # Only use the directory if it exists and is not empty
                    if not last_dir or not os.path.exists(last_dir):
                        last_dir = None
                        
                    self.settings = LabelSettings(
                        font_size_large=data.get('font_size_large', self.settings.font_size_large),
                        font_size_medium=data.get('font_size_medium', self.settings.font_size_medium),
                        barcode_width=data.get('barcode_width', self.settings.barcode_width),
                        barcode_height=data.get('barcode_height', self.settings.barcode_height),
                        always_on_top=data.get('always_on_top', self.settings.always_on_top),
                        transparency_level=data.get('transparency_level', self.settings.transparency_level),
                        last_directory=last_dir,
                        label_counter=data.get('label_counter', 0),
                        # Load view files window preferences
                        view_files_mirror_print=data.get('view_files_mirror_print', False),
                        view_files_pin_window=data.get('view_files_pin_window', False),
                        view_files_auto_switch=data.get('view_files_auto_switch', True),
                        view_files_print_minimize=data.get('view_files_new_feature', False)
                    )
        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self) -> None:
        """Save settings to JSON file"""
        try:
            settings_dict = {
                'font_size_large': self.settings.font_size_large,
                'font_size_medium': self.settings.font_size_medium,
                'barcode_width': self.settings.barcode_width,
                'barcode_height': self.settings.barcode_height,
                'always_on_top': self.settings.always_on_top,
                'transparency_level': self.settings.transparency_level,
                'last_directory': self.settings.last_directory if self.settings.last_directory else "",
                'label_counter': self.settings.label_counter,
                # Save view files window preferences
                'view_files_mirror_print': self.settings.view_files_mirror_print,
                'view_files_pin_window': self.settings.view_files_pin_window,
                'view_files_auto_switch': self.settings.view_files_auto_switch,
                'view_files_new_feature': self.settings.view_files_print_minimize
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings_dict, f)
        except Exception as e:
            print(f"Error saving settings: {e}")
