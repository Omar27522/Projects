import tkinter as tk
from tkinter import messagebox, filedialog, Toplevel, IntVar
from PIL import Image, ImageDraw, ImageFont, ImageTk
import barcode
from barcode.writer import ImageWriter
import os

# Initialize the main application window to create a root context
app = tk.Tk()
app.withdraw()  # Hide the main window immediately

# Default DPI and Label dimensions
DPI = 300
LABEL_WIDTH = 2 * DPI  # 600 pixels for 2 inches at 300 DPI
LABEL_HEIGHT = 2 * DPI  # 600 pixels for 2 inches at 300 DPI

# Default font sizes for text
FONT_SIZE_LARGE = 45  # Default font size for Name Line 1 and Name Line 2
FONT_SIZE_MEDIUM = 45  # Default font size for Variant
BARCODE_WIDTH = LABEL_WIDTH  # Default width for barcode
BARCODE_HEIGHT = 310  # Default height for barcode

# Font size and barcode size variables for adjustable settings
font_size_large = IntVar(app, value=FONT_SIZE_LARGE)
font_size_medium = IntVar(app, value=FONT_SIZE_MEDIUM)
barcode_width = IntVar(app, value=BARCODE_WIDTH)
barcode_height = IntVar(app, value=BARCODE_HEIGHT)

output_directory = None  # To hold the chosen output directory path

def generate_barcode_image(upc_code):
    """Generate a barcode image with python-barcode, adjusting quiet zone and text distance to avoid overlap."""
    upca = barcode.get('upca', upc_code, writer=ImageWriter())
    barcode_img_path = f"{upc_code}_barcode.png"
    options = {
        'module_height': 15.0,
        'module_width': 0.4,
        'quiet_zone': 8.0,  # Increase quiet zone for better spacing
        'font_size': 10,    # Set font size for barcode text
        'text_distance': 5, # Increase text distance from the barcode
    }
    upca.save(barcode_img_path.replace(".png", ""), options)
    return barcode_img_path

def generate_label_image(name_line1, name_line2, variant, upc_code):
    """Generate the label image with the provided inputs."""
    label_img = Image.new("RGB", (LABEL_WIDTH, LABEL_HEIGHT), "white")
    draw = ImageDraw.Draw(label_img)

    try:
        large_font = ImageFont.truetype("arialbd.ttf", font_size_large.get())
        medium_font = ImageFont.truetype("arial.ttf", font_size_medium.get())
    except IOError:
        large_font = ImageFont.load_default()
        medium_font = ImageFont.load_default()

    # Draw Name Line 1 and Name Line 2
    draw.text((20, 20), name_line1, fill="black", font=large_font)
    if name_line2:
        name1_height = draw.textbbox((0, 0), name_line1, font=large_font)[3]
        draw.text((20, 20 + name1_height), name_line2, fill="black", font=large_font)

    # Draw Variant
    variant_x = (LABEL_WIDTH - draw.textlength(variant, font=medium_font)) // 2
    draw.text((variant_x, 210), variant, fill="black", font=medium_font)

    # Draw Barcode
    barcode_img_path = generate_barcode_image(upc_code)
    barcode_img = Image.open(barcode_img_path)
    barcode_img = barcode_img.resize((barcode_width.get(), barcode_height.get()), Image.LANCZOS)
    barcode_y = 310  # Set the y-position of the barcode
    label_img.paste(barcode_img, ((LABEL_WIDTH - barcode_width.get()) // 2, barcode_y))
    
    os.remove(barcode_img_path)

    return label_img

def preview_label(inputs):
    """Generate and display a preview of the label."""
    name_line1 = inputs["name_line1"].get()
    name_line2 = inputs["name_line2"].get()
    variant = inputs["variant"].get()
    upc_code = inputs["upc_code"].get()

    if not all([name_line1, variant, upc_code]) or len(upc_code) != 12 or not upc_code.isdigit():
        messagebox.showerror("Error", "Please fill out all required fields with a 12-digit UPC code.")
        return

    label_img = generate_label_image(name_line1, name_line2, variant, upc_code)
    if label_img:
        preview_window = Toplevel()
        preview_window.title("Label Preview")
        
        # Resize with LANCZOS for high-quality downscaling
        display_img = label_img.resize((LABEL_WIDTH // 2, LABEL_HEIGHT // 2), Image.LANCZOS)
        
        img_tk = ImageTk.PhotoImage(display_img)
        label = tk.Label(preview_window, image=img_tk)
        label.image = img_tk
        label.pack()

        # Create a frame for buttons
        button_frame = tk.Frame(preview_window)
        button_frame.pack(pady=10)

        def print_label():
            try:
                # Create a temporary file
                temp_file = os.path.join(os.environ.get('TEMP', os.getcwd()), f"temp_label_{upc_code}.png")
                label_img.save(temp_file, dpi=(DPI, DPI))
                
                # Open the file with the default image viewer/printer
                os.startfile(temp_file, "print")
                
                # Schedule the temporary file for deletion after a delay
                preview_window.after(5000, lambda: os.remove(temp_file) if os.path.exists(temp_file) else None)
                
                messagebox.showinfo("Print", "Label sent to printer")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to print: {str(e)}")

        # Add Print button
        tk.Button(button_frame, text="Print Label", command=print_label).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close Preview", command=preview_window.destroy).pack(side=tk.LEFT, padx=5)

def generate_and_save_fixed_label(inputs):
    """Generate and save the final label image."""
    global output_directory
    name_line1 = inputs["name_line1"].get()
    name_line2 = inputs["name_line2"].get()
    variant = inputs["variant"].get()
    upc_code = inputs["upc_code"].get()

    if not all([name_line1, variant, upc_code]) or len(upc_code) != 12 or not upc_code.isdigit():
        messagebox.showerror("Error", "Please fill out all required fields with a 12-digit UPC code.")
        return

    if not output_directory:
        messagebox.showerror("Error", "Please select an output directory.")
        return

    label_img = generate_label_image(name_line1, name_line2, variant, upc_code)
    if label_img:
        file_name = f"{name_line1}_{variant}_label_{upc_code}.png"
        final_image_path = os.path.join(output_directory, file_name)
        try:
            # Save with DPI specified explicitly
            label_img.save(final_image_path, dpi=(DPI, DPI))
            messagebox.showinfo("Success", f"Label image saved as {final_image_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save label image: {e}")

def select_output_directory():
    """Allow the user to select an output directory."""
    global output_directory
    output_directory = filedialog.askdirectory(title="Choose Output Directory")
    if output_directory:
        messagebox.showinfo("Output Directory", f"Selected: {output_directory}")

def view_directory_files():
    """Display files from the output directory in a new window."""
    if not output_directory:
        messagebox.showerror("Error", "Please select an output directory first.")
        return

    # Create a new window
    file_window = Toplevel()
    file_window.title("Output Directory Files")
    file_window.geometry("600x400")

    # Create a frame for the search bar
    search_frame = tk.Frame(file_window)
    search_frame.pack(fill=tk.X, padx=5, pady=5)

    # Add search label and entry
    tk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var)
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    # Create a frame for the listbox and scrollbar
    list_frame = tk.Frame(file_window)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Add listbox with scrollbar
    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    listbox = tk.Listbox(list_frame)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Connect scrollbar to listbox
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    def update_file_list(*args):
        """Update the listbox based on search text"""
        search_text = search_var.get().lower()
        listbox.delete(0, tk.END)
        try:
            files = os.listdir(output_directory)
            for file in sorted(files):
                if search_text in file.lower():
                    listbox.insert(tk.END, file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read directory: {str(e)}")

    # Bind search entry to update function
    search_var.trace('w', update_file_list)

    def open_selected_file():
        """Open the selected file"""
        selection = listbox.curselection()
        if selection:
            file_name = listbox.get(selection[0])
            file_path = os.path.join(output_directory, file_name)
            try:
                os.startfile(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")

    # Add buttons frame
    button_frame = tk.Frame(file_window)
    button_frame.pack(fill=tk.X, padx=5, pady=5)

    # Add buttons
    tk.Button(button_frame, text="Open Selected", command=open_selected_file).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Close", command=file_window.destroy).pack(side=tk.RIGHT, padx=5)

    # Initial file list population
    update_file_list()

def clear_inputs(inputs):
    """Clear all input fields."""
    for key in inputs:
        inputs[key].delete(0, tk.END)

def open_input_window():
    """Main input window with settings, preview, and output options."""
    input_window = Toplevel(app)  # Use Toplevel for the main input window
    input_window.title("Enter Label Details")

    # Add stay on top state variable
    stay_on_top = tk.BooleanVar(value=False)

    def toggle_stay_on_top():
        """Toggle the window's stay-on-top state"""
        current_state = stay_on_top.get()
        input_window.attributes('-topmost', current_state)
        stay_on_top_btn.config(text="Always On Top ✓" if current_state else "Always On Top")

    # Add stay on top button at the top of the window
    stay_on_top_btn = tk.Button(input_window, text="Always On Top", command=lambda: [stay_on_top.set(not stay_on_top.get()), toggle_stay_on_top()])
    stay_on_top_btn.grid(row=0, column=0, columnspan=2, pady=5)

    inputs = {}
    labels = [
        ("Product Name Line 1", "name_line1"),
        ("Product Name Line 2 (optional)", "name_line2"),
        ("Variant", "variant"),
        ("UPC Code (12 digits)", "upc_code")
    ]

    for idx, (label_text, key) in enumerate(labels):
        tk.Label(input_window, text=label_text).grid(row=idx+1, column=0, padx=10, pady=5)  # Shifted down by 1 row
        entry = tk.Entry(input_window)
        
        # Add validation to the UPC Code entry to accept only numeric inputs and restrict to 12 characters
        if key == "upc_code":
            entry.config(validate="key")
            entry.bind("<KeyRelease>", lambda e: entry.delete(12, tk.END) if len(entry.get()) > 12 else None)
        
        entry.grid(row=idx+1, column=1, padx=10, pady=5)  # Shifted down by 1 row
        inputs[key] = entry

    def toggle_settings():
        """Toggle the visibility of the settings frame and adjust button positions."""
        if settings_frame.winfo_ismapped():
            settings_frame.grid_remove()
        else:
            settings_frame.grid(row=len(labels) + 3, column=0, columnspan=2, pady=10)
        # Adjust position of the buttons based on settings visibility
        generate_button.grid(row=len(labels) + (4 if settings_frame.winfo_ismapped() else 2), column=1, pady=10)
        settings_button.grid(row=len(labels) + (4 if settings_frame.winfo_ismapped() else 2), column=0, pady=10)

    # Settings Frame
    settings_frame = tk.Frame(input_window)
    tk.Label(settings_frame, text="Font Size for Name Lines:").grid(row=0, column=0, padx=10, pady=5)
    tk.Entry(settings_frame, textvariable=font_size_large).grid(row=0, column=1, padx=10, pady=5)
    tk.Label(settings_frame, text="Font Size for Variant:").grid(row=1, column=0, padx=10, pady=5)
    tk.Entry(settings_frame, textvariable=font_size_medium).grid(row=1, column=1, padx=10, pady=5)
    tk.Label(settings_frame, text="Barcode Width:").grid(row=2, column=0, padx=10, pady=5)
    tk.Entry(settings_frame, textvariable=barcode_width).grid(row=2, column=1, padx=10, pady=5)
    tk.Label(settings_frame, text="Barcode Height:").grid(row=3, column=0, padx=10, pady=5)
    tk.Entry(settings_frame, textvariable=barcode_height).grid(row=3, column=1, padx=10, pady=5)
    settings_frame.grid_remove()  # Hide initially

    # Buttons
    tk.Button(input_window, text="Preview", command=lambda: preview_label(inputs)).grid(row=len(labels)+1, column=0, pady=10)
    tk.Button(input_window, text="Select Output Directory", command=select_output_directory).grid(row=len(labels)+1, column=1, pady=10)
    tk.Button(input_window, text="View Files", command=view_directory_files).grid(row=len(labels)+2, column=0, pady=10)  # Add View Files button
    settings_button = tk.Button(input_window, text="Settings", command=toggle_settings)
    settings_button.grid(row=len(labels)+2, column=1, pady=10)
    generate_button = tk.Button(input_window, text="Generate Label", command=lambda: generate_and_save_fixed_label(inputs))
    generate_button.grid(row=len(labels)+3, column=1, pady=10)
    tk.Button(input_window, text="Reset", command=lambda: clear_inputs(inputs)).grid(row=len(labels)+4, column=0, columnspan=2, pady=10)

# Directly call the input window at startup
open_input_window()
app.mainloop()
