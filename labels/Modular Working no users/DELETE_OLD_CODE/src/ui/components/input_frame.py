import tkinter as tk
from ..utils.ui_helpers import add_context_menu

class InputFrame(tk.Frame):
    """Frame containing input fields for label data"""

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.inputs = {}
        
        self._create_input_fields()
        
    def _create_input_fields(self):
        """Create input fields"""
        labels = [
            ("Product Name Line 1:", "name_line1"),
            ("Product Name Line 2:", "name_line2"),
            ("Variant:", "variant"),
            ("UPC Code:", "upc_code")
        ]

        def validate_upc(action, value_if_allowed):
            """Only allow integers in UPC field and ensure exactly 12 digits"""
            if action == '0':  # Delete
                return True
            if len(value_if_allowed) > 12:
                return False
            return value_if_allowed.isdigit()

        def validate_variant(action, value_if_allowed):
            """Prevent numbers at the start of variant field"""
            if action == '0':  # Delete
                return True
            if not value_if_allowed:  # Empty is ok
                return True
            return not value_if_allowed[0].isdigit()

        def on_input_focus(event):
            """Enable Always on Top when user focuses on any input field"""
            self.master.always_on_top.set(True)
            self.master.toggle_always_on_top()

        def on_input_click(event):
            """Handle mouse click in input field"""
            event.widget.select_range(0, tk.END)
            event.widget.icursor(tk.END)

        for idx, (label_text, key) in enumerate(labels):
            # Label
            label = tk.Label(
                self,
                text=label_text,
                anchor="e",
                width=20,
                bg='SystemButtonFace'
            )
            label.grid(row=idx+2, column=0, padx=5, pady=3, sticky="e")

            # Entry
            if key == "upc_code":
                vcmd = (self.register(validate_upc), '%d', '%P')
                entry = tk.Entry(
                    self,
                    width=25,
                    relief='sunken',
                    bg='white',
                    validate='key',
                    validatecommand=vcmd
                )
            elif key == "variant":
                vcmd = (self.register(validate_variant), '%d', '%P')
                entry = tk.Entry(
                    self,
                    width=25,
                    relief='sunken',
                    bg='white',
                    validate='key',
                    validatecommand=vcmd
                )
            else:
                entry = tk.Entry(
                    self,
                    width=25,
                    relief='sunken',
                    bg='white'
                )

            # Bind events
            entry.bind("<FocusIn>", on_input_focus)
            entry.bind("<Button-1>", on_input_click)

            # Add context menu
            add_context_menu(entry)

            entry.grid(row=idx+2, column=1, padx=5, pady=3, sticky="w")
            self.inputs[key] = entry

    def get_values(self):
        """Get current values from all input fields"""
        return {
            key: entry.get().strip()
            for key, entry in self.inputs.items()
        }

    def clear_inputs(self):
        """Clear all input fields"""
        for entry in self.inputs.values():
            entry.delete(0, tk.END)

    def focus_first(self):
        """Focus on the first input field"""
        self.inputs["name_line1"].focus_set()

    def set_values(self, values):
        """Set values for input fields"""
        for key, value in values.items():
            if key in self.inputs:
                self.inputs[key].delete(0, tk.END)
                self.inputs[key].insert(0, value)
