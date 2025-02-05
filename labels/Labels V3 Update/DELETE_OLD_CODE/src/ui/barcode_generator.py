from dataclasses import dataclass
from typing import Optional

@dataclass
class LabelData:
    barcode: str
    name_line1: str
    name_line2: str = ""
    variant: str = ""
    price: Optional[float] = None

class BarcodeGenerator:
    def __init__(self, settings=None):
        self.settings = settings if settings else {}
        self.current_barcode = None
        self.current_label = None
    
    def generate_barcode(self, label_data: LabelData) -> str:
        """Generate a barcode for the given label data"""
        # For now, just return the barcode as is since it's provided
        self.current_barcode = label_data.barcode
        self.current_label = label_data
        return self.current_barcode
    
    def get_current_label(self) -> Optional[LabelData]:
        """Get the current label data"""
        return self.current_label
