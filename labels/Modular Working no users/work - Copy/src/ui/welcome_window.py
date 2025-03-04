import tkinter as tk
from tkinter import messagebox, filedialog
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
                "Click the 'Labels' button to set your Labels directory.")
            return
            
        # Create a dialog window for user input
        dialog = tk.Toplevel(self)
        dialog.title("Label Printing")
        dialog.geometry("400x300")  # Made taller for more status info
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
        
        # Status label - made multiline with more height
        status_frame = tk.Frame(content_frame, bg='white')
        status_frame.grid(row=4, column=0, sticky='we', pady=(5, 15))
        
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
        button_frame.grid(row=5, column=0, sticky='we')
        
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
                        status_label.config(text=f"Label {found_label} sent to printer.\n\nReady for next label.", fg='green')
                        
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
                    "Click the 'Labels' button to set your Labels directory.")
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
import pyautogui

# Add Label Maker directory to path
label_maker_dir = r"{label_maker_dir}"
if label_maker_dir not in sys.path:
    sys.path.insert(0, label_maker_dir)

try:
    # Run Label Maker
    import subprocess
    process = subprocess.Popen([sys.executable, r"{label_maker_main}"])
    
    # Wait for window to appear
    time.sleep(2)
    
    # Find and click the View Files button
    # Assuming the button has text "View Files" or similar
    try:
        # Try to find and click the button by image or position
        view_files_button = None
        
        # Try to find by position (assuming it's in the main window)
        # These coordinates are approximate and may need adjustment
        pyautogui.click(400, 200)  # Try clicking where the View Files button might be
        
        # Wait for file viewer to appear
        time.sleep(1)
        
    except Exception as e:
        print(f"Error clicking button: {{str(e)}}")
    
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
        """Handler for Labels button click"""
        # Placeholder for labels action
        try:
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
                
                messagebox.showinfo("Success", 
                    f"Labels directory set to:\n{directory}\n\n"
                    "You can now open the View Files window.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set labels directory: {str(e)}")
    
    def settings_action(self):
        """Handler for Settings button click"""
        # Placeholder for settings action
        messagebox.showinfo("Settings", "Settings functionality will be implemented soon.")
    
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
