"""
Frame for displaying and managing the list of files.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import logging
import sys
from pathlib import Path

# Add parent directory to Python path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from config import SUPPORTED_EXTENSIONS, THEME

class FileListFrame(ttk.Frame):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        
        # Initialize variables
        self.current_directory = None
        self.files = []
        
        self.create_widgets()
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Load files immediately
        self.load_directory()
        
    def create_widgets(self):
        """Create and arrange widgets in the frame."""
        # Create search frame
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add load directory button
        load_dir_btn = ttk.Button(
            search_frame,
            text="📁 Load Directory",
            command=self.load_directory,
            style='Action.TButton'
        )
        load_dir_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Create file list frame
        list_frame = ttk.LabelFrame(self, text="Label Files",
                                 style='FileList.TLabelframe')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create scrollbar and listbox
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            selectmode=tk.EXTENDED,
            bg=THEME['background_color'],
            fg=THEME['header_foreground'],
            font=('TkDefaultFont', 10)
        )
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Bind selection event
        self.file_listbox.bind('<<ListboxSelect>>', self.on_select)
        
        # Create action buttons
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        refresh_btn = ttk.Button(
            button_frame,
            text="🔄 Refresh",
            command=self.refresh_files,
            style='Action.TButton'
        )
        refresh_btn.pack(side=tk.LEFT, padx=2)
        
        # Add debug button
        self.debug_btn = ttk.Button(
            button_frame,
            text="Debug Info",
            command=self.show_debug_info
        )
        self.debug_btn.pack(side=tk.LEFT, padx=2)
        
    def load_directory(self):
        """Open directory dialog and load label files."""
        directory = r"C:\Users\Justin\Documents\Labels"
        print(f"\nTrying to load directory: {directory}")
        
        if os.path.exists(directory):
            print(f"Directory exists")
            self.current_directory = directory
            self.load_files_from_directory(directory)
        else:
            print(f"Directory not found!")
            messagebox.showerror("Error", "Labels directory not found!")
            
    def load_files_from_directory(self, directory):
        """Load all label files from the selected directory."""
        try:
            print("\n=== Starting file load ===")
            print(f"Loading files from: {directory}")
            
            # Clear current list
            print("Clearing listbox...")
            self.file_listbox.delete(0, tk.END)
            self.files.clear()
            
            # Get all PNG files in directory
            print("Reading directory...")
            all_files = os.listdir(directory)
            print(f"Found {len(all_files)} total files")
            
            # Filter and sort PNG files
            print("Filtering PNG files...")
            files = [f for f in all_files if f.lower().endswith('.png')]
            files.sort()
            
            print(f"Found {len(files)} PNG files")
            if files:
                print(f"First 5 PNG files: {files[:5]}")
            
            # Add to listbox and internal list
            print("\nAdding files to listbox...")
            for i, file in enumerate(files):
                self.file_listbox.insert(tk.END, file)
                self.files.append(os.path.join(directory, file))
                if i < 5:
                    print(f"Added: {file}")
                
            print(f"\nFinal stats:")
            print(f"- Files list size: {len(self.files)}")
            print(f"- Listbox size: {self.file_listbox.size()}")
            print(f"- Listbox visible: {self.file_listbox.winfo_ismapped()}")
            print(f"- Listbox width: {self.file_listbox.winfo_width()}")
            print(f"- Listbox height: {self.file_listbox.winfo_height()}")
            
            # Update status and force refresh
            self.main_window.set_status(f"Loaded {len(files)} PNG files from {directory}")
            
            # Force a refresh of the listbox
            self.file_listbox.update_idletasks()
            self.update_idletasks()
            self.file_listbox.see(0)  # Scroll to top
            
            print("=== File load complete ===\n")
            
        except Exception as e:
            print(f"Error loading files: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback:\n{traceback.format_exc()}")
            messagebox.showerror("Error", f"Failed to load directory: {str(e)}")
            
    def refresh_files(self):
        """Refresh the file list."""
        if self.current_directory:
            self.load_files_from_directory(self.current_directory)
            
    def show_debug_info(self):
        """Show debug information."""
        info = f"""Debug Information:
Current Directory: {self.current_directory}
Number of Files: {len(self.files)}
Listbox Size: {self.file_listbox.size()}
Listbox Visible: {self.file_listbox.winfo_ismapped()}
Listbox Width: {self.file_listbox.winfo_width()}
Listbox Height: {self.file_listbox.winfo_height()}
"""
        messagebox.showinfo("Debug Info", info)
        
    def on_select(self, event):
        """Handle file selection."""
        if not self.file_listbox.curselection():
            return
            
        selected_index = self.file_listbox.curselection()[0]
        selected_file = self.files[selected_index]
        print(f"Selected file: {selected_file}")
        
    def cleanup(self):
        """Clean up resources."""
        self.files.clear()
