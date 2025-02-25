import tkinter as tk
from ..components.tooltip import ToolTip

class ButtonManager:
    """Manages button creation and styling"""
    def __init__(self, root):
        self.root = root

    def create_styled_button(self, parent, text, command, width=8, has_icon=False, icon=None, tooltip_text="", color_scheme=None):
        """Create a styled button with hover effect"""
        if color_scheme is None:
            color_scheme = {
                'bg': '#f0f0f0',
                'activebackground': '#e0e0e0',
                'hoverbg': '#e5e5e5'
            }

        button = tk.Button(parent, text=text, command=command,
                          width=width, relief='raised',
                          bg=color_scheme['bg'],
                          activebackground=color_scheme['activebackground'])

        if has_icon and icon:
            button.config(image=icon, compound='left')

        def on_enter(e):
            if not button['state'] == 'disabled':
                button['background'] = color_scheme['hoverbg']

        def on_leave(e):
            if not button['state'] == 'disabled':
                button['background'] = color_scheme['bg']

        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)

        if tooltip_text:
            ToolTip(button, tooltip_text)

        return button

    def create_top_control_frame(self, parent, commands):
        """Create top control frame with Always on Top, Settings, and Labels Count buttons"""
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, padx=2, pady=2)

        # Always on Top button
        self.create_styled_button(frame, "📌 Pin", commands['toggle_always_on_top'],
                                tooltip_text="Toggle Always on Top",
                                color_scheme={'bg': '#e3f2fd', 'activebackground': '#bbdefb', 'hoverbg': '#90caf9'})

        # Settings button
        self.create_styled_button(frame, "⚙️ Settings", commands['show_settings'],
                                tooltip_text="Open Settings",
                                color_scheme={'bg': '#f5f5f5', 'activebackground': '#e0e0e0', 'hoverbg': '#bdbdbd'})

        return frame

    def create_control_frame(self, parent, commands):
        """Create control buttons frame (Reset)"""
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, padx=2, pady=2)

        # Reset button
        self.create_styled_button(frame, "🔄 Reset", commands['clear_inputs'],
                                tooltip_text="Clear all fields",
                                color_scheme={'bg': '#ffebee', 'activebackground': '#ffcdd2', 'hoverbg': '#ef9a9a'})

        return frame
