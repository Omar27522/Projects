import os
import sys
import tkinter as tk
import traceback
import atexit
import ctypes
import socket
import time

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

class SingleInstanceApp:
    """Ensures only one instance of the application is running"""
    
    def __init__(self, port=12345):
        """
        Initialize the single instance app
        
        Args:
            port: Port to use for socket communication
        """
        self.port = port
        self.sock = None
        self.is_first_instance = self._check_instance()
    
    def _check_instance(self):
        """
        Check if another instance is already running
        
        Returns:
            bool: True if this is the first instance, False otherwise
        """
        try:
            # Try to create a socket server
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('localhost', self.port))
            self.sock.listen(5)
            
            # Start a thread to listen for other instances
            import threading
            self.thread = threading.Thread(target=self._listen_for_other_instances, daemon=True)
            self.thread.start()
            
            return True
        except socket.error:
            # Socket is already in use, another instance is running
            # Notify the first instance
            try:
                # Connect to the first instance
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(('localhost', self.port))
                sock.send(b'show')
                sock.close()
            except:
                pass
            
            return False
    
    def _listen_for_other_instances(self):
        """Listen for connections from other instances"""
        while True:
            try:
                client, addr = self.sock.accept()
                data = client.recv(1024)
                client.close()
                
                if data == b'show':
                    # Bring the window to front
                    self._bring_to_front()
            except:
                break
    
    def _bring_to_front(self):
        """Bring the application window to the front"""
        try:
            import win32gui
            import win32con
            
            # Find the window
            def callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd) and "Welcome" in win32gui.GetWindowText(hwnd):
                    windows.append(hwnd)
                return True
            
            windows = []
            win32gui.EnumWindows(callback, windows)
            
            if windows:
                # Bring the window to front
                win32gui.ShowWindow(windows[0], win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(windows[0])
        except ImportError:
            # Fall back to tkinter method
            if hasattr(self, 'app') and self.app:
                self.app.deiconify()
                self.app.lift()
                self.app.focus_force()
    
    def set_app(self, app):
        """Set the application instance"""
        self.app = app
    
    def cleanup(self):
        """Clean up resources"""
        if self.sock:
            self.sock.close()

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
        
        # Check if another instance is already running
        single_instance = SingleInstanceApp()
        
        if not single_instance.is_first_instance:
            # Another instance is already running
            logger.info("Application is already running. Exiting.")
            tk.messagebox.showinfo("Label Maker", "Label Maker is already running.")
            sys.exit(0)
        
        # Create the welcome window
        app = WelcomeWindow()
        
        # Set the app instance in the single instance handler
        single_instance.set_app(app)
        
        # Set the taskbar icon
        set_taskbar_icon(app)
        
        # Register cleanup for the single instance handler
        atexit.register(single_instance.cleanup)
        
        # Center the window
        app.center_window()
        
        # Start the main loop
        app.mainloop()
    except Exception as e:
        # Log any errors during startup
        logger.error(f"Error during startup: {str(e)}")
        traceback.print_exc()
        
        # Show error message to user
        try:
            error_msg = f"An error occurred during startup:\n\n{str(e)}\n\nPlease check the logs for details."
            tk.messagebox.showerror("Error", error_msg)
        except:
            pass  # If showing the error dialog fails, at least we logged the error
