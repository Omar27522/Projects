import tkinter as tk

class UndoRedoManager:
    """A class for managing undo/redo functionality for entry widgets"""
    def __init__(self):
        self.undo_stacks = {}
        self.redo_stacks = {}

    def add_undo_support(self, entry, var):
        """Add undo/redo support to an entry widget"""
        # Initialize stacks for this entry
        self.undo_stacks[entry] = []
        self.redo_stacks[entry] = []
        
        def on_change(*args):
            current_value = var.get()
            # Only add to undo stack if the value actually changed
            if self.undo_stacks[entry] and self.undo_stacks[entry][-1] == current_value:
                return
            self.undo_stacks[entry].append(current_value)
            # Clear redo stack when new change is made
            self.redo_stacks[entry].clear()
        
        def undo(event):
            if len(self.undo_stacks[entry]) > 1:  # Keep the last state
                # Move current state to redo stack
                self.redo_stacks[entry].append(self.undo_stacks[entry].pop())
                # Restore previous state
                var.set(self.undo_stacks[entry][-1])
            return "break"
        
        def redo(event):
            if self.redo_stacks[entry]:
                # Get the state to redo
                value = self.redo_stacks[entry].pop()
                # Add it to undo stack
                self.undo_stacks[entry].append(value)
                # Restore the state
                var.set(value)
            return "break"
        
        def delete_word_before(event):
            # Get current cursor position
            cursor_pos = entry.index(tk.INSERT)
            # Get current text
            text = var.get()
            if cursor_pos == 0 or not text:  # Nothing to delete
                return "break"
            
            # Find the start of the word before cursor
            i = cursor_pos - 1
            # Skip spaces immediately before cursor
            while i >= 0 and text[i].isspace():
                i -= 1
            # Find start of word
            while i >= 0 and not text[i].isspace():
                i -= 1
            
            # Adjust index to keep the space before the word
            i += 1
                
            # Delete from start of word to cursor
            new_text = text[:i] + text[cursor_pos:]
            var.set(new_text)
            # Move cursor to deletion point
            entry.icursor(i)
            return "break"
            
        # Track changes
        var.trace_add('write', on_change)
        # Add initial state
        self.undo_stacks[entry].append(var.get())
        
        # Bind keyboard shortcuts
        entry.bind('<Control-z>', undo)
        entry.bind('<Control-y>', redo)
        entry.bind('<Control-BackSpace>', delete_word_before)
