import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Any, Callable
import os
from PIL import Image, ImageTk
import pyautogui
from ..config import ConfigManager
from .window_manager import WindowManager
from ..barcode_generator import BarcodeGenerator, LabelData

class MainWindow:
    def __init__(self):
        self.app = tk.Tk()
        self.app.withdraw()  # Hide the main window immediately
        
        self.config_manager = ConfigManager()
        self.window_manager = WindowManager()
        self.barcode_generator = BarcodeGenerator(self.config_manager.settings)
        
        self._setup_fonts()
        self._setup_variables()
        self._create_main_window()

    def _setup_fonts(self):
        """Configure default fonts"""
        self.default_font = ('TkDefaultFont', 11)
        self.button_font = ('TkDefaultFont', 11, 'normal')
        self.entry_font = ('TkDefaultFont', 11)
        self.label_font = ('TkDefaultFont', 11)
        self.view_files_font = ('TkDefaultFont', 12, 'bold')

        self.app.option_add('*Font', self.default_font)
        self.app.option_add('*Button*Font', self.button_font)
        self.app.option_add('*Entry*Font', self.entry_font)
        self.app.option_add('*Label*Font', self.label_font)

    def _setup_variables(self):
        """Initialize tkinter variables"""
        self.font_size_large = tk.IntVar(value=self.config_manager.settings.font_size_large)
        self.font_size_medium = tk.IntVar(value=self.config_manager.settings.font_size_medium)
        self.barcode_width = tk.IntVar(value=self.config_manager.settings.barcode_width)
        self.barcode_height = tk.IntVar(value=self.config_manager.settings.barcode_height)
        self.always_on_top = tk.BooleanVar(value=self.config_manager.settings.always_on_top)
        self.transparency_level = tk.DoubleVar(value=self.config_manager.settings.transparency_level)
        self.png_count = tk.StringVar(value="Labels: 0")

    def _create_main_window(self):
        """Create and setup the main application window"""
        self.main_window = self.window_manager.create_window("Enter Label Details", self.app)
        self.main_window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Create main frame with minimal padding
        main_frame = tk.Frame(self.main_window, padx=5, pady=3)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Create top control frame
        top_control_frame = tk.Frame(main_frame)
        top_control_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=2)

        # Always on top button
        self.always_on_top_btn = tk.Button(top_control_frame,
            text="Always On Top ",
            bg='#90EE90' if self.always_on_top.get() else 'SystemButtonFace',
            relief='sunken' if self.always_on_top.get() else 'raised',
            command=self._toggle_always_on_top
        )
        self.always_on_top_btn.pack(side=tk.LEFT, padx=3)

        # Labels count button
        self.png_count_btn = tk.Button(top_control_frame,
            textvariable=self.png_count,
            command=self._select_output_directory,
            fg='#191970',
            font=('TkDefaultFont', 9, 'bold')
        )
        self.png_count_btn.pack(side=tk.LEFT, padx=3)

        # Control buttons frame
        control_frame = tk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

        tk.Button(control_frame, text="Settings", width=8,
                 command=self.show_settings).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Reset", width=8,
                 command=self.clear_inputs).pack(side=tk.RIGHT, padx=5)

        # Input fields
        self.inputs = {}
        labels = [
            ("Product Name Line 1", "name_line1"),
            ("Line 2 (optional)", "name_line2"),
            ("Variant", "variant"),
            ("UPC Code (12 digits)", "upc_code")
        ]

        for idx, (label_text, key) in enumerate(labels):
            tk.Label(main_frame, text=label_text, anchor="e", width=20).grid(
                row=idx+2, column=0, padx=5, pady=3, sticky="e")
            
            entry = tk.Entry(main_frame, width=15)
            
            # Add validation for UPC Code
            if key == "upc_code":
                entry.config(validate="key")
                entry.bind("<KeyRelease>", 
                          lambda e, ent=entry: ent.delete(12, tk.END) 
                          if len(ent.get()) > 12 else None)
            
            # Add context menu
            self._add_context_menu(entry)
            
            entry.grid(row=idx+2, column=1, padx=5, pady=3, sticky="w")
            self.inputs[key] = entry

        # Action buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=len(labels)+3, column=0, columnspan=2, pady=5)

        tk.Button(button_frame, text="Preview",
                 command=self.preview_label).pack(side=tk.LEFT, padx=3)
        tk.Button(button_frame, text="Generate",
                 command=self.generate_label).pack(side=tk.LEFT, padx=3)
        tk.Button(button_frame, text="View Files",
                 command=self.view_directory_files,
                 font=self.view_files_font).pack(side=tk.LEFT, padx=3)

        # Update window settings
        self._update_window_settings()
        self._update_png_count()

    def _add_context_menu(self, widget):
        """Add right-click context menu to widget"""
        menu = tk.Menu(widget, tearoff=0)
        menu.add_command(label="Copy", 
                        command=lambda: widget.event_generate('<<Copy>>'))
        menu.add_command(label="Paste", 
                        command=lambda: widget.event_generate('<<Paste>>'))
        menu.add_command(label="Cut", 
                        command=lambda: widget.event_generate('<<Cut>>'))
        menu.add_separator()
        menu.add_command(label="Select All", 
                        command=lambda: widget.select_range(0, tk.END))
        
        widget.bind("<Button-3>", 
                   lambda e: menu.tk_popup(e.x_root, e.y_root))

    def _toggle_always_on_top(self):
        """Toggle always-on-top state"""
        self.always_on_top.set(not self.always_on_top.get())
        is_on_top = self.always_on_top.get()
        
        self.always_on_top_btn.config(
            bg='#90EE90' if is_on_top else 'SystemButtonFace',
            relief='sunken' if is_on_top else 'raised'
        )
        
        self.window_manager.set_window_on_top(self.main_window, is_on_top)
        self.config_manager.settings.always_on_top = is_on_top
        self.config_manager.save_settings()

    def _update_window_settings(self):
        """Update window settings based on current state"""
        self.window_manager.set_window_on_top(
            self.main_window, 
            self.always_on_top.get()
        )
        self.window_manager.make_draggable(self.main_window)

    def _update_png_count(self):
        """Update PNG count label"""
        if self.config_manager.settings.last_directory:
            count = len([f for f in os.listdir(self.config_manager.settings.last_directory)
                        if f.lower().endswith('.png')])
            self.png_count.set(f"Labels: {count}")

    def _select_output_directory(self):
        """Select output directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.config_manager.settings.last_directory = directory
            self.config_manager.save_settings()
            self._update_png_count()

    def preview_label(self):
        """Show label preview"""
        label_data = self._get_label_data()
        if not label_data:
            return

        # If preview window exists and is valid, just focus it
        if hasattr(self, 'preview_window') and self.preview_window and self.preview_window.winfo_exists():
            self.window_manager.focus_window(self.preview_window)
            return

        label_image = self.barcode_generator.generate_label(label_data)
        if label_image:
            self.preview_window = self.window_manager.create_window("Label Preview")
            self.preview_window.is_preview_window = True
            
            # Resize for display
            display_img = label_image.resize(
                (self.config_manager.settings.LABEL_WIDTH // 2,
                 self.config_manager.settings.LABEL_HEIGHT // 2),
                Image.Resampling.LANCZOS
            )
            
            photo = ImageTk.PhotoImage(display_img)
            img_label = ttk.Label(self.preview_window, image=photo)
            img_label.image = photo  # Keep reference
            img_label.pack(padx=5, pady=5)

            # Create button frame
            button_frame = ttk.Frame(self.preview_window)
            button_frame.pack(pady=5)

            # Generate Label button with styling
            generate_btn = tk.Button(button_frame, 
                text="Generate Label",
                command=lambda: self.generate_label(),
                bg='#e3f2fd',   # Light blue background
                activebackground='#bbdefb',  # Slightly darker when clicked
                font=('TkDefaultFont', 9, 'bold'),
                relief='raised'
            )
            generate_btn.pack(side=tk.LEFT, padx=3)

            # Add hover effect
            def on_generate_enter(e):
                generate_btn['bg'] = '#bbdefb'
            def on_generate_leave(e):
                generate_btn['bg'] = '#e3f2fd'
            generate_btn.bind("<Enter>", on_generate_enter)
            generate_btn.bind("<Leave>", on_generate_leave)

            # Print Label button
            def print_label():
                try:
                    # Create a temporary file
                    temp_file = os.path.join(os.environ.get('TEMP', os.getcwd()), 
                                           f"temp_label_{label_data.upc_code}.png")
                    label_image.save(temp_file, dpi=(self.config_manager.settings.DPI,
                                                   self.config_manager.settings.DPI))
                    
                    # Open the file with the default image viewer/printer
                    os.startfile(temp_file, "print")
                    
                    # Wait a moment for the print dialog to appear and press Enter
                    self.preview_window.after(1000, lambda: pyautogui.press('enter'))
                    
                    # Schedule the temporary file for deletion after a delay
                    self.preview_window.after(5000, 
                        lambda: os.remove(temp_file) if os.path.exists(temp_file) else None)
                    
                    # Close the preview window
                    self.preview_window.destroy()
                    self.preview_window = None
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to print: {str(e)}")

            print_btn = tk.Button(button_frame, 
                text="Print Label",
                command=print_label,
                bg='#e8f5e9',  # Light green background
                activebackground='#c8e6c9',  # Slightly darker when clicked
                font=('TkDefaultFont', 9, 'bold'),
                relief='raised'
            )
            print_btn.pack(side=tk.LEFT, padx=3)

            # Add hover effect
            def on_print_enter(e):
                print_btn['bg'] = '#c8e6c9'
            def on_print_leave(e):
                print_btn['bg'] = '#e8f5e9'
            print_btn.bind("<Enter>", on_print_enter)
            print_btn.bind("<Leave>", on_print_leave)

            # Set window properties
            self.window_manager.set_window_on_top(self.preview_window, self.always_on_top.get())
            self.window_manager.make_draggable(self.preview_window)

    def generate_label(self):
        """Generate and save label"""
        if not self.config_manager.settings.last_directory:
            self.config_manager.settings.last_directory = filedialog.askdirectory()
            if not self.config_manager.settings.last_directory:
                return
            self.config_manager.save_settings()

        label_data = self._get_label_data()
        if not label_data:
            return

        label_image = self.barcode_generator.generate_label(label_data)
        if label_image:
            filename = f"{label_data.upc_code}.png"
            filepath = os.path.join(self.config_manager.settings.last_directory, filename)
            label_image.save(filepath)
            messagebox.showinfo("Success", f"Label saved as {filename}")

    def show_settings(self):
        """Show settings window"""
        settings_window = self.window_manager.create_window("Settings")
        
        # Font size settings
        ttk.Label(settings_window, text="Large Font Size:").grid(row=0, column=0, padx=5, pady=2)
        ttk.Entry(settings_window, textvariable=self.font_size_large).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(settings_window, text="Medium Font Size:").grid(row=1, column=0, padx=5, pady=2)
        ttk.Entry(settings_window, textvariable=self.font_size_medium).grid(row=1, column=1, padx=5, pady=2)
        
        # Barcode size settings
        ttk.Label(settings_window, text="Barcode Width:").grid(row=2, column=0, padx=5, pady=2)
        ttk.Entry(settings_window, textvariable=self.barcode_width).grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(settings_window, text="Barcode Height:").grid(row=3, column=0, padx=5, pady=2)
        ttk.Entry(settings_window, textvariable=self.barcode_height).grid(row=3, column=1, padx=5, pady=2)
        
        # Window settings
        ttk.Checkbutton(settings_window, text="Always on Top", 
                       variable=self.always_on_top).grid(row=4, column=0, columnspan=2, pady=5)
        
        # Save button
        ttk.Button(settings_window, text="Save", 
                  command=lambda: self._save_settings(settings_window)).grid(row=5, column=0, columnspan=2, pady=10)

    def _save_settings(self, settings_window):
        """Save settings and close settings window"""
        self.config_manager.settings.font_size_large = self.font_size_large.get()
        self.config_manager.settings.font_size_medium = self.font_size_medium.get()
        self.config_manager.settings.barcode_width = self.barcode_width.get()
        self.config_manager.settings.barcode_height = self.barcode_height.get()
        self.config_manager.settings.always_on_top = self.always_on_top.get()
        self.config_manager.settings.transparency_level = self.transparency_level.get()
        
        self.config_manager.save_settings()
        self.window_manager.set_window_on_top(self.main_window, self.always_on_top.get())
        settings_window.destroy()

    def _get_label_data(self) -> Optional[LabelData]:
        """Get label data from input fields"""
        upc = self.inputs["upc_code"].get().strip()
        if not upc:
            messagebox.showerror("Error", "UPC Code is required")
            return None

        return LabelData(
            name_line1=self.inputs["name_line1"].get().strip(),
            name_line2=self.inputs["name_line2"].get().strip(),
            variant=self.inputs["variant"].get().strip(),
            upc_code=upc
        )

    def clear_inputs(self):
        """Clear all input fields"""
        for entry in self.inputs.values():
            entry.delete(0, tk.END)

    def view_directory_files(self):
        """Display files from the output directory in a new window"""
        # If file window exists and is valid, just focus it
        if hasattr(self, 'file_window') and self.file_window and self.file_window.winfo_exists():
            self.window_manager.focus_window(self.file_window)
            return

        if not self.config_manager.settings.last_directory:
            messagebox.showerror("Warning", "Please select an output directory first.")
            return

        self.file_window = self.window_manager.create_window("View Files")
        self.file_window.minsize(450, 200)

        # Create main content frame
        main_content = tk.Frame(self.file_window)
        main_content.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Create top frame for controls
        top_frame = tk.Frame(main_content)
        top_frame.pack(fill=tk.X, padx=0, pady=1)

        # Add Pin (Always on Top) button
        window_always_on_top = tk.BooleanVar(value=False)
        window_top_btn = tk.Button(top_frame, text="Pin", bg='#C71585', relief='raised', width=8)

        def toggle_window_on_top():
            current_state = window_always_on_top.get()
            self.file_window.attributes('-topmost', current_state)
            if current_state:
                self.file_window.lift()
                window_top_btn.config(
                    text="Pin",
                    bg='#90EE90',  # Light green when active
                    relief='sunken'
                )
            else:
                window_top_btn.config(
                    text="Pin",
                    bg='#C71585',  # Velvet color when inactive
                    relief='raised'
                )

        window_top_btn.config(
            command=lambda: [window_always_on_top.set(not window_always_on_top.get()), 
                           toggle_window_on_top()]
        )
        window_top_btn.pack(side=tk.LEFT, padx=2)

        # Add Magnifier button
        is_magnified = tk.BooleanVar(value=False)
        magnifier_btn = tk.Button(top_frame, text="🔍", bg='#C71585', relief='raised', width=3,
                                font=('TkDefaultFont', 14))

        def toggle_magnification():
            current_state = is_magnified.get()
            new_size = 16 if current_state else 9
            listbox.configure(font=('TkDefaultFont', new_size))
            if current_state:
                h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
                listbox.configure(wrap=tk.NONE)
            else:
                h_scrollbar.pack_forget()
                listbox.configure(wrap=tk.CHAR)
            magnifier_btn.config(
                bg='#90EE90' if current_state else '#C71585',
                relief='sunken' if current_state else 'raised'
            )

        magnifier_btn.config(
            command=lambda: [is_magnified.set(not is_magnified.get()), 
                           toggle_magnification()]
        )
        magnifier_btn.pack(side=tk.LEFT, padx=2)

        # Create search frame
        search_frame = tk.Frame(main_content)
        search_frame.pack(fill=tk.X, padx=0, pady=1)

        tk.Label(search_frame, text="Find:", 
                font=('TkDefaultFont', 9)).pack(side=tk.LEFT, padx=(2,0))
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, 
                              font=('TkDefaultFont', 9))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        search_entry.focus_set()

        # Create list frame
        list_frame = tk.Frame(main_content)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=1)

        # Add listbox with scrollbars
        listbox = tk.Listbox(list_frame, height=4, font=('TkDefaultFont', 9))
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_scrollbar = tk.Scrollbar(list_frame)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        h_scrollbar = tk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        listbox.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        v_scrollbar.config(command=listbox.yview)
        h_scrollbar.config(command=listbox.xview)

        def update_file_list(*args):
            """Update the listbox based on search text"""
            search_text = search_var.get().lower()
            listbox.delete(0, tk.END)
            try:
                files = os.listdir(self.config_manager.settings.last_directory)
                png_files = [f for f in files if f.lower().endswith('.png')]
                for file in sorted(png_files):
                    if search_text in file.lower():
                        listbox.insert(tk.END, file)
                if len(png_files) == 0:
                    listbox.insert(tk.END, "0")
                else:
                    listbox.selection_clear(0, tk.END)
                    listbox.selection_set(0)
                    listbox.see(0)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read directory: {str(e)}")

        search_var.trace('w', update_file_list)

        def open_selected_file():
            """Open the selected file"""
            selection = listbox.curselection()
            if selection:
                file_name = listbox.get(selection[0])
                file_path = os.path.join(self.config_manager.settings.last_directory, 
                                       file_name)
                try:
                    os.startfile(file_path)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open file: {str(e)}")

        def print_selected_file():
            """Print the selected file directly"""
            selection = listbox.curselection()
            if not selection:
                messagebox.showinfo("Info", "Please select a file to print.")
                return

            file_name = listbox.get(selection[0])
            file_path = os.path.join(self.config_manager.settings.last_directory, 
                                   file_name)
            try:
                os.startfile(file_path, "print")
                self.file_window.after(1000, lambda: pyautogui.press('enter'))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to print: {str(e)}")

        def preview_selected_file():
            """Preview the selected image file"""
            selection = listbox.curselection()
            if not selection:
                messagebox.showinfo("Info", "Please select an image to preview.")
                return

            file_name = listbox.get(selection[0])
            file_path = os.path.join(self.config_manager.settings.last_directory, 
                                   file_name)

            try:
                img = Image.open(file_path)
                display_width = min(400, img.width)
                ratio = display_width / img.width
                display_height = int(img.height * ratio)

                img = img.resize((display_width, display_height), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)

                preview_window = tk.Toplevel(self.file_window)
                preview_window.title(f"File Preview: {file_name}")
                preview_window.transient(self.file_window)

                # Create preview frame
                preview_frame = tk.Frame(preview_window)
                preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

                # Display image
                img_label = tk.Label(preview_frame, image=img_tk)
                img_label.image = img_tk
                img_label.pack(pady=5)

                # Add buttons
                button_frame = tk.Frame(preview_frame)
                button_frame.pack(pady=5)

                tk.Button(button_frame, text="Print", command=print_selected_file,
                         bg='#e8f5e9', activebackground='#c8e6c9',
                         font=('TkDefaultFont', 9, 'bold'),
                         relief='raised').pack(side=tk.LEFT, padx=3)

                tk.Button(button_frame, text="Open", command=open_selected_file,
                         bg='#e3f2fd', activebackground='#bbdefb',
                         font=('TkDefaultFont', 9, 'bold'),
                         relief='raised').pack(side=tk.LEFT, padx=3)

                # Make preview window draggable
                self.window_manager.make_draggable(preview_window)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to preview image: {str(e)}")

        # Create bottom button frame
        button_frame = tk.Frame(main_content)
        button_frame.pack(fill=tk.X, padx=2, pady=2)

        # Add buttons with styling
        tk.Button(button_frame, text="Open", command=open_selected_file,
                 bg='#e3f2fd', activebackground='#bbdefb',
                 font=('TkDefaultFont', 9, 'bold'),
                 relief='raised').pack(side=tk.LEFT, padx=2)

        tk.Button(button_frame, text="Print", command=print_selected_file,
                 bg='#e8f5e9', activebackground='#c8e6c9',
                 font=('TkDefaultFont', 9, 'bold'),
                 relief='raised').pack(side=tk.LEFT, padx=2)

        tk.Button(button_frame, text="Preview", command=preview_selected_file,
                 bg='#fff3e0', activebackground='#ffe0b2',
                 font=('TkDefaultFont', 9, 'bold'),
                 relief='raised').pack(side=tk.LEFT, padx=2)

        # Add Download All button
        def download_all():
            try:
                if not self.config_manager.settings.last_directory:
                    messagebox.showerror("Error", "Please select a folder first before downloading files.")
                    return
                    
                # Ask user for download directory, starting from last used directory
                download_dir = filedialog.askdirectory(
                    title="Select Download Directory",
                    initialdir=self.config_manager.settings.last_directory
                )
                if not download_dir:
                    return

                # Get all PNG files from the current directory
                files = [f for f in os.listdir(self.config_manager.settings.last_directory)
                        if f.lower().endswith('.png')]
                
                if not files:
                    messagebox.showinfo("Info", "No PNG files to download.")
                    return

                # Copy each file to the download directory
                copied_files = 0
                for file in files:
                    try:
                        src = os.path.join(self.config_manager.settings.last_directory, file)
                        dst = os.path.join(download_dir, file)
                        with open(src, 'rb') as fsrc:
                            with open(dst, 'wb') as fdst:
                                fdst.write(fsrc.read())
                        copied_files += 1
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to copy {file}: {str(e)}")

                if copied_files > 0:
                    messagebox.showinfo("Success", f"Downloaded {copied_files} files to {download_dir}")
                else:
                    messagebox.showerror("Error", "No files were downloaded due to errors")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to download files: {str(e)}")

        tk.Button(button_frame, text="Download All", command=download_all,
                 bg='#f3e5f5', activebackground='#e1bee7',
                 font=('TkDefaultFont', 9, 'bold'),
                 relief='raised').pack(side=tk.LEFT, padx=2)

        # Add double-click binding
        listbox.bind('<Double-Button-1>', lambda e: preview_selected_file())

        # Initial file list update
        update_file_list()

        # Make window draggable
        self.window_manager.make_draggable(self.file_window)

    def on_close(self):
        """Handle window close event"""
        self.config_manager.save_settings()
        self.app.quit()

    def run(self):
        """Start the application"""
        self.app.mainloop()
