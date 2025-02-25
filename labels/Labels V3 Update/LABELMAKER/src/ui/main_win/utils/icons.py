import tkinter as tk
import os

class IconManager:
    """Manages icons for the application"""
    def __init__(self):
        self.batch_icon = None
        self.load_icons()

    def load_icons(self):
        """Load icons for buttons"""
        # Create a simple batch icon using a PhotoImage
        self.batch_icon = tk.PhotoImage(width=16, height=16)
        # Create a simple spreadsheet-like icon using pixels
        data = """
        ................
        .##############.
        .#            #.
        .#############..
        .#            #.
        .#############..
        .#            #.
        .#############..
        .#            #.
        .#############..
        .#            #.
        .#############..
        .#            #.
        .##############.
        ................
        ................
        """
        # Put the data into the image
        for y, line in enumerate(data.split()):
            for x, c in enumerate(line):
                if c == '#':
                    self.batch_icon.put('#666666', (x, y))

    def set_window_icon(self, window, icon_size='64', icon_type='icon'):
        """Set the window icon for any window in the application
        Args:
            window: The window to set the icon for
            icon_size: Size of the icon to use ('16', '32', '64')
            icon_type: Type of icon to use ('icon' for main icon, 'settings' for settings window)
        """
        import ctypes
        from PIL import Image, ImageTk
        
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                'assets', 'icons', f'{icon_type}{icon_size}.png')
        
        try:
            if os.path.exists(icon_path):
                # Load and set window icon
                icon = Image.open(icon_path)
                photo = ImageTk.PhotoImage(icon)
                window.iconphoto(True, photo)
                
                # Set taskbar icon
                if hasattr(ctypes, 'windll'):
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                        'Labelmaker.Codeium.1.0'
                    )
        except Exception as e:
            print(f"Failed to set window icon: {str(e)}")
