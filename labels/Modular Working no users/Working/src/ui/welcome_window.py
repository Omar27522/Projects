import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os
import sys
import subprocess

from src.config.config_manager import ConfigManager
from src.ui.window_state import WindowState

class WelcomeWindow(tk.Tk):
    """Main welcome window for the Label Maker application"""
    
    def __init__(self):
        """Initialize the welcome window"""
        super().__init__()

        # Initialize window state
        self.window_state = WindowState()
        self.window_state.add_window(self)

        # Initialize config manager
        self.config_manager = ConfigManager()

        # Window setup
        self.title("Welcome")
        self.geometry("400x400")  # Window size
        self.resizable(False, False)  # Prevent resizing
        
        # Configure window style
        self.configure(bg='white')
        
        # Remove maximize button but keep minimize
        self.attributes('-toolwindow', 1)  # Remove minimize/maximize buttons
        self.attributes('-toolwindow', 0)  # Restore minimize button
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface elements"""
        # Add title
        self._create_title_section()
        
        # Create buttons
        self._create_button_section()
        
        # Add version label
        self._create_version_label()
    
    def _create_title_section(self):
        """Create the title section of the window"""
        title_frame = tk.Frame(self, bg='white')
        title_frame.pack(pady=20)
        
        tk.Label(title_frame, text="Welcome", font=("Arial", 16, "bold"), bg='white').pack()
        tk.Label(title_frame, text="Label Maker V3", font=("Arial", 14), bg='white').pack()
    
    def _create_button_section(self):
        """Create the button section of the window"""
        # Button frame
        button_frame = tk.Frame(self, bg='white')
        button_frame.pack(expand=True, padx=20)  # Added horizontal padding
        
        # Button colors (Material Design)
        colors = {
            'user': ('#4CAF50', '#A5D6A7'),        # Green, Light Green
            'management': ('#2196F3', '#90CAF9'),   # Blue, Light Blue
            'labels': ('#FF9800', '#FFCC80'),       # Orange, Light Orange
            'settings': ('#9E9E9E', '#E0E0E0')      # Gray, Light Gray
        }
        
        # Buttons with their respective styles
        self.user_btn = self._create_button(
            button_frame, "User", colors['user'], 
            self.user_action, big=True
        )
        
        self.management_btn = self._create_button(
            button_frame, "Management", colors['management'],
            self.management_action
        )
        
        self.labels_btn = self._create_button(
            button_frame, "Labels", colors['labels'],
            self.labels_action
        )
        
        self.settings_btn = self._create_button(
            button_frame, "Settings", colors['settings'],
            self.settings_action
        )
        
        # Grid layout for buttons
        button_frame.grid_columnconfigure(0, weight=3)  # Even more weight to User button column
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)
        button_frame.grid_rowconfigure(2, weight=1)
        
        # Place User button spanning both rows with more padding
        self.user_btn.grid(row=0, column=0, rowspan=2, padx=15, pady=10, sticky="nsew")
        
        # Place other buttons in the second column
        self.management_btn.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        self.labels_btn.grid(row=1, column=1, padx=(10, 10), pady=5, sticky="nsew")
        
        # Move settings to bottom, spanning both columns
        self.settings_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
    
    def _create_button(self, parent, text, color_pair, command, big=False):
        """
        Create a colored button with hover effect
        
        Args:
            parent: Parent widget
            text (str): Button text
            color_pair (tuple): Tuple of (normal_color, hover_color)
            command: Button command
            big (bool): Whether this is a big button
            
        Returns:
            tk.Button: The created button
        """
        color, light_color = color_pair
        btn = tk.Button(
            parent, 
            text=text,
            font=('Arial', 18 if big else 12, 'bold' if big else 'normal'),
            fg='white',
            bg=color,
            activeforeground='black',
            activebackground='white',
            relief='flat',
            borderwidth=0,
            width=20 if big else 15,
            height=4 if big else 2,
            cursor='hand2',
            command=command
        )
        
        # Add hover effect with delay
        hover_timer = None
        
        def apply_hover():
            btn['bg'] = light_color
            btn['fg'] = 'black'
        
        def remove_hover():
            btn['bg'] = color
            btn['fg'] = 'white'
        
        def on_enter(e):
            nonlocal hover_timer
            # Cancel any existing timer
            if hover_timer is not None:
                btn.after_cancel(hover_timer)
            # Start new timer for hover effect
            hover_timer = btn.after(25, apply_hover)  # 25ms delay
        
        def on_leave(e):
            nonlocal hover_timer
            # Cancel any pending hover effect
            if hover_timer is not None:
                btn.after_cancel(hover_timer)
                hover_timer = None
            remove_hover()
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def _create_version_label(self):
        """Create the version label at the bottom right"""
        version_label = tk.Label(
            self,
            text="Ver. 1.0.1.1",
            font=("Arial", 8),
            bg='white',
            fg='gray'
        )
        version_label.pack(side='bottom', anchor='se', padx=10, pady=5)
    
    def user_action(self):
        """Handler for User button click"""
        # Check if labels directory is set and exists
        if not self.config_manager.settings.last_directory or not os.path.exists(self.config_manager.settings.last_directory):
            messagebox.showinfo("Labels Required", 
                "Please select a Labels directory before using this feature.\n\n"
                "Click the 'Settings' button to set your Labels directory.")
            return
            
        # Create a dialog window for user input
        dialog = tk.Toplevel(self)
        dialog.title("Label Printing")
        dialog.geometry("400x350")  # Increased height to ensure all elements are visible
        dialog.resizable(False, False)
        dialog.configure(bg='white')
        dialog.transient(self)  # Make dialog modal
        dialog.grab_set()  # Make dialog modal
        
        # Center the dialog
        self.center_window(dialog)
        
        # Create a frame for the content
        content_frame = tk.Frame(dialog, bg='white', padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Create labels and entry fields
        tk.Label(content_frame, text="Tracking Number:", font=("Arial", 12), bg='white').grid(row=0, column=0, sticky='w', pady=(0, 5))
        tracking_entry = tk.Entry(content_frame, font=("Arial", 12), width=30)
        tracking_entry.grid(row=1, column=0, sticky='we', pady=(0, 15))
        tracking_entry.focus_set()  # Set focus to this field
        
        tk.Label(content_frame, text="SKU:", font=("Arial", 12), bg='white').grid(row=2, column=0, sticky='w', pady=(0, 5))
        sku_entry = tk.Entry(content_frame, font=("Arial", 12), width=30)
        sku_entry.grid(row=3, column=0, sticky='we', pady=(0, 15))
        
        # Add mirror print toggle button
        options_frame = tk.Frame(content_frame, bg='white')
        options_frame.grid(row=4, column=0, sticky='we', pady=(0, 10))
        
        # Create mirror print variable and initialize to False
        self.is_mirror_print = tk.BooleanVar(value=False)
        
        # Create mirror print toggle button with icon
        mirror_btn = tk.Button(options_frame, text=" ", bg='#C71585', relief='raised', width=3,
                             font=('Arial', 12), anchor='center')
        
        def toggle_mirror_print():
            current_state = self.is_mirror_print.get()
            mirror_btn.config(
                bg='#90EE90' if current_state else '#C71585',
                relief='sunken' if current_state else 'raised'
            )
        
        mirror_btn.config(
            command=lambda: [self.is_mirror_print.set(not self.is_mirror_print.get()),
                           toggle_mirror_print()]
        )
        mirror_btn.pack(side=tk.LEFT, padx=2)
        
        # Add label for the mirror button
        mirror_label = tk.Label(options_frame, text="Mirror Print", font=("Arial", 10), bg='white')
        mirror_label.pack(side=tk.LEFT, padx=(2, 10))
        
        # Status label - made multiline with more height
        status_frame = tk.Frame(content_frame, bg='white')
        status_frame.grid(row=5, column=0, sticky='we', pady=(5, 15))
        
        status_label = tk.Label(
            status_frame, 
            text="Enter Tracking Number and SKU, then click Print Label", 
            font=("Arial", 10), 
            bg='white', 
            fg='#666666',
            wraplength=350,  # Allow text to wrap
            justify=tk.LEFT
        )
        status_label.pack(fill='both', expand=True)
        
        # Create a frame for the buttons
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.grid(row=6, column=0, sticky='we')
        
        # Helper function to search for a SKU in label files
        def search_for_sku(sku, directory):
            """
            Search for a SKU in the label files
            
            Args:
                sku (str): SKU to search for
                directory (str): Directory to search in
                
            Returns:
                tuple: (found_file, error_message)
            """
            if not os.path.exists(directory):
                return None, f"Directory does not exist: {directory}"
                
            try:
                files = os.listdir(directory)
                status_label.config(text=f"Searching through {len(files)} files in {directory}...", fg='#666666')
                dialog.update()
                
                # First, try to find an exact filename match (most efficient)
                for file in files:
                    if sku.lower() in file.lower():
                        file_path = os.path.join(directory, file)
                        if not os.path.isdir(file_path):
                            status_label.config(text=f"Found matching filename: {file}", fg='green')
                            dialog.update()
                            return file, None
                
                # If no filename match, search file contents
                text_extensions = ('.txt', '.csv', '.json', '.xml', '.html')
                image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')
                
                # First check text files
                for file in files:
                    file_path = os.path.join(directory, file)
                    
                    # Skip directories
                    if os.path.isdir(file_path):
                        continue
                        
                    # Only search text files
                    if file.lower().endswith(text_extensions):
                        try:
                            status_label.config(text=f"Checking file contents: {file}...", fg='#666666')
                            dialog.update()
                            
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read().lower()
                                if sku.lower() in content:
                                    return file, None
                        except Exception as e:
                            print(f"Error reading file {file}: {str(e)}")
                
                # If we get here, no match was found
                return None, f"No label found with SKU: {sku}"
                
            except Exception as e:
                return None, f"Error searching directory: {str(e)}"
        
        # Function to handle the print action
        def print_label():
            tracking_number = tracking_entry.get().strip()
            sku = sku_entry.get().strip()
            
            if not tracking_number or not sku:
                status_label.config(text="Please enter both Tracking Number and SKU", fg='red')
                return
                
            # Search for the SKU in the labels directory
            labels_dir = self.config_manager.settings.last_directory
            
            status_label.config(text=f"Searching for SKU: {sku}...", fg='#666666')
            dialog.update()
            
            try:
                # Use the helper function to search for the SKU
                found_label, error_message = search_for_sku(sku, labels_dir)
                
                if found_label:
                    # Record the tracking number and SKU
                    log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs', 'shipping_records.txt')
                    
                    # Create logs directory if it doesn't exist
                    logs_dir = os.path.dirname(log_file)
                    if not os.path.exists(logs_dir):
                        os.makedirs(logs_dir)
                    
                    # Get current timestamp
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Write to log file
                    with open(log_file, 'a') as f:
                        f.write(f"{timestamp} | Tracking: {tracking_number} | SKU: {sku} | Label: {found_label}\n")
                    
                    # Print the label
                    status_label.config(text=f"Found label: {found_label}. Opening print dialog...", fg='green')
                    dialog.update()
                    
                    # Direct printing without temporary script
                    try:
                        # Get the full path to the label file
                        label_path = os.path.join(labels_dir, found_label)
                        
                        # If mirror print is enabled, create a mirrored temporary copy
                        if self.is_mirror_print.get():
                            from PIL import Image
                            import tempfile
                            
                            # Create temp directory if it doesn't exist
                            temp_dir = os.path.join(os.environ.get('TEMP', os.getcwd()), 'labelmaker_temp')
                            os.makedirs(temp_dir, exist_ok=True)
                            
                            # Create mirrored image
                            img = Image.open(label_path)
                            mirrored_img = img.transpose(Image.FLIP_LEFT_RIGHT)
                            temp_path = os.path.join(temp_dir, f'mirror_{found_label}')
                            mirrored_img.save(temp_path)
                            
                            # Update label path to use the mirrored version
                            label_path = temp_path
                            
                            status_label.config(text=f"Mirrored label created at: {temp_path}", fg='green')
                            dialog.update()
                        
                        # Use ShellExecute to open the print dialog
                        import win32api
                        win32api.ShellExecute(
                            0,          # Handle to parent window
                            "print",    # Operation to perform
                            label_path, # File to print
                            None,       # Parameters
                            ".",        # Working directory
                            0           # Show command
                        )
                        
                        # Wait briefly for print dialog to appear
                        import time
                        time.sleep(1.5)
                        
                        # Press Enter to confirm print
                        import pyautogui
                        pyautogui.press('enter')
                        
                        # Keep the dialog open with status message
                        status_label.config(text=f"Ready for next label.", fg='green')
                        
                        # Clear the entry fields for next input
                        tracking_entry.delete(0, tk.END)
                        sku_entry.delete(0, tk.END)
                        tracking_entry.focus_set()
                        
                    except Exception as e:
                        status_label.config(text=f"Error printing: {str(e)}", fg='red')
                        import traceback
                        traceback.print_exc()
                else:
                    if error_message:
                        status_label.config(text=error_message, fg='red')
                    else:
                        status_label.config(text=f"No label found with SKU: {sku}\n\nTry checking if the SKU is correct or if the label exists in the selected directory:\n{labels_dir}", fg='red')
            
            except Exception as e:
                error_msg = str(e)
                status_label.config(text=f"Error: {error_msg}\n\nPlease check the logs for more details.", fg='red')
                import traceback
                traceback.print_exc()  # Print full traceback to console for debugging
        
        # Create buttons
        print_button = tk.Button(
            button_frame, 
            text="Print Label", 
            font=("Arial", 12), 
            bg='#4CAF50', 
            fg='white',
            activebackground='#45a049',
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=print_label
        )
        print_button.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_button = tk.Button(
            button_frame, 
            text="Cancel", 
            font=("Arial", 12), 
            bg='#f44336', 
            fg='white',
            activebackground='#d32f2f',
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=dialog.destroy
        )
        cancel_button.pack(side=tk.LEFT)
        
        # Add hover effects to buttons
        def on_enter(e, button, color):
            button['background'] = color
            
        def on_leave(e, button, color):
            button['background'] = color
        
        print_button.bind("<Enter>", lambda e: on_enter(e, print_button, '#45a049'))
        print_button.bind("<Leave>", lambda e: on_leave(e, print_button, '#4CAF50'))
        
        cancel_button.bind("<Enter>", lambda e: on_enter(e, cancel_button, '#d32f2f'))
        cancel_button.bind("<Leave>", lambda e: on_leave(e, cancel_button, '#f44336'))
        
        # Bind Enter key to print_label function
        dialog.bind('<Return>', lambda event: print_label())
        
        # Wait for the dialog to be closed
        self.wait_window(dialog)
    
    def management_action(self):
        """Handler for Management button click"""
        try:
            # Check if labels directory is set and exists
            if not self.config_manager.settings.last_directory or not os.path.exists(self.config_manager.settings.last_directory):
                messagebox.showinfo("Labels Required", 
                    "Please select a Labels directory before managing files.\n\n"
                    "Click the 'Settings' button to set your Labels directory.")
                return
                
            # Get the path to the Label Maker main.pyw file
            label_maker_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'Label Maker')
            label_maker_main = os.path.join(label_maker_dir, 'main.pyw')
            
            if not os.path.exists(label_maker_main):
                messagebox.showerror("Error", f"Label Maker main file not found at: {label_maker_main}")
                return
            
            # Create a temporary Python script to run Label Maker and click the View Files button
            temp_script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'temp_view_files.py')
            
            with open(temp_script_path, 'w') as f:
                f.write(f'''
import os
import sys
import time
import tkinter as tk
from tkinter import messagebox
import subprocess

# Add Label Maker directory to path
label_maker_dir = r"{label_maker_dir}"
if label_maker_dir not in sys.path:
    sys.path.insert(0, label_maker_dir)

try:
    # Run Label Maker directly with a command line argument to open in View Files mode
    process = subprocess.Popen([sys.executable, r"{label_maker_main}", "--view-files"])
    
    # Keep script running until Label Maker closes
    process.wait()
    
except Exception as e:
    print(f"Error: {{str(e)}}")
    try:
        messagebox.showerror("Error", f"Failed to run Label Maker: {{str(e)}}")
    except:
        pass
finally:
    # Clean up
    if os.path.exists(r"{temp_script_path}"):
        try:
            os.remove(r"{temp_script_path}")
        except:
            pass
''')
            
            # Hide welcome window
            self.withdraw()
            
            # Run the temporary script
            process = subprocess.Popen([sys.executable, temp_script_path])
            
            # Set up a check to monitor when the script terminates
            def check_process():
                if process.poll() is not None:
                    # Process has terminated, show welcome window again
                    self.deiconify()
                    self.lift()
                    self.focus_force()
                    
                    # Clean up temp script if it still exists
                    if os.path.exists(temp_script_path):
                        try:
                            os.remove(temp_script_path)
                        except:
                            pass
                    return
                # Check again after 1 second
                self.after(1000, check_process)
                
            # Start monitoring the process
            self.after(1000, check_process)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Label Maker: {str(e)}")
            self.deiconify()  # Show welcome window again
            
            # Clean up temp script if it exists
            temp_script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'temp_view_files.py')
            if os.path.exists(temp_script_path):
                try:
                    os.remove(temp_script_path)
                except:
                    pass
    
    def labels_action(self):
        """Handler for Labels button click - Display and edit returns data"""
        # Create a dialog window for viewing and editing returns data
        dialog = tk.Toplevel(self)
        dialog.title("Returns Data")
        dialog.geometry("800x500")
        dialog.resizable(True, True)
        dialog.configure(bg='white')
        dialog.transient(self)  # Make dialog modal
        dialog.grab_set()  # Make dialog modal
        
        # Center the dialog
        self.center_window(dialog)
        
        # Create a frame for the content
        content_frame = tk.Frame(dialog, bg='white', padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(
            content_frame, 
            text="Returns Data", 
            font=("Arial", 16, "bold"), 
            bg='white'
        )
        title_label.pack(pady=(0, 20))
        
        # Create a frame for the treeview with scrollbars
        tree_frame = tk.Frame(content_frame, bg='white')
        tree_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Create vertical scrollbar
        vsb = tk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side='right', fill='y')
        
        # Create horizontal scrollbar
        hsb = tk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side='bottom', fill='x')
        
        # Create treeview
        columns = ("tracking", "sku", "label", "timestamp", "full_label")
        tree = ttk.Treeview(
            tree_frame, 
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        # Configure scrollbars
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        
        # Define column headings
        tree.heading("tracking", text="Tracking Number")
        tree.heading("sku", text="SKU")
        tree.heading("label", text="Label")
        tree.heading("timestamp", text="Timestamp")
        tree.heading("full_label", text="Full Label")  # Hidden column
        
        # Define column widths
        tree.column("tracking", width=200, minwidth=150)
        tree.column("sku", width=150, minwidth=100)
        tree.column("label", width=250, minwidth=150)
        tree.column("timestamp", width=150, minwidth=150)
        tree.column("full_label", width=0, stretch=False)  # Hidden column
        
        tree.pack(fill='both', expand=True)
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview", 
                        background="white",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="white")
        style.map('Treeview', background=[('selected', '#4CAF50')])
        
        # Function to load records from log file
        def load_records():
            # Clear existing items
            for item in tree.get_children():
                tree.delete(item)
                
            # Path to log file
            log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs', 'shipping_records.txt')
            
            if not os.path.exists(log_file):
                # No records yet
                tree.insert("", "end", values=("No records found", "", "", ""))
                return
                
            # Read and parse log file
            with open(log_file, 'r') as f:
                lines = f.readlines()
                
            # Add each record to the treeview
            for line in lines:
                try:
                    # Parse line
                    parts = line.strip().split(" | ")
                    if len(parts) >= 4:
                        timestamp = parts[0]
                        tracking = parts[1].replace("Tracking: ", "")
                        sku = parts[2].replace("SKU: ", "")
                        label_full = parts[3].replace("Label: ", "")
                        
                        # Extract name before "_label" if it exists
                        if "_label" in label_full:
                            label_display = label_full.split("_label")[0]
                        else:
                            label_display = label_full
                            
                        # Insert into treeview with full label stored in hidden column
                        tree.insert("", "end", values=(tracking, sku, label_display, timestamp, label_full))
                except Exception as e:
                    print(f"Error parsing log line: {str(e)}")
        
        # Function to edit a record
        def edit_record():
            # Get selected item
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showinfo("Select Record", "Please select a record to edit.")
                return
                
            # Get values of selected item
            item_values = tree.item(selected_item[0], "values")
            if not item_values or item_values[0] == "No records found":
                return
                
            # Get the original full label name from the log file
            log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs', 'shipping_records.txt')
            original_label_full = ""
            
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        parts = line.strip().split(" | ")
                        if len(parts) >= 4:
                            if parts[0] == item_values[3] and parts[1].replace("Tracking: ", "") == item_values[0]:
                                original_label_full = parts[3].replace("Label: ", "")
                                break
            
            # Create edit dialog
            edit_dialog = tk.Toplevel(dialog)
            edit_dialog.title("Edit Record")
            edit_dialog.geometry("500x300")
            edit_dialog.resizable(False, False)
            edit_dialog.configure(bg='white')
            edit_dialog.transient(dialog)
            edit_dialog.grab_set()
            
            # Center the dialog
            self.center_window(edit_dialog)
            
            # Create a frame for the content
            edit_frame = tk.Frame(edit_dialog, bg='white', padx=20, pady=20)
            edit_frame.pack(fill='both', expand=True)
            
            # Create form fields
            tk.Label(edit_frame, text="Timestamp:", font=("Arial", 10), bg='white').grid(row=0, column=0, sticky='w', pady=(0, 5))
            timestamp_var = tk.StringVar(value=item_values[3])
            timestamp_entry = tk.Entry(edit_frame, textvariable=timestamp_var, font=("Arial", 10), width=30)
            timestamp_entry.grid(row=0, column=1, sticky='we', pady=(0, 5))
            
            tk.Label(edit_frame, text="Tracking Number:", font=("Arial", 10), bg='white').grid(row=1, column=0, sticky='w', pady=(0, 5))
            tracking_var = tk.StringVar(value=item_values[0])
            tracking_entry = tk.Entry(edit_frame, textvariable=tracking_var, font=("Arial", 10), width=30)
            tracking_entry.grid(row=1, column=1, sticky='we', pady=(0, 5))
            
            tk.Label(edit_frame, text="SKU:", font=("Arial", 10), bg='white').grid(row=2, column=0, sticky='w', pady=(0, 5))
            sku_var = tk.StringVar(value=item_values[1])
            sku_entry = tk.Entry(edit_frame, textvariable=sku_var, font=("Arial", 10), width=30)
            sku_entry.grid(row=2, column=1, sticky='we', pady=(0, 5))
            
            tk.Label(edit_frame, text="Label:", font=("Arial", 10), bg='white').grid(row=3, column=0, sticky='w', pady=(0, 5))
            label_var = tk.StringVar(value=item_values[2])
            label_entry = tk.Entry(edit_frame, textvariable=label_var, font=("Arial", 10), width=30)
            label_entry.grid(row=3, column=1, sticky='we', pady=(0, 5))
            
            # Store the original full label name
            original_label_full_var = tk.StringVar(value=original_label_full)
            
            # Create a frame for the buttons
            button_frame = tk.Frame(edit_frame, bg='white')
            button_frame.grid(row=4, column=0, columnspan=2, sticky='e', pady=(20, 0))
            
            # Function to save changes
            def save_changes():
                # Get updated values
                new_timestamp = timestamp_var.get()
                new_tracking = tracking_var.get()
                new_sku = sku_var.get()
                new_label_display = label_var.get()
                
                # Determine the full label name to save
                new_label_full = original_label_full_var.get()
                if not new_label_full or new_label_display not in new_label_full:
                    # If the display name has changed or we don't have the original,
                    # reconstruct the full name with _label suffix if needed
                    if not new_label_display.endswith("_label") and "_label" not in new_label_display:
                        new_label_full = f"{new_label_display}_label"
                    else:
                        new_label_full = new_label_display
                
                # Update treeview with display values
                tree.item(selected_item[0], values=(new_tracking, new_sku, new_label_display, new_timestamp))
                
                # Store the full label name for the log update
                tree.set(selected_item[0], "full_label", new_label_full)
                
                # Update log file
                update_log_file()
                
                # Close dialog
                edit_dialog.destroy()
            
            # Save button
            save_button = tk.Button(
                button_frame, 
                text="Save", 
                font=("Arial", 10), 
                bg='#4CAF50', 
                fg='white',
                activebackground='#45a049',
                activeforeground='white',
                relief=tk.FLAT,
                padx=15,
                pady=5,
                command=save_changes
            )
            save_button.pack(side='right', padx=(10, 0))
            
            # Cancel button
            cancel_button = tk.Button(
                button_frame, 
                text="Cancel", 
                font=("Arial", 10), 
                bg='#f44336', 
                fg='white',
                activebackground='#d32f2f',
                activeforeground='white',
                relief=tk.FLAT,
                padx=15,
                pady=5,
                command=edit_dialog.destroy
            )
            cancel_button.pack(side='right')
        
        # Function to delete a record
        def delete_record():
            # Get selected item
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showinfo("Select Record", "Please select a record to delete.")
                return
                
            # Get values of selected item
            item_values = tree.item(selected_item[0], "values")
            if not item_values or item_values[0] == "No records found":
                return
                
            # Confirm deletion
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
                # Delete from treeview
                tree.delete(selected_item[0])
                
                # Update log file
                update_log_file()
        
        # Function to update the log file with current treeview contents
        def update_log_file():
            # Path to log file
            log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs', 'shipping_records.txt')
            
            # Get all items from treeview
            all_items = tree.get_children()
            
            # Create logs directory if it doesn't exist
            logs_dir = os.path.dirname(log_file)
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
            
            # Write to log file
            with open(log_file, 'w') as f:
                for item_id in all_items:
                    item_values = tree.item(item_id, "values")
                    if item_values and item_values[0] != "No records found":
                        timestamp = item_values[3]
                        tracking = item_values[0]
                        sku = item_values[1]
                        
                        # Get the full label name from the hidden column
                        full_label = item_values[4] if len(item_values) > 4 else None
                        
                        # If full_label is not available, use the display label
                        if not full_label:
                            label_display = item_values[2]
                            # If we don't have the full label, reconstruct it
                            if not label_display.endswith("_label") and "_label" not in label_display:
                                full_label = f"{label_display}_label"
                            else:
                                full_label = label_display
                        
                        f.write(f"{timestamp} | Tracking: {tracking} | SKU: {sku} | Label: {full_label}\n")
        
        # Create a frame for the buttons
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Refresh button
        refresh_button = tk.Button(
            button_frame, 
            text="Refresh", 
            font=("Arial", 10), 
            bg='#2196F3', 
            fg='white',
            activebackground='#1976D2',
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=load_records
        )
        refresh_button.pack(side='left')
        
        # Edit button
        edit_button = tk.Button(
            button_frame, 
            text="Edit", 
            font=("Arial", 10), 
            bg='#FF9800', 
            fg='white',
            activebackground='#F57C00',
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=edit_record
        )
        edit_button.pack(side='left', padx=(10, 0))
        
        # Delete button
        delete_button = tk.Button(
            button_frame, 
            text="Delete", 
            font=("Arial", 10), 
            bg='#f44336', 
            fg='white',
            activebackground='#d32f2f',
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=delete_record
        )
        delete_button.pack(side='left', padx=(10, 0))
        
        # Close button
        close_button = tk.Button(
            button_frame, 
            text="Close", 
            font=("Arial", 10), 
            bg='#9E9E9E', 
            fg='white',
            activebackground='#757575',
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=dialog.destroy
        )
        close_button.pack(side='right')
        
        # Load records initially
        load_records()
        
        # Wait for the dialog to be closed
        self.wait_window(dialog)
    
    def settings_action(self):
        """Handler for Settings button click"""
        # Create a settings dialog
        settings_dialog = tk.Toplevel(self)
        settings_dialog.title("Settings")
        settings_dialog.geometry("450x300")
        settings_dialog.resizable(False, False)
        settings_dialog.configure(bg='white')
        settings_dialog.transient(self)  # Make dialog modal
        settings_dialog.grab_set()  # Make dialog modal
        
        # Center the dialog
        self.center_window(settings_dialog)
        
        # Create a frame for the content
        content_frame = tk.Frame(settings_dialog, bg='white', padx=20, pady=20)
        content_frame.pack(fill='both', expand=True)
        
        # Labels Directory Section
        labels_section = tk.LabelFrame(content_frame, text="Labels Directory", font=("Arial", 12, "bold"), bg='white', padx=10, pady=10)
        labels_section.pack(fill='x', pady=(0, 15))
        
        # Current directory display
        current_dir = self.config_manager.settings.last_directory or "Not set"
        dir_var = tk.StringVar(value=current_dir)
        
        dir_label = tk.Label(labels_section, text="Current Directory:", font=("Arial", 10), bg='white')
        dir_label.grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        dir_display = tk.Entry(labels_section, textvariable=dir_var, font=("Arial", 10), width=30, state='readonly')
        dir_display.grid(row=1, column=0, sticky='we', padx=(0, 10))
        
        def select_labels_directory():
            initial_dir = self.config_manager.settings.last_directory
            if not initial_dir or not os.path.exists(initial_dir):
                initial_dir = os.path.expanduser("~")
                
            directory = filedialog.askdirectory(
                title="Select Labels Directory",
                initialdir=initial_dir
            )
            
            if directory:
                # Convert to absolute path and normalize
                directory = os.path.abspath(os.path.normpath(directory))
                
                # Update settings with new directory
                self.config_manager.settings.last_directory = directory
                self.config_manager.save_settings()
                
                # Update display
                dir_var.set(directory)
                
                messagebox.showinfo("Success", 
                    f"Labels directory set to:\n{directory}")
        
        browse_button = tk.Button(
            labels_section, 
            text="Browse...", 
            font=("Arial", 10), 
            bg='#4CAF50', 
            fg='white',
            activebackground='#45a049',
            activeforeground='white',
            relief=tk.FLAT,
            padx=10,
            pady=2,
            command=select_labels_directory
        )
        browse_button.grid(row=1, column=1, sticky='e')
        
        # Other settings can be added here in the future
        
        # Create a frame for the buttons
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(side='bottom', fill='x', pady=(10, 0))
        
        # Close button
        close_button = tk.Button(
            button_frame, 
            text="Close", 
            font=("Arial", 12), 
            bg='#9E9E9E', 
            fg='white',
            activebackground='#757575',
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=settings_dialog.destroy
        )
        close_button.pack(side='right')
        
        # Wait for the dialog to be closed
        self.wait_window(settings_dialog)
    
    def center_window(self, window=None):
        """
        Center a window on the screen
        
        Args:
            window: Window to center (defaults to self)
        """
        if window is None:
            window = self
            
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
