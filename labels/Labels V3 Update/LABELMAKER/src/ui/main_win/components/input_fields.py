import tkinter as tk
import re

class InputFieldManager:
    """Manages input field creation and validation"""
    def __init__(self, root, variable_manager):
        self.root = root
        self.variable_manager = variable_manager
        self.inputs = {}
        self.always_on_top = None  # Will be set by the main window

    def create_input_fields(self, parent):
        """Create input fields"""
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, padx=5, pady=5)

        # Create input fields with labels
        fields = [
            ('Name Line 1:', 'name_line1', None),
            ('Name Line 2:', 'name_line2', None),
            ('Variant:', 'variant', self.validate_variant),
            ('UPC Code:', 'upc_code', self.validate_upc)
        ]

        for label_text, var_name, validator in fields:
            label = tk.Label(frame, text=label_text)
            label.pack(fill=tk.X, padx=2, pady=(5,0))

            var = self.variable_manager.input_vars[var_name]
            entry = tk.Entry(frame, textvariable=var)
            
            if validator:
                vcmd = (frame.register(validator), '%d', '%P')
                entry.config(validate='key', validatecommand=vcmd)

            entry.pack(fill=tk.X, padx=2, pady=(0,5))
            
            # Add undo/redo support
            self._add_undo_support(entry, var)
            
            # Bind focus events
            entry.bind('<FocusIn>', self.on_input_focus)
            entry.bind('<Button-1>', self.on_input_click)
            
            # Add context menu
            self._add_context_menu(entry)
            
            # Store reference to input
            self.inputs[var_name] = entry

        return frame

    def validate_upc(self, action, value_if_allowed):
        """Only allow integers in UPC field and ensure exactly 12 digits"""
        if action == '0':  # This is a deletion
            return True
            
        if not value_if_allowed:  # Field is empty
            return True
            
        if not value_if_allowed.isdigit():  # Contains non-digits
            return False
            
        return len(value_if_allowed) <= 12  # Limit to 12 digits

    def validate_variant(self, action, value_if_allowed):
        """Prevent numbers at the start of variant field"""
        if action == '0':  # This is a deletion
            return True
            
        if not value_if_allowed:  # Field is empty
            return True
            
        # Check if the first character is a number
        if value_if_allowed[0].isdigit():
            return False
            
        return True

    def on_input_focus(self, event):
        """Enable Always on Top when user focuses on any input field"""
        if self.always_on_top is not None:
            self.always_on_top.set(True)
            self.root.attributes('-topmost', True)

    def on_input_click(self, event):
        """Handle mouse click in input field"""
        event.widget.select_range(0, tk.END)
        return "break"

    def _add_undo_support(self, entry, var):
        """Add undo/redo support to an entry widget"""
        undo_stack = []
        redo_stack = []
        old_value = var.get()

        def on_change(*args):
            nonlocal old_value
            new_value = var.get()
            if new_value != old_value:
                undo_stack.append(old_value)
                redo_stack.clear()
                old_value = new_value

        def undo(event):
            if undo_stack:
                current = var.get()
                redo_stack.append(current)
                var.set(undo_stack.pop())
            return "break"

        def redo(event):
            if redo_stack:
                current = var.get()
                undo_stack.append(current)
                var.set(redo_stack.pop())
            return "break"

        def delete_word_before(event):
            """Delete the word before the cursor"""
            text = entry.get()
            end = entry.index(tk.INSERT)
            
            # Find the start of the current word
            start = end - 1
            while start >= 0 and not text[start].isspace():
                start -= 1
            start += 1
            
            entry.delete(start, end)
            return "break"

        var.trace('w', on_change)
        entry.bind('<Control-z>', undo)
        entry.bind('<Control-y>', redo)
        entry.bind('<Control-BackSpace>', delete_word_before)

        # Store the stacks
        self.variable_manager.undo_stacks[entry] = undo_stack
        self.variable_manager.redo_stacks[entry] = redo_stack

    def _add_context_menu(self, widget):
        """Add right-click context menu to widget"""
        menu = tk.Menu(widget, tearoff=0)
        menu.add_command(label="Cut", command=lambda: widget.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: widget.event_generate("<<Paste>>"))
        menu.add_separator()
        menu.add_command(label="Select All", command=lambda: widget.select_range(0, tk.END))

        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)
            return "break"

        widget.bind('<Button-3>', show_menu)
