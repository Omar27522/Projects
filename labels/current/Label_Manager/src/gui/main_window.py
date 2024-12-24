"""
Main window implementation for the Label Manager application.
"""
import tkinter as tk
from tkinter import ttk
import logging
from PIL import Image, ImageTk
import os
from config import (
    WINDOW_TITLE, WINDOW_SIZE, THEME
)
from .frames import HeaderFrame, FileListFrame, PreviewFrame

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing main window")
        
        # Initialize main window
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        
        # Configure main window
        self.configure(bg=THEME['background_color'])
        
        # Configure styles first
        self.configure_styles()
        
        # Create main container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create header frame
        self.header_frame = HeaderFrame(self.main_container)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create main content frame
        content_frame = ttk.Frame(self.main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create file list frame
        self.file_list_frame = FileListFrame(content_frame, self)
        self.file_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create preview frame
        self.preview_frame = PreviewFrame(content_frame)
        self.preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Initialize status bar
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(
            self, 
            textvariable=self.status_var,
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg=THEME['header_background'],
            fg=THEME['header_foreground']
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind file selection to preview update
        self.file_list_frame.file_listbox.bind('<<ListboxSelect>>', self.file_list_frame.on_select)
        
        # Set initial status
        self.set_status("Ready")
        
        # Set window icon
        self.set_window_icon()
        
        # Create progress bar
        self.create_progress_bar()
        
        self.logger.info("Main window initialized successfully")
    
    def set_window_icon(self):
        """Set the application icon."""
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
            if os.path.exists(icon_path):
                icon = ImageTk.PhotoImage(file=icon_path)
                self.iconphoto(True, icon)
        except Exception as e:
            self.logger.warning(f"Could not set window icon: {e}")
    
    def create_progress_bar(self):
        """Create and configure the progress bar."""
        self.progress_frame = ttk.Frame(self)
        self.progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode='determinate',
            variable=self.progress_var
        )
        
        self.progress_label = ttk.Label(
            self.progress_frame,
            text="",
            style='Info.TLabel'
        )
        
    def show_progress(self, show=True, text=None):
        """Show or hide progress indicator."""
        # Placeholder for now - we'll implement proper progress indication later
        if show:
            self.set_status(text if text else "Processing...")
        else:
            self.set_status("")
            
    def update_progress(self, value, text=None):
        """Update the progress bar value and text."""
        self.progress_var.set(value)
        if text:
            self.progress_label.config(text=text)
        self.update_idletasks()
        
    def configure_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('Count.TLabel', font=('Helvetica', 12))
        style.configure('Search.TLabel', font=('Helvetica', 12))
        style.configure('FileList.TLabelframe', font=('Helvetica', 10))
        style.configure('Action.TButton', font=('Helvetica', 10))
        style.configure('Clear.TButton', font=('Helvetica', 8))
        style.configure('Info.TLabel', font=('TkDefaultFont', 10))
        style.configure('Link.TLabel', 
                       font=('TkDefaultFont', 10, 'underline'), 
                       foreground=THEME['header_background'])
        
    def get_preview_frame(self):
        """Get the preview frame instance."""
        return self.preview_frame
    
    def set_status(self, message):
        """Set the status bar message."""
        self.status_var.set(message)
        self.update_idletasks()
        
    def run(self):
        """Start the main event loop."""
        self.mainloop()
        
    def cleanup(self):
        """Clean up resources before exit."""
        self.logger.info("Cleaning up resources")
        if hasattr(self, 'file_list_frame'):
            self.file_list_frame.cleanup()
        if hasattr(self, 'preview_frame'):
            self.preview_frame.cleanup()
