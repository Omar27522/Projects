import tkinter as tk
from tkinter import messagebox, filedialog, Toplevel, IntVar
from PIL import Image, ImageDraw, ImageFont, ImageTk
import barcode
from barcode.writer import ImageWriter
import os
import json
import pyautogui

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
        window.attributes('-alpha', 1.0)
    
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

def update_png_count_label():
    """Update the PNG count label with current count from output directory."""
    try:
        if output_directory and os.path.exists(output_directory):
            png_files = [f for f in os.listdir(output_directory) if f.lower().endswith('.png')]
            png_count_label.config(text=f"Labels: {len(png_files)}", 
                                 fg='#191970',  # Maintain midnight blue color
                                 font=('TkDefaultFont', 9, 'bold'))  # Maintain bold font
        else:
            png_count_label.config(text="Labels: 0",
                                 fg='#191970',  # Maintain midnight blue color
                                 font=('TkDefaultFont', 9, 'bold'))  # Maintain bold font
    except Exception as e:
        print(f"Error updating PNG count: {str(e)}")

def select_output_directory():
    """Allow the user to select an output directory."""
    global output_directory
    new_directory = filedialog.askdirectory(title="Choose Output Directory", initialdir=output_directory)
    if new_directory:
        output_directory = new_directory
        save_settings()
        update_png_count_label()

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
        update_png_count_label()
    except Exception as e:
        show_error_message("Error", f"Failed to generate label: {str(e)}")

def view_directory_files():
    """Display files from the output directory in a new window."""
    global file_window
    
    # If file window exists and is valid, just focus it
    if file_window and file_window.winfo_exists():
        focus_window(file_window)
        return
        
    if not output_directory:
        show_error_message("Warning", "Please select an output directory first.")
        return
        
    file_window = Toplevel(app)
    file_window.title("View Files")
    file_window.protocol("WM_DELETE_WINDOW", lambda: close_file_window())
    
    # Set minimum window size
    file_window.minsize(450, 200)  # Set minimum width to 450 pixels
    
    def close_file_window():
        global file_window
        if file_window:
            file_window.destroy()
            file_window = None

    # Create a new window
    # Create a variable for this window's always-on-top state
    window_always_on_top = tk.BooleanVar(value=False)  # Default to False
    
    def toggle_window_on_top():
        current_state = window_always_on_top.get()
        file_window.attributes('-topmost', current_state)
        if current_state:
            file_window.lift()  # No transparency change, just lift
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
    
    # Create main content frame to hold everything except buttons
    main_content = tk.Frame(file_window)
    main_content.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    # Create top frame for the Always on Top button
    top_frame = tk.Frame(main_content)
    top_frame.pack(fill=tk.X, padx=0, pady=1)
    
    # Add Always on Top button
    window_top_btn = tk.Button(top_frame, 
        text="Pin",
        bg='#C71585',
        relief='raised',
        width=8)
    window_top_btn.config(command=lambda: [window_always_on_top.set(not window_always_on_top.get()), toggle_window_on_top()])
    window_top_btn.pack(side=tk.LEFT, padx=2)

    # Add Magnifier button and state variable
    is_magnified = tk.BooleanVar(value=False)
    def toggle_magnification():
        current_state = is_magnified.get()
        new_size = 16 if current_state else 9  # Toggle between normal (9) and large (16) font size
        listbox.configure(font=('TkDefaultFont', new_size))
        # Enable/disable horizontal scrolling based on magnification state
        if current_state:
            h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            listbox.configure(wrap=tk.NONE)  # Disable text wrapping
        else:
            h_scrollbar.pack_forget()  # Hide horizontal scrollbar
            listbox.configure(wrap=tk.CHAR)  # Enable text wrapping
        magnifier_btn.config(
            bg='#90EE90' if current_state else '#C71585',
            relief='sunken' if current_state else 'raised'
        )

    magnifier_btn = tk.Button(top_frame,
        text="🔍",
        bg='#C71585',
        relief='raised',
        width=3,
        font=('TkDefaultFont', 14),  # Larger font for the magnifier icon
        command=lambda: [is_magnified.set(not is_magnified.get()), toggle_magnification()])
    magnifier_btn.pack(side=tk.LEFT, padx=2)

    # Create a frame for the search bar
    search_frame = tk.Frame(main_content)
    search_frame.pack(fill=tk.X, padx=0, pady=1)

    # Add search label and entry on same line with reduced height
    tk.Label(search_frame, text="Find:", font=('TkDefaultFont', 9)).pack(side=tk.LEFT, padx=(2,0))
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var, font=('TkDefaultFont', 9))
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
    
    # Set focus on search entry
    search_entry.focus_set()
    
    # Create a frame for the listbox and scrollbar
    list_frame = tk.Frame(main_content)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=1)  

    # Add listbox with scrollbar
    listbox = tk.Listbox(list_frame, height=4, font=('TkDefaultFont', 9))
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  
    
    # Vertical scrollbar
    v_scrollbar = tk.Scrollbar(list_frame)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Horizontal scrollbar
    h_scrollbar = tk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Connect scrollbars to listbox
    listbox.config(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    v_scrollbar.config(command=listbox.yview)
    h_scrollbar.config(command=listbox.xview)

    def update_file_list(*args):
        """Update the listbox based on search text"""
        search_text = search_var.get().lower()
        listbox.delete(0, tk.END)
        try:
            files = os.listdir(output_directory)
            png_files = [f for f in files if f.lower().endswith('.png')]
            for file in sorted(png_files):
                if search_text in file.lower():
                    listbox.insert(tk.END, file)
            if len(png_files) == 0:
                listbox.insert(tk.END, "0")
            else:
                # Select the first item if there are matches
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(0)
                listbox.see(0)  # Ensure the selected item is visible
        except Exception as e:
            show_error_message("Error", f"Failed to read directory: {str(e)}")

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
                show_error_message("Error", f"Failed to open file: {str(e)}")

    def print_selected_file():
        """Print the selected file directly"""
        selection = listbox.curselection()
        if not selection:
            show_error_message("Info", "Please select a file to print.")
            return
            
        file_name = listbox.get(selection[0])
        file_path = os.path.join(output_directory, file_name)
        try:
            os.startfile(file_path, "print")
            # Wait a moment for the print dialog to appear and press Enter
            file_window.after(1000, lambda: pyautogui.press('enter'))
        except Exception as e:
            show_error_message("Error", f"Failed to print: {str(e)}")

    def preview_selected_file():
        """Preview the selected image file"""
        selection = listbox.curselection()
        if not selection:
            show_error_message("Info", "Please select an image to preview.")
            return
            
        file_name = listbox.get(selection[0])
        file_path = os.path.join(output_directory, file_name)
        
        try:
            # Load and display image in a new window
            img = Image.open(file_path)
            # Calculate resize dimensions while maintaining aspect ratio
            display_width = min(400, img.width)
            ratio = display_width / img.width
            display_height = int(img.height * ratio)
            
            img = img.resize((display_width, display_height), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            
            # Create preview window as a child of the file window
            preview_window = Toplevel(file_window)
            preview_window.title(f"File Preview: {file_name}")
            preview_window.transient(file_window)  # Make it a transient window of file_window
            
            def on_preview_close():
                preview_window.destroy()
            
            preview_window.protocol("WM_DELETE_WINDOW", on_preview_close)
            
            # Apply always-on-top setting to the preview window
            set_window_on_top(preview_window)
            
            # Calculate position to center the preview window relative to file window
            x = file_window.winfo_x() + (file_window.winfo_width() - display_width) // 2
            y = file_window.winfo_y() + (file_window.winfo_height() - display_height) // 2
            preview_window.geometry(f"+{x}+{y}")
            
            preview_window.lift()  # Bring window to front
            preview_window.focus_force()  # Force focus
            
            # Display image
            label = tk.Label(preview_window, image=img_tk)
            label.image = img_tk  # Keep a reference
            label.pack(padx=10, pady=10)
            
            def print_file():
                try:
                    # Open the file with the default image viewer/printer
                    os.startfile(file_path, "print")
                    # Wait a moment for the print dialog to appear and press Enter
                    preview_window.after(1000, lambda: pyautogui.press('enter'))
                    # Close the preview window
                    preview_window.destroy()
                except Exception as e:
                    show_error_message("Error", f"Failed to print: {str(e)}")
            
            # Add buttons frame
            button_frame = tk.Frame(preview_window)
            button_frame.pack(pady=5)
            
            # Add buttons
            tk.Button(button_frame, text="Print Label", 
                     command=print_file).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="Open in Default App", 
                     command=lambda: os.startfile(file_path)).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="Close", 
                     command=preview_window.destroy).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            show_error_message("Error", f"Failed to preview image: {str(e)}")

    # Add buttons frame at the bottom of the window
    button_frame = tk.Frame(file_window, height=80)  # Fixed height for button area
    button_frame.pack(side=tk.BOTTOM, fill=tk.X)
    button_frame.pack_propagate(False)  # Prevent the frame from shrinking

    # Create left and right button containers
    left_buttons = tk.Frame(button_frame)
    left_buttons.pack(side=tk.LEFT, padx=3)
    
    right_buttons = tk.Frame(button_frame)
    right_buttons.pack(side=tk.RIGHT, padx=3, pady=2)

    # Add Print Selected button
    print_btn = tk.Button(left_buttons, text="Print Selected",
                        command=print_selected_file,
                        font=('TkDefaultFont', 10, 'bold'),
                        width=14,  # Slightly wider
                        height=5)
    print_btn.pack(side=tk.LEFT)

    # Add hover effects for Print button
    def on_print_enter(e):
        e.widget['bg'] = '#4CAF50'  # Green on hover
        e.widget['fg'] = 'white'    # White text on hover

    def on_print_leave(e):
        e.widget['bg'] = 'SystemButtonFace'  # Default color
        e.widget['fg'] = 'black'    # Default text color

    print_btn.bind('<Enter>', on_print_enter)
    print_btn.bind('<Leave>', on_print_leave)

    # Add other buttons on the right
    tk.Button(right_buttons, text="Preview",
             command=preview_selected_file,
             width=10).pack(side=tk.LEFT, padx=2)  # Slightly wider
    tk.Button(right_buttons, text="Open",
             command=open_selected_file,
             width=10).pack(side=tk.LEFT, padx=2)  # Slightly wider
    tk.Button(right_buttons, text="Close",
             command=file_window.destroy,
             width=10).pack(side=tk.LEFT, padx=2)  # Slightly wider

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
        text="Always On Top " if always_on_top.get() else "Always On Top ",
        bg='#90EE90' if always_on_top.get() else 'SystemButtonFace',
        relief='sunken' if always_on_top.get() else 'raised',
        command=lambda: [always_on_top.set(not always_on_top.get()), toggle_always_on_top()]
    )
    always_on_top_btn.pack(side=tk.LEFT, padx=3)  # Minimal horizontal spacing

    # Create and pack the directory label/button with minimal padding
    global png_count_label
    png_count_label = tk.Button(top_control_frame, text="Labels: 0", 
                               command=select_output_directory,
                               fg='#191970',  # Midnight blue
                               font=('TkDefaultFont', 9, 'bold'))
    png_count_label.pack(side=tk.LEFT, padx=3)
    
    # Update the label count if there's a directory already set
    if output_directory:
        update_png_count_label()

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
    
    # Add Always on Top button at the top of settings
    global settings_always_on_top_btn
    settings_always_on_top_btn = tk.Button(settings_frame, 
        text="Always On Top " if always_on_top.get() else "Always On Top ",
        bg='#90EE90' if always_on_top.get() else 'SystemButtonFace',
        relief='sunken' if always_on_top.get() else 'raised',
        command=lambda: [always_on_top.set(not always_on_top.get()), toggle_always_on_top()]
    )
    settings_always_on_top_btn.grid(row=0, column=0, columnspan=2, pady=10)
    
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

    # Left side - View button
    left_frame = tk.Frame(buttons_frame)
    left_frame.pack(side=tk.LEFT, padx=2)
    
    # Right side - Preview and Save buttons
    right_frame = tk.Frame(buttons_frame)
    right_frame.pack(side=tk.RIGHT, padx=2)

    # Create a larger, more prominent view files button
    view_files_btn = tk.Button(
        left_frame,
        text="📁\nView Labels",
        bg='#4a90e2',  # Blue
        command=view_directory_files,
        font=('TkDefaultFont', 12, 'bold'),
        fg='white',
        width=14,  # Make it wider
        height=2,
        relief='raised'
    )
    view_files_btn.pack(side=tk.LEFT, padx=2)

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
        relief='raised'
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
    view_files_btn._tooltip = ToolTip(view_files_btn, "View and manage all your saved labels\n• Open labels\n• Print labels\n• Search through labels")
    preview_btn._tooltip = ToolTip(preview_btn, "Preview your label before saving\n• Check layout\n• Verify barcode\n• Print directly")
    generate_button._tooltip = ToolTip(generate_button, "Save your label\n• Generate barcode\n• Save as PNG\n• Auto-named with UPC")

    # Add hover effects
    def on_enter(e):
        if e.widget == view_files_btn:
            e.widget['bg'] = '#357abd'  # Darker blue
        elif e.widget == preview_btn:
            e.widget['bg'] = '#27ae60'  # Darker green
        else:  # generate button
            e.widget['bg'] = '#8e44ad'  # Darker purple

    def on_leave(e):
        if e.widget == view_files_btn:
            e.widget['bg'] = '#4a90e2'  # Original blue
        elif e.widget == preview_btn:
            e.widget['bg'] = '#2ecc71'  # Original green
        else:  # generate button
            e.widget['bg'] = '#9b59b6'  # Original purple

    def on_preview_press(e):
        preview_btn['bg'] = '#219a51'  # Even darker green when pressed

    def on_preview_release(e):
        preview_btn['bg'] = '#27ae60'  # Back to hover green
        preview_label(inputs)  # Call preview function

    # Bind events for all buttons
    for btn in (view_files_btn, preview_btn, generate_button):
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

load_settings()

# Directly call the input window at startup
open_input_window()
app.mainloop()
