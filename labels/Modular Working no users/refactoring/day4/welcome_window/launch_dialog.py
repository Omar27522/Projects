import os
import sys
import tkinter as tk
from PIL import Image, ImageTk
import ctypes
import time

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Set DPI awareness before creating any windows
try:
    awareness = ctypes.c_int(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    ctypes.windll.shcore.SetProcessDpiAwareness(awareness)
except AttributeError:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception as e:
    print(f"Failed to set DPI awareness: {e}")

# Cache for icon images to improve performance
_icon_cache = {}

def set_taskbar_icon(dialog, icon_name):
    try:
        print(f"Setting taskbar icon: {icon_name} for dialog {dialog}")
        
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "assets", icon_name)
        
        print(f"Icon path: {icon_path}")
        print(f"Icon exists: {os.path.exists(icon_path)}")
        
        if os.path.exists(icon_path):
            # Check if icon is already in cache
            if icon_path in _icon_cache:
                icon = _icon_cache[icon_path]
                print("Using cached icon")
            else:
                # Load and cache the icon
                print("Loading new icon")
                icon = tk.PhotoImage(file=icon_path)
                _icon_cache[icon_path] = icon
            
            # Set the icon for the dialog
            dialog.iconphoto(False, icon)  # Changed to False to only affect this window
            
            # Keep reference to prevent garbage collection
            dialog._icon = icon
            
            # Set unique AppUserModelID for Windows taskbar
            app_id = f'LabelMaker.{icon_name.split("_")[0]}'
            print(f"Setting AppUserModelID: {app_id}")
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
            
            # Set window title to include the dialog type for better taskbar identification
            dialog_type = icon_name.split("_")[0].capitalize()
            current_title = dialog.title()
            if dialog_type not in current_title:
                dialog.title(f"{dialog_type} - {current_title}")
                
            print(f"Icon set successfully for {dialog_type}")
        else:
            print(f"Icon file not found at {icon_path}")
    except Exception as e:
        print(f"Failed to set taskbar icon: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python launch_dialog.py <dialog_type>")
        sys.exit(1)
        
    dialog_type = sys.argv[1]
    
    if dialog_type == "create_label":
        from src.utils.dialog_handlers import create_label_dialog
        from src.config.config_manager import ConfigManager
        
        # Start timing for performance analysis
        start_time = time.time()
        
        # Create the config manager
        config_manager = ConfigManager()
        
        # Create a root window
        root = tk.Tk()
        root.withdraw()
        
        # Create the dialog
        dialog = create_label_dialog(root, config_manager, lambda: None)
        
        # Debug output
        print(f"Create Label dialog created, setting icon...")
        print(f"Dialog class: {dialog.__class__.__name__}")
        
        # Set the taskbar icon directly on the dialog
        set_taskbar_icon(dialog, "createlabels_64.png")
        
        # Force update to ensure icon is applied
        dialog.update_idletasks()
        
        # Print timing information
        print(f"Create Label dialog initialization time: {time.time() - start_time:.2f} seconds")
        
        # Run the dialog
        root.mainloop()
        
    elif dialog_type == "returns_data":
        from src.utils.dialog_handlers import create_labels_dialog
        from src.config.config_manager import ConfigManager
        
        # Start timing for performance analysis
        start_time = time.time()
        
        # Create a root window
        root = tk.Tk()
        root.withdraw()
        
        # Create the dialog
        dialog, _ = create_labels_dialog(root)
        
        # Debug output
        print(f"Returns Data dialog created, setting icon...")
        print(f"Dialog class: {dialog.__class__.__name__}")
        
        # Set the taskbar icon directly on the dialog
        set_taskbar_icon(dialog, "returnsdata_64.png")
        
        # Force update to ensure icon is applied
        dialog.update_idletasks()
        
        # Print timing information
        print(f"Returns Data dialog initialization time: {time.time() - start_time:.2f} seconds")
        
        # Run the dialog
        root.mainloop()
        
    elif dialog_type == "settings":
        from src.utils.dialog_handlers import create_settings_dialog_handler
        from src.config.config_manager import ConfigManager
        
        # Start timing for performance analysis
        start_time = time.time()
        
        # Create the config manager
        config_manager = ConfigManager()
        
        # Create a root window
        root = tk.Tk()
        root.withdraw()
        
        # Create the dialog
        dialog = create_settings_dialog_handler(root, config_manager, lambda dir=None: None)
        
        # Debug output
        print(f"Settings dialog created, setting icon...")
        print(f"Dialog class: {dialog.__class__.__name__}")
        
        # Set the taskbar icon directly on the dialog
        set_taskbar_icon(dialog, "settings_64.png")
        
        # Force update to ensure icon is applied
        dialog.update_idletasks()
        
        # Print timing information
        print(f"Settings dialog initialization time: {time.time() - start_time:.2f} seconds")
        
        # Run the dialog
        root.mainloop()
        
    elif dialog_type == "google_sheets":
        from src.utils.dialog_handlers import create_google_sheets_dialog_handler
        from src.config.config_manager import ConfigManager
        
        # Start timing for performance analysis
        start_time = time.time()
        
        # Create the config manager
        config_manager = ConfigManager()
        
        # Create a root window
        root = tk.Tk()
        root.withdraw()
        
        # Create the dialog
        dialog = create_google_sheets_dialog_handler(root, config_manager, None)
        
        # Debug output
        print(f"Google Sheets dialog created, setting icon...")
        print(f"Dialog class: {dialog.__class__.__name__}")
        
        # Set the taskbar icon directly on the dialog
        set_taskbar_icon(dialog, "settings_64.png")
        
        # Force update to ensure icon is applied
        dialog.update_idletasks()
        
        # Print timing information
        print(f"Google Sheets dialog initialization time: {time.time() - start_time:.2f} seconds")
        
        # Run the dialog
        root.mainloop()
    else:
        print(f"Unknown dialog type: {dialog_type}")
        sys.exit(1)
