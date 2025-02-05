def is_valid_barcode(barcode: str) -> bool:
    """Check if barcode consists of exactly 12 digits"""
    if not barcode:
        return False
    return len(barcode) == 12 and barcode.isdigit()

def process_product_name(full_name: str) -> tuple[str, str, str]:
    """Process product name into name_line1, name_line2, and variant"""
    # Split the name by '/'
    parts = [part.strip() for part in full_name.split('/')]
    
    # Initialize default values
    name_line1 = parts[0] if parts else ""
    name_line2 = parts[1] if len(parts) > 1 else ""
    variant = parts[2] if len(parts) > 2 else ""
    
    return name_line1, name_line2, variant
