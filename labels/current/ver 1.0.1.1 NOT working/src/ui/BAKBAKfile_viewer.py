import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
import pyautogui
import time
import re
from ..config import ConfigManager
from .window_state import WindowState

class FileViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Initialize window state and config
        self.window_state = WindowState()
        self.window_state.add_window(self)
        self.config_manager = ConfigManager()
        
        # Store the current PhotoImage
        self.current_photo = None
        
        # Window setup
        self.title("View Files")
        self.geometry("800x600")
        self.minsize(600, 400)
        
        # Main frame
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top control frame
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Pin button
        self.always_on_top = tk.BooleanVar(value=False)
        pin_btn = tk.Button(control_frame, text="Pin", 
                          bg='#C71585', relief='raised',
                          command=self.toggle_window_on_top,
                          width=8)
        pin_btn.pack(side=tk.LEFT, padx=2)
        
        # Labels count
        self.label_count = tk.Label(control_frame, text="Labels: 0", fg='green')
        self.label_count.pack(side=tk.LEFT, padx=10)
        
        # Search frame
        search_frame = tk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(search_frame, text="Find:").pack(side=tk.LEFT)
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.update_file_list)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # List and preview frame
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Listbox
        listbox_frame = tk.Frame(content_frame)
        listbox_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbars
        y_scroll = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scroll = tk.Scrollbar(content_frame, orient=tk.HORIZONTAL, command=self.listbox.xview)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.listbox.config(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        # Right side - Preview
        preview_frame = tk.Frame(content_frame, bg='white')
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.preview_label = tk.Label(preview_frame, bg='white')
        self.preview_label.pack(expand=True, fill=tk.BOTH)
        
        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Open button
        tk.Button(button_frame, text="Open", 
                 command=self.open_selected_file,
                 bg='#e3f2fd', activebackground='#bbdefb',
                 font=('TkDefaultFont', 9, 'bold'),
                 relief='raised', width=15, height=2).pack(side=tk.LEFT, padx=2)
        
        # Print button
        tk.Button(button_frame, text="Print",
                 command=self.print_selected_file,
                 bg='#e8f5e9', activebackground='#c8e6c9',
                 font=('TkDefaultFont', 9, 'bold'),
                 relief='raised', width=15, height=2).pack(side=tk.LEFT, padx=2)
        
        # Bind events
        self.listbox.bind('<<ListboxSelect>>', lambda e: self.after(100, self.show_preview))
        
        # Initial file list
        self.update_file_list()
    
    def show_preview(self):
        """Show preview of selected file"""
        try:
            selection = self.listbox.curselection()
            if not selection:
                self.preview_label.config(image='')
                self.current_photo = None
                return
            
            filename = self.listbox.get(selection[0])
            filepath = os.path.join(self.config_manager.settings.last_directory, filename)
            
            # Load image
            image = Image.open(filepath)
            
            # Get preview dimensions
            width = self.preview_label.winfo_width()
            height = self.preview_label.winfo_height()
            
            # Only resize if we have valid dimensions
            if width > 1 and height > 1:
                # Calculate aspect ratios
                img_ratio = image.width / image.height
                frame_ratio = width / height
                
                # Determine new size maintaining aspect ratio
                if img_ratio > frame_ratio:
                    new_width = width
                    new_height = int(width / img_ratio)
                else:
                    new_height = height
                    new_width = int(height * img_ratio)
                
                # Resize image
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create and store PhotoImage
            self.current_photo = ImageTk.PhotoImage(image)
            self.preview_label.config(image=self.current_photo)
            
        except Exception as e:
            print(f"Preview error: {str(e)}")
            self.preview_label.config(image='')
            self.current_photo = None
    
    def update_file_list(self, *args):
        """Update listbox with filtered files"""
        try:
            search_text = self.search_var.get().lower()
            self.listbox.delete(0, tk.END)
            
            if not self.config_manager.settings.last_directory:
                return
                
            files = [f for f in os.listdir(self.config_manager.settings.last_directory)
                    if f.lower().endswith('.png')]
            
            matched_files = [f for f in sorted(files)
                           if all(term in f.lower() 
                                for term in search_text.split())]
            
            for file in matched_files:
                self.listbox.insert(tk.END, file)
                
            self.label_count.config(text=f"Labels: {len(matched_files)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list files: {str(e)}")
    
    def open_selected_file(self):
        """Open selected file with default program"""
        selection = self.listbox.curselection()
        if not selection:
            return
            
        filename = self.listbox.get(selection[0])
        filepath = os.path.join(self.config_manager.settings.last_directory, filename)
        
        try:
            os.startfile(filepath)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")
    
    def print_selected_file(self):
        """Print selected file"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select a file to print.")
            return
            
        filename = self.listbox.get(selection[0])
        filepath = os.path.join(self.config_manager.settings.last_directory, filename)
        
        try:
            os.startfile(filepath, "print")
            self.after(1000, lambda: pyautogui.press('enter'))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print: {str(e)}")
    
    def toggle_window_on_top(self):
        """Toggle always on top state"""
        current = self.always_on_top.get()
        self.always_on_top.set(not current)
        self.attributes('-topmost', not current)
        if not current:
            self.lift()
