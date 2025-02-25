import tkinter as tk
from tkinter import messagebox
import os
import time
from PIL import Image, ImageTk
import pyautogui
import re

class FileViewer:
    """Manages file viewing window and functionality"""
    def __init__(self, parent, config_manager, icon_manager):
        self.parent = parent
        self.config_manager = config_manager
        self.icon_manager = icon_manager
        self.file_window = None
        self.listbox = None
        self.last_print_time = None
        self.last_printed_upc = None
        self.is_auto_switch = tk.BooleanVar(value=True)
        self.is_mirror_print = tk.BooleanVar(value=self.config_manager.settings.mirror_print)

    def show(self):
        """View files in the current directory"""
        # If file window exists and is valid, focus it
        if self.file_window and self.file_window.winfo_exists():
            self.file_window.deiconify()  # Ensure window is not minimized
            self.file_window.lift()       # Bring to front
            self.file_window.focus_force() # Force focus
            return

        if not self.config_manager.settings.last_directory:
            messagebox.showinfo("Info", "Please select a directory first.")
            return

        self._create_file_window()

    def _create_file_window(self):
        """Create the file viewer window"""
        self.file_window = tk.Toplevel(self.parent)
        self.file_window.title("View Files")
        self.file_window.geometry("600x400")  # Default size
        self.file_window.minsize(375, 200)    # Minimum size
        
        # Add keyboard shortcuts
        self.file_window.bind('<Control-o>', lambda e: self.open_selected_file())
        self.file_window.bind('<Control-p>', lambda e: self.print_selected_file())
        
        # Enable window resizing
        self.file_window.resizable(True, True)
        
        # Set window icon
        self.icon_manager.set_window_icon(self.file_window, '32', 'viewfiles')
        
        self._create_main_content()

    def _create_main_content(self):
        """Create the main content of the file viewer"""
        main_content = tk.Frame(self.file_window)
        main_content.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self._create_top_frame(main_content)
        self._create_search_frame(main_content)
        self._create_list_frame(main_content)

    def _create_top_frame(self, parent):
        """Create top frame with control buttons"""
        top_frame = tk.Frame(parent)
        top_frame.pack(fill=tk.X, padx=0, pady=1)

        # Add control buttons
        self._create_control_buttons(top_frame)

    def _create_control_buttons(self, parent):
        """Create control buttons in the top frame"""
        # Pin button
        pin_btn = tk.Checkbutton(parent, text="Pin", variable=self.is_auto_switch,
                                font=('TkDefaultFont', 9))
        pin_btn.pack(side=tk.LEFT, padx=4)

        # Mirror print button
        mirror_btn = tk.Checkbutton(parent, text="Mirror Print", 
                                  variable=self.is_mirror_print,
                                  font=('TkDefaultFont', 9))
        mirror_btn.pack(side=tk.LEFT, padx=4)

    def _create_search_frame(self, parent):
        """Create search frame with search entry"""
        search_frame = tk.Frame(parent)
        search_frame.pack(fill=tk.X, padx=0, pady=6)

        tk.Label(search_frame, text="Find:", 
                font=('TkDefaultFont', 11, 'bold')).pack(side=tk.LEFT, padx=(4,2))
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                              font=('TkDefaultFont', 11))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, pady=6)
        
        # Bind search updates
        self.search_var.trace('w', self.update_file_list)
        search_entry.bind('<FocusIn>', self.select_all)
        search_entry.focus_set()

    def _create_list_frame(self, parent):
        """Create frame containing file list and preview"""
        list_frame = tk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=1)

        # Left side for file list
        left_frame = tk.Frame(list_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(left_frame, height=4, font=('TkDefaultFont', 9))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add scrollbars
        self._add_scrollbars(left_frame)

        # Right side for preview
        preview_frame = tk.Frame(list_frame, bg='white')
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.preview_label = tk.Label(preview_frame, bg='white')
        self.preview_label.pack(expand=True, fill=tk.BOTH)

        # Create bottom button frame
        self._create_bottom_frame(parent)

        # Initial file list update
        self.update_file_list()

    def update_file_list(self, *args):
        """Update the listbox based on search text"""
        search_text = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)
        
        try:
            files = os.listdir(self.config_manager.settings.last_directory)
            png_files = [f for f in files if f.lower().endswith('.png')]
            matched_files = []
            
            # Check if search is a 12-digit UPC
            is_upc_search = search_text.isdigit() and len(search_text) == 12
            
            # Split search into terms
            search_terms = [] if is_upc_search else search_text.split()
            
            for file in sorted(png_files):
                file_lower = file.lower()
                
                # UPC search takes precedence
                if is_upc_search:
                    if search_text in file_lower:
                        matched_files.append(file)
                # If no search terms, include all files
                elif not search_terms:
                    matched_files.append(file)
                # Check if ALL search terms are in the filename
                elif all(term in file_lower for term in search_terms):
                    matched_files.append(file)
            
            for file in matched_files:
                self.listbox.insert(tk.END, file)
                
            if len(matched_files) == 0:
                self._handle_no_matches(search_text, is_upc_search)
            else:
                self._handle_matches(len(matched_files))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read directory: {str(e)}")

    def open_selected_file(self):
        """Open the selected file"""
        selection = self.listbox.curselection()
        if not selection:
            return

        file_name = self.listbox.get(selection[0])
        if file_name == "No matching files found":
            return
            
        file_path = os.path.join(self.config_manager.settings.last_directory, file_name)
        os.startfile(file_path)

    def print_selected_file(self):
        """Print the selected file directly"""
        selection = self.listbox.curselection()
        if not selection:
            return

        file_name = self.listbox.get(selection[0])
        if file_name == "No matching files found":
            return
            
        file_path = os.path.join(self.config_manager.settings.last_directory, file_name)
        
        try:
            # Open the image
            img = Image.open(file_path)
            
            # Mirror the image if mirror print is enabled
            if self.is_mirror_print.get():
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            
            # Save a temporary copy
            temp_path = os.path.join(os.path.dirname(file_path), "_temp_print.png")
            img.save(temp_path)
            
            # Print the file
            os.startfile(temp_path, "print")
            
            # Update last print time and UPC
            self.last_print_time = time.time()
            # Extract UPC from filename (assuming it's a 12-digit number)
            upc_match = re.search(r'\d{12}', file_name)
            if upc_match:
                self.last_printed_upc = upc_match.group(0)
            
            # Clean up temp file after a delay
            self.file_window.after(5000, lambda: os.remove(temp_path) if os.path.exists(temp_path) else None)
            
        except Exception as e:
            messagebox.showerror("Print Error", f"Failed to print file: {str(e)}")

    def _handle_no_matches(self, search_text, is_upc_search):
        """Handle case when no files match the search"""
        self.listbox.insert(tk.END, "No matching files found")
        self.listbox.selection_clear(0, tk.END)
        self.listbox.select_set(0)
        self.listbox.see(0)
        
        # If it's a UPC search with no matches and auto-switch is enabled
        if is_upc_search and self.is_auto_switch.get():
            self.file_window.after(375, lambda: self._switch_to_main(search_text))

    def _handle_matches(self, count):
        """Handle case when files match the search"""
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(0)
        self.listbox.see(0)
        self._update_label_count(count)
        self.show_preview(None)

    def _switch_to_main(self, upc):
        """Switch back to main window with UPC"""
        self.file_window.destroy()
        self.file_window = None
        # Signal to main window to set UPC
        self.parent.event_generate('<<SetUPC>>', data=upc)

    def _update_label_count(self, count):
        """Update the label count display"""
        if hasattr(self, 'label_count_label'):
            self.label_count_label.config(
                text=f"Labels: {count}",
                fg='#2ecc71' if count > 0 else '#e74c3c'
            )

    def _add_scrollbars(self, parent):
        """Add scrollbars to the listbox"""
        scrollbar = tk.Scrollbar(parent)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

    def _create_bottom_frame(self, parent):
        """Create the bottom frame with buttons"""
        bottom_frame = tk.Frame(parent)
        bottom_frame.pack(fill=tk.X, padx=0, pady=1)

        # Open button
        open_btn = tk.Button(bottom_frame, text="Open", 
                             command=self.open_selected_file,
                             font=('TkDefaultFont', 9))
        open_btn.pack(side=tk.LEFT, padx=4)

        # Print button
        print_btn = tk.Button(bottom_frame, text="Print", 
                              command=self.print_selected_file,
                              font=('TkDefaultFont', 9))
        print_btn.pack(side=tk.LEFT, padx=4)

    def select_all(self, event):
        """Select all text in the search entry"""
        event.widget.select_range(0, tk.END)
        event.widget.icursor(tk.END)
