import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
import pyautogui
import time
import re

from src.config import ConfigManager
from .window_state import WindowState

class FileViewer(tk.Toplevel):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        # Initialize window state
        self.window_state = WindowState()
        self.window_state.add_window(self)

        self.config_manager = ConfigManager()

        # Store the current PhotoImage
        self.current_photo = None

        # Verify labels directory exists
        if not self.config_manager.settings.last_directory or not os.path.exists(self.config_manager.settings.last_directory):
            messagebox.showerror("Error", 
                "Labels directory not set or does not exist.\n"
                "Please set a valid Labels Location in the Welcome Window.")
            self.destroy()
            return

        # Add tracking for last printed label
        self.last_print_time = None
        self.last_printed_upc = None
        self.last_print_label = None

        self.title("View Files")
        self.geometry("600x400")  # Match old version size
        self.minsize(375, 200)    # Set minimum size
        
        # Configure grid weights for proper resizing
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Main content frame
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top control frame
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Pin button (Always on Top)
        self.always_on_top = tk.BooleanVar(value=False)
        pin_btn = tk.Button(control_frame, text="Pin", 
                          bg='#C71585', relief='raised',
                          command=self.toggle_window_on_top,
                          width=8)
        pin_btn.pack(side=tk.LEFT, padx=2)
        
        # Labels count
        self.labels_count = tk.Label(control_frame, text=f"Labels: {len(os.listdir(self.config_manager.settings.last_directory))}", 
                                   fg='green')
        self.labels_count.pack(side=tk.LEFT, padx=10)

        # Magnifier button
        is_magnified = tk.BooleanVar(value=False)
        magnifier_btn = tk.Button(control_frame, text="🔍", bg='#C71585', relief='raised', width=3,
                                font=('TkDefaultFont', 14))

        def toggle_magnification():
            current_state = is_magnified.get()
            new_size = 16 if current_state else 9
            self.listbox.configure(font=('TkDefaultFont', new_size))
            if current_state:
                h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            else:
                h_scrollbar.pack_forget()
            magnifier_btn.config(
                bg='#90EE90' if current_state else '#C71585',
                relief='sunken' if current_state else 'raised'
            )

        magnifier_btn.config(
            command=lambda: [is_magnified.set(not is_magnified.get()),
                           toggle_magnification()]
        )
        magnifier_btn.pack(side=tk.LEFT, padx=2)

        # Add preview size control with cycling states
        preview_size = tk.IntVar(value=3)  # Default to largest size

        def cycle_preview_size():
            """Cycle through preview sizes: 1 -> 2 -> 3 -> 1"""
            current = preview_size.get()
            next_size = current + 1 if current < 3 else 1
            preview_size.set(next_size)
            # Update button appearance based on size
            colors = {1: '#C71585', 2: '#90EE90', 3: '#4169E1'}  # Different color for each state
            zoom_btn.config(bg=colors[next_size])
            # Refresh preview with new size
            show_preview(None)

        zoom_btn = tk.Button(control_frame, text="➕", bg='#4169E1', relief='raised', width=3,
                           font=('TkDefaultFont', 14))
        zoom_btn.config(command=cycle_preview_size)
        zoom_btn.pack(side=tk.LEFT, padx=2)

        # Add New Label button
        new_label_btn = tk.Button(control_frame, text="New Label", bg='#3498db', relief='raised', width=10,
                                font=('TkDefaultFont', 10, 'bold'), fg='white')

        def open_label_maker():
            try:
                # Import here to avoid circular import
                from .main_window import MainWindow

                # Check for existing Label Maker
                label_maker = self.window_state.get_window_by_type(MainWindow)

                if label_maker:
                    # If exists, bring it to front
                    label_maker.deiconify()
                    label_maker.lift()
                    label_maker.focus_force()
                else:
                    # Create Label Maker window
                    label_maker = MainWindow()

                    # Set up close handler
                    def on_close():
                        self.window_state.remove_window(label_maker)
                        label_maker.destroy()

                    label_maker.protocol("WM_DELETE_WINDOW", on_close)

                    # Center the window
                    label_maker.update_idletasks()
                    x = self.winfo_x() + (self.winfo_width() - label_maker.winfo_width()) // 2
                    y = self.winfo_y() + (self.winfo_height() - label_maker.winfo_height()) // 2
                    label_maker.geometry(f"+{x}+{y}")

                    # Start Label Maker
                    label_maker.mainloop()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to open Label Maker: {str(e)}")

        new_label_btn.config(command=open_label_maker)
        new_label_btn.pack(side=tk.LEFT, padx=5)

        # Last printed label - clickable and shows time ago
        self.last_print_label = tk.Label(control_frame, text="", font=('TkDefaultFont', 9), fg='#666666', cursor="")
        self.last_print_label.pack(side=tk.LEFT, padx=10)

        # Add mirror print toggle
        self.is_mirror_print = tk.BooleanVar(value=False)
        mirror_btn = tk.Button(control_frame, text="🖨️", bg='#C71585', relief='raised', width=4)

        def toggle_mirror_print():
            current_state = self.is_mirror_print.get()
            mirror_btn.config(
                bg='#90EE90' if current_state else '#C71585',
                relief='sunken' if current_state else 'raised'
            )

        mirror_btn.config(
            command=lambda: [self.is_mirror_print.set(not self.is_mirror_print.get()),
                           toggle_mirror_print()]
        )

        # Pack mirror button after the label
        mirror_btn.pack(side=tk.RIGHT, padx=(0, 2))

        # Start the update cycle
        self.update_last_print_time()
        
        # Search frame
        search_frame = tk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(search_frame, text="Find:").pack(side=tk.LEFT)
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # List frame with preview
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side for listbox
        listbox_frame = tk.Frame(list_frame)
        listbox_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Listbox with scrollbar
        self.listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = tk.Scrollbar(listbox_frame, orient=tk.HORIZONTAL, command=self.listbox.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.listbox.config(xscrollcommand=h_scrollbar.set)
        
        # Right side for preview
        preview_frame = tk.Frame(list_frame, bg='white')
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Preview label
        self.preview_label = tk.Label(preview_frame, bg='white')
        self.preview_label.pack(expand=True, fill=tk.BOTH)
        
        def show_preview(*args):
            """Show preview of selected file in the preview frame"""
            selection = self.listbox.curselection()
            if not selection:
                self.preview_label.config(image='')
                return

            file_name = self.listbox.get(selection[0])
            file_path = os.path.join(self.config_manager.settings.last_directory, file_name)

            try:
                img = Image.open(file_path)
                # Calculate size to fit in preview frame while maintaining aspect ratio
                preview_width = preview_frame.winfo_width()
                preview_height = preview_frame.winfo_height()
                
                if preview_width > 1 and preview_height > 1:  # Only resize if frame has valid dimensions
                    # Adjust preview size based on selected size button (1 = 70%, 2 = 80%, 3 = 95%)
                    size_map = {1: 0.70, 2: 0.80, 3: 0.95}  # Map button numbers to size multipliers
                    size_multiplier = size_map[preview_size.get()]
                    preview_width = int(preview_width * size_multiplier)
                    preview_height = int(preview_height * size_multiplier)
                    
                    img_ratio = img.width / img.height
                    frame_ratio = preview_width / preview_height
                    
                    if img_ratio > frame_ratio:
                        # Image is wider than frame
                        display_width = preview_width
                        display_height = int(preview_width / img_ratio)
                    else:
                        # Image is taller than frame
                        display_height = preview_height
                        display_width = int(preview_height * img_ratio)
                    
                    img = img.resize((display_width, display_height), Image.Resampling.LANCZOS)
                
                # Update the current photo
                self.current_photo = ImageTk.PhotoImage(img)
                self.preview_label.config(image=self.current_photo)
            except Exception as e:
                self.preview_label.config(image='')
                print(f"Failed to preview image: {str(e)}")
        
        # Bind listbox selection with a delay
        self.listbox.bind('<<ListboxSelect>>', lambda e: self.after(100, show_preview))
        
        # Update preview when window is resized
        def on_resize(event):
            self.after(100, show_preview)  # Add delay for resize too
        preview_frame.bind('<Configure>', on_resize)

        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Open button
        open_btn = tk.Button(button_frame, text="Open", 
                           command=lambda: self.open_selected_file(self.listbox),
                           bg='#e3f2fd', activebackground='#bbdefb',
                           font=('TkDefaultFont', 9, 'bold'),
                           relief='raised', width=15, height=2)
        open_btn.pack(side=tk.LEFT, padx=2)
        
        # Print button
        print_btn = tk.Button(button_frame, text="Print",
                            command=lambda: self.print_selected_file(self.listbox),
                            bg='#e8f5e9', activebackground='#c8e6c9',
                            font=('TkDefaultFont', 9, 'bold'),
                            relief='raised', width=15, height=2)
        print_btn.pack(side=tk.LEFT, padx=2)
        
        # Update file list
        def update_file_list(*args):
            """Update the listbox based on search text"""
            search_text = self.search_var.get().lower()
            self.listbox.delete(0, tk.END)
            
            try:
                files = os.listdir(self.config_manager.settings.last_directory)
                png_files = [f for f in files if f.lower().endswith('.png')]
                matched_files = []
                
                # Split search into terms
                search_terms = search_text.split()
                
                for file in sorted(png_files):
                    file_lower = file.lower()
                    # If no search terms, include all files
                    if not search_terms:
                        matched_files.append(file)
                    # Check if ALL search terms are in the filename
                    elif all(term in file_lower for term in search_terms):
                        matched_files.append(file)
                
                for file in matched_files:
                    self.listbox.insert(tk.END, file)
                    
                if len(matched_files) == 0:
                    self.listbox.insert(tk.END, "No matching files found")
                    self.labels_count.config(text="No Labels", fg='#e74c3c')  # Red text for no labels
                else:
                    self.listbox.selection_clear(0, tk.END)
                    self.listbox.selection_set(0)
                    self.listbox.see(0)
                    self.labels_count.config(text=f"Labels: {len(matched_files)}", fg='#2ecc71')  # Green text for label count
                    # Show preview of first item
                    show_preview(None)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read directory: {str(e)}")

        # Bind the search variable to update_file_list
        self.search_var.trace('w', update_file_list)
        
        # Initial file list population
        update_file_list()
        
    def insert_last_upc(self):
        """Insert the last printed UPC into search field and select first result"""
        if self.last_printed_upc:
            self.search_var.set("")  # Clear first
            self.search_entry.focus_set()
            self.search_var.set(self.last_printed_upc)
            self.search_entry.select_range(0, tk.END)
            
            # Wait briefly for the listbox to update, then select first item
            def select_first():
                if self.listbox.size() > 0:
                    self.listbox.selection_clear(0, tk.END)
                    self.listbox.selection_set(0)
                    self.listbox.see(0)
                    # Trigger the preview update
                    self.show_preview(None)
            
            # Give time for the search to update the list
            self.after(100, select_first)

    def update_last_print_time(self):
        """Update the last print time display"""
        if self.last_print_time:
            elapsed = int(time.time() - self.last_print_time)
            
            # Only show text after 10 seconds
            if elapsed < 10:
                self.last_print_label.config(text="")
                self.last_print_label.config(cursor="")
                self.last_print_label.unbind('<Button-1>')
                # Check again in 1 second
                self.after(1000, self.update_last_print_time)
                return
                
            if elapsed < 60:
                time_text = f"Last Label Printed {elapsed}s ago"
                # Update every 5 seconds for the first minute
                self.after(5000, self.update_last_print_time)
            elif elapsed < 3600:
                time_text = f"Last Label Printed {elapsed//60}m ago"
                # Update every 30 seconds after the first minute
                self.after(30000, self.update_last_print_time)
            else:
                time_text = f"Last Label Printed {elapsed//3600}h ago"
                # Update every 30 seconds after the first hour
                self.after(30000, self.update_last_print_time)
            
            self.last_print_label.config(text=time_text)
            # Make label clickable when there's a time
            self.last_print_label.config(cursor="hand2")
            self.last_print_label.bind('<Button-1>', lambda e: self.insert_last_upc())
        else:
            self.last_print_label.config(text="")
            self.last_print_label.config(cursor="")
            self.last_print_label.unbind('<Button-1>')
            # Keep checking every 30 seconds even when no print time
            self.after(30000, self.update_last_print_time)

    def toggle_window_on_top(self):
        current_state = self.always_on_top.get()
        self.attributes('-topmost', current_state)
        if current_state:
            self.lift()
            self.always_on_top.set(False)
        else:
            self.always_on_top.set(True)

    def open_selected_file(self, listbox):
        """Open the selected file"""
        selection = listbox.curselection()
        if selection:
            file_name = listbox.get(selection[0])
            file_path = os.path.join(self.config_manager.settings.last_directory,
                                   file_name)
            try:
                # Open the saved file with the default program
                os.startfile(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")

    def print_selected_file(self, listbox):
        """Print the selected file directly"""
        selection = listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select a file to print.")
            return

        file_name = listbox.get(selection[0])
        file_path = os.path.join(self.config_manager.settings.last_directory,
                               file_name)
        try:
            # Extract UPC from filename (assuming it's in the filename)
            upc_match = re.search(r'\d{12}', file_name)
            if upc_match:
                self.last_printed_upc = upc_match.group(0)

            # Update last print time and start/update the display immediately
            self.last_print_time = time.time()
            self.update_last_print_time()

            # Check mirror print state using the BooleanVar
            if self.is_mirror_print.get():
                img = Image.open(file_path)
                mirrored_img = img.transpose(Image.FLIP_LEFT_RIGHT)
                temp_dir = os.path.join(os.environ['TEMP'], 'label_maker')
                os.makedirs(temp_dir, exist_ok=True)
                temp_path = os.path.join(temp_dir, f'mirror_{file_name}')
                mirrored_img.save(temp_path)
                os.startfile(temp_path, "print")
            else:
                os.startfile(file_path, "print")
            self.after(1000, lambda: pyautogui.press('enter'))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print: {str(e)}")
