from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
from dataclasses import dataclass
from typing import Optional, Tuple
import os

@dataclass
class LabelData:
    name_line1: str
    name_line2: str
    variant: str
    upc_code: str

class BarcodeGenerator:
    def __init__(self, settings):
        self.settings = settings
        self._setup_fonts()

    def _setup_fonts(self):
        """Setup font paths and sizes"""
        font_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "fonts", "arial.ttf")
        self.font_large = ImageFont.truetype(font_path, self.settings.font_size_large)
        self.font_medium = ImageFont.truetype(font_path, self.settings.font_size_medium)

    def generate_barcode_image(self, upc_code: str) -> Optional[Image.Image]:
        """Generate barcode image using python-barcode"""
        try:
            barcode_class = barcode.get_barcode_class('upc')
            barcode_writer = ImageWriter()
            barcode_writer.set_options({
                'quiet_zone': 0,
                'text_distance': 2,
                'module_height': self.settings.barcode_height * 0.8
            })
            
            barcode_obj = barcode_class(upc_code, writer=barcode_writer)
            barcode_image = barcode_obj.render()
            
            return barcode_image
        except Exception as e:
            print(f"Error generating barcode: {e}")
            return None

    def generate_label(self, data: LabelData) -> Optional[Image.Image]:
        """Generate complete label with text and barcode"""
        try:
            # Create blank label
            label = Image.new('RGB', (self.settings.LABEL_WIDTH, self.settings.LABEL_HEIGHT), 'white')
            draw = ImageDraw.Draw(label)

            # Generate and paste barcode
            barcode_img = self.generate_barcode_image(data.upc_code)
            if barcode_img:
                # Resize barcode
                barcode_img = barcode_img.resize(
                    (self.settings.barcode_width, self.settings.barcode_height),
                    Image.Resampling.LANCZOS
                )
                # Calculate position to center barcode
                x = (label.width - barcode_img.width) // 2
                y = label.height - barcode_img.height - 20
                label.paste(barcode_img, (x, y))

            # Add text
            self._add_text_to_label(draw, data)

            return label
        except Exception as e:
            print(f"Error generating label: {e}")
            return None

    def _add_text_to_label(self, draw: ImageDraw.ImageDraw, data: LabelData):
        """Add text elements to the label"""
        # Calculate text positions
        name1_pos = self._center_text(data.name_line1, self.font_large, self.settings.LABEL_WIDTH)
        name2_pos = self._center_text(data.name_line2, self.font_large, self.settings.LABEL_WIDTH)
        variant_pos = self._center_text(data.variant, self.font_medium, self.settings.LABEL_WIDTH)

        # Draw text
        draw.text((name1_pos, 20), data.name_line1, font=self.font_large, fill='black')
        draw.text((name2_pos, 80), data.name_line2, font=self.font_large, fill='black')
        draw.text((variant_pos, 140), data.variant, font=self.font_medium, fill='black')

    def _center_text(self, text: str, font: ImageFont.FreeTypeFont, width: int) -> int:
        """Calculate x position to center text"""
        text_width = font.getlength(text)
        return (width - text_width) // 2
