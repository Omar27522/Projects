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

# GitHub configuration
config = configparser.ConfigParser()
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'github_config.ini')

# Path for storing settings
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'label_maker_settings.json')

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

# Initialize variables
transparency_level = tk.DoubleVar(value=0.9)  # Default to 90% opacity
always_on_top = tk.BooleanVar(app, value=False)
preview_window = None
file_window = None
settings_window = None

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

# Load GitHub configuration from file
def load_github_config():
    """Load GitHub configuration from file"""
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        return {
            'owner': config.get('GitHub', 'owner', fallback='Omar27522'),
            'repo': config.get('GitHub', 'repo', fallback='Projects'),
            'token': config.get('GitHub', 'token', fallback=''),
            'labels_path': config.get('GitHub', 'labels_path', fallback='labels/files')
        }
    return {
        'owner': 'Omar27522',
        'repo': 'Projects',
        'token': '',
        'labels_path': 'labels/files'
    }

# Set window always-on-top state and apply transparency if needed
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

# Make a widget contribute to window dragging
def make_draggable(widget):
    """Make a widget contribute to window dragging."""
    widget.bind('<Button-1>', start_drag)
    widget.bind('<B1-Motion>', drag)
    # Recursively apply to all children
    for child in widget.winfo_children():
        make_draggable(child)

# Remove dragging bindings from a widget
def disable_dragging(widget):
    """Remove dragging bindings from a widget."""
    widget.unbind('<Button-1>')
    widget.unbind('<B1-Motion>')
    # Recursively remove from all children
    for child in widget.winfo_children():
        disable_dragging(child)

# Remember the starting position for the drag
def start_drag(event):
    """Remember the starting position for the drag."""
    widget = event.widget
    while not isinstance(widget, Toplevel):
        widget = widget.master
    widget._drag_start_x = event.x_root
    widget._drag_start_y = event.y_root
    widget._window_start_x = widget.winfo_x()
    widget._window_start_y = widget.winfo_y()

# Handle the dragging motion
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

# Toggle the global always-on-top state
def toggle_always_on_top():
    """Toggle the global always-on-top state"""
    current_state = always_on_top.get()
    # Update both Always on Top buttons in the main window
    for btn in [always_on_top_btn, settings_always_on_top_btn]:
        if btn.winfo_exists():  # Check if button still exists
            btn.config(
                text="Always On Top " if current_state else "Always On Top ",
                bg='#90EE90' if current_state else 'SystemButtonFace',  # Light green when active
                relief='sunken' if current_state else 'raised'
            )
    
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

# Focus and lift an existing window
def focus_window(window):
    """Focus and lift an existing window"""
    if window and window.winfo_exists():
        window.deiconify()  # Restore the window if minimized
        window.focus_force()
        window.lift()
        set_window_on_top(window)
        return True
    return False

# Generate a barcode image with python-barcode, adjusting quiet zone and text distance to avoid overlap
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

# Generate the label image with the provided inputs
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

# Generate and display a preview of the label
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

# Generate and save the final label image
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
    except Exception as e:
        show_error_message("Error", f"Failed to generate label: {str(e)}")

# Display files from GitHub repository in a new window
def view_directory_files():
    """Display files from GitHub repository in a new window."""
    global file_window
    
    # If file window exists and is valid, just focus it
    if file_window and file_window.winfo_exists():
        focus_window(file_window)
        return

    file_window = Toplevel(app)
    file_window.title("View GitHub Labels")
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

    # Add search label and entry
    tk.Label(search_frame, text="Find:", font=('TkDefaultFont', 9)).pack(side=tk.LEFT, padx=(2,0))
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var, font=('TkDefaultFont', 9))
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
    
    # Create list frame
    list_frame = tk.Frame(main_content)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=1)

    # Add listbox with scrollbar
    listbox = tk.Listbox(list_frame, height=10, font=('TkDefaultFont', 9))
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Connect scrollbar
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)

    def update_file_list(*args):
        """Update the listbox based on search text"""
        search_text = search_var.get().lower()
        listbox.delete(0, tk.END)
        
        try:
            # Get files from GitHub
            github_files = get_github_files()
            
            # Filter based on search text
            matching_files = [f for f in sorted(github_files) if search_text in f.lower()]
            
            for file in matching_files:
                listbox.insert(tk.END, file)
                
            if len(matching_files) == 0:
                listbox.insert(tk.END, "No files found")
            else:
                # Select the first item if there are matches
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(0)
                listbox.see(0)
        except Exception as e:
            show_error_message("Error", f"Failed to read files: {str(e)}")

    # Bind search entry to update function
    search_var.trace('w', update_file_list)

    def preview_selected_file():
        """Preview the selected image file"""
        selection = listbox.curselection()
        if not selection:
            show_error_message("Info", "Please select an image to preview.")
            return
            
        file_name = listbox.get(selection[0])
        
        # Download file from GitHub
        temp_path = download_from_github(file_name)
        if not temp_path:
            show_error_message("Error", "Failed to download file from GitHub")
            return
            
        try:
            # Load and display image in a new window
            img = Image.open(temp_path)
            # Calculate resize dimensions while maintaining aspect ratio
            display_width = min(400, img.width)
            ratio = display_width / img.width
            display_height = int(img.height * ratio)
            
            img = img.resize((display_width, display_height), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            
            # Create preview window
            preview_window = Toplevel(file_window)
            preview_window.title(f"Preview: {file_name}")
            preview_window.transient(file_window)
            
            # Add image label
            img_label = tk.Label(preview_window, image=img_tk)
            img_label.image = img_tk  # Keep a reference
            img_label.pack(padx=10, pady=10)
            
            # Add buttons frame
            button_frame = tk.Frame(preview_window)
            button_frame.pack(fill=tk.X, pady=5)
            
            # Add Print button
            print_btn = tk.Button(button_frame, text="Print", command=lambda: print_preview(temp_path))
            print_btn.pack(side=tk.LEFT, padx=5)
            
            # Add Close button
            tk.Button(button_frame, text="Close", command=preview_window.destroy).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            show_error_message("Error", f"Failed to preview image: {str(e)}")

    def print_preview(file_path):
        """Print the previewed file"""
        try:
            os.startfile(file_path, "print")
            # Wait a moment for the print dialog to appear and press Enter
            file_window.after(1000, lambda: pyautogui.press('enter'))
        except Exception as e:
            show_error_message("Error", f"Failed to print: {str(e)}")

    # Add buttons frame
    button_frame = tk.Frame(main_content)
    button_frame.pack(fill=tk.X, pady=5)

    # Add Preview button
    preview_btn = tk.Button(button_frame, text="Preview", command=preview_selected_file)
    preview_btn.pack(side=tk.LEFT, padx=5)

    # Initial population of the list
    update_file_list()
    
    # Set focus on search entry
    search_entry.focus_set()

# Clear all input fields
def clear_inputs(inputs):
    """Clear all input fields."""
    for key in inputs:
        inputs[key].delete(0, tk.END)

# Get the number of labels from GitHub repository
def get_label_count():
    """Get the number of labels from GitHub repository"""
    try:
        files = get_github_files()
        return len(files)
    except:
        return 0

# Main input window with settings, preview, and output options
def open_input_window():
    """Main input window with settings, preview, and output options."""
    input_window = Toplevel(app)  # Use Toplevel for the main input window
    input_window.title("Label Maker")
    input_window.protocol("WM_DELETE_WINDOW", lambda: app.quit())
    
    # Create a dictionary to store input field references
    inputs = {}
    
    # Create main frame with padding
    main_frame = tk.Frame(input_window, padx=10, pady=5)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create input fields frame
    input_fields_frame = tk.Frame(main_frame)
    input_fields_frame.pack(fill=tk.X, pady=(0, 10))
    
    # Configure grid columns
    input_fields_frame.grid_columnconfigure(1, weight=1)
    
    # Add input fields with labels
    tk.Label(input_fields_frame, text="Name Line 1:").grid(row=0, column=0, sticky='e', padx=5, pady=2)
    inputs["name_line1"] = tk.Entry(input_fields_frame)
    inputs["name_line1"].grid(row=0, column=1, sticky='ew', padx=5, pady=2)
    
    tk.Label(input_fields_frame, text="Name Line 2:").grid(row=1, column=0, sticky='e', padx=5, pady=2)
    inputs["name_line2"] = tk.Entry(input_fields_frame)
    inputs["name_line2"].grid(row=1, column=1, sticky='ew', padx=5, pady=2)
    
    tk.Label(input_fields_frame, text="Variant:").grid(row=2, column=0, sticky='e', padx=5, pady=2)
    inputs["variant"] = tk.Entry(input_fields_frame)
    inputs["variant"].grid(row=2, column=1, sticky='ew', padx=5, pady=2)
    
    tk.Label(input_fields_frame, text="UPC Code:").grid(row=3, column=0, sticky='e', padx=5, pady=2)
    inputs["upc_code"] = tk.Entry(input_fields_frame)
    inputs["upc_code"].grid(row=3, column=1, sticky='ew', padx=5, pady=2)
    
    # Create buttons frame
    buttons_frame = tk.Frame(main_frame)
    buttons_frame.pack(fill=tk.X, pady=5)
    
    # Add buttons
    preview_btn = tk.Button(buttons_frame, text="Preview Label",
                          command=lambda: preview_label(inputs))
    preview_btn.pack(side=tk.LEFT, padx=5)
    
    generate_btn = tk.Button(buttons_frame, text="Generate Label",
                           command=lambda: generate_and_save_fixed_label(inputs))
    generate_btn.pack(side=tk.LEFT, padx=5)
    
    # Add Labels count label with click functionality
    label_count = get_label_count()
    labels_label = tk.Label(buttons_frame, text=f"Labels: {label_count}",
                         font=view_files_font, cursor="hand2")
    labels_label.pack(side=tk.LEFT, padx=5)
    labels_label.bind("<Button-1>", lambda e: view_directory_files())
    
    clear_btn = tk.Button(buttons_frame, text="Clear",
                        command=lambda: clear_inputs(inputs))
    clear_btn.pack(side=tk.LEFT, padx=5)
    
    # Add Always on Top button
    global always_on_top_btn
    always_on_top_btn = tk.Button(buttons_frame, 
        text="Always On Top",
        command=toggle_always_on_top,
        relief='raised')
    always_on_top_btn.pack(side=tk.RIGHT, padx=5)
    
    # Update button state based on current always-on-top setting
    def update_button_state():
        current_state = always_on_top.get()
        always_on_top_btn.config(
            bg='#90EE90' if current_state else 'SystemButtonFace',
            relief='sunken' if current_state else 'raised'
        )
        input_window.attributes('-topmost', current_state)
        if current_state:
            input_window.lift()
    
    # Bind to always_on_top variable changes
    always_on_top.trace('w', lambda *args: update_button_state())
    
    # Initial button state update
    update_button_state()
    
    # Make window draggable
    make_draggable(input_window)
    
    # Center the window on screen
    window_width = 400
    window_height = 300
    screen_width = input_window.winfo_screenwidth()
    screen_height = input_window.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    input_window.geometry(f"+{x}+{y}")

# Show an error message dialog that stays on top
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

# Get list of files from GitHub repository
def get_github_files():
    """Get list of files from GitHub repository"""
    try:
        github_config = load_github_config()
        
        # For public repositories, we don't need authentication for read operations
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if github_config['token']:
            headers['Authorization'] = f"token {github_config['token']}"
        
        url = f"https://api.github.com/repos/{github_config['owner']}/{github_config['repo']}/contents/{github_config['labels_path']}"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return [item['name'] for item in response.json() if item['type'] == 'file' and item['name'].lower().endswith('.png')]
        else:
            print(f"GitHub API Error: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"List files error: {str(e)}")
        return []

# Download a file from GitHub repository
def download_from_github(filename):
    """Download a file from GitHub repository"""
    try:
        github_config = load_github_config()
        
        # For public repositories, we don't need authentication for read operations
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if github_config['token']:
            headers['Authorization'] = f"token {github_config['token']}"
        
        file_path = f"{github_config['labels_path']}/{filename}"
        url = f"https://api.github.com/repos/{github_config['owner']}/{github_config['repo']}/contents/{file_path}"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            content = base64.b64decode(response.json()['content'])
            
            # Save to temp directory
            temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, filename)
            
            with open(temp_path, 'wb') as f:
                f.write(content)
            
            return temp_path
        else:
            print(f"GitHub API Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Download error: {str(e)}")
        return None

load_settings()

# Directly call the input window at startup
open_input_window()

# Start the main event loop
app.mainloop()
