import tkinter as tk
from PIL import ImageTk
from tkinter import messagebox

class PreviewWindow(tk.Toplevel):
    """Window for previewing labels before saving"""
    
    def __init__(self, master, preview_image, label_data, window_state, save_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.preview_image = preview_image
        self.label_data = label_data
        self.save_callback = save_callback
        self.window_state = window_state
        self.current_photo = None  # Initialize the PhotoImage reference

        self._setup_window()
        self._create_widgets()
        self._layout_widgets()
        
        # Display the initial preview
        self.update_preview(preview_image, label_data)

    def _setup_window(self):
        """Configure window properties"""
        self.title("Label Preview")
        self.resizable(False, False)
        self.transient(self.master)

        # Add to window tracking
        self.window_state.add_window(self)

        # Set up close handler
        def on_close():
            self.window_state.remove_window(self)
            self.destroy()
        self.protocol("WM_DELETE_WINDOW", on_close)

    def _create_widgets(self):
        """Create window widgets"""
        # Create main frame that fills the window
        self.main_frame = tk.Frame(self)
        
        # Create preview frame with white background
        self.preview_frame = tk.Frame(self.main_frame, bg='white')
        
        # Create preview label that expands
        self.preview_label = tk.Label(self.preview_frame, bg='white')
        
        # Create save button with styling
        self.save_btn = tk.Button(
            self.main_frame,
            text="Save Label",
            command=lambda: self.save_callback(self.label_data),
            bg='#2ecc71',
            fg='white',
            activebackground='#27ae60',
            activeforeground='white',
            font=('TkDefaultFont', 10, 'bold'),
            relief='raised',
            width=15,
            height=2
        )

    def _layout_widgets(self):
        """Layout window widgets"""
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.preview_frame.pack(fill=tk.BOTH, expand=True)
        self.preview_label.pack(expand=True)
        self.save_btn.pack(pady=10)

    def update_preview(self, preview_image=None, label_data=None):
        """Update the preview image and label data"""
        if preview_image is not None:
            self.preview_image = preview_image
        if label_data is not None:
            self.label_data = label_data

        try:
            if self.preview_image is None:
                raise ValueError("Preview image is None")
                
            # Print debug info
            print(f"Preview image details:")
            print(f"Type: {type(self.preview_image)}")
            print(f"Mode: {self.preview_image.mode}")
            print(f"Size: {self.preview_image.size}")

            # Ensure image is in RGB mode
            if self.preview_image.mode != 'RGB':
                self.preview_image = self.preview_image.convert('RGB')

            # Create PhotoImage and keep reference
            photo = ImageTk.PhotoImage(self.preview_image)
            self.preview_label.config(image=photo)
            self.current_photo = photo  # Keep a strong reference

            # Size window to fit image plus padding
            width = self.preview_image.width + 40
            height = self.preview_image.height + 100
            self.geometry(f"{width}x{height}")

            # Center on parent
            self.update_idletasks()
            x = self.master.winfo_x() + (self.master.winfo_width() - width) // 2
            y = self.master.winfo_y() + (self.master.winfo_height() - height) // 2
            self.geometry(f"+{x}+{y}")

        except Exception as e:
            error_msg = f"Failed to update preview:\nError type: {type(e).__name__}\nDetails: {str(e)}"
            messagebox.showerror("Error", error_msg)
            print(f"Error updating preview: {error_msg}")
