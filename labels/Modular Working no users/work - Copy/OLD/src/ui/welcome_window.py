import tkinter as tk
from tkinter import messagebox, filedialog
import os
import sys

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
        # Placeholder for user action
        messagebox.showinfo("User Action", "User functionality will be implemented soon.")
    
    def management_action(self):
        """Handler for Management button click"""
        # Placeholder for management action
        messagebox.showinfo("Management", "Management functionality will be implemented soon.")
    
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
