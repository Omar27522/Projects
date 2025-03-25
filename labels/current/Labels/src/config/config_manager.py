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
    mirror_print: bool = False
    enable_advanced_features: bool = False
    default_print_quality: str = "Standard"
    stay_on_top: bool = False  # New setting for window stay-on-top feature
    # Google Sheets settings
    google_sheet_url: Optional[str] = None
    google_sheet_name: Optional[str] = None
    google_sheet_tracking_column: str = "D"
    google_sheet_tracking_row: int = 3
    google_sheet_sku_column: str = "F"
    google_sheet_sku_row: int = 3
    google_sheets_connection_status: str = "Not Connected"

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
                    last_directory=data.get('last_directory'),
                    mirror_print=data.get('mirror_print', False),
                    enable_advanced_features=data.get('enable_advanced_features', False),
                    default_print_quality=data.get('default_print_quality', "Standard"),
                    stay_on_top=data.get('stay_on_top', False),  # Load stay_on_top setting
                    # Google Sheets settings
                    google_sheet_url=data.get('google_sheet_url'),
                    google_sheet_name=data.get('google_sheet_name'),
                    google_sheet_tracking_column=data.get('google_sheet_tracking_column', 'D'),
                    google_sheet_tracking_row=data.get('google_sheet_tracking_row', 3),
                    google_sheet_sku_column=data.get('google_sheet_sku_column', 'F'),
                    google_sheet_sku_row=data.get('google_sheet_sku_row', 3),
                    google_sheets_connection_status=data.get('google_sheets_connection_status', "Not Connected")
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
