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
        """Bring the application window to the front, even if minimized"""
        try:
            # Try to use the Windows API for better control
            try:
                import win32gui
                import win32con
                import win32process
                import win32api
                import psutil
                import os
                
                # Get the current process ID
                current_pid = os.getpid()
                
                # Find all windows belonging to our process
                def callback(hwnd, windows):
                    # Check if window is visible or minimized
                    if win32gui.IsWindow(hwnd):
                        # Get the process ID for this window
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        
                        # Check if this window belongs to our application
                        window_title = win32gui.GetWindowText(hwnd)
                        if (pid == current_pid or 
                            "Label Maker" in window_title or 
                            "Welcome" in window_title):
                            windows.append(hwnd)
                    return True
                
                windows = []
                win32gui.EnumWindows(callback, windows)
                
                if windows:
                    # Get the main window (usually the first one)
                    hwnd = windows[0]
                    
                    # If window is minimized, restore it
                    if win32gui.IsIconic(hwnd):
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    
                    # Bring window to foreground
                    win32gui.SetForegroundWindow(hwnd)
                    
                    # Flash the window to get user's attention
                    win32gui.FlashWindow(hwnd, True)
                    
                    # Force the window to redraw
                    win32gui.RedrawWindow(hwnd, None, None, 
                                         win32con.RDW_INVALIDATE | 
                                         win32con.RDW_ERASE | 
                                         win32con.RDW_FRAME | 
                                         win32con.RDW_ALLCHILDREN)
                    
                    return True
                
            except ImportError:
                # If win32gui is not available, fall back to simpler method
                pass
                
            # Fall back to tkinter method if win32gui approach didn't work
            if hasattr(self, 'app') and self.app:
                # Make sure window is not minimized
                self.app.deiconify()
                
                # Bring to front
                self.app.attributes('-topmost', True)
                self.app.update()
                self.app.attributes('-topmost', False)
                
                # Force focus
                self.app.lift()
                self.app.focus_force()
                
                # Update the window to ensure changes take effect
                self.app.update_idletasks()
                
                return True
                
            return False
            
        except Exception as e:
            print(f"Error bringing window to front: {str(e)}")
            return False
    
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
        
        # Create a file association for .pyw files to ensure clicking on main.pyw
        # will use the single instance mechanism
        try:
            import winreg
            
            # Get the path to the Python executable
            python_exe = sys.executable
            
            # Get the full path to this script
            script_path = os.path.abspath(__file__)
            
            # Create a registry key for the file association
            # This is done silently and only affects this user's settings
            try:
                # Check if we have write access to the registry
                test_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\Test")
                winreg.CloseKey(test_key)
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\Test")
                
                # We have access, so create the file association
                key_path = r"Software\Classes\LabelMakerApp"
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
                winreg.SetValue(key, "", winreg.REG_SZ, "Label Maker Application")
                winreg.CloseKey(key)
                
                # Create command key
                cmd_key_path = f"{key_path}\\shell\\open\\command"
                cmd_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, cmd_key_path)
                winreg.SetValue(cmd_key, "", winreg.REG_SZ, f'"{python_exe}" "{script_path}"')
                winreg.CloseKey(cmd_key)
                
                # Associate .labelmaker extension
                ext_key_path = r"Software\Classes\.labelmaker"
                ext_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, ext_key_path)
                winreg.SetValue(ext_key, "", winreg.REG_SZ, "LabelMakerApp")
                winreg.CloseKey(ext_key)
                
                logger.info("File association created successfully")
            except Exception as e:
                # If we can't create the registry keys, just log it and continue
                logger.warning(f"Could not create file association: {str(e)}")
        except ImportError:
            # If winreg is not available, just log it and continue
            logger.warning("winreg module not available, skipping file association")
        
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
