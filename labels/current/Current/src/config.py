import os
import json
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

    DPI: int = 300
    LABEL_WIDTH: int = DPI * 2
    LABEL_HEIGHT: int = DPI * 2

class ConfigManager:
    def __init__(self):
        self.settings_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                        'label_maker_settings.json')
        self.settings = LabelSettings()
        self.load_settings()

    def load_settings(self) -> None:
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    self.settings = LabelSettings(
                        font_size_large=data.get('font_size_large', self.settings.font_size_large),
                        font_size_medium=data.get('font_size_medium', self.settings.font_size_medium),
                        barcode_width=data.get('barcode_width', self.settings.barcode_width),
                        barcode_height=data.get('barcode_height', self.settings.barcode_height),
                        always_on_top=data.get('always_on_top', self.settings.always_on_top),
                        transparency_level=data.get('transparency_level', self.settings.transparency_level),
                        last_directory=data.get('last_directory', '')
                    )
                    if self.settings.last_directory and not os.path.exists(self.settings.last_directory):
                        self.settings.last_directory = None
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
                'last_directory': self.settings.last_directory if self.settings.last_directory else ""
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings_dict, f)
        except Exception as e:
            print(f"Error saving settings: {e}")
