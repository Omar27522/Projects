import tkinter as tk
from tkinter import messagebox
import os
from PIL import Image, ImageTk

class PreviewWindow:
    """Manages label preview functionality"""
    def __init__(self, parent, barcode_generator):
        self.parent = parent
        self.barcode_generator = barcode_generator
        self.preview_window = None

    def show(self, label_data):
        """Show label preview window"""
        if self.preview_window is not None and self.preview_window.winfo_exists():
            self.preview_window.destroy()

        self.preview_window = tk.Toplevel(self.parent)
        self.preview_window.title("Label Preview")
        self.preview_window.geometry("400x300")
        self.preview_window.resizable(False, False)
        self.preview_window.transient(self.parent)

        try:
            # Generate preview image
            preview_image = self.barcode_generator.generate_label(label_data)
            
            # Convert PIL image to PhotoImage
            photo = ImageTk.PhotoImage(preview_image)
            
            # Create and pack label with image
            label = tk.Label(self.preview_window, image=photo)
            label.image = photo  # Keep a reference
            label.pack(expand=True, fill=tk.BOTH)
            
            # Add save button
            save_button = tk.Button(self.preview_window, text="Save",
                                  command=lambda: self.save_label(label_data))
            save_button.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Preview Error", f"Failed to generate preview: {str(e)}")
            self.preview_window.destroy()

    def save_label(self, label_data):
        """Save the label to a file"""
        try:
            # Generate the label
            label_image = self.barcode_generator.generate_label(label_data)
            
            # Create filename from UPC
            filename = f"{label_data.upc_code}.png"
            filepath = os.path.join(self.barcode_generator.settings.last_directory, filename)
            
            # Save the image
            label_image.save(filepath)
            
            # Close preview window
            self.preview_window.destroy()
            
            # Show success message
            messagebox.showinfo("Success", f"Label saved as {filename}")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save label: {str(e)}")
