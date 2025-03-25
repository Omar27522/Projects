import os
import sys
import tkinter as tk
from PIL import Image, ImageTk
import ctypes

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

def set_taskbar_icon(dialog, icon_name):
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "assets", icon_name)
        
        if os.path.exists(icon_path):
            # Load and set the icon using PhotoImage for the window icon
            icon = tk.PhotoImage(file=icon_path)
            dialog.iconphoto(True, icon)
            
            # Keep reference to prevent garbage collection
            dialog._icon = icon
            
            # Set unique AppUserModelID for Windows taskbar
            app_id = f'LabelMaker.{icon_name.split("_")[0]}'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        else:
            print(f"Icon file not found at {icon_path}")
    except Exception as e:
        print(f"Failed to set taskbar icon: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python launch_dialog.py <dialog_type>")
        sys.exit(1)
        
    dialog_type = sys.argv[1]
    
    if dialog_type == "create_label":
        from src.utils.dialog_handlers import create_label_dialog
        from src.config.config_manager import ConfigManager
        
        # Create a dummy root window to avoid errors
        root = tk.Tk()
        root.withdraw()
        
        # Set the taskbar icon
        set_taskbar_icon(root, "createlabels_64.png")
        
        # Create the dialog
        config_manager = ConfigManager()
        dialog = create_label_dialog(root, config_manager, lambda: None)
        
        # Run the dialog
        root.mainloop()
        
    elif dialog_type == "returns_data":
        from src.utils.dialog_handlers import create_labels_dialog
        from src.config.config_manager import ConfigManager
        
        # Create a dummy root window to avoid errors
        root = tk.Tk()
        root.withdraw()
        
        # Set the taskbar icon
        set_taskbar_icon(root, "returnsdata_64.png")
        
        # Create the dialog
        dialog, _ = create_labels_dialog(root)
        
        # Run the dialog
        root.mainloop()
        
    elif dialog_type == "settings":
        from src.utils.dialog_handlers import create_settings_dialog_handler
        from src.config.config_manager import ConfigManager
        
        # Create a dummy root window to avoid errors
        root = tk.Tk()
        root.withdraw()
        
        # Set the taskbar icon
        set_taskbar_icon(root, "settings_64.png")
        
        # Create the dialog
        config_manager = ConfigManager()
        dialog = create_settings_dialog_handler(root, config_manager, lambda dir=None: None)
        
        # Run the dialog
        root.mainloop()
        
    elif dialog_type == "google_sheets":
        from src.utils.dialog_handlers import create_google_sheets_dialog_handler
        from src.config.config_manager import ConfigManager
        
        # Create a dummy root window to avoid errors
        root = tk.Tk()
        root.withdraw()
        
        # Set the taskbar icon
        set_taskbar_icon(root, "settings_64.png")
        
        # Create the dialog
        config_manager = ConfigManager()
        dialog = create_google_sheets_dialog_handler(root, config_manager, None)
        
        # Run the dialog
        root.mainloop()
    else:
        print(f"Unknown dialog type: {dialog_type}")
        sys.exit(1)
