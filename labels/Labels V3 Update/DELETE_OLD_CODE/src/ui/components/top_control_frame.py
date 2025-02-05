import tkinter as tk
from ..utils.ui_helpers import create_styled_button

class TopControlFrame(tk.Frame):
    """Frame containing top control buttons (Always on Top, Labels Count)"""

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        
        self.png_count = tk.StringVar(value=f"Labels: {self.master.config_manager.settings.label_counter}")
        
        self._create_widgets()
        self._layout_widgets()
        
    def _create_widgets(self):
        """Create top control widgets"""
        # Create Always on Top button
        self.always_on_top_btn = create_styled_button(
            self,
            text="Always on Top",
            command=self.master.toggle_always_on_top,
            width=12,
            tooltip_text="Toggle window always on top"
        )
        self.always_on_top_btn.config(
            bg='#e74c3c',  # Red
            activebackground='#c0392b'
        )

        # Create Labels Count label
        self.png_count_label = tk.Label(
            self,
            textvariable=self.png_count,
            bg='SystemButtonFace',
            font=('TkDefaultFont', 10)
        )

    def _layout_widgets(self):
        """Layout top control widgets"""
        self.always_on_top_btn.pack(side=tk.LEFT, padx=5)
        self.png_count_label.pack(side=tk.RIGHT, padx=5)

    def update_label_count(self):
        """Update the label counter display"""
        self.png_count.set(f"Labels: {self.master.config_manager.settings.label_counter}")
