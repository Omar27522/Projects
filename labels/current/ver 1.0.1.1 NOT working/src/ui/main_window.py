import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Any, Callable
import os
from PIL import Image, ImageTk
import pyautogui
import pandas as pd
from ..config import ConfigManager
from ..utils.logger import setup_logger
from .window_manager import WindowManager
from ..barcode_generator import BarcodeGenerator, LabelData
from ..utils.csv_processor import is_valid_barcode, process_product_name, sanitize_filename
from .window_state import WindowState
import time
import re

# Get logger instance
logger = setup_logger()

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Initialize window state
        self.window_state = WindowState()
        self.window_state.add_window(self)
        
        self.config_manager = ConfigManager()
        self.window_manager = WindowManager()
        self.barcode_generator = BarcodeGenerator(self.config_manager.settings)
        
        # Add tracking for last printed label
        self.last_print_time = None
        self.last_printed_upc = None
        
        self._setup_fonts()
        self._setup_variables()
        self._create_tooltip_class()
        self._create_main_window()
        
        # Bind focus event to main window
        self.bind("<FocusIn>", lambda e: self._on_window_focus(self))

    def view_directory_files(self):
        """View files in the current directory"""
        try:
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
                # Create new FileViewer
                file_viewer = FileViewer()
                
                # Set up close handler
                def on_close():
                    self.window_state.remove_window(file_viewer)
                    file_viewer.destroy()
                
                file_viewer.protocol("WM_DELETE_WINDOW", on_close)
                
                # Center relative to main window
                file_viewer.update_idletasks()
                x = self.winfo_x() + (self.winfo_width() - file_viewer.winfo_width()) // 2
                y = self.winfo_y() + (self.winfo_height() - file_viewer.winfo_height()) // 2
                file_viewer.geometry(f"+{x}+{y}")
                
                file_viewer.mainloop()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file viewer: {str(e)}")

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

    def _set_window_icon(self, window, icon_size='64', icon_type='icon'):
        """Set the window icon for any window in the application"""
        try:
            # Set the Windows taskbar icon
            myappid = 'labelmaker.app.ver3.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            logger.error(f"Failed to set window icon: {str(e)}")

    def _create_main_window(self):
        """Create and setup the main application window"""
        # Configure main window
        self.title("Label Maker")
        self.minsize(450, 200)
        
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
        for window in self.window_state.get_all_windows():
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
        """Create top control frame with Always on Top and Labels Count buttons"""
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
        
        # Always on Top button
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

        # Labels count label
        self.png_count_label = tk.Label(
            control_frame,
            textvariable=self.png_count,
            font=('TkDefaultFont', 10, 'bold'),
            fg='#2ecc71',  # Green text
            bg='SystemButtonFace'
        )
        self.png_count_label.pack(side=tk.LEFT, padx=10)

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
        
        # Import CSV button with green theme
        csv_colors = {
            'bg': '#27ae60',  # Green
            'fg': 'white',
            'hover_bg': '#219a52',
            'active_bg': '#1e8449'
        }
        csv_btn = self._create_styled_button(
            button_frame,
            text="Import CSV",
            command=self.upload_csv,
            width=10,
            tooltip_text="Import labels from a CSV file",
            color_scheme=csv_colors
        )
        csv_btn.pack(side=tk.LEFT, padx=2)

    def upload_csv(self):
        """Handle CSV file upload"""
        try:
            # Create file dialog
            file_path = filedialog.askopenfilename(
                title="Select CSV File",
                filetypes=[("CSV files", "*.csv")],
                parent=self  # Make dialog modal to main window
            )
            
            if not file_path:
                return
                
            # Create progress window
            progress_window = tk.Toplevel(self)
            progress_window.title("Processing CSV")
            progress_window.geometry("300x150")
            progress_window.transient(self)  # Make it modal
            progress_window.grab_set()  # Make it modal
            
            # Center the progress window
            progress_window.update_idletasks()
            x = self.winfo_x() + (self.winfo_width() - progress_window.winfo_width()) // 2
            y = self.winfo_y() + (self.winfo_height() - progress_window.winfo_height()) // 2
            progress_window.geometry(f"+{x}+{y}")
            
            # Add progress label
            progress_label = tk.Label(progress_window, text="Processing CSV file...\nPlease wait...", pady=10)
            progress_label.pack()
            
            # Add progress bar
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(
                progress_window,
                variable=progress_var,
                maximum=100,
                mode='determinate',
                length=200
            )
            progress_bar.pack(pady=10)
            
            # Add cancel button
            self._cancel_process = False
            cancel_btn = ttk.Button(
                progress_window,
                text="Cancel",
                command=lambda: setattr(self, '_cancel_process', True)
            )
            cancel_btn.pack(pady=5)
            
            def process_csv():
                try:
                    # Read the CSV file
                    df = pd.read_csv(file_path)
                    
                    # Validate required columns
                    required_columns = ['Goods Barcode', 'Goods Name']
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    if missing_columns:
                        raise ValueError(f"Missing required columns in CSV: {', '.join(missing_columns)}\n"
                                      f"CSV must contain columns: {', '.join(required_columns)}")
                    
                    total_rows = len(df)
                    
                    # Get save directory from settings or use default
                    save_dir = self.config_manager.settings.last_directory
                    if not os.path.exists(save_dir):
                        os.makedirs(save_dir, exist_ok=True)
                    
                    labels_created = 0
                    skipped_labels = 0
                    
                    # Process each row
                    for index, row in df.iterrows():
                        if self._cancel_process:
                            messagebox.showinfo("Cancelled", "CSV processing was cancelled.")
                            break
                            
                        barcode = str(row['Goods Barcode'])
                        
                        # Skip if barcode is invalid
                        if not is_valid_barcode(barcode):
                            skipped_labels += 1
                            logger.warning(f"Skipping invalid barcode: {barcode}")
                            continue
                        
                        # Process product name
                        name_line1, name_line2, variant = process_product_name(str(row['Goods Name']))
                        
                        # Create label data
                        label_data = LabelData(
                            name_line1=name_line1,
                            name_line2=name_line2,
                            variant=variant,
                            upc_code=barcode
                        )
                        
                        # Generate and save label
                        self.barcode_generator.generate_and_save(label_data, save_dir)
                        labels_created += 1
                        
                        # Update progress
                        progress = (index + 1) / total_rows * 100
                        progress_var.set(progress)
                        progress_window.update()
                    
                    # Show completion message
                    messagebox.showinfo(
                        "Complete",
                        f"CSV processing complete!\n"
                        f"Labels created: {labels_created}\n"
                        f"Labels skipped: {skipped_labels}"
                    )
                    
                    # Update label counter
                    self._update_png_count()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to process CSV: {str(e)}")
                finally:
                    progress_window.destroy()
            
            # Start processing in the main thread since we have a progress window
            process_csv()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload CSV: {str(e)}")

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
        if self.config_manager.settings.last_directory and os.path.exists(self.config_manager.settings.last_directory):
            # Count PNG files in directory
            png_files = [f for f in os.listdir(self.config_manager.settings.last_directory)
                        if f.lower().endswith('.png')]
            self.config_manager.settings.label_counter = len(png_files)
            self.config_manager.save_settings()
        
        # Update label
        self.png_count.set(f"Labels: {self.config_manager.settings.label_counter}")

    def preview_label(self):
        """Show label preview window"""
        # If preview window exists and is valid, focus it
        if hasattr(self, 'preview_window') and self.preview_window and self.preview_window.winfo_exists():
            self.preview_window.deiconify()
            self.preview_window.lift()
            self.preview_window.focus_force()
            return

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
            self.window_state.add_window(self.preview_window)
            
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
