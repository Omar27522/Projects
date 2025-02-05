"""
Button Factory for creating dynamic, styled buttons with hover effects.
Separates button creation logic from the main window class.
"""

import tkinter as tk
from typing import Callable, Tuple

from .styles import COLORS, BUTTON_STYLES

class ButtonFactory:
    @staticmethod
    def create_button(
        parent: tk.Frame, 
        text: str, 
        color_key: str, 
        command: Callable[[], None], 
        big: bool = False
    ) -> tk.Button:
        """
        Create a styled button with hover effects.
        
        Args:
            parent (tk.Frame): Parent widget
            text (str): Button text
            color_key (str): Key for color palette
            command (Callable): Function to call on button press
            big (bool, optional): Whether to use large button style. Defaults to False.
        
        Returns:
            tk.Button: Configured button with hover effects
        """
        colors = COLORS.get(color_key, COLORS['settings'])
        color, light_color = colors['primary'], colors['secondary']
        
        btn = tk.Button(
            parent, 
            text=text,
            font=(
                BUTTON_STYLES['font']['family'], 
                BUTTON_STYLES['font']['sizes']['large'] if big else BUTTON_STYLES['font']['sizes']['normal'], 
                'bold' if big else 'normal'
            ),
            fg='white',
            bg=color,
            activeforeground='black',
            activebackground='white',
            relief='flat',
            borderwidth=0,
            width=BUTTON_STYLES['width']['large'] if big else BUTTON_STYLES['width']['normal'],
            height=BUTTON_STYLES['height']['large'] if big else BUTTON_STYLES['height']['normal'],
            cursor='hand2',
            command=command
        )
        
        # Hover effect management
        def apply_hover():
            btn['bg'] = light_color
            btn['fg'] = 'black'
        
        def remove_hover():
            btn['bg'] = color
            btn['fg'] = 'white'
        
        hover_timer = None
        
        def on_enter(e):
            nonlocal hover_timer
            if hover_timer is not None:
                btn.after_cancel(hover_timer)
            hover_timer = btn.after(25, apply_hover)
        
        def on_leave(e):
            nonlocal hover_timer
            if hover_timer is not None:
                btn.after_cancel(hover_timer)
                hover_timer = None
            remove_hover()
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
