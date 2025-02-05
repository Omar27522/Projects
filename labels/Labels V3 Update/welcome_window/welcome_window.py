import os
import sys
import tkinter as tk
from tkinter import ttk

# Add the current directory to Python path to allow importing
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Use absolute imports from src
from src.button_factory import ButtonFactory
from src.styles import WINDOW_CONFIG, COLORS
from src.config import WelcomeWindowConfig

class WelcomeWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title(WINDOW_CONFIG['title'])
        self.geometry(WINDOW_CONFIG['size'])
        self.resizable(False, False)
        
        # Configure window style
        self.configure(bg='white')
        
        # Remove maximize button but keep minimize
        self.attributes('-toolwindow', 1)
        self.attributes('-toolwindow', 0)
        
        # Create UI components
        self._create_title()
        self._create_button_frame()
        self._create_version_label()

    def _create_title(self):
        """Create title frame with welcome text"""
        title_frame = tk.Frame(self, bg='white')
        title_frame.pack(pady=20)
        
        tk.Label(title_frame, text="Welcome", font=("Arial", 16, "bold"), bg='white').pack()
        tk.Label(title_frame, text="Label Maker V3", font=("Arial", 14), bg='white').pack()

    def _create_button_frame(self):
        """Create and configure button frame"""
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
        """Create version label at bottom right"""
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
