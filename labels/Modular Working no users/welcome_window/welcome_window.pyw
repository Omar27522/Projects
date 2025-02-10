"""
Welcome Window Module for Label Maker V3

This module implements the main welcome window interface for the Label Maker V3 application.
It provides a clean, modern interface with quick access to core functionalities including
user operations, management tools, label creation, and settings.

The window is implemented using tkinter and follows a consistent styling approach defined
in the src.styles module. All buttons are created using the ButtonFactory to ensure
consistent appearance and behavior.

Author: Label Maker V3 Team
Version: 3.0
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
import win32gui
import win32con
import ctypes

# Add the current directory to Python path to allow importing
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Use absolute imports from src
from src.button_factory import ButtonFactory
from src.styles import WINDOW_CONFIG, COLORS
from src.config import WelcomeWindowConfig
from src.assets import get_window_icon
from src.system_tray import SystemTrayIcon

class WelcomeWindow(tk.Tk):
    """
    Main welcome window for the Label Maker V3 application.

    This class creates a non-resizable window with a clean, modern interface that provides
    quick access to core functionalities. The window includes:
    - A title section with welcome message
    - A large user access button
    - Management and labels quick access buttons
    - A settings button
    - Version information display

    The window uses custom styling defined in src.styles and creates buttons using
    the ButtonFactory to ensure consistent appearance across the application.

    Attributes:
        None

    Methods:
        _create_title(): Creates the welcome title section
        _create_button_frame(): Creates and configures the main button layout
        _create_version_label(): Adds version information to the window
    """

    def __init__(self):
        """
        Initialize the welcome window with all UI components.

        Sets up the window properties including title, size, and styling.
        Creates all UI components including title, buttons, and version label.
        Disables window resizing and removes maximize button while keeping minimize.
        """
        super().__init__()

        # Set app ID for Windows taskbar
        try:
            myappid = 'labelmaker.app.ver3.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            print(f"Warning: Could not set app ID: {e}")

        # Window setup
        self.title(WINDOW_CONFIG['title'])
        self.geometry(WINDOW_CONFIG['size'])
        self.resizable(False, False)

        # Set window icon
        try:
            icon_path = get_window_icon('png')
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                self.iconphoto(True, icon)
                self._icon = icon  # Keep reference to prevent garbage collection
        except Exception as e:
            print(f"Warning: Could not load window icon: {e}")

        # Configure window style
        self.configure(bg='white')
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Store initial state
        self.minimized = False
        self.exit_requested = False
        self.system_tray = None

        # Create UI components
        self._create_title()
        self._create_button_frame()
        self._create_version_label()

        # Initialize system tray icon
        try:
            self.system_tray = SystemTrayIcon(self)
        except Exception as e:
            print(f"Error initializing system tray: {e}")

        # Bind minimize event to the window itself
        self.bind("<Unmap>", self._on_minimize)

    def exit_application(self):
        """Properly cleanup and exit the application."""
        self._on_close()

    def _on_close(self):
        """Handle window close event."""
        if hasattr(self, 'system_tray') and self.system_tray:
            self.system_tray.destroy()
        self.quit()
        self.destroy()
        import sys
        sys.exit(0)

    def _on_minimize(self, event=None):
        """Handle window minimize event."""
        if not self.minimized and self.state() == 'iconic':
            self.minimized = True
            # Don't withdraw, just ensure tray icon is visible
            if self.system_tray:
                self.system_tray.visible = True
                self.system_tray._create_icon()

    def _show_window(self):
        """Show and focus the window."""
        self.minimized = False
        if self.state() == 'withdrawn':
            self.deiconify()
        self.state('normal')  # Ensure window is not minimized
        self.lift()
        self.focus_force()

    def _create_title(self):
        """
        Create and configure the title section of the window.

        Creates a frame containing two labels:
        - "Welcome" in bold Arial 16pt font
        - "Label Maker V3" in regular Arial 14pt font
        Both labels are displayed on white background with appropriate padding.
        """
        title_frame = tk.Frame(self, bg='white')
        title_frame.pack(pady=20)

        tk.Label(title_frame, text="UserName", font=("Arial", 16, "bold"), bg='white').pack()
        tk.Label(title_frame, text=WINDOW_CONFIG['title'], font=("Arial", 14), bg='white').pack()

    def _create_button_frame(self):
        """
        Create and configure the main button layout.

        Sets up a grid layout containing four buttons:
        - User button (large, spans 2 rows)
        - Management button
        - Labels button
        - Settings button (spans 2 columns)

        Each button is created using ButtonFactory with specific styling and
        grid configuration. The layout is designed to be visually balanced
        and user-friendly.
        """
        button_frame = tk.Frame(self, bg='white')
        button_frame.pack(expand=True, padx=20)

        # Configure grid layout
        button_frame.grid_columnconfigure(0, weight=3)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)
        button_frame.grid_rowconfigure(2, weight=1)

        # Create buttons using ButtonFactory
        buttons_config = [
            {
                'text': 'User',
                'color_key': 'user',
                'command': WelcomeWindowConfig.user_action,
                'big': True,
                'grid_config': {'row': 0, 'column': 0, 'rowspan': 2, 'padx': 15, 'pady': 10, 'sticky': "nsew"}
            },
            {
                'text': 'Management',
                'color_key': 'management',
                'command': WelcomeWindowConfig.management_action,
                'grid_config': {'row': 0, 'column': 1, 'padx': 10, 'pady': 5, 'sticky': "nsew"}
            },
            {
                'text': 'Labels',
                'color_key': 'labels',
                'command': WelcomeWindowConfig.labels_action,
                'grid_config': {'row': 1, 'column': 1, 'padx': (10, 10), 'pady': 5, 'sticky': "nsew"}
            },
            {
                'text': 'Settings',
                'color_key': 'settings',
                'command': WelcomeWindowConfig.settings_action,
                'grid_config': {'row': 2, 'column': 0, 'columnspan': 2, 'padx': 10, 'pady': 5, 'sticky': "ew"}
            }
        ]

        for btn_config in buttons_config:
            button = ButtonFactory.create_button(
                button_frame,
                btn_config['text'],
                btn_config['color_key'],
                btn_config['command'],
                btn_config.get('big', False)
            )
            button.grid(**btn_config['grid_config'])

    def _create_version_label(self):
        """
        Create and position the version label.

        Adds a small version label (Arial 8pt) at the bottom right of the window.
        The version number is pulled from WINDOW_CONFIG['version'].
        """
        version_label = tk.Label(
            self,
            text=WINDOW_CONFIG['version'],
            font=("Arial", 8),
            bg='white',
            fg='gray'
        )
        version_label.pack(side='bottom', anchor='se', padx=10, pady=5)

if __name__ == "__main__":
    app = WelcomeWindow()
    app.mainloop()
