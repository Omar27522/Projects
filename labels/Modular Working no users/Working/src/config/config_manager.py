import os
import json
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class Settings:
    """Data class for application settings"""
    font_size_large: int = 14
    font_size_medium: int = 12
    barcode_width: int = 300
    barcode_height: int = 100
    last_directory: Optional[str] = None

class ConfigManager:
    """Manages application configuration and settings"""
    
    def __init__(self):
        """Initialize the ConfigManager"""
        # Get the root directory
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Settings file path
        self.settings_file = os.path.join(self.root_dir, "label_maker_settings.json")
        
        # Load or create settings
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Settings:
        """
        Load settings from file or create default settings
        
        Returns:
            Settings: Application settings
        """
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                
                # Create Settings object from loaded data
                settings = Settings(
                    font_size_large=data.get('font_size_large', 14),
                    font_size_medium=data.get('font_size_medium', 12),
                    barcode_width=data.get('barcode_width', 300),
                    barcode_height=data.get('barcode_height', 100),
                    last_directory=data.get('last_directory')
                )
                return settings
            except Exception as e:
                print(f"Error loading settings: {str(e)}")
                return Settings()
        else:
            # Create default settings
            return Settings()
    
    def save_settings(self) -> bool:
        """
        Save settings to file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert settings to dictionary
            settings_dict = asdict(self.settings)
            
            # Save to file
            with open(self.settings_file, 'w') as f:
                json.dump(settings_dict, f, indent=4)
            
            return True
        except Exception as e:
            print(f"Error saving settings: {str(e)}")
            return False
