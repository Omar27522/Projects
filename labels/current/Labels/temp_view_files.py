
import os
import sys
import time
import tkinter as tk
from tkinter import messagebox
import subprocess

# Add Label Maker directory to path
label_maker_dir = r"C:\Users\Justin\Desktop\welcome_window\Label Maker"
if label_maker_dir not in sys.path:
    sys.path.insert(0, label_maker_dir)

try:
    # Run Label Maker directly with a command line argument to open in View Files mode
    process = subprocess.Popen([sys.executable, r"C:\Users\Justin\Desktop\welcome_window\Label Maker\main.pyw", "--view-files"])
    
    # Keep script running until Label Maker closes
    process.wait()
    
except Exception as e:
    print(f"Error: {str(e)}")
    try:
        messagebox.showerror("Error", f"Failed to run Label Maker: {str(e)}")
    except:
        pass
finally:
    # Clean up
    if os.path.exists(r"C:\Users\Justin\Desktop\welcome_window\temp_view_files.py"):
        try:
            os.remove(r"C:\Users\Justin\Desktop\welcome_window\temp_view_files.py")
        except:
            pass
