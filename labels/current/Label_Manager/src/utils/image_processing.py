"""
Image processing utilities.
"""
import os
import pytesseract
from PIL import Image, ImageTk
from io import BytesIO
from config import TESSERACT_PATH

# Configure Tesseract path
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def process_image(image_data):
    """Process image data and extract text using Tesseract."""
    try:
        image = Image.open(BytesIO(image_data))
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        print(f"Error processing image: {e}")
        return ""

def create_photo_image(image_data):
    """Create a PhotoImage from image data."""
    try:
        image = Image.open(BytesIO(image_data))
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"Error creating photo image: {e}")
        return None
