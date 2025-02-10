import tkinter as tk

def create_styled_button(parent, text, command, width=8, has_icon=False, icon=None, tooltip_text="", color_scheme=None):
    """Create a styled button with hover effect"""
    if color_scheme is None:
        color_scheme = {
            'bg': '#3498db',  # Default blue
            'fg': 'white',
            'hover_bg': '#2980b9',
            'active_bg': '#2473a6'
        }

    button = tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        bg=color_scheme['bg'],
        fg=color_scheme['fg'],
        activebackground=color_scheme['active_bg'],
        activeforeground=color_scheme['fg'],
        relief='raised',
        bd=0,
        padx=10,
        pady=5,
        font=('TkDefaultFont', 10, 'bold')
    )

    def on_enter(e):
        if not getattr(button, 'is_active', False):
            button.config(bg=color_scheme['hover_bg'])

    def on_leave(e):
        if not getattr(button, 'is_active', False):
            button.config(bg=color_scheme['bg'])

    button.bind('<Enter>', on_enter)
    button.bind('<Leave>', on_leave)

    if has_icon and icon:
        button.config(image=icon, compound=tk.LEFT)

    if tooltip_text:
        create_tooltip(button, tooltip_text)

    return button

def create_tooltip(widget, text):
    """Create a tooltip for a widget"""
    def enter(event=None):
        widget.tooltip = tk.Toplevel()
        widget.tooltip.wm_overrideredirect(True)
        widget.tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

        label = tk.Label(
            widget.tooltip,
            text=text,
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("TkDefaultFont", "8", "normal")
        )
        label.pack()

    def leave(event=None):
        if hasattr(widget, 'tooltip'):
            widget.tooltip.destroy()
            widget.tooltip = None

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)
    widget.bind('<ButtonPress>', leave)

def add_context_menu(widget):
    """Add right-click context menu to widget"""
    menu = tk.Menu(widget, tearoff=0)
    menu.add_command(label="Copy",
                    command=lambda: widget.event_generate('<<Copy>>'))
    menu.add_command(label="Paste",
                    command=lambda: widget.event_generate('<<Paste>>'))
    menu.add_command(label="Cut",
                    command=lambda: widget.event_generate('<<Cut>>'))
    menu.add_separator()
    menu.add_command(label="Select All",
                    command=lambda: widget.select_range(0, tk.END))

    widget.bind("<Button-3>",
               lambda e: menu.tk_popup(e.x_root, e.y_root))
