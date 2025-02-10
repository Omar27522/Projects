#!/usr/bin/env python3
"""
Icon Maker
-----------
A GUI tool to create icons in multiple sizes.
The input image should be at least 256x256 pixels for best results.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import shutil
import ctypes

class IconMaker(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set the app ID for Windows taskbar
        try:
            myappid = 'labelmaker.iconmaker.ver1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            print(f"Failed to set app ID: {e}")

        # Window setup
        self.title("Icon Maker")
        self.geometry("500x450")  # Increased height
        self.minsize(400, 450)    # Increased minimum height
        self.configure(bg='white')
        self.resizable(True, True)  # Allow resizing
        self.maxsize(800, 800)    # Set maximum size
        
        # Remove maximize button
        self.attributes('-toolwindow', 1)  # Remove minimize/maximize buttons
        self.attributes('-toolwindow', 0)  # Restore minimize button
        
        # Set window icon
        try:
            # Get icon path
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'icon_maker_64.png')
            if not os.path.exists(icon_path):
                icon_path = os.path.join(os.path.dirname(__file__), '..', 'icon_maker_32.png')
            
            if os.path.exists(icon_path):
                # Load and set the icon using PhotoImage
                icon = tk.PhotoImage(file=icon_path)
                self.iconphoto(True, icon)
                # Keep reference to prevent garbage collection
                self._icon = icon
        except Exception as e:
            print(f"Failed to set window icon: {e}")
        
        # Initialize variables
        self.input_path = None
        self.preview_photo = None
        self.sizes = [16, 32, 48, 64, 128, 256]
        self.output_prefix = "icon"
        
        # Create GUI
        self._create_gui()
        
        # Center window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _create_gui(self):
        """Create the GUI elements"""
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Main frame with padding
        main_frame = ttk.Frame(self, padding="5")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Content frame (everything except create button)
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=0, column=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_frame = ttk.Frame(content_frame)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(
            title_frame,
            text="Icon Maker",
            font=('TkDefaultFont', 12, 'bold')
        ).pack()
        
        # Input frame
        input_frame = ttk.LabelFrame(content_frame, text="Input Image", padding="5")
        input_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        input_frame.grid_columnconfigure(1, weight=1)
        
        select_btn = ttk.Button(
            input_frame,
            text="Select Image",
            command=self._select_file,
            width=15
        )
        select_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.file_label = ttk.Label(
            input_frame,
            text="No file selected",
            font=('TkDefaultFont', 8),
            wraplength=350
        )
        self.file_label.grid(row=0, column=1, columnspan=2, sticky="w", padx=5)
        
        # Size tip
        tip_text = "Tooltip: Best results with square images.\nRecommended size: 256×256 pixels or smaller."
        self.tip_label = ttk.Label(
            input_frame,
            text=tip_text,
            font=('TkDefaultFont', 8),
            foreground='gray',
            justify='right'
        )
        self.tip_label.grid(row=0, column=2, padx=10, sticky="e")
        
        # Preview frame
        preview_frame = ttk.LabelFrame(content_frame, text="Preview", padding="5")
        preview_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 5))
        preview_frame.grid_rowconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        
        # Preview container with minimum size
        preview_container = ttk.Frame(preview_frame)
        preview_container.grid(row=0, column=0, sticky="nsew", pady=5)
        preview_container.grid_propagate(False)
        preview_container.configure(height=100)
        
        self.preview_label = ttk.Label(preview_container)
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Settings frame
        settings_frame = ttk.LabelFrame(content_frame, text="Settings", padding="5")
        settings_frame.grid(row=3, column=0, sticky="ew", pady=(0, 5))
        settings_frame.grid_columnconfigure(1, weight=1)
        
        # Output directory
        ttk.Label(settings_frame, text="Output:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        
        output_subframe = ttk.Frame(settings_frame)
        output_subframe.grid(row=0, column=1, columnspan=2, sticky="ew", pady=2)
        output_subframe.grid_columnconfigure(0, weight=1)
        
        default_output = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.output_dir_var = tk.StringVar(value=default_output)
        self.output_dir_label = ttk.Label(
            output_subframe,
            text=default_output,
            font=('TkDefaultFont', 8),
            wraplength=200
        )
        self.output_dir_label.grid(row=0, column=0, sticky="ew", padx=5)
        
        browse_btn = ttk.Button(
            output_subframe,
            text="Browse",
            command=self._browse_output_dir,
            width=8
        )
        browse_btn.grid(row=0, column=1, padx=5)
        
        # Prefix
        ttk.Label(settings_frame, text="Prefix:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        
        prefix_subframe = ttk.Frame(settings_frame)
        prefix_subframe.grid(row=1, column=1, columnspan=2, sticky="ew", pady=2)
        
        self.prefix_var = tk.StringVar(value="icon")
        self.prefix_var.trace_add("write", self._update_example)
        prefix_entry = ttk.Entry(prefix_subframe, textvariable=self.prefix_var, width=15)
        prefix_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(prefix_subframe, text="Example:").pack(side=tk.LEFT, padx=(10, 2))
        self.example_label = ttk.Label(
            prefix_subframe,
            text="icon_32.png",
            font=('TkDefaultFont', 8),
            foreground='gray'
        )
        self.example_label.pack(side=tk.LEFT, padx=2)
        
        # Sizes
        ttk.Label(settings_frame, text="Sizes:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        
        size_subframe = ttk.Frame(settings_frame)
        size_subframe.grid(row=2, column=1, columnspan=2, sticky="ew", pady=2)
        
        self.size_vars = {}
        for size in self.sizes:
            var = tk.BooleanVar(value=True)
            self.size_vars[size] = var
            ttk.Checkbutton(
                size_subframe,
                text=str(size),
                variable=var,
                padding=(2, 0)
            ).pack(side=tk.LEFT, padx=2)
        
        # Button frame at bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky="e", pady=(5, 0))
        
        create_btn = ttk.Button(
            button_frame,
            text="Create Icons",
            command=self._create_icons,
            style='Accent.TButton',
            width=15
        )
        create_btn.pack(side=tk.RIGHT)
        
        # Style for accent button
        style = ttk.Style()
        style.configure('Accent.TButton', font=('TkDefaultFont', 9, 'bold'))

    def _select_file(self):
        """Handle file selection"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Open and validate image
                with Image.open(file_path) as img:
                    # Store input path
                    self.input_path = file_path
                    
                    # Update file label with just the filename
                    filename = os.path.basename(file_path)
                    self.file_label.grid(columnspan=2)  # Span both columns when tip is hidden
                    self.file_label.config(text=filename)
                    
                    # Hide the tip
                    self.tip_label.grid_remove()
                    
                    # Show preview
                    self._update_preview(img)
                    
                    # Set prefix to filename without extension
                    filename = os.path.splitext(os.path.basename(file_path))[0]
                    self.prefix_var.set(filename)
                    
                    # Check image size
                    width, height = img.size
                    if width < 256 or height < 256:
                        messagebox.showwarning(
                            "Small Image",
                            "The selected image is smaller than 256x256 pixels.\n"
                            "This may result in lower quality icons."
                        )
            
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open image: {str(e)}")
                self.input_path = None
                self.file_label.grid(columnspan=1)  # Reset to single column when showing tip
                self.file_label.config(text="No file selected")
                self.preview_photo = None
                self.preview_label.config(image='')
                # Show the tip again on error
                self.tip_label.grid()

    def _update_preview(self, img):
        """Update the preview image"""
        # Calculate preview size (max 150x150 for more compact display)
        width, height = img.size
        if width > height:
            new_width = min(width, 120)  # Reduced from 150 to 120
            new_height = int(height * (new_width / width))
        else:
            new_height = min(height, 120)  # Reduced from 150 to 120
            new_width = int(width * (new_height / height))
        
        # Resize for preview
        preview = img.resize((new_width, new_height), Image.LANCZOS)
        self.preview_photo = ImageTk.PhotoImage(preview)
        self.preview_label.config(image=self.preview_photo)

    def _browse_output_dir(self):
        """Handle output directory selection"""
        dir_path = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir_var.get()
        )
        
        if dir_path:
            self.output_dir_var.set(dir_path)
            self.output_dir_label.config(text=dir_path)

    def _create_icons(self):
        """Create icons in selected sizes"""
        if not self.input_path:
            messagebox.showwarning("Warning", "Please select an image first.")
            return
        
        try:
            # Get selected sizes
            selected_sizes = [size for size, var in self.size_vars.items() if var.get()]
            if not selected_sizes:
                messagebox.showwarning("Warning", "Please select at least one size.")
                return
            
            # Get output prefix
            prefix = self.prefix_var.get().strip()
            if not prefix:
                messagebox.showwarning("Warning", "Please enter an output prefix.")
                return
            
            # Get output directory
            output_dir = self.output_dir_var.get()
            if not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to create output directory: {str(e)}")
                    return
            
            # Open input image
            with Image.open(self.input_path) as img:
                # Store resized images for ICO creation
                ico_images = []
                
                # Process each selected size
                for size in selected_sizes:
                    # Calculate new dimensions maintaining aspect ratio
                    width, height = img.size
                    if width > height:
                        new_width = size
                        new_height = int(size * (height / width))
                    else:
                        new_height = size
                        new_width = int(size * (width / height))
                    
                    # Resize image
                    resized = img.resize((new_width, new_height), Image.LANCZOS)
                    
                    # Create square image if needed
                    if new_width != new_height:
                        square = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                        x = (size - new_width) // 2
                        y = (size - new_height) // 2
                        square.paste(resized, (x, y))
                        resized = square
                    
                    # Save PNG icon
                    output_path = os.path.join(output_dir, f"{prefix}_{size}.png")
                    resized.save(output_path, 'PNG', optimize=True)
                    
                    # Store resized image for ICO creation
                    ico_images.append(resized.copy())
                
                # Create and save ICO file with all sizes
                ico_path = os.path.join(output_dir, f"{prefix}.ico")
                ico_images[0].save(
                    ico_path,
                    format='ICO',
                    sizes=[(size, size) for size in selected_sizes],
                    append_images=ico_images[1:]
                )
            
            # Show success message with ICO file mention
            messagebox.showinfo(
                "Success",
                f"Created {len(selected_sizes)} PNG icons and 1 ICO file in:\n{output_dir}"
            )
            
            # Open output directory
            os.startfile(output_dir)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create icons: {str(e)}")

    def _update_example(self, *args):
        """Update the example filename when prefix changes"""
        prefix = self.prefix_var.get().strip()
        if not prefix:
            prefix = "icon"
        self.example_label.config(text=f"{prefix}_32.png")

def main():
    app = IconMaker()
    app.mainloop()

if __name__ == "__main__":
    main()
