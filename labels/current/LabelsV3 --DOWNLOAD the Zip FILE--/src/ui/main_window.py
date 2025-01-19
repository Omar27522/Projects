import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Any, Callable
import os
from PIL import Image, ImageTk
import pyautogui
from ..config import ConfigManager
from .window_manager import WindowManager
from ..barcode_generator import BarcodeGenerator, LabelData

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Initialize window tracking
        self.app_windows = []  # Track all windows
        self.app_windows.append(self)  # Include main window
        
        self.config_manager = ConfigManager()
        self.window_manager = WindowManager()
        self.barcode_generator = BarcodeGenerator(self.config_manager.settings)
        
        self._setup_fonts()
        self._setup_variables()
        self._load_icons()
        self._create_tooltip_class()
        self._create_main_window()
        
        # Bind focus event to main window
        self.bind("<FocusIn>", lambda e: self._on_window_focus(self))

    def view_directory_files(self):
        """View files in the current directory"""
        # If file window exists and is valid, focus it
        if hasattr(self, 'file_window') and self.file_window and self.file_window.winfo_exists():
            self.file_window.deiconify()  # Ensure window is not minimized
            self.file_window.lift()       # Bring to front
            self.file_window.focus_force() # Force focus
            return

        if not self.config_manager.settings.last_directory:
            messagebox.showinfo("Info", "Please select a directory first.")
            return

        # Create view files window
        self.file_window = tk.Toplevel(self)
        self.file_window.title("View Files")
        self.file_window.geometry("600x400")  # Default size
        self.file_window.minsize(375, 200)    # Minimum size
        
        # Enable window resizing and add maximize/minimize buttons
        self.file_window.resizable(True, True)
        
        # Bind focus events
        self.file_window.bind("<FocusIn>", lambda e: self._on_window_focus(self.file_window))
        
        # Give initial focus
        self.file_window.focus_set()

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

        # Add Label Count display
        label_count_label = tk.Label(
            top_frame,
            text="",  # Will be set by update_file_list
            font=('TkDefaultFont', 10, 'bold'),
            fg='#2ecc71'  # Green text
        )
        label_count_label.pack(side=tk.LEFT, padx=10)

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

        # Create and configure zoom button with plus icon
        zoom_btn = tk.Button(top_frame, text="➕", bg='#4169E1', relief='raised', width=3,  # Start with size 3 color
                          font=('TkDefaultFont', 14),
                          command=cycle_preview_size)
        zoom_btn.pack(side=tk.LEFT, padx=2)

        # Add mirror print toggle button
        is_mirror_print = tk.BooleanVar(value=False)
        mirror_btn = tk.Button(top_frame, text=" 🖨️ ", bg='#C71585', relief='raised', width=3,
                             font=('TkDefaultFont', 14), anchor='center')

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
        mirror_btn.pack(side=tk.LEFT, padx=2)

        # Create search frame
        search_frame = tk.Frame(main_content)
        search_frame.pack(fill=tk.X, padx=0, pady=6)

        tk.Label(search_frame, text="Find:", 
                font=('TkDefaultFont', 11, 'bold')).pack(side=tk.LEFT, padx=(4,2))
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, 
                              font=('TkDefaultFont', 11))
        
        # Auto-select contents when entry gets focus
        def select_all(event):
            event.widget.select_range(0, tk.END)
            return "break"  # Prevents default behavior
            
        search_entry.bind('<FocusIn>', select_all)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, pady=6)
        search_entry.focus_set()

        # Create list frame with preview side by side
        list_frame = tk.Frame(main_content)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=1)

        # Left side for file list
        left_frame = tk.Frame(list_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add listbox with scrollbars
        listbox = tk.Listbox(left_frame, height=4, font=('TkDefaultFont', 9))
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        v_scrollbar = tk.Scrollbar(left_frame)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        h_scrollbar = tk.Scrollbar(left_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        listbox.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        v_scrollbar.config(command=listbox.yview)
        h_scrollbar.config(command=listbox.xview)

        # Right side for preview
        preview_frame = tk.Frame(list_frame, bg='white')
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Preview label
        preview_label = tk.Label(preview_frame, bg='white')
        preview_label.pack(expand=True, fill=tk.BOTH)
        
        # Store preview label reference
        self.file_window.preview_label = preview_label

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
                    listbox.insert(tk.END, "No PNG files found")
                    label_count_label.config(text="No Labels", fg='#e74c3c')  # Red text for no labels
                else:
                    listbox.selection_clear(0, tk.END)
                    listbox.selection_set(0)
                    listbox.see(0)
                    label_count_label.config(text=f"Labels: {len(png_files)}", fg='#2ecc71')  # Green text for label count
                    # Show preview of first item
                    show_preview(None)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read directory: {str(e)}")

        def show_preview(event):
            """Show preview of selected file in the preview frame"""
            selection = listbox.curselection()
            if not selection:
                preview_label.config(image='')
                return

            file_name = listbox.get(selection[0])
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
                    
                img_tk = ImageTk.PhotoImage(img)
                preview_label.config(image=img_tk)
                preview_label.image = img_tk  # Keep reference
            except Exception as e:
                preview_label.config(image='')
                print(f"Failed to preview image: {str(e)}")

        search_var.trace('w', update_file_list)
        listbox.bind('<<ListboxSelect>>', show_preview)

        # Update preview when window is resized
        def on_resize(event):
            show_preview(None)
        preview_frame.bind('<Configure>', on_resize)

        # Initial file list update
        update_file_list()

        # Force initial preview to be size 3
        show_preview(None)

        # Create bottom button frame
        button_frame = tk.Frame(main_content)
        button_frame.pack(fill=tk.X, padx=2, pady=2)

        def open_selected_file():
            """Open the selected file"""
            selection = listbox.curselection()
            if selection:
                file_name = listbox.get(selection[0])
                file_path = os.path.join(self.config_manager.settings.last_directory, 
                                       file_name)
                try:
                    # Open the saved file with the default program
                    os.startfile(file_path)
                    
                    # Close the view files window
                    self.file_window.destroy()
                    self.file_window = None
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
                # If mirror print is enabled, create a mirrored temporary copy
                if is_mirror_print.get():
                    img = Image.open(file_path)
                    mirrored_img = img.transpose(Image.FLIP_LEFT_RIGHT)
                    temp_dir = os.path.join(os.environ['TEMP'], 'label_maker')
                    os.makedirs(temp_dir, exist_ok=True)
                    temp_path = os.path.join(temp_dir, f'mirror_{file_name}')
                    mirrored_img.save(temp_path)
                    os.startfile(temp_path, "print")
                else:
                    os.startfile(file_path, "print")
                self.file_window.after(1000, lambda: pyautogui.press('enter'))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to print: {str(e)}")

        # Add buttons with styling
        tk.Button(button_frame, text="Open", command=open_selected_file,
                 bg='#e3f2fd', activebackground='#bbdefb',
                 font=('TkDefaultFont', 9, 'bold'),
                 relief='raised',
                 width=15,
                 height=2
                ).pack(side=tk.LEFT, padx=2)

        tk.Button(button_frame, text="Print", command=print_selected_file,
                 bg='#e8f5e9', activebackground='#c8e6c9',
                 font=('TkDefaultFont', 9, 'bold'),
                 relief='raised',
                 width=15,
                 height=2
                ).pack(side=tk.LEFT, padx=2)

    def _setup_fonts(self):
        """Configure default fonts"""
        self.default_font = ('TkDefaultFont', 11)
        self.button_font = ('TkDefaultFont', 11, 'normal')
        self.entry_font = ('TkDefaultFont', 11)
        self.label_font = ('TkDefaultFont', 11)
        self.view_files_font = ('TkDefaultFont', 12, 'bold')

        self.option_add('*Font', self.default_font)
        self.option_add('*Button*Font', self.button_font)
        self.option_add('*Entry*Font', self.entry_font)
        self.option_add('*Label*Font', self.label_font)

    def _setup_variables(self):
        """Initialize tkinter variables"""
        self.font_size_large = tk.IntVar(value=self.config_manager.settings.font_size_large)
        self.font_size_medium = tk.IntVar(value=self.config_manager.settings.font_size_medium)
        self.barcode_width = tk.IntVar(value=self.config_manager.settings.barcode_width)
        self.barcode_height = tk.IntVar(value=self.config_manager.settings.barcode_height)
        self.always_on_top = tk.BooleanVar(value=self.config_manager.settings.always_on_top)
        self.transparency_level = tk.DoubleVar(value=self.config_manager.settings.transparency_level)
        self.png_count = tk.StringVar(value=f"Labels: {self.config_manager.settings.label_counter}")

    def _load_icons(self):
        """Load icons for buttons"""
        # Create a simple batch icon using a PhotoImage
        self.batch_icon = tk.PhotoImage(width=16, height=16)
        # Create a simple spreadsheet-like icon using pixels
        data = """
        ................
        .##############.
        .#            #.
        .#############..
        .#            #.
        .#############..
        .#            #.
        .#############..
        .#            #.
        .#############..
        .#            #.
        .#############..
        .#            #.
        .##############.
        ................
        ................
        """
        # Put the data into the image
        for y, line in enumerate(data.split()):
            for x, c in enumerate(line):
                if c == '#':
                    self.batch_icon.put('#666666', (x, y))

    def _create_tooltip_class(self):
        """Create a tooltip class for button hints"""
        class ToolTip(object):
            def __init__(self, widget, text):
                self.widget = widget
                self.text = text
                self.tooltip = None
                self.widget.bind('<Enter>', self.enter)
                self.widget.bind('<Leave>', self.leave)
                self.widget.bind('<ButtonPress>', self.leave)

            def enter(self, event=None):
                x, y, _, _ = self.widget.bbox("insert")
                x += self.widget.winfo_rootx() + 25
                y += self.widget.winfo_rooty() + 20
                self.tooltip = tk.Toplevel(self.widget)
                self.tooltip.wm_overrideredirect(True)
                self.tooltip.wm_geometry(f"+{x}+{y}")
                label = tk.Label(self.tooltip, text=self.text, 
                               justify='left',
                               background="#ffffe0", 
                               relief='solid', 
                               borderwidth=1,
                               font=("TkDefaultFont", "8", "normal"))
                label.pack()

            def leave(self, event=None):
                if self.tooltip:
                    self.tooltip.destroy()
                    self.tooltip = None

        self.CreateToolTip = ToolTip

    def _create_main_window(self):
        """Create and setup the main application window"""
        # Configure main window
        self.title("Label Maker")
        self.minsize(450, 200)
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'icon_64.png')
        if os.path.exists(icon_path):
            # Load the icon
            icon = tk.PhotoImage(file=icon_path)
            # Set both the window icon and the taskbar icon
            self.iconphoto(True, icon)
            
            # For Windows taskbar icon
            try:
                import ctypes
                myappid = 'labelmaker.app.ver3.0'  # Arbitrary string
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except Exception:
                pass  # Fail silently if Windows-specific call fails
        
        # Center window on screen
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - self.winfo_width()) // 2
        y = (screen_height - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        
        # Prevent window resizing
        self.resizable(False, False)
        
        # Bind window close event
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Create main frame with comfortable padding
        self.main_frame = tk.Frame(self, padx=8, pady=5, bg='SystemButtonFace')
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Create top control frame
        self._create_top_control_frame()
        
        # Create control buttons frame (Reset)
        self._create_control_frame()
        
        # Create input fields
        self._create_input_fields()
        
        # Create action buttons frame
        self._create_action_buttons()
        
        # Add separator
        ttk.Separator(self.main_frame, orient='horizontal').grid(
            row=8, column=0, columnspan=2, sticky=tk.EW, pady=10
        )

    def on_close(self):
        """Handle window close event"""
        self.config_manager.save_settings()
        self.quit()

    def run(self):
        """Start the application"""
        try:
            self.mainloop()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start application: {str(e)}")
            raise

    def _on_window_focus(self, focused_window):
        """Handle window focus to manage stacking order"""
        # Lower all windows
        for window in self.app_windows:
            if window.winfo_exists():  # Check if window still exists
                if isinstance(window, tk.Tk):  # Main window
                    window.attributes('-topmost', self.always_on_top.get())
                else:  # Child windows
                    window.attributes('-topmost', False)
        
        # Raise the focused window
        if focused_window != self or self.always_on_top.get():  # Don't set main window topmost unless Always on Top is enabled
            focused_window.attributes('-topmost', True)
        focused_window.lift()

    def _create_styled_button(self, parent, text, command, width=8, has_icon=False, icon=None, tooltip_text="", color_scheme=None):
        """Create a styled button with hover effect"""
        if color_scheme is None:
            color_scheme = {
                'bg': '#3498db',  # Default blue
                'fg': 'white',
                'hover_bg': '#2980b9',
                'active_bg': '#2473a6'
            }

        btn = tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            font=('TkDefaultFont', 10, 'bold'),  # Increased font size and made bold
            relief='raised',
            bg=color_scheme['bg'],
            fg=color_scheme['fg'],
            activebackground=color_scheme['active_bg'],
            activeforeground='white',
            bd=1,  # Border width
            padx=10,  # Horizontal padding
            pady=4,   # Vertical padding
        )
        
        if has_icon and icon:
            btn.config(image=icon, compound=tk.LEFT)

        # Add hover effect
        def on_enter(e):
            if not (hasattr(btn, 'is_active') and btn.is_active):
                btn['background'] = color_scheme['hover_bg']
                btn['cursor'] = 'hand2'

        def on_leave(e):
            if not (hasattr(btn, 'is_active') and btn.is_active):
                btn['background'] = color_scheme['bg']
                btn['cursor'] = ''

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        # Add tooltip
        if tooltip_text:
            self.CreateToolTip(btn, tooltip_text)

        return btn

    def _create_top_control_frame(self):
        """Create top control frame with Always on Top, Settings, and Labels Count buttons"""
        top_control_frame = tk.Frame(self.main_frame, bg='SystemButtonFace')
        top_control_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)  # Increased padding
        
        # Create a sub-frame for the buttons to ensure proper horizontal alignment
        button_frame = tk.Frame(top_control_frame, bg='SystemButtonFace')
        button_frame.pack(side=tk.LEFT, padx=8)  # Increased padding
        
        # Color schemes for different buttons
        always_on_top_colors = {
            'bg': '#e74c3c',  # Red
            'fg': 'white',
            'hover_bg': '#c0392b',
            'active_bg': '#2ecc71'  # Green when active
        }
        
        settings_colors = {
            'bg': '#9b59b6',  # Purple
            'fg': 'white',
            'hover_bg': '#8e44ad',
            'active_bg': '#7d3c98'
        }
        
        labels_count_colors = {
            'bg': '#2ecc71',  # Green
            'fg': 'white',
            'hover_bg': '#27ae60',
            'active_bg': '#219a52'
        }
        
        # Always on Top button with toggle styling
        self.always_on_top = tk.BooleanVar(value=False)
        self.always_on_top_btn = self._create_styled_button(
            button_frame,
            text="Always on Top",
            command=self.toggle_always_on_top,
            width=12,
            tooltip_text="Keep window on top of other windows",
            color_scheme=always_on_top_colors
        )
        self.always_on_top_btn.is_active = False
        self.always_on_top_btn.pack(side=tk.LEFT, padx=3)  # Increased padding
        
        # Settings button with matching style
        settings_btn = self._create_styled_button(
            button_frame,
            text="Settings",
            command=self.show_settings,
            width=8,
            tooltip_text="Configure application settings",
            color_scheme=settings_colors
        )
        settings_btn.pack(side=tk.LEFT, padx=3)  # Increased padding
        
        # Labels count button
        self.png_count_btn = self._create_styled_button(
            button_frame,
            text="",  # Text will be set by textvariable
            command=self._select_output_directory,
            width=12,
            tooltip_text="Click to change labels output directory",
            color_scheme=labels_count_colors
        )
        self.png_count_btn.config(textvariable=self.png_count)
        self.png_count_btn.pack(side=tk.LEFT, padx=3)  # Increased padding

    def _create_control_frame(self):
        """Create control buttons frame (Reset)"""
        control_frame = tk.Frame(self.main_frame, bg='SystemButtonFace')
        control_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Reset button with vibrant red theme
        reset_btn = tk.Button(control_frame,
            text="Reset",
            width=8,
            bg='#e74c3c',  # Bright red
            activebackground='#c0392b',  # Darker red when clicked
            fg='white',
            command=self.clear_inputs
        )
        reset_btn.pack(side=tk.LEFT, padx=5)

    def _create_input_fields(self):
        """Create input fields"""
        self.inputs = {}
        labels = [
            ("Product Name Line 1", "name_line1"),
            ("Line 2 (optional)", "name_line2"),
            ("Variant", "variant"),
            ("UPC Code (12 digits)", "upc_code")
        ]

        def on_input_focus(event):
            """Enable Always on Top when user focuses on any input field"""
            if not self.always_on_top.get():
                self.always_on_top.set(True)
                self.always_on_top_btn.config(
                    bg='#2ecc71',  # Bright green when active
                    activebackground='#27ae60',  # Darker green when clicked
                    relief='sunken'
                )
                self.attributes('-topmost', True)
            
            # If preview window is open, select all text in the field
            if hasattr(self, 'preview_window') and self.preview_window and self.preview_window.winfo_exists():
                event.widget.select_range(0, tk.END)
                event.widget.icursor(tk.END)

        def on_input_click(event):
            """Handle mouse click in input field"""
            if hasattr(self, 'preview_window') and self.preview_window and self.preview_window.winfo_exists():
                event.widget.select_range(0, tk.END)
                event.widget.icursor(tk.END)

        def validate_upc(action, value_if_allowed):
            """Only allow integers in UPC field and ensure exactly 12 digits"""
            if action == '1':  # Insert action
                if not value_if_allowed:  # Allow empty field
                    return True
                # Only allow digits and ensure length doesn't exceed 12
                if not value_if_allowed.isdigit():
                    return False
                return len(value_if_allowed) <= 12
            return True

        def validate_variant(action, value_if_allowed):
            """Prevent numbers at the start of variant field"""
            if action == '1':  # Insert action
                if not value_if_allowed:  # Allow empty field
                    return True
                # Check if the first character is a digit
                if value_if_allowed[0].isdigit():
                    return False
                return True
        
        for idx, (label_text, key) in enumerate(labels):
            # Label
            label = tk.Label(self.main_frame,
                text=label_text,
                anchor="e",
                width=20,
                bg='SystemButtonFace'
            )
            label.grid(row=idx+2, column=0, padx=5, pady=3, sticky="e")
            
            # Entry
            if key == "upc_code":
                vcmd = (self.register(validate_upc), '%d', '%P')
                entry = tk.Entry(self.main_frame,
                    width=25,
                    relief='sunken',
                    bg='white',
                    validate='key',
                    validatecommand=vcmd
                )
            elif key == "variant":
                vcmd = (self.register(validate_variant), '%d', '%P')
                entry = tk.Entry(self.main_frame,
                    width=25,
                    relief='sunken',
                    bg='white',
                    validate='key',
                    validatecommand=vcmd
                )
            else:
                entry = tk.Entry(self.main_frame,
                    width=25,
                    relief='sunken',
                    bg='white'
                )
            
            # Bind events
            entry.bind("<FocusIn>", on_input_focus)
            entry.bind("<Button-1>", on_input_click)  # Handle mouse click
            
            # Add context menu
            self._add_context_menu(entry)
            
            entry.grid(row=idx+2, column=1, padx=5, pady=3, sticky="w")
            self.inputs[key] = entry

    def _create_action_buttons(self):
        """Create action buttons frame"""
        button_frame = tk.Frame(self.main_frame, bg='SystemButtonFace')
        button_frame.grid(row=6, column=0, columnspan=2, pady=5)
        
        # Preview button with vibrant blue theme
        preview_btn = self._create_styled_button(
            button_frame,
            text="Preview",
            command=self.preview_label,
            width=10,
            tooltip_text="Show a preview of the label"
        )
        preview_btn.pack(side=tk.LEFT, padx=2)
        
        # View Files button with vibrant purple theme
        view_files_btn = self._create_styled_button(
            button_frame,
            text="View Files",
            command=self.view_directory_files,
            width=10,
            tooltip_text="Open the directory viewer"
        )
        view_files_btn.pack(side=tk.LEFT, padx=2)

    def upload_csv(self):
        """Handle CSV file upload"""
        csv_path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if csv_path:
            from ..utils.csv_processor import create_batch_labels
            create_batch_labels(csv_path, self)

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

    def toggle_always_on_top(self):
        """Toggle the always on top state"""
        self.always_on_top.set(not self.always_on_top.get())
        if self.always_on_top.get():
            self.always_on_top_btn.is_active = True
            self.always_on_top_btn.config(
                bg='#2ecc71',  # Bright green when active
                activebackground='#27ae60',  # Darker green when clicked
                relief='sunken'
            )
            self.attributes('-topmost', True)
            self.lift()
            self.focus_force()
        else:
            self.always_on_top_btn.is_active = False
            self.always_on_top_btn.config(
                bg='#e74c3c',  # Back to red
                activebackground='#c0392b',
                relief='raised'
            )
            self.attributes('-topmost', False)

    def clear_inputs(self):
        """Clear all input fields"""
        for entry in self.inputs.values():
            entry.delete(0, tk.END)

    def _select_output_directory(self):
        """Select output directory"""
        last_dir = self.config_manager.settings.last_directory
        directory = filedialog.askdirectory(
            title="Select where to save labels",
            initialdir=last_dir if last_dir and os.path.exists(last_dir) else None
        )
        if directory:
            self.config_manager.settings.last_directory = directory
            self.config_manager.save_settings()
            self._update_png_count()
            # Also open the directory viewer
            self.view_directory_files()

    def _update_png_count(self):
        """Update PNG count label"""
        if self.config_manager.settings.last_directory:
            count = len([f for f in os.listdir(self.config_manager.settings.last_directory)
                        if f.lower().endswith('.png')])
            self.config_manager.settings.label_counter = count
            self.png_count.set(f"Labels: {count}")
            self.config_manager.save_settings()

    def show_settings(self):
        """Show settings window"""
        # Create settings window if it doesn't exist
        if not hasattr(self, 'settings_window') or not self.settings_window or not self.settings_window.winfo_exists():
            self.settings_window = tk.Toplevel(self)
            self.settings_window.title("Settings")
            self.settings_window.geometry("400x500")  # Slightly taller to accommodate the pin button
            self.settings_window.resizable(False, False)
            
            # Add to window tracking
            self.app_windows.append(self.settings_window)
            
            # Bind focus event
            self.settings_window.bind("<FocusIn>", lambda e: self._on_window_focus(self.settings_window))
            
            # Center on parent
            self.settings_window.update_idletasks()
            x = self.winfo_x() + (self.winfo_width() - self.settings_window.winfo_width()) // 2
            y = self.winfo_y() + (self.winfo_height() - self.settings_window.winfo_height()) // 2
            self.settings_window.geometry(f"+{x}+{y}")
            
            # Create top frame for pin button
            top_frame = ttk.Frame(self.settings_window, padding="5")
            top_frame.pack(fill=tk.X)
            
            # Add Pin button
            window_always_on_top = tk.BooleanVar(value=False)
            window_top_btn = tk.Button(top_frame, text="Pin", bg='#C71585', relief='raised', width=8)

            def toggle_window_on_top():
                current_state = window_always_on_top.get()
                self.settings_window.attributes('-topmost', current_state)
                if current_state:
                    self.settings_window.lift()
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
            
            # Create settings content
            self._create_settings_content()
        else:
            self.settings_window.deiconify()  # Show window if it exists
            self.settings_window.lift()       # Bring to front
            self.settings_window.focus_force() # Force focus

    def _create_settings_content(self):
        """Create settings window content"""
        # Create main frame with padding
        main_frame = ttk.Frame(self.settings_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Font Sizes
        font_frame = ttk.LabelFrame(main_frame, text="Font Settings", padding="5")
        font_frame.pack(fill=tk.X, pady=5)

        # Large Font Size
        ttk.Label(font_frame, text="Large Font Size:").grid(row=0, column=0, padx=5, pady=2)
        large_font_size = ttk.Entry(font_frame, width=10)
        large_font_size.insert(0, str(self.config_manager.settings.font_size_large))
        large_font_size.grid(row=0, column=1, padx=5, pady=2)

        # Medium Font Size
        ttk.Label(font_frame, text="Medium Font Size:").grid(row=1, column=0, padx=5, pady=2)
        medium_font_size = ttk.Entry(font_frame, width=10)
        medium_font_size.insert(0, str(self.config_manager.settings.font_size_medium))
        medium_font_size.grid(row=1, column=1, padx=5, pady=2)

        # Barcode Settings
        barcode_frame = ttk.LabelFrame(main_frame, text="Barcode Settings", padding="5")
        barcode_frame.pack(fill=tk.X, pady=5)

        # Barcode Width
        ttk.Label(barcode_frame, text="Barcode Width:").grid(row=0, column=0, padx=5, pady=2)
        barcode_width = ttk.Entry(barcode_frame, width=10)
        barcode_width.insert(0, str(self.config_manager.settings.barcode_width))
        barcode_width.grid(row=0, column=1, padx=5, pady=2)

        # Barcode Height
        ttk.Label(barcode_frame, text="Barcode Height:").grid(row=1, column=0, padx=5, pady=2)
        barcode_height = ttk.Entry(barcode_frame, width=10)
        barcode_height.insert(0, str(self.config_manager.settings.barcode_height))
        barcode_height.grid(row=1, column=1, padx=5, pady=2)

        # CSV Import Frame
        csv_frame = ttk.LabelFrame(main_frame, text="Batch Import", padding="5")
        csv_frame.pack(fill=tk.X, pady=5)

        # CSV Import Description
        ttk.Label(csv_frame, text="Import multiple labels from a CSV file.\nRequired columns: 'Goods Name', 'Goods Barcode'", 
                 justify=tk.LEFT).pack(padx=5, pady=2)

        # Upload CSV Button
        upload_csv_btn = ttk.Button(
            csv_frame,
            text="Upload CSV File",
            command=self.upload_csv,
            style="Accent.TButton"
        )
        upload_csv_btn.pack(pady=5)

        # Save Button
        def save_settings():
            try:
                # Update settings
                self.config_manager.settings.font_size_large = int(large_font_size.get())
                self.config_manager.settings.font_size_medium = int(medium_font_size.get())
                self.config_manager.settings.barcode_width = int(barcode_width.get())
                self.config_manager.settings.barcode_height = int(barcode_height.get())
                
                # Save to file
                self.config_manager.save_settings()
                
                # Reinitialize barcode generator with new settings
                self.barcode_generator = BarcodeGenerator(self.config_manager.settings)
                
                # Close window
                self.settings_window.destroy()
                
                # Show success message
                messagebox.showinfo("Success", "Settings saved successfully!")
                
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid value: {str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

        save_btn = ttk.Button(
            main_frame,
            text="Save Settings",
            command=save_settings,
            style="Accent.TButton"
        )
        save_btn.pack(pady=10)

    def preview_label(self):
        """Show label preview window"""
        # Get input values
        name_line1 = self.inputs["name_line1"].get().strip()
        name_line2 = self.inputs["name_line2"].get().strip()
        variant = self.inputs["variant"].get().strip()
        upc_code = self.inputs["upc_code"].get().strip()
        
        # Validate inputs
        if not name_line1:
            messagebox.showwarning("Warning", "Product Name Line 1 is required.")
            self.inputs["name_line1"].focus_set()
            return
            
        if not upc_code or len(upc_code) != 12:
            messagebox.showwarning("Warning", "UPC Code must be exactly 12 digits.")
            self.inputs["upc_code"].focus_set()
            return
        
        # Create label data object
        label_data = LabelData(
            name_line1=name_line1,
            name_line2=name_line2,
            variant=variant,
            upc_code=upc_code
        )
        
        # Generate preview image
        try:
            preview_image = self.barcode_generator.generate_label(label_data)
            if not preview_image:
                raise Exception("Failed to generate label")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate preview: {str(e)}")
            return
        
        # Create or update preview window
        if not hasattr(self, 'preview_window') or not self.preview_window or not self.preview_window.winfo_exists():
            self.preview_window = tk.Toplevel(self)
            self.preview_window.title("Label Preview")
            self.preview_window.resizable(False, False)
            self.preview_window.transient(self)
            
            # Add to window tracking
            self.app_windows.append(self.preview_window)
            
            # Bind focus event
            self.preview_window.bind("<FocusIn>", lambda e: self._on_window_focus(self.preview_window))
            
            # Create preview frame
            preview_frame = tk.Frame(self.preview_window)
            preview_frame.pack(padx=10, pady=10)
            
            # Create preview label
            self.preview_label = tk.Label(preview_frame)
            self.preview_label.pack()
            
            # Create save button with styling
            save_btn = tk.Button(preview_frame,
                text="Save Label",
                command=lambda: self.save_label(label_data),
                bg='#2ecc71',  # Green
                fg='white',
                activebackground='#27ae60',
                activeforeground='white',
                font=('TkDefaultFont', 10, 'bold'),
                relief='raised',
                width=15,
                height=2
            )
            save_btn.pack(pady=10)
        
        # Update preview image
        preview_photo = ImageTk.PhotoImage(preview_image)
        self.preview_label.config(image=preview_photo)
        self.preview_label.image = preview_photo  # Keep reference
        
        # Center on parent
        self.preview_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - self.preview_window.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - self.preview_window.winfo_height()) // 2
        self.preview_window.geometry(f"+{x}+{y}")
        
        # Show window
        self.preview_window.deiconify()
        self.preview_window.lift()
        self.preview_window.focus_force()

    def save_label(self, label_data):
        """Save the label to a file"""
        if not self.config_manager.settings.last_directory:
            directory = filedialog.askdirectory(
                title="Select where to save labels"
            )
            if not directory:
                return
            self.config_manager.settings.last_directory = directory
            self.config_manager.save_settings()
        
        try:
            # Generate and save the label
            self.barcode_generator.generate_and_save(
                label_data,
                self.config_manager.settings.last_directory
            )
            
            # Update PNG count
            self._update_png_count()
            
            # Close preview window
            if hasattr(self, 'preview_window') and self.preview_window:
                self.preview_window.destroy()
                self.preview_window = None
            
            # Show success message
            messagebox.showinfo("Success", "Label saved successfully!")
            
            # Clear inputs
            self.clear_inputs()
            
            # Focus on first input
            self.inputs["name_line1"].focus_set()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save label: {str(e)}")
