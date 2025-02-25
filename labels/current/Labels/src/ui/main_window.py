import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Any, Callable
import os
import pandas as pd
from PIL import Image, ImageTk
import pyautogui
from ..config import ConfigManager
from .window_manager import WindowManager
from .window_icon_manager import WindowIconManager
from .settings_window import SettingsWindow
from .main_win.file_viewer_window import FileViewerWindow
from .main_win.input_field_manager import InputFieldManager
from .main_win.undo_redo_manager import UndoRedoManager
from .main_win.tooltip_manager import ToolTip
from ..barcode_generator import BarcodeGenerator, LabelData
from ..utils.csv_processor import is_valid_barcode, process_product_name, sanitize_filename
from ..utils.logger import setup_logger

# Get logger instance
logger = setup_logger()

class MainWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        
        # Initialize window tracking
        self.app_windows = []  # Track all windows
        self.app_windows.append(self)  # Include main window
        
        # Initialize managers
        self.config_manager = parent.config_manager
        try:
            self.window_manager = WindowManager()
            logger.debug("Window manager initialized")
        except Exception as e:
            logger.error("Failed to initialize window manager", exc_info=True)
            raise
            
        try:
            self.window_icon_manager = parent.window_icon_manager
            logger.debug("Window icon manager initialized")
        except Exception as e:
            logger.error("Failed to initialize window icon manager", exc_info=True)
            raise
            
        try:
            self.barcode_generator = BarcodeGenerator(self.config_manager.settings)
            logger.debug("Barcode generator initialized")
        except Exception as e:
            logger.error("Failed to initialize barcode generator", exc_info=True)
            raise
            
        try:
            self.undo_redo_manager = UndoRedoManager()
            logger.debug("Undo/Redo manager initialized")
        except Exception as e:
            logger.error("Failed to initialize Undo/Redo manager", exc_info=True)
            raise
            
        # Add tracking for last printed label
        self.last_print_time = None
        self.last_printed_upc = None
        
        # Add auto-switch state
        self.is_auto_switch = tk.BooleanVar(value=True)  # Default to auto-switch enabled
        
        # Set initial transparency
        self.attributes('-alpha', self.config_manager.settings.transparency_level)
        
        # Initialize UI components
        self._setup_fonts()
        self._setup_variables()
        self._load_icons()
        
        # Create main window and frame
        self._create_main_window()
        
    def on_error(self, error_msg: str, exc_info=None):
        """Handle errors by showing message box and logging"""
        logger.error(error_msg, exc_info=exc_info)
        messagebox.showerror("Error", error_msg)

    def _setup_fonts(self):
        """Configure default fonts"""
        self.default_font = ('TkDefaultFont', 10, 'bold')
        self.button_font = ('TkDefaultFont', 10, 'bold')
        self.entry_font = ('TkDefaultFont', 10, 'bold')
        self.label_font = ('TkDefaultFont', 10, 'bold')
        
        # Set fonts for all widgets
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
        self.png_count = tk.StringVar(value=str(self.config_manager.settings.label_counter))
        
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

    def _create_main_window(self):
        """Create and setup the main application window"""
        # Set window title and icon
        self.title("Label Maker")
        WindowIconManager.set_window_icon(self, '64', 'icon')
        
        # Configure main window
        self.geometry("453x321")  # Set exact window size
        self.minsize(453, 321)
        
        try:
            # Set the main window app ID
            import ctypes
            app_id = 'labelmaker.main.window'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except Exception:
            pass  # Fail silently if Windows-specific call fails
        
        # Center window on screen
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 453) // 2
        y = (screen_height - 321) // 2
        self.geometry(f"+{x}+{y}")
        
        # Prevent window resizing
        self.resizable(False, False)
        
        # Bind window close event
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Create main frame
        self.main_frame = tk.Frame(self, bg='SystemButtonFace')
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        
        # Create top button row
        self._create_top_buttons()
        
        # Create input fields frame with more vertical space
        input_frame = tk.Frame(self.main_frame, bg='SystemButtonFace')
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        # Configure input frame rows to expand
        input_frame.grid_rowconfigure(0, weight=1)
        input_frame.grid_rowconfigure(1, weight=1)
        input_frame.grid_rowconfigure(2, weight=1)
        input_frame.grid_rowconfigure(3, weight=1)
        
        # Create input fields with more height
        self.input_field_manager = InputFieldManager(self, input_frame, self.config_manager, self.undo_redo_manager)
        
        # Create bottom button row
        self._create_bottom_buttons()

    def _create_top_buttons(self):
        """Create top row of buttons"""
        top_frame = tk.Frame(self.main_frame, bg='SystemButtonFace')
        top_frame.pack(fill=tk.X, pady=2)
        
        # Always on Top button (red)
        always_on_top_btn = tk.Button(
            top_frame,
            text="Always on Top",
            bg='#FF6B6B',  # Red
            fg='white',
            command=self.toggle_always_on_top
        )
        always_on_top_btn.pack(side=tk.LEFT, padx=2)
        
        # Settings button (purple)
        settings_btn = tk.Button(
            top_frame,
            text="Settings",
            bg='#9C27B0',  # Purple
            fg='white',
            command=self.show_settings
        )
        settings_btn.pack(side=tk.LEFT, padx=2)
        
        # Labels count (green)
        tk.Label(
            top_frame,
            text="Labels:",
            font=('TkDefaultFont', 10),
            fg='green',
            bg='SystemButtonFace'
        ).pack(side=tk.LEFT)
        
        tk.Label(
            top_frame,
            textvariable=self.png_count,
            font=('TkDefaultFont', 10),
            fg='green',
            bg='SystemButtonFace'
        ).pack(side=tk.LEFT, padx=(2, 5))

    def _create_bottom_buttons(self):
        """Create bottom row of buttons"""
        bottom_frame = tk.Frame(self.main_frame, bg='SystemButtonFace')
        bottom_frame.pack(fill=tk.X, pady=(10, 5))
        
        # Reset button (red)
        reset_btn = tk.Button(
            bottom_frame,
            text="Reset",
            bg='#FF6B6B',  # Red
            fg='white',
            command=self.reset_fields
        )
        reset_btn.pack(side=tk.LEFT, padx=2)
        
        # Preview button (blue)
        preview_btn = tk.Button(
            bottom_frame,
            text="Preview",
            bg='#2196F3',  # Blue
            fg='white',
            command=self.preview_label
        )
        preview_btn.pack(side=tk.LEFT, padx=2)
        
        # View Files button (blue)
        view_files_btn = tk.Button(
            bottom_frame,
            text="View Files",
            bg='#2196F3',  # Blue
            fg='white',
            command=self.view_directory_files
        )
        view_files_btn.pack(side=tk.LEFT, padx=2)

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
        self.file_window = FileViewerWindow(self, self.config_manager, self.window_icon_manager)
        
    def show_settings(self):
        """Show settings window"""
        settings_window = SettingsWindow(self, self.config_manager)
        self.app_windows.append(settings_window)

    def toggle_always_on_top(self):
        """Toggle the always on top state"""
        current_state = self.always_on_top.get()
        self.always_on_top.set(not current_state)
        self.attributes('-topmost', not current_state)

    def update_window_transparency(self):
        """Update the transparency of the main window"""
        self.attributes('-alpha', self.transparency_level.get())

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

    def _add_context_menu(self, widget):
        """Add right-click context menu to widget"""
        menu = tk.Menu(widget, tearoff=0)
        menu.add_command(label="Cut", command=lambda: widget.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: widget.event_generate("<<Paste>>"))
        menu.add_separator()
        menu.add_command(label="Select All", command=lambda: widget.select_range(0, tk.END))
        
        def show_menu(event):
            menu.post(event.x_root, event.y_root)
            
        widget.bind("<Button-3>", show_menu)

    def preview_label(self):
        """Show a preview of the label"""
        try:
            # Get current input values
            label_data = self.get_label_data()
            if not label_data:
                return
            
            # Generate preview image
            preview_img = self.barcode_generator.generate_label(label_data)
            if not preview_img:
                raise ValueError("Failed to generate preview image")
            
            # Scale down for preview
            preview_width = int(self.config_manager.settings.LABEL_WIDTH * 0.5)  # 50% of original size
            preview_height = int(self.config_manager.settings.LABEL_HEIGHT * 0.5)
            preview_img = preview_img.resize(
                (preview_width, preview_height),
                Image.Resampling.LANCZOS
            )
            
            # Convert PIL image to PhotoImage
            preview_photo = ImageTk.PhotoImage(preview_img)
            
            # Create preview window
            preview_window = tk.Toplevel(self)
            preview_window.title("Label Preview")
            preview_window.resizable(False, False)
            
            # Keep a reference to prevent garbage collection
            preview_window.preview_photo = preview_photo
            
            # Show preview
            preview_label = tk.Label(preview_window, image=preview_photo)
            preview_label.pack(padx=10, pady=10)
            
            # Center preview window relative to main window
            preview_window.geometry("+{}+{}".format(self.winfo_rootx() + 50,
                                              self.winfo_rooty() + 50))
            
            # Make window modal
            preview_window.transient(self)
            preview_window.grab_set()
            
            # Set window icon
            self.window_icon_manager.set_window_icon(preview_window, '32', 'icon')
            
        except Exception as e:
            self.on_error(f"Failed to generate preview: {str(e)}", exc_info=True)

    def get_label_data(self) -> Optional[LabelData]:
        """Get label data from input fields"""
        try:
            # Get input values
            name_line1 = self.input_field_manager.input_vars['name_line1'].get().strip()
            name_line2 = self.input_field_manager.input_vars['name_line2'].get().strip()
            variant = self.input_field_manager.input_vars['variant'].get().strip()
            upc_code = self.input_field_manager.input_vars['upc_code'].get().strip()
            
            # Basic validation
            if not name_line1:
                self.on_error("Name Line 1 is required")
                return None
                
            if not upc_code:
                self.on_error("UPC Code is required")
                return None
                
            if not is_valid_barcode(upc_code):
                self.on_error("Invalid UPC Code. Must be exactly 12 digits.")
                return None
            
            return LabelData(
                name_line1=name_line1,
                name_line2=name_line2,
                variant=variant,
                upc_code=upc_code
            )
            
        except Exception as e:
            self.on_error(f"Failed to get label data: {str(e)}", exc_info=True)
            return None

    def save_label(self, label_data=None):
        """Save the label to a file"""
        try:
            # If no label data provided, get from input fields
            if label_data is None:
                label_data = self.get_label_data()
                
            if not label_data:
                return
                
            # Check if we have a save directory
            if not self.config_manager.settings.last_directory:
                self.on_error("Please select an output directory in Settings first")
                return
                
            # Generate and save the label
            self.barcode_generator.generate_and_save(label_data, self.config_manager.settings.last_directory)
            
            # Update label counter by counting files
            self.config_manager.update_label_counter()
            self.png_count.set(str(self.config_manager.settings.label_counter))
            
        except Exception as e:
            self.on_error(f"Failed to save label: {str(e)}", exc_info=True)

    def upload_csv(self):
        """Handle CSV file upload"""
        try:
            file_path = filedialog.askopenfilename(
                title="Select CSV File",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if file_path:
                # Read CSV file
                df = pd.read_csv(file_path)
                
                # Process each row
                for _, row in df.iterrows():
                    try:
                        # Create label data
                        label_data = LabelData(
                            name_line1=process_product_name(str(row['name_line1'])),
                            name_line2=process_product_name(str(row['name_line2'])) if 'name_line2' in row else '',
                            variant=process_product_name(str(row['variant'])) if 'variant' in row else '',
                            upc_code=str(row['upc_code'])
                        )
                        
                        # Validate UPC
                        if not is_valid_barcode(label_data.upc_code):
                            logger.warning(f"Invalid UPC code: {label_data.upc_code}")
                            continue
                        
                        # Save label
                        self.save_label(label_data)
                        
                    except Exception as e:
                        logger.error(f"Failed to process row: {str(e)}")
                        continue
                
                messagebox.showinfo("Success", "CSV processing complete!")
                
        except Exception as e:
            self.on_error(f"Failed to process CSV: {str(e)}", exc_info=True)

    def on_close(self):
        """Handle window close event"""
        # Just hide the window instead of closing the application
        self.withdraw()

    def run(self):
        """Start the application"""
        try:
            self.mainloop()
        except Exception as e:
            self.on_error(f"Failed to start application: {str(e)}", exc_info=True)
            raise

    def reset_fields(self):
        """Reset all input fields"""
        self.input_field_manager.clear_inputs()

    def load_labels_from_csv(self, file_path):
        """Load label data from a CSV file"""
        try:
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
                length=250
            )
            progress_bar.pack(pady=20)
            
            # Add cancel button
            cancel_button = ttk.Button(
                progress_window,
                text="Cancel",
                command=lambda: [progress_window.destroy(), setattr(self, '_cancel_process', True)]
            )
            cancel_button.pack(pady=10)
            
            # Initialize cancel flag
            self._cancel_process = False
            
            def process_csv():
                try:
                    # Read the CSV file
                    df = pd.read_csv(file_path)
                    
                    # Check if required columns exist
                    required_columns = ['Goods Name', 'Goods Barcode']
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    if missing_columns:
                        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
                    
                    if df.empty:
                        raise ValueError("CSV file is empty")

                    total_rows = len(df)
                    processed_rows = 0
                    failed_rows = []

                    # Process each row
                    for index, row in df.iterrows():
                        if self._cancel_process:
                            break

                        try:
                            barcode = str(row['Goods Barcode'])
                            if not is_valid_barcode(barcode):
                                failed_rows.append(f"Row {index + 1}: Invalid barcode format: {barcode}")
                                continue

                            # Process the product name
                            full_name = str(row['Goods Name'])
                            name_line1, name_line2, variant = process_product_name(full_name)

                            # Create label data
                            label_data = LabelData(
                                name_line1=name_line1,
                                name_line2=name_line2,
                                variant=variant,
                                upc_code=barcode
                            )

                            # Save the label
                            self.save_label(label_data)
                            processed_rows += 1

                            # Update progress
                            progress = (processed_rows / total_rows) * 100
                            progress_var.set(progress)
                            progress_label.config(text=f"Processing row {processed_rows} of {total_rows}...")
                            progress_window.update()

                        except Exception as e:
                            failed_rows.append(f"Row {index + 1}: {str(e)}")
                            logger.error(f"Error processing row {index + 1}: {str(e)}")
                            continue

                    # Final status message
                    status_msg = f"Processed {processed_rows} of {total_rows} labels."
                    if failed_rows:
                        status_msg += f"\n\nFailed rows:\n" + "\n".join(failed_rows)

                    # Schedule UI updates on the main thread
                    progress_window.after(500, lambda: [
                        progress_window.destroy(),
                        messagebox.showinfo("Complete", status_msg)
                    ])

                except Exception as e:
                    # Schedule UI updates on the main thread
                    progress_window.after(0, lambda: [
                        progress_window.destroy(),
                        messagebox.showerror("Error", f"Failed to load CSV file: {str(e)}")
                    ])
                    logger.error(f"Error loading CSV: {str(e)}")
            
            # Start processing in a separate thread to keep UI responsive
            import threading
            thread = threading.Thread(target=process_csv)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            raise Exception(f"Error reading CSV file: {str(e)}")

    def _select_output_directory(self):
        """Select output directory"""
        directory = filedialog.askdirectory(
            initialdir=self.config_manager.settings.last_directory,
            title="Select Output Directory"
        )
        if directory:
            self.config_manager.settings.last_directory = directory
            self.config_manager.update_label_counter()  # Update counter when directory changes
            self.png_count.set(str(self.config_manager.settings.label_counter))
            self.config_manager.save_settings()
