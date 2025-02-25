import os
import ctypes
from PIL import Image, ImageTk
import tkinter as tk

class WindowIconManager:
    """A class for managing window icons in the application"""
    @staticmethod
    def set_window_icon(window, icon_size='64', icon_type='icon'):
        """Set the window icon for any window in the application
        Args:
            window: The window to set the icon for
            icon_size: Size of the icon to use ('16', '32', '64')
            icon_type: Type of icon to use ('icon' for main icon, 'settings' for settings window)
        """
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                'assets', f'{icon_type}_{icon_size}.png')
        
        if os.path.exists(icon_path):
            try:
                # Load the icon using PIL
                img = Image.open(icon_path)
                # Convert to PhotoImage for the window icon
                photo = ImageTk.PhotoImage(img)
                window.iconphoto(False, photo)  # False means don't use as default
                # Keep a reference to prevent garbage collection
                if not hasattr(window, '_icon'):
                    window._icon = photo
                
                # Set unique taskbar icon for Windows
                if isinstance(window, tk.Toplevel):
                    try:
                        # Generate unique app ID based on window type
                        if icon_type == 'settings':
                            app_id = 'labelmaker.settings.window'
                        elif icon_type == 'viewfiles':
                            app_id = 'labelmaker.viewfiles.window'
                        else:
                            app_id = 'labelmaker.main.window'
                        
                        # Set the app user model ID
                        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
                        
                        # Get the window handle
                        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
                        
                        # Associate the window with its unique app ID
                        SetWindowAttribute = ctypes.windll.user32.SetPropW
                        SetWindowAttribute(hwnd, "AppUserModelID", app_id)
                        
                    except Exception as e:
                        print(f"Failed to set taskbar icon: {str(e)}")
            except Exception as e:
                print(f"Failed to set window icon: {str(e)}")
