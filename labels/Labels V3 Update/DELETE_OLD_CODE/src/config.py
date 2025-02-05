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
                    if last_dir and os.path.exists(last_dir):
                        self.settings.last_directory = os.path.normpath(last_dir)
                    else:
                        self.settings.last_directory = None
                        
                    self.settings = LabelSettings(
                        font_size_large=data.get('font_size_large', self.settings.font_size_large),
                        font_size_medium=data.get('font_size_medium', self.settings.font_size_medium),
                        barcode_width=data.get('barcode_width', self.settings.barcode_width),
                        barcode_height=data.get('barcode_height', self.settings.barcode_height),
                        always_on_top=data.get('always_on_top', self.settings.always_on_top),
                        transparency_level=data.get('transparency_level', self.settings.transparency_level),
                        last_directory=self.settings.last_directory,
                        label_counter=data.get('label_counter', self.settings.label_counter)
                    )
        except Exception as e:
            print(f"Failed to load settings: {e}")
            # Keep default settings
            pass

    def save_settings(self) -> None:
        """Save settings to JSON file"""
        try:
            data = {
                'font_size_large': self.settings.font_size_large,
                'font_size_medium': self.settings.font_size_medium,
                'barcode_width': self.settings.barcode_width,
                'barcode_height': self.settings.barcode_height,
                'always_on_top': self.settings.always_on_top,
                'transparency_level': self.settings.transparency_level,
                'last_directory': os.path.normpath(self.settings.last_directory) if self.settings.last_directory else None,
                'label_counter': self.settings.label_counter
            }
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            with open(self.settings_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Failed to save settings: {e}")
