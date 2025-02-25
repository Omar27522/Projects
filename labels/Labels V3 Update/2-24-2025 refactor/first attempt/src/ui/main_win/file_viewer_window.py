import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
import time
import re
from ..window_icon_manager import WindowIconManager

class FileViewerWindow(tk.Toplevel):
    """A class for handling file viewing functionality"""
    def __init__(self, parent, config_manager, window_icon_manager):
        super().__init__(parent)
        
        self.parent = parent
        self.config_manager = config_manager
        self.window_icon_manager = window_icon_manager
        
        self.title("View Files")
        self.geometry("600x400")  # Default size
        self.minsize(375, 200)    # Minimum size
        
        # Add keyboard shortcuts
        self.bind('<Control-o>', lambda e: self.open_selected_file())
        self.bind('<Control-p>', lambda e: self.print_selected_file())
        
        # Enable window resizing and add maximize/minimize buttons
        self.resizable(True, True)
        
        # Set window icon using viewfiles-specific icon
        self.window_icon_manager.set_window_icon(self, '32', 'viewfiles')
        
        # Give initial focus
        self.focus_set()

        # Create main content frame
        main_content = tk.Frame(self)
        main_content.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Create top frame for controls
        top_frame = tk.Frame(main_content)
        top_frame.pack(fill=tk.X, padx=0, pady=1)

        # Add Pin (Always on Top) button
        self.window_always_on_top = tk.BooleanVar(value=False)
        self.window_top_btn = tk.Button(top_frame, text="Pin", bg='#C71585', relief='raised', width=8)
        self.window_top_btn.config(command=self.toggle_window_on_top)
        self.window_top_btn.pack(side=tk.LEFT, padx=2)

        # Add Label Count display
        self.label_count_label = tk.Label(
            top_frame,
            text="",  # Will be set by update_file_list
            font=('TkDefaultFont', 10, 'bold'),
            fg='#2ecc71'  # Green text
        )
        self.label_count_label.pack(side=tk.LEFT, padx=10)

        # Add Magnifier button
        self.is_magnified = tk.BooleanVar(value=False)
        self.magnifier_btn = tk.Button(top_frame, text="🔍", bg='#C71585', relief='raised', width=3,
                                     font=('TkDefaultFont', 14))
        self.magnifier_btn.config(command=self.toggle_magnification)
        self.magnifier_btn.pack(side=tk.LEFT, padx=2)

        # Add preview size control with cycling states
        self.preview_size = tk.IntVar(value=3)  # Default to largest size
        
        # Create and configure zoom button with plus icon
        self.zoom_btn = tk.Button(top_frame, text="➕", bg='#4169E1', relief='raised', width=3,  # Start with size 3 color
                               font=('TkDefaultFont', 14),
                               command=self.cycle_preview_size)
        self.zoom_btn.pack(side=tk.LEFT, padx=2)

        # Add mirror print toggle button
        self.is_mirror_print = tk.BooleanVar(value=self.config_manager.settings.mirror_print)
        self.mirror_btn = tk.Button(top_frame, text=" 🖨️ ", bg='#32CD32' if self.config_manager.settings.mirror_print else '#C71585', relief='raised', width=3,
                                  font=('TkDefaultFont', 14), anchor='center')
        self.mirror_btn.config(command=self.toggle_mirror_print)
        self.mirror_btn.pack(side=tk.LEFT, padx=2)
        
        # Add auto-switch toggle button
        self.auto_switch_btn = tk.Button(top_frame, text=" ⚡ ", bg='#90EE90' if self.parent.is_auto_switch.get() else '#C71585',
                                       relief='sunken' if self.parent.is_auto_switch.get() else 'raised', width=3,
                                       font=('TkDefaultFont', 14), anchor='center')
        self.auto_switch_btn.config(command=self.toggle_auto_switch)
        self.auto_switch_btn.pack(side=tk.LEFT, padx=2)

        # Create frame for listbox and scrollbar
        list_frame = tk.Frame(main_content)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Create listbox
        self.listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, font=('TkDefaultFont', 9))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create vertical scrollbar
        v_scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create horizontal scrollbar (initially hidden)
        self.h_scrollbar = tk.Scrollbar(list_frame, orient=tk.HORIZONTAL)

        # Configure scrollbars
        self.listbox.config(yscrollcommand=v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        v_scrollbar.config(command=self.listbox.yview)
        self.h_scrollbar.config(command=self.listbox.xview)

        # Create preview frame
        preview_frame = tk.Frame(main_content)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Create preview label
        self.preview_label = tk.Label(preview_frame)
        self.preview_label.pack(fill=tk.BOTH, expand=True)

        # Bind listbox selection event
        self.listbox.bind('<<ListboxSelect>>', self.show_preview)
        self.listbox.bind('<Double-Button-1>', lambda e: self.print_selected_file())
        
        # Update file list
        self.update_file_list()
        
    def toggle_window_on_top(self):
        """Toggle always on top state"""
        current_state = self.window_always_on_top.get()
        self.window_always_on_top.set(not current_state)
        self.attributes('-topmost', not current_state)
        if not current_state:
            self.lift()
            self.window_top_btn.config(
                text="Pin",
                bg='#90EE90',  # Light green when active
                relief='sunken'
            )
        else:
            self.window_top_btn.config(
                text="Pin",
                bg='#C71585',  # Velvet color when inactive
                relief='raised'
            )
            
    def toggle_magnification(self):
        """Toggle magnification state"""
        current_state = self.is_magnified.get()
        self.is_magnified.set(not current_state)
        new_size = 16 if not current_state else 9
        self.listbox.configure(font=('TkDefaultFont', new_size))
        if not current_state:
            self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        else:
            self.h_scrollbar.pack_forget()
        self.magnifier_btn.config(
            bg='#90EE90' if not current_state else '#C71585',
            relief='sunken' if not current_state else 'raised'
        )
        
    def cycle_preview_size(self):
        """Cycle through preview sizes: 1 -> 2 -> 3 -> 1"""
        current = self.preview_size.get()
        next_size = current + 1 if current < 3 else 1
        self.preview_size.set(next_size)
        # Update button appearance based on size
        colors = {1: '#C71585', 2: '#90EE90', 3: '#4169E1'}  # Different color for each state
        self.zoom_btn.config(bg=colors[next_size])
        # Refresh preview with new size
        self.show_preview(None)
        
    def toggle_mirror_print(self):
        """Toggle mirror print state"""
        current_state = self.is_mirror_print.get()
        self.is_mirror_print.set(not current_state)
        self.mirror_btn.config(
            bg='#32CD32' if not current_state else '#C71585'
        )
        # Save mirror print state to settings
        self.config_manager.settings.mirror_print = not current_state
        self.config_manager.save_settings()
        
    def toggle_auto_switch(self):
        """Toggle auto switch state"""
        current_state = self.parent.is_auto_switch.get()
        self.parent.is_auto_switch.set(not current_state)
        self.auto_switch_btn.config(
            bg='#90EE90' if not current_state else '#C71585',
            relief='sunken' if not current_state else 'raised'
        )
        
    def update_file_list(self):
        """Update the list of files in the current directory"""
        if not self.config_manager.settings.last_directory:
            return

        # Clear current list
        self.listbox.delete(0, tk.END)

        # Get list of PNG files
        png_files = [f for f in os.listdir(self.config_manager.settings.last_directory) 
                    if f.lower().endswith('.png')]
        png_files.sort()  # Sort files alphabetically

        # Update label count
        self.label_count_label.config(text=f"{len(png_files)} Labels")

        # Add files to listbox
        for file in png_files:
            self.listbox.insert(tk.END, file)

        # Select first item if available
        if png_files:
            self.listbox.selection_set(0)
            self.show_preview(None)
            
    def show_preview(self, event):
        """Show preview of selected file"""
        if not self.listbox.curselection():
            return

        # Get selected file
        selected = self.listbox.get(self.listbox.curselection())
        file_path = os.path.join(self.config_manager.settings.last_directory, selected)

        try:
            # Open and resize image
            image = Image.open(file_path)
            
            # Calculate new size based on preview_size setting
            scale_factors = {1: 0.5, 2: 0.75, 3: 1.0}  # Scale factors for each size setting
            scale = scale_factors[self.preview_size.get()]
            
            # Get original size
            orig_width, orig_height = image.size
            
            # Calculate new size
            new_width = int(orig_width * scale)
            new_height = int(orig_height * scale)
            
            # Resize image
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Update preview label
            self.preview_label.config(image=photo)
            self.preview_label.image = photo  # Keep reference
            
        except Exception as e:
            print(f"Error showing preview: {e}")
            self.preview_label.config(image='')
            
    def print_selected_file(self):
        """Print the selected file"""
        if not self.listbox.curselection():
            return

        # Get selected file
        selected = self.listbox.get(self.listbox.curselection())
        file_path = os.path.join(self.config_manager.settings.last_directory, selected)

        try:
            # Open image
            image = Image.open(file_path)
            
            # Mirror image if mirror print is enabled
            if self.is_mirror_print.get():
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
            
            # Save temporary file
            temp_path = os.path.join(os.path.dirname(file_path), "temp_print.png")
            image.save(temp_path)
            
            # Print image
            os.startfile(temp_path, "print")
            
            # Delete temporary file after a short delay
            self.after(1000, lambda: os.remove(temp_path) if os.path.exists(temp_path) else None)
            
            # Auto-switch to next file if enabled
            if self.parent.is_auto_switch.get():
                current_index = self.listbox.curselection()[0]
                if current_index < self.listbox.size() - 1:
                    self.listbox.selection_clear(0, tk.END)
                    self.listbox.selection_set(current_index + 1)
                    self.listbox.see(current_index + 1)
                    self.show_preview(None)
                    
        except Exception as e:
            print(f"Error printing file: {e}")
            
    def open_selected_file(self):
        """Open the selected file in the default image viewer"""
        if not self.listbox.curselection():
            return

        # Get selected file
        selected = self.listbox.get(self.listbox.curselection())
        file_path = os.path.join(self.config_manager.settings.last_directory, selected)

        try:
            os.startfile(file_path)
        except Exception as e:
            print(f"Error opening file: {e}")
