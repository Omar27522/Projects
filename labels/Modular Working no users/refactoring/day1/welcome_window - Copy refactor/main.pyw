import os
import sys
import tkinter as tk
import traceback
import atexit
import ctypes

# Set DPI awareness before creating any windows
# This prevents scaling issues when interacting with system dialogs
try:
    # Try the newer API first (Windows 10+)
    awareness = ctypes.c_int(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    ctypes.windll.shcore.SetProcessDpiAwareness(awareness)
except AttributeError:
    # Fall back to older API (Windows 8.1 and earlier)
    ctypes.windll.user32.SetProcessDPIAware()
except Exception as e:
    # If it fails, just log it and continue
    print(f"Failed to set DPI awareness: {e}")

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.utils.logger import setup_logger
from src.ui.welcome_window import WelcomeWindow

# Setup logger
logger = setup_logger()

def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Call the default handler for KeyboardInterrupt
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))

    # Show error message to user
    try:
        error_msg = f"An unexpected error occurred:\n\n{str(exc_value)}\n\nPlease check the logs for details."
        tk.messagebox.showerror("Error", error_msg)
    except:
        pass  # If showing the error dialog fails, at least we logged the error

def cleanup():
    """Cleanup resources before exit"""
    logger.info("Application shutting down")
    try:
        # Use system temp directory instead of relative path
        temp_dir = os.path.join(os.environ.get('TEMP', os.getcwd()), 'labelmaker_temp')
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                try:
                    os.remove(os.path.join(temp_dir, file))
                except:
                    pass
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

def set_taskbar_icon(root):
    """Set the taskbar icon and Windows taskbar icon"""
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "assets", "icon_64.png")

        if os.path.exists(icon_path):
            # Load and set the icon using PhotoImage for the window icon
            icon = tk.PhotoImage(file=icon_path)
            root.iconphoto(True, icon)
            # Keep reference to prevent garbage collection
            root._icon = icon

            # Set the Windows taskbar icon
            myappid = 'labelmaker.app.ver3.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        else:
            logger.warning(f"Icon file not found at {icon_path}")
            # Try alternate path
            icon_path = os.path.join(script_dir, "assets", "icon", "icon_64.png")
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                root.iconphoto(True, icon)
                root._icon = icon
                myappid = 'labelmaker.app.ver3.0'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            else:
                logger.warning(f"Icon file not found at alternate path {icon_path}")
    except Exception as e:
        logger.error(f"Failed to set taskbar icon: {str(e)}")

if __name__ == "__main__":
    try:
        # Set exception handler
        sys.excepthook = handle_exception
        
        # Register cleanup function
        atexit.register(cleanup)
        
        # Create welcome window
        app = WelcomeWindow()
        
        # Set taskbar icon
        set_taskbar_icon(app)
        
        # Center the window
        app.center_window()
        
        # Start main loop
        app.mainloop()
        
    except Exception as e:
        # Log the error
        traceback.print_exc()
        
        # Show error message
        tk.messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
