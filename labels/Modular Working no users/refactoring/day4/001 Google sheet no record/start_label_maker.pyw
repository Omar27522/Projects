import os
import sys
import socket
import subprocess
import win32gui
import win32con
import win32process
import tkinter as tk
from tkinter import messagebox

def is_app_running(port=12345):
    """Check if the application is already running by trying to connect to its socket"""
    try:
        # Try to connect to the socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', port))
        sock.send(b'show')
        sock.close()
        return True
    except:
        # If we can't connect to the socket, try to find the window by title
        try:
            # Find all windows with "Label Maker" or "Welcome" in the title
            def callback(hwnd, windows):
                if win32gui.IsWindow(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if "Label Maker" in window_title or "Welcome" in window_title:
                        windows.append(hwnd)
                return True
            
            windows = []
            win32gui.EnumWindows(callback, windows)
            
            if windows:
                # Found a window, bring it to front
                hwnd = windows[0]
                
                # If window is minimized, restore it
                if win32gui.IsIconic(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                
                # Bring window to foreground
                win32gui.SetForegroundWindow(hwnd)
                
                # Flash the window to get user's attention
                win32gui.FlashWindow(hwnd, True)
                
                return True
        except:
            pass
        
        return False

def main():
    """Main entry point for the application"""
    # Check if the application is already running
    if is_app_running():
        # Application is already running, show a message and exit
        messagebox.showinfo("Label Maker", "Label Maker is already running and has been brought to the front.")
        return
    
    # Application is not running, start it
    try:
        # Get the path to the main.pyw script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        main_script = os.path.join(script_dir, "main.pyw")
        
        # Start the application using the Python executable
        python_exe = sys.executable
        subprocess.Popen([python_exe, main_script], 
                         creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        # Show error message
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Failed to start Label Maker: {str(e)}")
        root.destroy()

if __name__ == "__main__":
    main()
