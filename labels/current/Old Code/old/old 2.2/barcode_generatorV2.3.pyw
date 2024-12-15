import tkinter as tk
from tkinter import messagebox, filedialog, Toplevel, IntVar
from PIL import Image, ImageDraw, ImageFont, ImageTk
import barcode
from barcode.writer import ImageWriter
import os
import json
import pyautogui
import requests
import base64
from datetime import datetime
import configparser
import urllib.parse
import tkinter.ttk as ttk

# Initialize the main application window to create a root context
app = tk.Tk()
app.withdraw()  # Hide the main window immediately

# Configure default font size (15% bigger)
default_font = ('TkDefaultFont', 11)  # Default system font, 15% bigger
button_font = ('TkDefaultFont', 11, 'normal')
entry_font = ('TkDefaultFont', 11)
label_font = ('TkDefaultFont', 11)
view_files_font = ('TkDefaultFont', 12, 'bold')  # Bigger and bold font for view files button

# Configure fonts for all widgets
app.option_add('*Font', default_font)
app.option_add('*Button*Font', button_font)
app.option_add('*Entry*Font', entry_font)
app.option_add('*Label*Font', label_font)

# Path for storing settings
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'label_maker_settings.json')

# Load settings
def load_settings():
    global output_directory
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                font_size_large.set(settings.get('font_size_large', 45))
                font_size_medium.set(settings.get('font_size_medium', 45))
                barcode_width.set(settings.get('barcode_width', 600))
                barcode_height.set(settings.get('barcode_height', 310))
                always_on_top.set(settings.get('always_on_top', False))
                transparency_level.set(settings.get('transparency_level', 0.9))
                output_directory = settings.get('last_directory', None)
                if output_directory and not os.path.exists(output_directory):
                    output_directory = None
    except:
        output_directory = None

# Save settings
def save_settings():
    try:
        settings = {
            'font_size_large': font_size_large.get(),
            'font_size_medium': font_size_medium.get(),
            'barcode_width': barcode_width.get(),
            'barcode_height': barcode_height.get(),
            'always_on_top': always_on_top.get(),
            'transparency_level': transparency_level.get(),
            'last_directory': output_directory if output_directory else ""
        }
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)
    except:
        pass

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

# Initialize variables at the start of the file, after other global variables
transparency_level = tk.DoubleVar(value=0.9)  # Default to 90% opacity

output_directory = None  # To hold the chosen output directory path

# Add global always on top state variable
always_on_top = tk.BooleanVar(app, value=False)

# Add global window trackers at the top level
preview_window = None
file_window = None
settings_window = None

def set_window_on_top(window):
    """Set window always-on-top state and apply transparency if needed."""
    current_state = always_on_top.get()
    window.attributes('-topmost', current_state)
    # Only apply transparency if it's a global command (from main window)
    if current_state:
        window.attributes('-alpha', transparency_level.get())
        window.lift()
    else:
        window.attributes('-alpha', 1.0)  # Reset transparency when not on top
    
    # Update the view files window button if it exists
    if file_window and file_window.winfo_exists():
        for widget in file_window.winfo_children():
            if isinstance(widget, tk.Frame):
                for btn in widget.winfo_children():
                    if isinstance(btn, tk.Button) and "Always On Top" in str(btn.cget('text')):
                        btn.config(
                            text="Always On Top ",
                            bg='#90EE90' if current_state else '#C71585',
                            relief='sunken' if current_state else 'raised'
                        )
                        # Update the window's local always-on-top variable
                        for var in file_window.children.values():
                            if isinstance(var, tk.BooleanVar) and 'window_always_on_top' in str(var):
                                var.set(current_state)
                                break

def make_draggable(widget):
    """Make a widget contribute to window dragging."""
    widget.bind('<Button-1>', start_drag)
    widget.bind('<B1-Motion>', drag)
    # Recursively apply to all children
    for child in widget.winfo_children():
        make_draggable(child)

def disable_dragging(widget):
    """Remove dragging bindings from a widget."""
    widget.unbind('<Button-1>')
    widget.unbind('<B1-Motion>')
    # Recursively remove from all children
    for child in widget.winfo_children():
        disable_dragging(child)

def start_drag(event):
    """Remember the starting position for the drag."""
    widget = event.widget
    while not isinstance(widget, Toplevel):
        widget = widget.master
    widget._drag_start_x = event.x_root
    widget._drag_start_y = event.y_root
    widget._window_start_x = widget.winfo_x()
    widget._window_start_y = widget.winfo_y()

def drag(event):
    """Handle the dragging motion."""
    widget = event.widget
    while not isinstance(widget, Toplevel):
        widget = widget.master
    
    # Calculate the distance moved
    dx = event.x_root - widget._drag_start_x
    dy = event.y_root - widget._drag_start_y
    
    # Move the window
    new_x = widget._window_start_x + dx
    new_y = widget._window_start_y + dy
    widget.geometry(f"+{new_x}+{new_y}")

def toggle_always_on_top():
    """Toggle the global always-on-top state"""
    current_state = not always_on_top.get()  # Get the opposite of current state
    always_on_top.set(current_state)  # Set the new state
    
    # Update all existing Toplevel windows
    for window in app.winfo_children():
        if isinstance(window, Toplevel):
            window.attributes('-topmost', current_state)
            if current_state:
                window.attributes('-alpha', transparency_level.get())
                window.lift()
            else:
                window.attributes('-alpha', 1.0)  # Reset transparency when not on top
    
    # Save settings after toggle
    save_settings()

def focus_window(window):
    """Focus and lift an existing window"""
    if window and window.winfo_exists():
        window.deiconify()  # Restore the window if minimized
        window.focus_force()
        window.lift()
        set_window_on_top(window)
        return True
    return False

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

    # Draw Name Line 1 if provided
    if name_line1:
        draw.text((20, 20), name_line1, fill="black", font=large_font)
        
    # Draw Name Line 2 if provided
    if name_line2:
        name1_height = draw.textbbox((0, 0), name_line1 if name_line1 else "", font=large_font)[3]
        draw.text((20, 20 + name1_height), name_line2, fill="black", font=large_font)

    # Draw Variant if provided
    if variant:
        variant_x = (LABEL_WIDTH - draw.textlength(variant, font=medium_font)) // 2
        draw.text((variant_x, 210), variant, fill="black", font=medium_font)

    # Draw Barcode only if UPC code is provided and valid
    if upc_code and len(upc_code) == 12 and upc_code.isdigit():
        barcode_img_path = generate_barcode_image(upc_code)
        barcode_img = Image.open(barcode_img_path)
        barcode_img = barcode_img.resize((barcode_width.get(), barcode_height.get()), Image.LANCZOS)
        barcode_y = 310  # Set the y-position of the barcode
        label_img.paste(barcode_img, ((LABEL_WIDTH - barcode_width.get()) // 2, barcode_y))
        os.remove(barcode_img_path)

    return label_img

def preview_label(inputs):
    """Generate and display a preview of the label."""
    global preview_window
    
    # If preview window exists and is valid, just focus it
    if preview_window and preview_window.winfo_exists():
        focus_window(preview_window)
        return
    
    name_line1 = inputs["name_line1"].get()
    name_line2 = inputs["name_line2"].get()
    variant = inputs["variant"].get()
    upc_code = inputs["upc_code"].get()

    if not upc_code or len(upc_code) != 12:
        show_error_message("Error", "Please enter a valid 12-digit UPC code.")
        return

    label_img = generate_label_image(name_line1, name_line2, variant, upc_code)
    if label_img:
        preview_window = Toplevel(app)
        preview_window.title("Label Preview")
        preview_window.is_preview_window = True  # Mark this as a preview window
        preview_window.protocol("WM_DELETE_WINDOW", lambda: close_preview_window())
        preview_window.resizable(False, False)  # Make window non-resizable
        
        # Apply always-on-top setting to new window
        set_window_on_top(preview_window)
        
        def close_preview_window():
            global preview_window
            if preview_window:
                preview_window.destroy()
                preview_window = None
        
        # Resize with LANCZOS for high-quality downscaling
        display_img = label_img.resize((LABEL_WIDTH // 2, LABEL_HEIGHT // 2), Image.LANCZOS)
        
        # Convert to PhotoImage for display
        photo = ImageTk.PhotoImage(display_img)
        
        # Create label to display image
        img_label = tk.Label(preview_window, image=photo)
        img_label.image = photo  # Keep a reference
        img_label.pack(padx=5, pady=5)

        # Create button frame
        button_frame = tk.Frame(preview_window)
        button_frame.pack(pady=5)

        # Add Generate Label button with styling
        generate_btn = tk.Button(button_frame, 
            text="Generate Label",
            command=lambda: generate_and_save_fixed_label(inputs),
            bg='#e3f2fd',   # Light blue background
            activebackground='#bbdefb',  # Slightly darker when clicked
            font=('TkDefaultFont', 9, 'bold'),
            relief='raised'
        )
        generate_btn.pack(side=tk.LEFT, padx=3)

        # Add hover effect for Generate Label button
        def on_generate_enter(e):
            generate_btn['bg'] = '#bbdefb'  # Slightly darker blue on hover
            
        def on_generate_leave(e):
            generate_btn['bg'] = '#e3f2fd'  # Return to original light blue
            
        generate_btn.bind("<Enter>", on_generate_enter)
        generate_btn.bind("<Leave>", on_generate_leave)

        def print_label():
            try:
                # Create a temporary file
                temp_file = os.path.join(os.environ.get('TEMP', os.getcwd()), f"temp_label_{upc_code}.png")
                label_img.save(temp_file, dpi=(DPI, DPI))
                
                # Open the file with the default image viewer/printer
                os.startfile(temp_file, "print")
                
                # Wait a moment for the print dialog to appear and press Enter
                preview_window.after(1000, lambda: pyautogui.press('enter'))
                
                # Schedule the temporary file for deletion after a delay
                preview_window.after(5000, lambda: os.remove(temp_file) if os.path.exists(temp_file) else None)
                
                # Close the preview window
                preview_window.destroy()
            except Exception as e:
                show_error_message("Error", f"Failed to print: {str(e)}")

        # Add Print Label button
        print_btn = tk.Button(button_frame, text="Print Label", 
                            command=print_label,
                            bg='#e8f5e9',  # Light green background
                            activebackground='#c8e6c9',  # Slightly darker when clicked
                            font=('TkDefaultFont', 9, 'bold'),
                            relief='raised')
        print_btn.pack(side=tk.LEFT, padx=3)

        # Add hover effect for Print Label button
        def on_print_enter(e):
            print_btn['bg'] = '#c8e6c9'  # Slightly darker green on hover
            
        def on_print_leave(e):
            print_btn['bg'] = '#e8f5e9'  # Return to original light green
            
        print_btn.bind("<Enter>", on_print_enter)
        print_btn.bind("<Leave>", on_print_leave)

        # Add Close button
        tk.Button(button_frame, text="Close", 
                 command=close_preview_window).pack(side=tk.LEFT, padx=3)

def generate_and_save_fixed_label(inputs):
    """Generate and save the final label image."""
    name_line1 = inputs["name_line1"].get().strip()
    name_line2 = inputs["name_line2"].get().strip()
    variant = inputs["variant"].get().strip()
    upc_code = inputs["upc_code"].get().strip()

    if not all([name_line1, variant, upc_code]):
        show_error_message("Error", "Please fill in all required fields.")
        return

    if not output_directory:
        show_error_message("Error", "Please select an output directory first.")
        return

    if len(upc_code) != 12 or not upc_code.isdigit():
        show_error_message("Error", "UPC Code must be exactly 12 digits.")
        return

    try:
        # Generate label image
        label_image = generate_label_image(name_line1, name_line2, variant, upc_code)
        
        # Save the image
        filename = f"{upc_code}_{name_line1}_{variant}.png"
        filepath = os.path.join(output_directory, filename)
        label_image.save(filepath)
        show_error_message("Success", f"Label saved as {filename}")
        
        # Ask if user wants to upload to GitHub
        if messagebox.askyesno("Upload to GitHub", "Would you like to upload this label to GitHub?"):
            upload_to_github(filepath)
    except Exception as e:
        show_error_message("Error", f"Failed to generate label: {str(e)}")

def clear_inputs(inputs):
    """Clear all input fields."""
    for key in inputs:
        inputs[key].delete(0, tk.END)

def open_input_window():
    """Main input window with settings, preview, and output options."""
    input_window = Toplevel(app)  # Use Toplevel for the main input window
    input_window.title("Enter Label Details")
    
    # Prevent window resizing
    input_window.resizable(False, False)
    
    # Create main frame with minimal padding
    main_frame = tk.Frame(input_window, padx=5, pady=3)  # Minimal padding
    main_frame.pack(expand=True, fill=tk.BOTH)

    # Create top control frame with minimal spacing
    top_control_frame = tk.Frame(main_frame)
    top_control_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=2)  # Minimal vertical spacing

    # Add always on top button at the top of the window with minimal padding
    global always_on_top_btn
    always_on_top_btn = tk.Button(top_control_frame, 
        text="Always On Top",
        bg='SystemButtonFace',
        relief='raised',
        command=toggle_always_on_top
    )
    always_on_top_btn.pack(side=tk.LEFT, padx=3)  # Minimal horizontal spacing

    # Update button state based on current always-on-top setting
    def update_button_state(*args):
        current_state = always_on_top.get()
        always_on_top_btn.config(
            bg='#90EE90' if current_state else 'SystemButtonFace',
            relief='sunken' if current_state else 'raised'
        )
        input_window.attributes('-topmost', current_state)
        if current_state:
            input_window.lift()
    
    # Bind the button state to the variable
    always_on_top.trace_add('write', update_button_state)
    
    # Initial button state update
    update_button_state()

    # Apply current always-on-top state
    set_window_on_top(input_window)

    # Create right-click context menu
    def create_context_menu(widget):
        menu = tk.Menu(widget, tearoff=0)
        menu.add_command(label="Copy", command=lambda: widget.event_generate('<<Copy>>'))
        menu.add_command(label="Paste", command=lambda: widget.event_generate('<<Paste>>'))
        menu.add_command(label="Cut", command=lambda: widget.event_generate('<<Cut>>'))
        menu.add_separator()
        menu.add_command(label="Select All", command=lambda: widget.select_range(0, tk.END))
        return menu

    def show_context_menu(event, widget):
        menu = create_context_menu(widget)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    # Control buttons frame (Settings and Reset)
    control_frame = tk.Frame(main_frame)
    control_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

    settings_button = tk.Button(control_frame, text="Settings", width=8, command=lambda: toggle_settings())
    settings_button.pack(side=tk.LEFT, padx=5)

    reset_button = tk.Button(control_frame, text="Reset", width=8, command=lambda: clear_inputs(inputs))
    reset_button.pack(side=tk.RIGHT, padx=5)

    inputs = {}
    labels = [
        ("Product Name Line 1", "name_line1"),
        ("Line 2 (optional)", "name_line2"),
        ("Variant", "variant"),
        ("UPC Code (12 digits)", "upc_code")
    ]

    for idx, (label_text, key) in enumerate(labels):
        tk.Label(main_frame, text=label_text, anchor="e", width=20).grid(row=idx+2, column=0, padx=5, pady=3, sticky="e")
        entry = tk.Entry(main_frame, width=15)
        
        # Add validation to the UPC Code entry to accept only numeric inputs and restrict to 12 characters
        if key == "upc_code":
            entry.config(validate="key")
            entry.bind("<KeyRelease>", lambda e: entry.delete(12, tk.END) if len(entry.get()) > 12 else None)
        
        # Bind right-click event to show context menu
        entry.bind("<Button-3>", lambda event, widget=entry: show_context_menu(event, widget))
        
        entry.grid(row=idx+2, column=1, padx=5, pady=3, sticky="w")
        inputs[key] = entry

    def toggle_settings():
        """Toggle the visibility of the settings frame and adjust button positions."""
        global settings_window
        
        if settings_frame.winfo_ismapped():
            settings_frame.grid_remove()
        else:
            settings_frame.grid(row=len(labels)+5, column=0, columnspan=2, pady=10)
            # Ensure the main window is focused and visible
            focus_window(input_window)

    # Settings Frame - adjust its position
    settings_frame = tk.Frame(main_frame)
    
    # Create button frame for download and load buttons
    button_frame = tk.Frame(settings_frame)
    button_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")
    
    # Add download button
    download_btn = tk.Button(
        button_frame,
        text="⬇️ Download Labels",
        command=download_all_labels,
        bg='#4CAF50',  # Green
        fg='white',
        font=('TkDefaultFont', 10, 'bold'),
        width=15
    )
    download_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
    
    # Add load local button
    load_btn = tk.Button(
        button_frame,
        text="📂 Local Labels",
        command=view_local_labels,
        bg='#2196F3',  # Blue
        fg='white',
        font=('TkDefaultFont', 10, 'bold'),
        width=15
    )
    load_btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
    
    # Add hover effects
    def on_button_enter(e):
        if e.widget == download_btn:
            e.widget['bg'] = '#45a049'  # Darker green
        else:  # load_btn
            e.widget['bg'] = '#1976D2'  # Darker blue
        
    def on_button_leave(e):
        if e.widget == download_btn:
            e.widget['bg'] = '#4CAF50'  # Original green
        else:  # load_btn
            e.widget['bg'] = '#2196F3'  # Original blue
        
    download_btn.bind('<Enter>', on_button_enter)
    download_btn.bind('<Leave>', on_button_leave)
    load_btn.bind('<Enter>', on_button_enter)
    load_btn.bind('<Leave>', on_button_leave)
    
    # Add transparency control
    tk.Label(settings_frame, text="Transparency when on top:").grid(row=1, column=0, padx=5, pady=2)
    transparency_scale = tk.Scale(settings_frame, from_=0.3, to=1.0, resolution=0.1,
                                orient=tk.HORIZONTAL, variable=transparency_level,
                                command=lambda x: [set_window_on_top(window) for window in app.winfo_children() if isinstance(window, Toplevel)])
    transparency_scale.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
    
    tk.Label(settings_frame, text="Font Size for Name Lines:").grid(row=2, column=0, padx=5, pady=2)
    tk.Entry(settings_frame, textvariable=font_size_large).grid(row=2, column=1, padx=5, pady=2)
    tk.Label(settings_frame, text="Font Size for Variant:").grid(row=3, column=0, padx=5, pady=2)
    tk.Entry(settings_frame, textvariable=font_size_medium).grid(row=3, column=1, padx=5, pady=2)
    tk.Label(settings_frame, text="Barcode Width:").grid(row=4, column=0, padx=5, pady=2)
    tk.Entry(settings_frame, textvariable=barcode_width).grid(row=4, column=1, padx=5, pady=2)
    tk.Label(settings_frame, text="Barcode Height:").grid(row=5, column=0, padx=5, pady=2)
    tk.Entry(settings_frame, textvariable=barcode_height).grid(row=5, column=1, padx=5, pady=2)
    settings_frame.grid_remove()  # Hide initially

    # Buttons Frame with minimal spacing
    buttons_frame = tk.Frame(main_frame)
    buttons_frame.grid(row=len(labels)+7, column=0, columnspan=2, pady=5, sticky='ew')
    buttons_frame.grid_columnconfigure(1, weight=1)  # Add space between left and right buttons

    # Left side - View GitHub button
    left_frame = tk.Frame(buttons_frame)
    left_frame.pack(side=tk.LEFT, padx=2)
    
    # Create a larger, more prominent view files button
    global view_files_btn
    view_files_btn = tk.Button(
        left_frame,
        text="📁\nLabels: ...",  # Initial text while counting
        bg='#4a90e2',  # Blue
        command=view_directory_files,
        font=('TkDefaultFont', 12, 'bold'),
        fg='white',
        width=14,  # Make it wider
        height=2,
        relief='raised'
    )
    view_files_btn.pack(side=tk.LEFT, padx=2)
    
    # Update label count after button creation
    input_window.after(100, update_view_button_text)
    
    # Right side - Preview and Save buttons
    right_frame = tk.Frame(buttons_frame)
    right_frame.pack(side=tk.RIGHT, padx=2)

    # Style the preview button with green
    preview_btn = tk.Button(
        right_frame,
        text="🔍\nPreview",
        bg='#2ecc71',  # Green
        font=('TkDefaultFont', 12, 'bold'),
        fg='white',
        width=6,
        height=2,
        relief='raised'
    )
    preview_btn.pack(side=tk.LEFT, padx=2)

    # Style the generate button with purple
    generate_button = tk.Button(
        right_frame,
        text="💾\nSave",
        bg='#9b59b6',  # Purple
        command=lambda: generate_and_save_fixed_label(inputs),
        font=('TkDefaultFont', 12, 'bold'),
        fg='white',
        width=6,
        height=2,
    )
    generate_button.pack(side=tk.LEFT, padx=2)

    # Create tooltip class
    class ToolTip(object):
        def __init__(self, widget, text):
            self.widget = widget
            self.text = text
            self.tooltip = None
            self.id = None

        def show_tooltip(self):
            x, y, _, _ = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 25

            # Create tooltip window
            self.tooltip = tk.Toplevel()
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")

            label = tk.Label(self.tooltip, text=self.text, justify='left',
                           background="#ffffe0", relief='solid', borderwidth=1,
                           font=("TkDefaultFont", "10", "normal"))
            label.pack()

        def enter(self, event=None):
            self.id = self.widget.after(1500, self.show_tooltip)

        def leave(self, event=None):
            if self.id:
                self.widget.after_cancel(self.id)
                self.id = None
            if self.tooltip:
                self.tooltip.destroy()
                self.tooltip = None

    # Add tooltips to buttons
    preview_btn._tooltip = ToolTip(preview_btn, "Preview your label before saving\n• Check layout\n• Verify barcode\n• Print directly")
    generate_button._tooltip = ToolTip(generate_button, "Save your label\n• Generate barcode\n• Save as PNG\n• Auto-named with UPC")

    # Add hover effects
    def on_enter(e):
        if e.widget == preview_btn:
            e.widget['bg'] = '#27ae60'  # Darker green
        else:  # generate button
            e.widget['bg'] = '#8e44ad'  # Darker purple

    def on_leave(e):
        if e.widget == preview_btn:
            e.widget['bg'] = '#2ecc71'  # Original green
        else:  # generate button
            e.widget['bg'] = '#9b59b6'  # Original purple

    def on_preview_press(e):
        preview_btn['bg'] = '#219a51'  # Even darker green when pressed

    def on_preview_release(e):
        preview_btn['bg'] = '#27ae60'  # Back to hover green
        preview_label(inputs)  # Call preview function

    # Bind events for all buttons
    for btn in (preview_btn, generate_button):
        btn.bind('<Enter>', lambda e: [on_enter(e), e.widget._tooltip.enter()])
        btn.bind('<Leave>', lambda e: [on_leave(e), e.widget._tooltip.leave()])

    # Add press/release effects for preview button
    preview_btn.bind('<Button-1>', on_preview_press)
    preview_btn.bind('<ButtonRelease-1>', on_preview_release)
    preview_btn.configure(command='')  # Remove command since we're using bind

    # If always on top is already enabled, make the window draggable immediately
    if always_on_top.get():
        make_draggable(main_frame)

    # After all widgets are added, update window size
    input_window.update_idletasks()  # Make sure all widgets are rendered
    input_window.geometry('')  # Reset any previous geometry
    
    # Center the window on screen
    window_width = input_window.winfo_width()
    window_height = input_window.winfo_height()
    screen_width = input_window.winfo_screenwidth()
    screen_height = input_window.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    input_window.geometry(f"+{x}+{y}")

def get_label_count():
    """Get the number of labels from GitHub repository"""
    try:
        files = get_github_files()
        return len(files)
    except:
        return 0

def update_view_button_text():
    """Update the view button text with current label count"""
    if view_files_btn and view_files_btn.winfo_exists():
        count = get_label_count()
        view_files_btn.config(text=f"📁\nLabels: {count}")

# GitHub configuration
config = configparser.ConfigParser()
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'github_config.ini')

# Load GitHub configuration from file, create it if it doesn't exist
def load_github_config():
    """Load GitHub configuration from file, create it if it doesn't exist"""
    default_config = {
        'owner': 'Omar27522',
        'repo': 'Projects',
        'token': '',
        'labels_path': 'labels/files'
    }
    
    # Create config file if it doesn't exist
    if not os.path.exists(CONFIG_FILE):
        config['GitHub'] = default_config
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, 'w') as configfile:
                config.write(configfile)
        except Exception as e:
            print(f"Error creating config file: {str(e)}")
            return default_config
    
    # Load existing config
    try:
        config.read(CONFIG_FILE)
        return {
            'owner': config.get('GitHub', 'owner', fallback=default_config['owner']),
            'repo': config.get('GitHub', 'repo', fallback=default_config['repo']),
            'token': config.get('GitHub', 'token', fallback=default_config['token']),
            'labels_path': config.get('GitHub', 'labels_path', fallback=default_config['labels_path'])
        }
    except Exception as e:
        print(f"Error reading config file: {str(e)}")
        return default_config

# Get list of files from GitHub repository
def get_github_files():
    """Get list of files from GitHub repository"""
    github_config = load_github_config()
    headers = {'Authorization': f'token {github_config["token"]}'} if github_config['token'] else {}
    
    try:
        url = f'https://api.github.com/repos/{github_config["owner"]}/{github_config["repo"]}/contents/{github_config["labels_path"]}'
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            files = response.json()
            return [file['name'] for file in files if file['type'] == 'file' and file['name'].lower().endswith('.png')]
        return []
    except Exception as e:
        print(f"Error getting GitHub files: {str(e)}")
        return []

# Download a file from GitHub repository
def download_from_github(filename):
    """Download a file from GitHub repository"""
    github_config = load_github_config()
    headers = {'Authorization': f'token {github_config["token"]}'} if github_config['token'] else {}
    
    try:
        # URL encode the filename and path
        encoded_path = urllib.parse.quote(f'{github_config["labels_path"]}/{filename}')
        url = f'https://api.github.com/repos/{github_config["owner"]}/{github_config["repo"]}/contents/{encoded_path}'
        
        # Get file content
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()
            if content.get('content'):
                # Decode base64 content
                file_content = base64.b64decode(content['content'])
                
                # Create temp directory if it doesn't exist
                temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
                os.makedirs(temp_dir, exist_ok=True)
                
                # Save file to temp directory
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(file_content)
                return file_path
        return None
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        return None

def download_all_labels():
    """Download all labels from GitHub repository"""
    # Get the directory to save files
    save_dir = filedialog.askdirectory(title="Choose Directory to Save Labels")
    if not save_dir:
        return
        
    # Get list of files
    files = get_github_files()
    if not files:
        show_error_message("Error", "No labels found in GitHub repository.")
        return
        
    # Create progress window
    progress_window = Toplevel(app)
    progress_window.title("Downloading Labels")
    progress_window.geometry("300x150")
    progress_window.transient(app)
    progress_window.grab_set()
    
    # Center the progress window
    progress_window.geometry("+%d+%d" % (
        app.winfo_screenwidth()/2 - 150,
        app.winfo_screenheight()/2 - 75))
    
    # Add progress label
    progress_label = tk.Label(progress_window, text="Downloading labels...\n0 of 0")
    progress_label.pack(pady=20)
    
    # Add progress bar
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(
        progress_window, 
        variable=progress_var,
        maximum=len(files),
        length=200,
        mode='determinate'
    )
    progress_bar.pack(pady=10)
    
    # Download counter
    successful = 0
    
    # Update progress
    def update_progress(current, total, success):
        progress_label.config(text=f"Downloading labels...\n{success} of {total} completed")
        progress_var.set(current)
        progress_window.update()
    
    # Start downloading
    try:
        for i, filename in enumerate(files, 1):
            file_path = download_from_github(filename)
            if file_path:
                # Move file to selected directory
                new_path = os.path.join(save_dir, filename)
                try:
                    os.replace(file_path, new_path)
                    successful += 1
                except Exception as e:
                    print(f"Error saving {filename}: {str(e)}")
                    if os.path.exists(file_path):
                        os.remove(file_path)
            update_progress(i, len(files), successful)
            
        # Show completion message
        progress_label.config(text=f"Download complete!\n{successful} of {len(files)} labels saved")
        tk.Button(progress_window, text="OK", command=progress_window.destroy).pack(pady=10)
        
    except Exception as e:
        show_error_message("Error", f"Failed to download labels: {str(e)}")
        progress_window.destroy()

def view_directory_files():
    """Display files from GitHub repository in a new window."""
    global file_window
    
    # If file window exists and is valid, just focus it
    if file_window and file_window.winfo_exists():
        focus_window(file_window)
        return
    
    # Get files from GitHub
    files = get_github_files()
    if not files:
        show_error_message("Warning", "No files found in GitHub repository.")
        return
    
    file_window = Toplevel(app)
    file_window.title("View Files from GitHub")
    file_window.protocol("WM_DELETE_WINDOW", lambda: close_file_window())
    
    # Set minimum window size
    file_window.minsize(450, 200)
    
    def close_file_window():
        global file_window
        if file_window:
            file_window.destroy()
            file_window = None

    # Create main content frame
    main_content = tk.Frame(file_window)
    main_content.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    # Create search frame
    search_frame = tk.Frame(main_content)
    search_frame.pack(fill=tk.X, padx=0, pady=1)

    def create_magnifier_icon(size=16, color='black'):
        """Create a magnifying glass icon"""
        # Create a new image with transparency
        icon = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(icon)
        
        # Draw the circle part of the magnifying glass
        circle_size = int(size * 0.7)  # Circle takes up 70% of the image
        circle_bbox = [2, 2, circle_size, circle_size]
        draw.ellipse(circle_bbox, outline=color, width=2)
        
        # Draw the handle of the magnifying glass
        handle_start = (circle_size - 1, circle_size - 1)
        handle_end = (size - 2, size - 2)
        draw.line([handle_start, handle_end], fill=color, width=2)
        
        return ImageTk.PhotoImage(icon)

    # Create and add magnifying glass icon
    magnifier_icon = create_magnifier_icon()
    icon_label = tk.Label(search_frame, image=magnifier_icon)
    icon_label.image = magnifier_icon  # Keep a reference to prevent garbage collection
    icon_label.pack(side=tk.LEFT, padx=(2,0))

    tk.Label(search_frame, text="Find:", font=('TkDefaultFont', 9)).pack(side=tk.LEFT, padx=(2,0))
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var, font=('TkDefaultFont', 9))
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
    
    # Create listbox frame
    list_frame = tk.Frame(main_content)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=1)

    listbox = tk.Listbox(list_frame, height=10, font=('TkDefaultFont', 9))
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    def update_file_list(*args):
        search_text = search_var.get().lower()
        listbox.delete(0, tk.END)
        for file in sorted(files):
            if search_text in file.lower():
                listbox.insert(tk.END, file)

    search_var.trace('w', update_file_list)

    def preview_selected_file():
        selection = listbox.curselection()
        if not selection:
            show_error_message("Info", "Please select a file to preview.")
            return
            
        file_name = listbox.get(selection[0])
        file_path = download_from_github(file_name)
        
        if not file_path:
            show_error_message("Error", "Failed to download file from GitHub.")
            return
            
        try:
            img = Image.open(file_path)
            display_width = min(400, img.width)
            ratio = display_width / img.width
            display_height = int(img.height * ratio)
            
            img = img.resize((display_width, display_height), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            
            preview_window = Toplevel(file_window)
            preview_window.title(f"File Preview: {file_name}")
            preview_window.transient(file_window)
            
            # Center the preview window
            x = file_window.winfo_x() + (file_window.winfo_width() - display_width) // 2
            y = file_window.winfo_y() + (file_window.winfo_height() - display_height) // 2
            preview_window.geometry(f"+{x}+{y}")
            
            # Image label
            label = tk.Label(preview_window, image=img_tk)
            label.image = img_tk
            label.pack(padx=10, pady=10)
            
            # Button frame
            button_frame = tk.Frame(preview_window)
            button_frame.pack(pady=5)
            
            def print_label():
                try:
                    # Create a temporary file
                    temp_file = os.path.join(os.environ.get('TEMP', os.getcwd()), f"temp_label_{file_name}.png")
                    img.save(temp_file, dpi=(DPI, DPI))
                    
                    # Open the file with the default image viewer/printer
                    os.startfile(temp_file, "print")
                    
                    # Wait a moment for the print dialog to appear and press Enter
                    preview_window.after(1000, lambda: pyautogui.press('enter'))
                    
                    # Schedule the temporary file for deletion after a delay
                    preview_window.after(5000, lambda: os.remove(temp_file) if os.path.exists(temp_file) else None)
                    
                    # Close the preview window
                    preview_window.destroy()
                except Exception as e:
                    show_error_message("Error", f"Failed to print: {str(e)}")

            # Add Print Label button
            print_btn = tk.Button(
                button_frame,
                text="🖨️ Print",
                command=print_label,
                bg='#4CAF50',  # Green
                fg='white',
                font=('TkDefaultFont', 10, 'bold'),
                width=10
            )
            print_btn.pack(side=tk.LEFT, padx=5)

            # Add hover effect for Print Label button
            def on_print_enter(e):
                print_btn['bg'] = '#45a049'  # Darker green on hover
                
            def on_print_leave(e):
                print_btn['bg'] = '#4CAF50'  # Return to original green
                
            print_btn.bind("<Enter>", on_print_enter)
            print_btn.bind("<Leave>", on_print_leave)

            # Add Close button
            tk.Button(button_frame, text="Close", 
                     command=preview_window.destroy).pack(side=tk.LEFT, padx=5)

        except Exception as e:
            show_error_message("Error", f"Failed to preview image: {str(e)}")
            if file_path and os.path.exists(file_path):
                os.remove(file_path)

    # Add buttons frame
    button_frame = tk.Frame(file_window)
    button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

    tk.Button(button_frame, text="Preview",
             command=preview_selected_file,
             width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Close",
             command=file_window.destroy,
             width=10).pack(side=tk.RIGHT, padx=5)

    # Initial file list population
    update_file_list()
    
    # Set window position
    file_window.geometry("+100+100")
    set_window_on_top(file_window)

def view_local_labels():
    """Display files from local directory in a new window."""
    global file_window
    
    # If file window exists and is valid, just focus it
    if file_window and file_window.winfo_exists():
        focus_window(file_window)
        return
    
    # Get directory to load files from
    local_dir = filedialog.askdirectory(title="Choose Labels Directory")
    if not local_dir:
        return
    
    # Get list of PNG files
    try:
        files = [f for f in os.listdir(local_dir) if f.lower().endswith('.png')]
        if not files:
            show_error_message("Warning", "No PNG files found in selected directory.")
            return
    except Exception as e:
        show_error_message("Error", f"Failed to read directory: {str(e)}")
        return
    
    file_window = Toplevel(app)
    file_window.title(f"View Local Labels - {len(files)} labels found")
    file_window.protocol("WM_DELETE_WINDOW", lambda: close_file_window())
    
    # Set minimum window size
    file_window.minsize(450, 200)
    
    def close_file_window():
        global file_window
        if file_window:
            file_window.destroy()
            file_window = None

    # Create main content frame
    main_content = tk.Frame(file_window)
    main_content.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    # Create top frame for label count
    top_frame = tk.Frame(main_content)
    top_frame.pack(fill=tk.X, padx=2, pady=(2, 0))
    
    # Add label count display
    count_label = tk.Label(
        top_frame, 
        text=f"Total Labels: {len(files)}", 
        font=('TkDefaultFont', 9, 'bold'),
        fg='#191970'  # Midnight blue
    )
    count_label.pack(side=tk.LEFT)

    # Create search frame
    search_frame = tk.Frame(main_content)
    search_frame.pack(fill=tk.X, padx=0, pady=1)

    tk.Label(search_frame, text="Find:", font=('TkDefaultFont', 9)).pack(side=tk.LEFT, padx=(2,0))
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var, font=('TkDefaultFont', 9))
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
    
    # Create listbox frame
    list_frame = tk.Frame(main_content)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=1)

    listbox = tk.Listbox(list_frame, height=10, font=('TkDefaultFont', 9))
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    def update_file_list(*args):
        search_text = search_var.get().lower()
        listbox.delete(0, tk.END)
        matching_files = [file for file in sorted(files) if search_text in file.lower()]
        for file in matching_files:
            listbox.insert(tk.END, file)
        # Update count label to show matching files
        count_label.config(text=f"Labels: {len(matching_files)}")

    search_var.trace('w', update_file_list)

    def preview_selected_file():
        selection = listbox.curselection()
        if not selection:
            show_error_message("Info", "Please select a file to preview.")
            return
            
        file_name = listbox.get(selection[0])
        file_path = os.path.join(local_dir, file_name)
        
        if not os.path.exists(file_path):
            show_error_message("Error", "File not found.")
            return
            
        try:
            img = Image.open(file_path)
            display_width = min(400, img.width)
            ratio = display_width / img.width
            display_height = int(img.height * ratio)
            
            img = img.resize((display_width, display_height), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            
            preview_window = Toplevel(file_window)
            preview_window.title(f"File Preview: {file_name}")
            preview_window.transient(file_window)
            
            # Center the preview window
            x = file_window.winfo_x() + (file_window.winfo_width() - display_width) // 2
            y = file_window.winfo_y() + (file_window.winfo_height() - display_height) // 2
            preview_window.geometry(f"+{x}+{y}")
            
            # Image label
            label = tk.Label(preview_window, image=img_tk)
            label.image = img_tk
            label.pack(padx=10, pady=10)
            
            # Button frame
            button_frame = tk.Frame(preview_window)
            button_frame.pack(pady=5)
            
            def print_label():
                try:
                    os.startfile(file_path, "print")
                    # Wait a moment for the print dialog to appear and press Enter
                    preview_window.after(1000, lambda: pyautogui.press('enter'))
                except Exception as e:
                    show_error_message("Error", f"Failed to print: {str(e)}")
            
            # Print button
            print_btn = tk.Button(
                button_frame,
                text="🖨️ Print",
                command=print_label,
                bg='#4CAF50',  # Green
                fg='white',
                font=('TkDefaultFont', 10, 'bold'),
                width=10
            )
            print_btn.pack(side=tk.LEFT, padx=5)
            
            # Open button
            open_btn = tk.Button(
                button_frame,
                text="📂 Open",
                command=lambda: os.startfile(file_path),
                bg='#2196F3',  # Blue
                fg='white',
                font=('TkDefaultFont', 10, 'bold'),
                width=10
            )
            open_btn.pack(side=tk.LEFT, padx=5)
            
            # Close button
            close_btn = tk.Button(
                button_frame,
                text="❌ Close",
                command=preview_window.destroy,
                bg='#f44336',  # Red
                fg='white',
                font=('TkDefaultFont', 10, 'bold'),
                width=10
            )
            close_btn.pack(side=tk.LEFT, padx=5)
            
            # Add hover effects
            def on_button_enter(e):
                if e.widget == print_btn:
                    e.widget['bg'] = '#45a049'  # Darker green
                elif e.widget == open_btn:
                    e.widget['bg'] = '#1976D2'  # Darker blue
                else:  # close_btn
                    e.widget['bg'] = '#d32f2f'  # Darker red
                
            def on_button_leave(e):
                if e.widget == print_btn:
                    e.widget['bg'] = '#4CAF50'  # Original green
                elif e.widget == open_btn:
                    e.widget['bg'] = '#2196F3'  # Original blue
                else:  # close_btn
                    e.widget['bg'] = '#f44336'  # Original red
            
            for btn in (print_btn, open_btn, close_btn):
                btn.bind('<Enter>', on_button_enter)
                btn.bind('<Leave>', on_button_leave)
            
        except Exception as e:
            show_error_message("Error", f"Failed to preview image: {str(e)}")

    # Add buttons frame
    button_frame = tk.Frame(file_window)
    button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

    tk.Button(button_frame, text="Preview",
             command=preview_selected_file,
             width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Close",
             command=file_window.destroy,
             width=10).pack(side=tk.RIGHT, padx=5)

    # Initial file list population
    update_file_list()
    
    # Set window position
    file_window.geometry("+100+100")
    set_window_on_top(file_window)

def show_error_message(title, message):
    """Show an error message dialog that stays on top"""
    error_window = Toplevel()
    error_window.title(title)
    error_window.attributes('-topmost', True)
    error_window.grab_set()  # Make the window modal
    
    # Calculate position to center the window
    window_width = 300
    window_height = 150
    screen_width = error_window.winfo_screenwidth()
    screen_height = error_window.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    error_window.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    # Add message
    msg_label = tk.Label(error_window, text=message, wraplength=250, justify='center', pady=20)
    msg_label.pack(expand=True, fill='both')
    
    # Add OK button
    ok_button = tk.Button(error_window, text="OK", command=error_window.destroy, width=10)
    ok_button.pack(pady=10)
    
    # Make window non-resizable
    error_window.resizable(False, False)
    
    # Focus on the OK button
    ok_button.focus_set()
    
    # Bind Enter and Escape to close the window
    error_window.bind('<Return>', lambda e: error_window.destroy())
    error_window.bind('<Escape>', lambda e: error_window.destroy())

def upload_to_github(file_path, commit_message="Add new label"):
    try:
        config = load_github_config()
        if not config:
            show_error_message("GitHub Error", "GitHub configuration not found. Please check your github_config.ini file.")
            return False

        # Read the file content
        with open(file_path, 'rb') as file:
            content = file.read()
        
        # Encode content to base64
        content_base64 = base64.b64encode(content).decode()
        
        # Get the filename from the path
        filename = os.path.basename(file_path)
        
        # Prepare the API request
        url = f"https://api.github.com/repos/{config['owner']}/{config['repo']}/contents/labels/{filename}"
        headers = {
            'Authorization': f"token {config['token']}",
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Check if file already exists
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                # File exists, get its SHA
                sha = response.json()['sha']
                data = {
                    'message': commit_message,
                    'content': content_base64,
                    'sha': sha
                }
            else:
                # New file
                data = {
                    'message': commit_message,
                    'content': content_base64
                }
        except Exception as e:
            # New file
            data = {
                'message': commit_message,
                'content': content_base64
            }
        
        # Make the PUT request to create/update the file
        response = requests.put(url, headers=headers, json=data)
        
        if response.status_code in [201, 200]:
            messagebox.showinfo("Success", "Label successfully uploaded to GitHub!")
            update_view_button_text()  # Update the label count
            return True
        else:
            show_error_message("GitHub Error", f"Failed to upload file. Status code: {response.status_code}")
            return False
            
    except Exception as e:
        show_error_message("GitHub Error", f"Error uploading to GitHub: {str(e)}")
        return False

load_settings()

# Directly call the input window at startup
open_input_window()
app.mainloop()
