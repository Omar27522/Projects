import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
import pyautogui
import time
import re

from src.config import ConfigManager
from .window_state import WindowState

class FileViewer(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize window state
        self.window_state = WindowState()
        self.window_state.add_window(self)

        self.config_manager = ConfigManager()

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

        self.title("View Files")
        self.geometry("800x600")  # Match DELETE version size
        self.minsize(600, 400)    # Set minimum size
        
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
            listbox.configure(font=('TkDefaultFont', new_size))
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

        # Add mirror print toggle
        is_mirror_print = tk.BooleanVar(value=False)
        mirror_btn = tk.Button(control_frame, text="🖨️", bg='#C71585', relief='raised', width=4)

        def toggle_mirror_print():
            current_state = is_mirror_print.get()
            mirror_btn.config(
                bg='#90EE90' if current_state else '#C71585',
                relief='sunken' if current_state else 'raised'
            )

        mirror_btn.config(
            command=lambda: [is_mirror_print.set(not is_mirror_print.get()),
                           toggle_mirror_print()]
        )
        mirror_btn.pack(side=tk.RIGHT, padx=2)

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

        # Search frame
        search_frame = tk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(search_frame, text="Find:").pack(side=tk.LEFT)
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.update_file_list)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # List frame with preview
        list_frame = tk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side for listbox
        listbox_frame = tk.Frame(list_frame)
        listbox_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Listbox with scrollbar
        listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = tk.Scrollbar(listbox_frame, orient=tk.HORIZONTAL, command=listbox.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        listbox.config(xscrollcommand=h_scrollbar.set)
        
        # Right side for preview
        preview_frame = tk.Frame(list_frame, bg='white')
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Preview label
        preview_label = tk.Label(preview_frame, bg='white')
        preview_label.pack(expand=True, fill=tk.BOTH)
        
        def show_preview(event=None):
            """Show preview of selected file"""
            selection = listbox.curselection()
            if not selection:
                preview_label.config(image='')
                return
                
            file_name = listbox.get(selection[0])
            file_path = os.path.join(self.config_manager.settings.last_directory, file_name)
            
            try:
                # Load and display image
                img = Image.open(file_path)
                
                # Mirror image if mirror print is enabled
                if is_mirror_print.get():
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                
                # Get preview frame size
                preview_width = preview_frame.winfo_width()
                preview_height = preview_frame.winfo_height()
                
                if preview_width > 1 and preview_height > 1:
                    # Calculate scaling to fit preview frame
                    img_ratio = img.width / img.height
                    frame_ratio = preview_width / preview_height
                    
                    # Scale based on preview size setting
                    size_factors = {1: 0.7, 2: 0.85, 3: 1.0}
                    scale = size_factors[preview_size.get()]
                    
                    if img_ratio > frame_ratio:
                        new_width = int(preview_width * scale)
                        new_height = int(new_width / img_ratio)
                    else:
                        new_height = int(preview_height * scale)
                        new_width = int(new_height * img_ratio)
                    
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(img)
                preview_label.config(image=photo)
                preview_label.image = photo  # Keep reference!
                
            except Exception as e:
                preview_label.config(image='')
                print(f"Preview error: {str(e)}")
        
        # Bind listbox selection
        listbox.bind('<<ListboxSelect>>', show_preview)
        
        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Open button
        open_btn = tk.Button(button_frame, text="Open", 
                           command=lambda: self.open_selected_file(listbox),
                           bg='#e3f2fd', activebackground='#bbdefb',
                           font=('TkDefaultFont', 9, 'bold'),
                           relief='raised', width=15, height=2)
        open_btn.pack(side=tk.LEFT, padx=2)
        
        # Print button
        print_btn = tk.Button(button_frame, text="Print",
                            command=lambda: self.print_selected_file(listbox),
                            bg='#e8f5e9', activebackground='#c8e6c9',
                            font=('TkDefaultFont', 9, 'bold'),
                            relief='raised', width=15, height=2)
        print_btn.pack(side=tk.LEFT, padx=2)
        
        # Initial file list population
        self.update_file_list()
        
        # Update preview when window is resized
        def on_resize(event):
            show_preview(None)
        preview_frame.bind('<Configure>', on_resize)

    def toggle_window_on_top(self):
        current_state = self.always_on_top.get()
        self.attributes('-topmost', current_state)
        if current_state:
            self.lift()
            self.always_on_top.set(False)
        else:
            self.always_on_top.set(True)

    def update_file_list(self, *args):
        """Update the listbox based on search text"""
        search_text = self.search_var.get().lower()
        listbox = self.winfo_children()[0].winfo_children()[2].winfo_children()[0].winfo_children()[0]
        listbox.delete(0, tk.END)

        try:
            labels_dir = os.path.normpath(self.config_manager.settings.last_directory)
            if not labels_dir or not os.path.exists(labels_dir):
                return
                
            files = os.listdir(labels_dir)
            png_files = [f for f in files if f.lower().endswith('.png')]
            matched_files = []

            # Split search into terms
            search_terms = search_text.split()

            for file in sorted(png_files):
                file_lower = file.lower()
                # If no search terms, include all files
                if not search_terms:
                    matched_files.append(file)
                # Check if all search terms are in filename
                elif all(term in file_lower for term in search_terms):
                    matched_files.append(file)

            for file in matched_files:
                listbox.insert(tk.END, file)

            # Update label count
            self.labels_count.config(text=f"Labels: {len(matched_files)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to list files: {str(e)}")

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

            # Update last print time
            self.last_print_time = time.time()

            # If mirror print is enabled, create a mirrored temporary copy
            is_mirror_print = self.winfo_children()[0].winfo_children()[0].winfo_children()[7].cget('text') == '🖨️'
            if is_mirror_print:
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
