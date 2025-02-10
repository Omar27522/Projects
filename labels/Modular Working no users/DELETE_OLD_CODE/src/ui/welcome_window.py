import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import json
from datetime import datetime
from PIL import Image, ImageTk
import pyautogui
import pandas as pd
import re
import time

from src.ui.config import ConfigManager
from src.ui.barcode_generator import BarcodeGenerator
from src.ui.window_state import WindowState

class WelcomeWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        # Initialize window state
        self.window_state = WindowState()
        self.window_state.add_window(self)

        # Initialize config manager
        self.config_manager = ConfigManager()

        # Window setup
        self.title("Welcome")
        self.geometry("500x450")  # Increased window size
        self.resizable(False, False)  # Prevent resizing
        
        # Configure window style
        self.configure(bg='white')
        
        # Remove maximize button but keep minimize
        self.attributes('-toolwindow', 1)  # Remove minimize/maximize buttons
        self.attributes('-toolwindow', 0)  # Restore minimize button
        
        # Add title
        title_frame = tk.Frame(self, bg='white')
        title_frame.pack(pady=20)
        
        tk.Label(title_frame, text="Welcome", font=("Arial", 16, "bold"), bg='white').pack()
        tk.Label(title_frame, text="Label Maker V3", font=("Arial", 14), bg='white').pack()
        
        # Button frame
        button_frame = tk.Frame(self, bg='white')
        button_frame.pack(expand=True, padx=20)  # Added horizontal padding
        
        # Button colors (Material Design)
        colors = {
            'user': ('#4CAF50', '#A5D6A7'),        # Green, Light Green
            'management': ('#2196F3', '#90CAF9'),   # Blue, Light Blue
            'labels': ('#FF9800', '#FFCC80'),       # Orange, Light Orange
            'settings': ('#9E9E9E', '#E0E0E0')      # Gray, Light Gray
        }
        
        def create_button(parent, text, color_pair, command, big=False):
            """Create a colored button with hover effect"""
            color, light_color = color_pair
            btn = tk.Button(
                parent, 
                text=text,
                font=('Arial', 18 if big else 12, 'bold' if big else 'normal'),
                fg='white',
                bg=color,
                activeforeground='black',
                activebackground='white',
                relief='flat',
                borderwidth=0,
                width=20 if big else 15,
                height=4 if big else 2,
                cursor='hand2',
                command=command
            )
            
            # Add hover effect with delay
            hover_timer = None
            
            def apply_hover():
                btn['bg'] = light_color
                btn['fg'] = 'black'
            
            def remove_hover():
                btn['bg'] = color
                btn['fg'] = 'white'
            
            def on_enter(e):
                nonlocal hover_timer
                # Cancel any existing timer
                if hover_timer is not None:
                    btn.after_cancel(hover_timer)
                # Start new timer for hover effect
                hover_timer = btn.after(25, apply_hover)  # 150ms delay
            
            def on_leave(e):
                nonlocal hover_timer
                # Cancel any pending hover effect
                if hover_timer is not None:
                    btn.after_cancel(hover_timer)
                    hover_timer = None
                remove_hover()
                
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            
            return btn
        
        # Buttons with their respective styles
        self.user_btn = create_button(
            button_frame, "User", colors['user'], 
            self.user_action, big=True
        )
        
        self.management_btn = create_button(
            button_frame, "Management", colors['management'],
            self.open_management
        )
        
        self.labels_btn = create_button(
            button_frame, "Labels", colors['labels'],
            self.labels_action
        )
        
        self.settings_btn = create_button(
            button_frame, "Settings", colors['settings'],
            self.settings_action
        )
        
        # Grid layout for buttons
        button_frame.grid_columnconfigure(0, weight=3)  # Even more weight to User button column
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)
        button_frame.grid_rowconfigure(2, weight=1)
        
        # Place User button spanning both rows with more padding
        self.user_btn.grid(row=0, column=0, rowspan=2, padx=15, pady=10, sticky="nsew")
        
        # Place other buttons in the second column
        self.management_btn.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        self.labels_btn.grid(row=1, column=1, padx=(10, 10), pady=5, sticky="nsew")
        
        # Move settings to bottom, spanning both columns
        self.settings_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # Version label at bottom right
        version_label = tk.Label(
            self,
            text="Ver. 1.0.1.1",
            font=("Arial", 8),
            bg='white',
            fg='gray'
        )
        version_label.pack(side='bottom', anchor='se', padx=10, pady=5)

    def settings_action(self):
        """Show settings window"""
        try:
            # If settings window exists and is valid, focus it
            if hasattr(self, 'settings_window') and self.settings_window and self.settings_window.winfo_exists():
                self.settings_window.deiconify()
                self.settings_window.lift()
                self.settings_window.focus_force()
                return

            # Create settings window
            self.settings_window = tk.Toplevel(self)
            self.settings_window.title("Settings")
            self.settings_window.geometry("400x500")
            self.settings_window.minsize(400, 500)
            self.settings_window.resizable(False, False)
            self.settings_window.transient(self)  # Make it modal
            
            # Create main content frame with padding
            main_frame = ttk.Frame(self.settings_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Tools section
            ttk.Label(main_frame, text="Tools", font=('TkDefaultFont', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))
            
            tools_frame = ttk.Frame(main_frame)
            tools_frame.pack(fill=tk.X, pady=(0, 20))
            
            # Icon Maker button
            icon_maker_btn = ttk.Button(
                tools_frame,
                text="Icon Maker",
                command=self.open_icon_maker,
                width=20
            )
            icon_maker_btn.pack(side=tk.LEFT, padx=5)
            
            # Font size settings
            ttk.Label(main_frame, text="Font Sizes", font=('TkDefaultFont', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))
            
            # Large font size
            large_font_frame = ttk.Frame(main_frame)
            large_font_frame.pack(fill=tk.X, pady=5)
            ttk.Label(large_font_frame, text="Large Font Size:").pack(side=tk.LEFT)
            large_font_size = ttk.Entry(large_font_frame, width=10)
            large_font_size.pack(side=tk.RIGHT)
            large_font_size.insert(0, str(self.config_manager.settings.font_size_large))
            
            # Medium font size
            medium_font_frame = ttk.Frame(main_frame)
            medium_font_frame.pack(fill=tk.X, pady=5)
            ttk.Label(medium_font_frame, text="Medium Font Size:").pack(side=tk.LEFT)
            medium_font_size = ttk.Entry(medium_font_frame, width=10)
            medium_font_size.pack(side=tk.RIGHT)
            medium_font_size.insert(0, str(self.config_manager.settings.font_size_medium))
            
            # Separator
            ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=20)
            
            # Barcode settings
            ttk.Label(main_frame, text="Barcode Settings", font=('TkDefaultFont', 12, 'bold')).pack(anchor=tk.W, pady=(0, 10))
            
            # Barcode width
            width_frame = ttk.Frame(main_frame)
            width_frame.pack(fill=tk.X, pady=5)
            ttk.Label(width_frame, text="Barcode Width:").pack(side=tk.LEFT)
            barcode_width = ttk.Entry(width_frame, width=10)
            barcode_width.pack(side=tk.RIGHT)
            barcode_width.insert(0, str(self.config_manager.settings.barcode_width))
            
            # Barcode height
            height_frame = ttk.Frame(main_frame)
            height_frame.pack(fill=tk.X, pady=5)
            ttk.Label(height_frame, text="Barcode Height:").pack(side=tk.LEFT)
            barcode_height = ttk.Entry(height_frame, width=10)
            barcode_height.pack(side=tk.RIGHT)
            barcode_height.insert(0, str(self.config_manager.settings.barcode_height))

            def save_settings():
                try:
                    # Update settings
                    self.config_manager.settings.font_size_large = int(large_font_size.get())
                    self.config_manager.settings.font_size_medium = int(medium_font_size.get())
                    self.config_manager.settings.barcode_width = int(barcode_width.get())
                    self.config_manager.settings.barcode_height = int(barcode_height.get())
                    
                    # Save to file
                    self.config_manager.save_settings()
                    
                    # Close window
                    self.settings_window.destroy()
                    
                    # Show success message
                    messagebox.showinfo("Success", "Settings saved successfully!")
                    
                except ValueError as e:
                    messagebox.showerror("Error", f"Invalid value: {str(e)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

            # Create style for the save button
            settings_style = ttk.Style()
            settings_style.configure("Accent.TButton", font=('TkDefaultFont', 10, 'bold'))
            
            # Save button with styling
            save_btn = ttk.Button(
                main_frame,
                text="Save Settings",
                command=save_settings,
                style="Accent.TButton"
            )
            save_btn.pack(pady=20)
            
            # Center the settings window
            self.center_window(self.settings_window)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open settings window: {str(e)}")

    def open_icon_maker(self):
        """Open the Icon Maker window"""
        try:
            # Get the root directory (where main.pyw is)
            if getattr(sys, 'frozen', False):
                root_dir = os.path.dirname(sys.executable)
            else:
                # Get the directory containing the welcome_window.py file
                current_dir = os.path.dirname(os.path.abspath(__file__))
                # Go up two levels to get to the root directory
                root_dir = os.path.dirname(os.path.dirname(current_dir))
            
            icon_maker_path = os.path.join(root_dir, 'assets', 'icon_maker', 'make_icons.py')
            
            # Verify the path exists
            if not os.path.exists(icon_maker_path):
                raise FileNotFoundError(f"Icon Maker not found at: {icon_maker_path}")
            
            # Close the settings window
            if hasattr(self, 'settings_window') and self.settings_window and self.settings_window.winfo_exists():
                self.settings_window.destroy()
            
            # Run the Icon Maker
            subprocess.Popen([sys.executable, icon_maker_path], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
        except Exception as e:
            error_msg = f"Failed to open Icon Maker:\n\nError: {str(e)}"
            if isinstance(e, FileNotFoundError):
                error_msg += f"\n\nTried path: {icon_maker_path}"
            messagebox.showerror("Error", error_msg)

    def user_action(self):
        # To be implemented later
        pass

    def open_management(self):
        """Open the View Files window"""
        try:
            # Check if labels directory is set and exists
            if not self.config_manager.settings.last_directory or not os.path.exists(self.config_manager.settings.last_directory):
                messagebox.showinfo("Labels Required", 
                    "Please select a Labels directory before managing files.\n\n"
                    "Click the 'Labels' button to set your Labels directory.")
                return
                
            # Import here to avoid circular import
            from .file_viewer import FileViewer
            
            # Check for existing FileViewer
            file_viewer = self.window_state.get_window_by_type(FileViewer)
            
            if file_viewer:
                # If exists, bring it to front
                file_viewer.deiconify()
                file_viewer.lift()
                file_viewer.focus_force()
            else:
                # Hide welcome window and open view files window
                self.withdraw()
                
                # Create new FileViewer
                file_viewer = FileViewer()
                
                # Set up close handler to show welcome window again
                def on_close():
                    self.window_state.remove_window(file_viewer)
                    file_viewer.destroy()
                    self.deiconify()
                    self.lift()
                    self.focus_force()
                
                file_viewer.protocol("WM_DELETE_WINDOW", on_close)
                
                # Center the view files window
                self.center_window(file_viewer)
                
                # Start view files window's main loop
                file_viewer.mainloop()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file viewer: {str(e)}")
            self.deiconify()  # Show welcome window again

    def on_management_close(self):
        """Handle management window closing"""
        # Show welcome window again
        self.deiconify()

    def center_window(self, window):
        """Center a window on the screen"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def labels_action(self):
        """Select directory for saving labels"""
        try:
            initial_dir = self.config_manager.settings.last_directory
            if not initial_dir or not os.path.exists(initial_dir):
                initial_dir = os.path.expanduser("~")
                
            directory = filedialog.askdirectory(
                title="Select Labels Directory",
                initialdir=initial_dir
            )
            
            if directory:
                # Convert to absolute path and normalize
                directory = os.path.abspath(os.path.normpath(directory))
                
                # Update settings with new directory
                self.config_manager.settings.last_directory = directory
                self.config_manager.save_settings()
                
                messagebox.showinfo("Success", 
                    f"Labels directory set to:\n{directory}\n\n"
                    "You can now open the View Files window.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set labels directory: {str(e)}")
