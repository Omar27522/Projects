import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os
import pandas as pd

from src.ui.config import ConfigManager
from src.utils.logger import setup_logger
from src.ui.window_manager import WindowManager
from src.ui.barcode_generator import BarcodeGenerator, LabelData
from src.utils.csv_processor import is_valid_barcode, process_product_name
from src.ui.window_state import WindowState

from src.ui.components.preview_window import PreviewWindow
from src.ui.components.input_frame import InputFrame
from src.ui.components.action_buttons import ActionButtons
from src.ui.components.top_control_frame import TopControlFrame

# Get logger instance
logger = setup_logger()

class MainWindow(tk.Tk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()

        # Initialize managers
        self.window_state = WindowState()
        self.window_state.add_window(self)
        self.config_manager = ConfigManager()
        self.window_manager = WindowManager()
        self.barcode_generator = BarcodeGenerator(settings=self.config_manager.settings)

        # Initialize state variables
        self.last_print_time = None
        self.last_printed_upc = None
        self.current_preview = None
        self.always_on_top = tk.BooleanVar(value=self.config_manager.settings.always_on_top)

        self._setup_window()
        self._create_components()
        self._layout_components()

    def _setup_window(self):
        """Configure main window"""
        self.title("Label Generator")
        self.resizable(False, False)
        self.configure(bg='SystemButtonFace')
        self.bind("<FocusIn>", lambda e: self._on_window_focus(self))

    def _create_components(self):
        """Create UI components"""
        self.main_frame = tk.Frame(self, bg='SystemButtonFace')
        self.top_control = TopControlFrame(self.main_frame)
        self.input_frame = InputFrame(self.main_frame)
        self.action_buttons = ActionButtons(self.main_frame)

    def _layout_components(self):
        """Layout UI components"""
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.top_control.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
        self.input_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=5)
        self.action_buttons.grid(row=2, column=0, columnspan=2, pady=10)

    def _on_window_focus(self, focused_window):
        """Handle window focus to manage stacking order"""
        if self.always_on_top.get():
            focused_window.lift()
            focused_window.focus_force()

    def preview_label(self):
        """Show label preview window"""
        # Get input values
        values = self.input_frame.get_values()
        
        # Validate inputs
        if not values["name_line1"]:
            messagebox.showwarning("Warning", "Product Name Line 1 is required.")
            self.input_frame.inputs["name_line1"].focus_set()
            return

        if not values["upc_code"] or len(values["upc_code"]) != 12:
            messagebox.showwarning("Warning", "UPC Code must be exactly 12 digits.")
            self.input_frame.inputs["upc_code"].focus_set()
            return

        # Create label data object
        label_data = LabelData(**values)

        # Generate preview image
        try:
            preview_image = self.barcode_generator.generate_label(label_data)
            if not preview_image:
                raise Exception("Failed to generate label")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate preview: {str(e)}")
            return

        # Create or focus existing preview window
        preview_window = self.window_state.get_window_by_type(PreviewWindow)
        if preview_window and preview_window.winfo_exists():
            preview_window.update_preview(preview_image, label_data)
            preview_window.deiconify()
            preview_window.lift()
            preview_window.focus_force()
        else:
            preview_window = PreviewWindow(
                master=self,
                preview_image=preview_image,
                label_data=label_data,
                window_state=self.window_state,
                save_callback=self.save_label
            )

    def save_label(self, label_data):
        """Save the label to a file"""
        try:
            if not self.config_manager.settings.last_directory:
                directory = filedialog.askdirectory(
                    title="Select where to save labels"
                )
                if not directory:
                    return
                self.config_manager.settings.last_directory = directory
                self.config_manager.save_settings()
                self.top_control.update_label_count()
                self.view_directory_files()

            # Generate and save the label
            self.barcode_generator.generate_and_save(
                label_data,
                self.config_manager.settings.last_directory
            )

            # Update label counter
            self.top_control.update_label_count()

            # Close preview window
            preview_window = self.window_state.get_window_by_type(PreviewWindow)
            if preview_window:
                preview_window.destroy()

            # Show success message
            messagebox.showinfo("Success", "Label saved successfully!")

            # Clear inputs and focus first field
            self.input_frame.clear_inputs()
            self.input_frame.focus_first()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save label: {str(e)}")

    def toggle_always_on_top(self):
        """Toggle the always on top state"""
        self.always_on_top.set(not self.always_on_top.get())
        if self.always_on_top.get():
            self.top_control.always_on_top_btn.config(
                bg='#2ecc71',  # Bright green when active
                activebackground='#27ae60',  # Darker green when clicked
                relief='sunken'
            )
            self.attributes('-topmost', True)
            self.lift()
            self.focus_force()
        else:
            self.top_control.always_on_top_btn.config(
                bg='#e74c3c',  # Back to red
                activebackground='#c0392b',
                relief='raised'
            )
            self.attributes('-topmost', False)

    def view_directory_files(self):
        """View files in the current directory"""
        try:
            # Import here to avoid circular import
            from src.ui.file_viewer import FileViewer

            # Check for existing FileViewer
            file_viewer = self.window_state.get_window_by_type(FileViewer)

            if file_viewer:
                # If exists, bring it to front
                file_viewer.deiconify()
                file_viewer.lift()
                file_viewer.focus_force()
            else:
                # Create new FileViewer
                file_viewer = FileViewer(master=self)

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

                file_viewer.focus_force()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file viewer: {str(e)}")

    def upload_csv(self):
        """Handle CSV file upload"""
        try:
            # Create file dialog
            file_path = filedialog.askopenfilename(
                title="Select CSV File",
                filetypes=[("CSV files", "*.csv")],
                parent=self
            )

            if not file_path:
                return

            # Create progress window
            progress_window = tk.Toplevel(self)
            progress_window.title("Processing CSV")
            progress_window.geometry("300x150")
            progress_window.transient(self)
            progress_window.grab_set()

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
                    self.top_control.update_label_count()

                except Exception as e:
                    messagebox.showerror("Error", f"Failed to process CSV: {str(e)}")
                finally:
                    progress_window.destroy()

            # Start processing in the main thread since we have a progress window
            process_csv()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload CSV: {str(e)}")

    def run(self):
        """Start the application"""
        self.mainloop()
