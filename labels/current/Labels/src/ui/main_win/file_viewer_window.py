import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
import time
import re
from ..window_icon_manager import WindowIconManager

class FileViewerWindow(tk.Tk):
    """A class for handling file viewing functionality"""
    def __init__(self, config_manager, window_icon_manager):
        super().__init__()
        
        self.config_manager = config_manager
        self.window_icon_manager = window_icon_manager
        
        # Store the show_label_maker function reference
        self.show_label_maker = None
        
        self.title("View Files")
        self.geometry("500x400")  # More compact default size
        self.minsize(400, 300)    # Smaller minimum size
        
        # Add keyboard shortcuts
        self.bind('<Control-o>', lambda e: self.open_selected_file())
        self.bind('<Control-p>', lambda e: self.print_selected_file())
        
        # Enable window resizing and add maximize/minimize buttons
        self.resizable(True, True)
        
        # Set window icon using viewfiles-specific icon
        self.window_icon_manager.set_window_icon(self, '32', 'viewfiles')
        
        # Give initial focus
        self.focus_set()

        # Create main content frame with less padding
        main_content = tk.Frame(self)
        main_content.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Create top frame for controls with less padding
        top_frame = tk.Frame(main_content)
        top_frame.pack(fill=tk.X, padx=0, pady=0)

        # Add Pin (Always on Top) button - magenta color
        self.window_always_on_top = tk.BooleanVar(value=False)
        self.window_top_btn = tk.Button(top_frame, text="Pin", bg='#C71585', fg='white',
                                      relief='raised', width=8)
        self.window_top_btn.config(command=self.toggle_window_on_top)
        self.window_top_btn.pack(side=tk.LEFT, padx=1)

        # Add Label Count display - bright green color
        self.label_count_label = tk.Label(
            top_frame,
            text="Labels: 0",  # Will be updated by update_file_list
            font=('TkDefaultFont', 10),
            fg='#00FF00'  # Bright green
        )
        self.label_count_label.pack(side=tk.LEFT, padx=5)

        # Add Magnifier button - blue color
        self.is_magnified = tk.BooleanVar(value=False)
        self.magnifier_btn = tk.Button(top_frame, text="🔍", bg='#4169E1', fg='white',
                                     relief='raised', width=3)
        self.magnifier_btn.config(command=self.toggle_magnification)
        self.magnifier_btn.pack(side=tk.LEFT, padx=1)

        # Add zoom button - blue color
        self.preview_size = tk.IntVar(value=3)  # Start with largest size
        self.zoom_btn = tk.Button(top_frame, text="➕", bg='#4169E1', fg='white',
                                relief='raised', width=3,
                                command=self.cycle_preview_size)
        self.zoom_btn.pack(side=tk.LEFT, padx=1)

        # Add print button - magenta color
        self.print_btn = tk.Button(top_frame, text="🖨️", bg='#C71585', fg='white',
                                relief='raised', width=3,
                                command=self.print_selected_file)
        self.print_btn.pack(side=tk.LEFT, padx=1)

        # Add lightning button - green color
        self.is_auto_switch = tk.BooleanVar(value=False)
        self.auto_switch_btn = tk.Button(top_frame, text="⚡", bg='#32CD32', fg='white',
                                     relief='raised', width=3)
        self.auto_switch_btn.config(command=self.toggle_auto_switch)
        self.auto_switch_btn.pack(side=tk.LEFT, padx=1)

        # Add Label Maker button - green color
        self.label_maker_btn = tk.Button(top_frame, text="Label Maker", bg='#32CD32', fg='white',
                                       font=('TkDefaultFont', 10), command=self.show_label_maker)
        self.label_maker_btn.pack(side=tk.RIGHT, padx=5)

        # Create search frame
        search_frame = tk.Frame(main_content)
        search_frame.pack(fill=tk.X, padx=1, pady=1)

        # Add Find label
        find_label = tk.Label(search_frame, text="Find:", font=('TkDefaultFont', 10))
        find_label.pack(side=tk.LEFT, padx=1)

        # Add search entry
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        self.search_entry.bind('<KeyRelease>', self.filter_files)

        # Create main split frame
        split_frame = tk.Frame(main_content)
        split_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Create left frame for listbox (give it more initial space)
        left_frame = tk.Frame(split_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(1, 3))
        # Set initial weight for left frame
        split_frame.grid_columnconfigure(0, weight=2)

        # Create frame for listbox and scrollbar
        list_frame = tk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Create listbox with smaller font
        self.listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, font=('TkDefaultFont', 9))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create vertical scrollbar
        v_scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create horizontal scrollbar
        h_scrollbar = tk.Scrollbar(left_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Configure scrollbars
        self.listbox.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        v_scrollbar.config(command=self.listbox.yview)
        h_scrollbar.config(command=self.listbox.xview)

        # Create right frame for preview (give it less initial space)
        right_frame = tk.Frame(split_frame, width=200)  # Set initial width
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(3, 1))
        right_frame.pack_propagate(False)  # Prevent frame from shrinking
        # Set initial weight for right frame
        split_frame.grid_columnconfigure(1, weight=1)

        # Create preview label with white background
        self.preview_label = tk.Label(right_frame, bg='white')
        self.preview_label.pack(fill=tk.BOTH, expand=True)

        # Create bottom frame for action buttons
        bottom_frame = tk.Frame(main_content)
        bottom_frame.pack(fill=tk.X, padx=1, pady=1)

        # Add Open and Print buttons
        self.open_btn = tk.Button(bottom_frame, text="Open", width=15, command=self.open_selected_file)
        self.open_btn.pack(side=tk.LEFT, padx=1)

        self.print_btn = tk.Button(bottom_frame, text="Print", width=15, command=self.print_selected_file)
        self.print_btn.pack(side=tk.LEFT, padx=1)

        # Bind listbox selection event
        self.listbox.bind('<<ListboxSelect>>', self.show_preview)
        self.listbox.bind('<Double-Button-1>', lambda e: self.print_selected_file())
        
        # Update file list
        self.update_file_list()
        
        # Make this window control the application lifecycle
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def toggle_window_on_top(self):
        """Toggle always on top state"""
        current_state = self.window_always_on_top.get()
        self.window_always_on_top.set(not current_state)
        self.attributes('-topmost', not current_state)
        if not current_state:
            self.lift()
            self.window_top_btn.config(
                text="Pin",
                bg='#32CD32',  # Green when active
                relief='sunken'
            )
        else:
            self.window_top_btn.config(
                text="Pin",
                bg='#C71585',  # Magenta when inactive
                relief='raised'
            )
            
    def toggle_magnification(self):
        """Toggle magnification state"""
        current_state = self.is_magnified.get()
        self.is_magnified.set(not current_state)
        new_size = 9 if current_state else 16  # Changed to match old code: 16pt when magnified
        self.listbox.configure(font=('TkDefaultFont', new_size))
        self.magnifier_btn.config(
            bg='#32CD32' if not current_state else '#4169E1',  # Green when active, blue when inactive
            relief='sunken' if not current_state else 'raised'
        )
        
    def cycle_preview_size(self):
        """Cycle through preview sizes: 3 -> 4 -> 5 -> 3"""
        current = self.preview_size.get()
        next_size = current + 1 if current < 5 else 3  # Cycle between 3 and 5
        self.preview_size.set(next_size)
        # Update button appearance based on size
        colors = {3: '#4169E1', 4: '#32CD32', 5: '#C71585'}  # Blue, green, magenta
        self.zoom_btn.config(bg=colors[next_size])
        # Refresh preview with new size
        self.show_preview(None)
        
    def toggle_auto_switch(self):
        """Toggle auto switch state"""
        current_state = self.is_auto_switch.get()
        self.is_auto_switch.set(not current_state)
        self.auto_switch_btn.config(
            bg='#32CD32',  # Always green
            relief='sunken' if not current_state else 'raised'
        )
        
    def show_label_maker(self):
        """Show the Label Maker window"""
        # This method is currently empty, as the Label Maker window is not implemented
        pass
        
    def update_file_list(self):
        """Update the list of files in the current directory"""
        if not self.config_manager.settings.last_directory:
            return

        # Clear current list
        self.listbox.delete(0, tk.END)
        
        # Get list of PNG files from the last used directory
        try:
            png_files = [f for f in os.listdir(self.config_manager.settings.last_directory) 
                        if f.lower().endswith('.png')]
            png_files.sort()  # Sort files alphabetically
            
            # Store files for filtering
            self.all_files = png_files
            
            # Update label count with green color
            self.label_count_label.config(text=f"Labels: {len(png_files)}")
            
            # Add files to listbox
            for file in png_files:
                self.listbox.insert(tk.END, file)
                
            # Select first item if available
            if png_files:
                self.listbox.selection_set(0)
                self.show_preview(None)
        except Exception as e:
            print(f"Error updating file list: {e}")
            
    def show_preview(self, event):
        """Show preview of selected file"""
        if not self.listbox.curselection():
            # Clear preview if nothing selected
            self.preview_label.config(image='')
            return

        # Get selected file
        selected = self.listbox.get(self.listbox.curselection())
        file_path = os.path.join(self.config_manager.settings.last_directory, selected)

        try:
            # Open image
            image = Image.open(file_path)
            
            # Get preview frame size
            preview_width = self.preview_label.winfo_width()
            preview_height = self.preview_label.winfo_height()
            
            if preview_width > 1 and preview_height > 1:  # Only resize if we have valid dimensions
                # Calculate scale factors
                width_scale = preview_width / image.width
                height_scale = preview_height / image.height
                
                # Use the smaller scale to fit the image while maintaining aspect ratio
                scale = min(width_scale, height_scale) * 0.7  # 70% of available space
                
                # Calculate new dimensions
                new_width = int(image.width * scale)
                new_height = int(image.height * scale)
                
                # Apply preview size adjustment - larger scale factors
                size_factors = {3: 1.0, 4: 1.3, 5: 1.6}  # Increased scale factors
                size_scale = size_factors.get(self.preview_size.get(), 1.0)
                
                new_width = int(new_width * size_scale)
                new_height = int(new_height * size_scale)
                
                # Ensure minimum size
                new_width = max(new_width, 100)
                new_height = max(new_height, 100)
                
                # Resize image
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Update preview
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
            
            # Save temporary file
            temp_path = os.path.join(os.path.dirname(file_path), "temp_print.png")
            image.save(temp_path)
            
            # Print image
            os.startfile(temp_path, "print")
            
            # Delete temporary file after a short delay
            self.after(1000, lambda: os.remove(temp_path) if os.path.exists(temp_path) else None)
            
            # Auto-switch to next file if enabled
            if self.is_auto_switch.get():
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

    def filter_files(self, event=None):
        """Filter files based on search text"""
        search_text = self.search_entry.get().lower()
        self.listbox.delete(0, tk.END)
        
        for file in self.all_files:
            if search_text in file.lower():
                self.listbox.insert(tk.END, file)

    def on_close(self):
        """Handle window close event"""
        # Save any settings if needed
        self.config_manager.save_settings()
        
        # Destroy all windows and quit the application
        self.destroy()
        self.quit()
