"""
GUI frames for the Label Manager application.
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import shutil
from PIL import Image, ImageTk
import re
from datetime import datetime
import logging
import json
from functools import lru_cache
import difflib
import pytesseract
import hashlib
import subprocess
from config import THEME, SUPPORTED_EXTENSIONS, CONFIG_FILE, DEFAULT_LABELS_DIR
from src.local.repository import LocalRepository
from pathlib import Path

class HeaderFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()
        
    def create_widgets(self):
        """Create and arrange widgets in the frame."""
        # Create title label
        self.title_label = ttk.Label(
            self,
            text="Label Manager",
            style='Header.TLabel',
            font=('Helvetica', 16, 'bold')
        )
        self.title_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Create file count label
        self.count_label = ttk.Label(
            self,
            text="",
            style='Count.TLabel',
            font=('Helvetica', 12)
        )
        self.count_label.pack(side=tk.LEFT, padx=5, pady=5)
        
    def update_file_count(self, count):
        """Update the file count display."""
        self.count_label.config(text=f"({count:,} files)")

class FileListFrame(ttk.Frame):
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.main_window = main_window
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Initialize variables
        self.current_directory = None
        self.files = []
        self.filtered_files = []  # Store filtered results
        self.last_search = ""
        self.matching_count = 0  # Store count of matching files
        
        # Load last directory from config
        self.load_config()
        
        self.create_widgets()
        
        # Load files immediately
        self.load_directory(initial_load=True)
        
    def load_config(self):
        """Load configuration including last used directory."""
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.current_directory = config.get('last_directory', DEFAULT_LABELS_DIR)
            else:
                self.current_directory = DEFAULT_LABELS_DIR
        except Exception as e:
            print(f"Error loading config: {e}")
            self.current_directory = DEFAULT_LABELS_DIR
            
    def save_config(self):
        """Save configuration including last used directory."""
        try:
            config = {'last_directory': self.current_directory} if self.current_directory else {}
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving config: {e}")
        
    def load_directory(self, initial_load=False):
        """Open directory dialog and load label files."""
        try:
            if not initial_load:
                # Ask user for directory
                directory = filedialog.askdirectory(
                    title="Select Labels Directory",
                    initialdir=self.current_directory or DEFAULT_LABELS_DIR
                )
                
                if not directory:  # User cancelled
                    return
            else:
                directory = self.current_directory or DEFAULT_LABELS_DIR
                
            print(f"\nTrying to load directory: {directory}")
            
            if os.path.exists(directory):
                print(f"Directory exists")
                self.current_directory = directory
                self.load_files_from_directory(directory)
                self.save_config()  # Save the last used directory
            else:
                print(f"Directory not found!")
                messagebox.showerror("Error", "Selected directory not found!")
                
        except Exception as e:
            print(f"Error selecting directory: {str(e)}")
            messagebox.showerror("Error", f"Failed to load directory: {str(e)}")
            
    def create_widgets(self):
        """Create and arrange widgets in the frame."""
        # Create search frame
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create search label
        search_label = ttk.Label(
            search_frame,
            text="🔍",
            style='Search.TLabel'
        )
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Create search entry
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self.on_search_change)
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            style='Search.TEntry'
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Create clear search button
        self.clear_btn = ttk.Button(
            search_frame,
            text="✖",
            command=self.clear_search,
            style='Clear.TButton',
            width=3
        )
        self.clear_btn.pack(side=tk.LEFT, padx=(5, 0))
        self.clear_btn.pack_forget()  # Hide initially
        
        # Create buttons frame
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Load directory button
        load_btn = ttk.Button(
            buttons_frame,
            text="📁 Load Directory",
            command=self.load_directory,
            style='Action.TButton'
        )
        load_btn.pack(side=tk.LEFT, padx=2)
        
        # Refresh button
        refresh_btn = ttk.Button(
            buttons_frame,
            text="🔄 Refresh",
            command=lambda: self.load_files_from_directory(self.current_directory),
            style='Action.TButton'
        )
        refresh_btn.pack(side=tk.LEFT, padx=2)
        
        # Rename button
        rename_btn = ttk.Button(
            buttons_frame,
            text="✏️ Rename",
            command=self.rename_files,
            style='Action.TButton'
        )
        rename_btn.pack(side=tk.LEFT, padx=2)
        
        # Delete button
        delete_btn = ttk.Button(
            buttons_frame,
            text="🗑️ Delete",
            command=self.delete_selected,
            style='Action.TButton'
        )
        delete_btn.pack(side=tk.LEFT, padx=2)
        
        # Cleanup button
        cleanup_btn = ttk.Button(
            buttons_frame,
            text="🧹 Cleanup",
            command=self.cleanup_files,
            style='Action.TButton'
        )
        cleanup_btn.pack(side=tk.LEFT, padx=2)
        
        # Print button
        print_btn = ttk.Button(
            buttons_frame,
            text="🖨️ Print",
            command=self.print_selected,
            style='Action.TButton'
        )
        print_btn.pack(side=tk.LEFT, padx=2)
        
        # Create listbox with scrollbar
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
            bg=THEME['listbox_background'],
            fg=THEME['listbox_foreground'],
            selectbackground=THEME['listbox_selected_background'],
            selectforeground=THEME['listbox_selected_foreground'],
            font=('TkDefaultFont', THEME['listbox_font_size']),
            activestyle='none',  # Remove dotted line around selected item
            highlightthickness=1,  # Add border
            highlightcolor=THEME['listbox_selected_background'],
            relief=tk.SOLID  # Add solid border
        )
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Bind selection event and keyboard shortcuts
        self.file_listbox.bind('<<ListboxSelect>>', self.on_select)
        self.file_listbox.bind('<Delete>', lambda e: self.delete_selected())
        
        # Create action buttons
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
    @lru_cache(maxsize=1000)
    def calculate_similarity(self, str1, str2):
        """Calculate similarity between two strings."""
        return difflib.SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    def fuzzy_search(self, query, text):
        """Perform fuzzy search with multiple improvements."""
        if not query:
            return True, 0
            
        query = query.lower()
        text = text.lower()
        
        # If query looks like a UPC (12-13 digits), do exact matching only
        if re.match(r'^\d{12,13}$', query):
            return query in text, 1.0 if query in text else 0
            
        # Exact match
        if query in text:
            return True, 1.0
            
        # Split into words for partial matching
        query_words = query.split()
        text_words = text.split()
        
        # Check if all query words match partially
        matches = []
        for q_word in query_words:
            # If this word is a number sequence, require exact match
            if q_word.isdigit() and len(q_word) > 3:
                if q_word not in text:
                    return False, 0
                matches.append(1.0)
                continue
                
            word_matches = []
            for t_word in text_words:
                # Calculate similarity
                similarity = self.calculate_similarity(q_word, t_word)
                if similarity > 0.6:  # Threshold for fuzzy matching
                    word_matches.append(similarity)
            if word_matches:
                matches.append(max(word_matches))
            else:
                return False, 0
                
        # Return average similarity of best matches
        return True, sum(matches) / len(matches)

    def filter_files(self, search_text):
        """Filter files based on search text."""
        if not search_text:
            self.filtered_files = self.files.copy()
            self.matching_count = len(self.files)
            return
            
        # Store results with their scores
        results = []
        for file_path in self.files:
            filename = os.path.basename(file_path)
            matched, score = self.fuzzy_search(search_text, filename)
            if matched:
                results.append((file_path, score))
        
        # Sort by score in descending order
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Only keep matching files
        self.filtered_files = [r[0] for r in results]
        self.matching_count = len(self.filtered_files)

    def update_listbox(self):
        """Update listbox with current filtered files."""
        self.file_listbox.delete(0, tk.END)
        
        search_text = self.search_var.get()
        
        if not self.filtered_files and search_text:
            # Show "No matches found" message
            self.file_listbox.insert(tk.END, f"No matches found for '{search_text}'")
            self.file_listbox.itemconfig(0, {'fg': THEME['error_color']})
            return
            
        # Show result count if searching
        header_rows = 0
        if search_text:
            # Add header
            self.file_listbox.insert(tk.END, f"Found {len(self.filtered_files)} matches")
            self.file_listbox.itemconfig(header_rows, {'fg': THEME['success_color']})
            header_rows += 1
            
            # Add separator
            self.file_listbox.insert(tk.END, "─" * 50)
            self.file_listbox.itemconfig(header_rows, {'fg': THEME['warning_color']})
            header_rows += 1
        
        # Add all matching files
        for i, file_path in enumerate(self.filtered_files):
            filename = os.path.basename(file_path)
            self.file_listbox.insert(tk.END, filename)
            
            # Highlight matching parts if searching
            if search_text:
                self.highlight_matches(self.file_listbox.size() - 1)
        
        # Auto-select first result if there are any matches
        if self.filtered_files:
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(header_rows)  # Select first file after headers
            self.file_listbox.see(header_rows)
            self.on_select(None)  # Trigger preview update

    def highlight_matches(self, index):
        """Highlight matching parts of the filename."""
        filename = self.file_listbox.get(index)
        search_text = self.search_var.get().lower()
        
        if not search_text:
            return
            
        # Find all matching positions
        pos = 0
        while True:
            pos = filename.lower().find(search_text, pos)
            if pos == -1:
                break
            self.file_listbox.itemconfig(
                index,
                fg=THEME['success_color'],
                selectforeground=THEME['listbox_selected_foreground']
            )
            pos += 1

    def on_search_change(self, *args):
        """Handle search text changes."""
        search_text = self.search_var.get()
        
        # Show/hide clear button
        if search_text:
            self.clear_btn.pack(side=tk.LEFT, padx=(5, 0))
        else:
            self.clear_btn.pack_forget()
        
        # Update results
        self.filter_files(search_text)
        self.update_listbox()

    def clear_search(self):
        """Clear search field."""
        self.search_var.set("")
        
    def load_files_from_directory(self, directory):
        """Load all label files from the selected directory."""
        try:
            if not os.path.exists(directory):
                raise FileNotFoundError(f"Directory not found: {directory}")
                
            # Get all PNG files
            self.files = []
            for filename in os.listdir(directory):
                if filename.lower().endswith('.png'):
                    self.files.append(os.path.join(directory, filename))
                    
            # Sort files by name
            self.files.sort(key=lambda x: os.path.basename(x).lower())
            
            # Update filtered files and listbox
            self.filter_files(self.search_var.get())
            self.update_listbox()
            
            # Update header count
            if hasattr(self.main_window, 'header_frame'):
                self.main_window.header_frame.update_file_count(len(self.files))
            
            print(f"\nLoaded {len(self.files)} files from {directory}")
            
        except Exception as e:
            print(f"Error loading files: {e}")
            messagebox.showerror("Error", f"Failed to load files: {str(e)}")
            
    def refresh_files(self):
        """Refresh the file list."""
        if self.current_directory:
            self.load_files_from_directory(self.current_directory)
            
    def cleanup_files(self):
        """Clean up label files by organizing and removing duplicates."""
        try:
            if not self.current_directory:
                messagebox.showinfo("Info", "Please select a directory first")
                return
                
            # Count files before cleanup
            before_count = len([f for f in os.listdir(self.current_directory) 
                             if f.lower().endswith('.png')])
                
            # Find duplicate files
            files_by_content = {}
            duplicates = []
            
            print("\nScanning for duplicates...")
            for filename in os.listdir(self.current_directory):
                if not filename.lower().endswith('.png'):
                    continue
                    
                filepath = os.path.join(self.current_directory, filename)
                try:
                    # Calculate file hash
                    with open(filepath, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        
                    if file_hash in files_by_content:
                        duplicates.append((filename, files_by_content[file_hash]))
                    else:
                        files_by_content[file_hash] = filename
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
            
            # Create duplicates directory if needed
            duplicates_dir = os.path.join(self.current_directory, "duplicates")
            if duplicates and not os.path.exists(duplicates_dir):
                os.makedirs(duplicates_dir)
            
            # Move duplicates
            moved_count = 0
            for dup_file, original_file in duplicates:
                try:
                    dup_path = os.path.join(self.current_directory, dup_file)
                    new_path = os.path.join(duplicates_dir, dup_file)
                    os.rename(dup_path, new_path)
                    moved_count += 1
                except Exception as e:
                    print(f"Error moving {dup_file}: {e}")
            
            # Count files after cleanup
            after_count = len([f for f in os.listdir(self.current_directory) 
                             if f.lower().endswith('.png')])
            
            # Show results
            message = f"Cleanup complete!\n\n"
            message += f"Before: {before_count} files\n"
            message += f"After: {after_count} files\n"
            message += f"Duplicates moved: {moved_count}\n\n"
            
            if moved_count > 0:
                message += f"Duplicates have been moved to:\n{duplicates_dir}"
            else:
                message += "No duplicates found!"
                
            messagebox.showinfo("Cleanup Results", message)
            
            # Refresh the file list
            self.load_files_from_directory(self.current_directory)
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            messagebox.showerror("Error", f"Cleanup failed: {str(e)}")
            
    def rename_files(self):
        """Rename files to standard format: NAME_VARIANT_label_UPC."""
        try:
            if not self.current_directory:
                messagebox.showinfo("Info", "Please select a directory first")
                return
                
            # Get files to rename
            files_to_rename = []
            for filename in os.listdir(self.current_directory):
                if not filename.lower().endswith('.png'):
                    continue
                    
                old_path = os.path.join(self.current_directory, filename)
                new_name = standardize_filename(filename, image_path=old_path)
                
                if new_name != filename:
                    files_to_rename.append((old_path, new_name))
            
            if not files_to_rename:
                messagebox.showinfo("Info", "No files need renaming")
                return
                
            # Confirm renaming
            count = len(files_to_rename)
            if not messagebox.askyesno(
                "Confirm Rename",
                f"Rename {count} file{'s' if count > 1 else ''} to standard format?\n\n"
                "Format: NAME_VARIANT_label_UPC\n"
                "Example: PC_BCO_2.0_GLNVY_label_840168722402\n\n"
                "This will scan each label image to extract:\n"
                "- Product name from the label text\n"
                "- Variant code (e.g., BLKV1, GLNVY)\n"
                "- UPC number (12-13 digits)"
            ):
                return
                
            # Rename files
            renamed_count = 0
            skipped_count = 0
            errors = []
            
            for old_path, new_name in files_to_rename:
                try:
                    new_path = os.path.join(self.current_directory, new_name)
                    
                    # Handle filename conflicts
                    if os.path.exists(new_path):
                        choice = self.show_collision_dialog(new_path, old_path, new_name)
                        
                        if choice == "keep_existing":
                            # Move new file to duplicates
                            duplicates_dir = os.path.join(self.current_directory, "duplicates")
                            if not os.path.exists(duplicates_dir):
                                os.makedirs(duplicates_dir)
                            os.rename(old_path, os.path.join(duplicates_dir, os.path.basename(old_path)))
                            skipped_count += 1
                            continue
                            
                        elif choice == "keep_new":
                            # Move existing file to duplicates
                            duplicates_dir = os.path.join(self.current_directory, "duplicates")
                            if not os.path.exists(duplicates_dir):
                                os.makedirs(duplicates_dir)
                            os.rename(new_path, os.path.join(duplicates_dir, os.path.basename(new_path)))
                            
                        elif choice == "keep_both":
                            # Add number to new filename
                            base, ext = os.path.splitext(new_name)
                            counter = 1
                            while os.path.exists(new_path):
                                new_path = os.path.join(self.current_directory, f"{base}_{counter}{ext}")
                                counter += 1
                                
                        else:  # skip
                            skipped_count += 1
                            continue
                    
                    os.rename(old_path, new_path)
                    renamed_count += 1
                except Exception as e:
                    errors.append(f"{os.path.basename(old_path)}: {str(e)}")
                    skipped_count += 1
            
            # Show results
            message = f"Renamed {renamed_count} file{'s' if renamed_count > 1 else ''}\n"
            if skipped_count:
                message += f"Skipped {skipped_count} file{'s' if skipped_count > 1 else ''}\n\n"
                if errors:
                    message += "Errors:\n" + "\n".join(errors)
            
            if renamed_count > 0:
                messagebox.showinfo("Rename Complete", message)
            else:
                messagebox.showerror("Rename Failed", message)
            
            # Refresh the file list
            self.load_files_from_directory(self.current_directory)
            
        except Exception as e:
            print(f"Error during rename: {e}")
            messagebox.showerror("Error", f"Rename failed: {str(e)}")
            
    def show_collision_dialog(self, existing_path, new_path, new_name):
        """Show dialog for resolving filename collisions."""
        dialog = tk.Toplevel(self)
        dialog.title("File Collision")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.geometry("800x600")
        dialog.resizable(False, False)
        
        # Create frames
        info_frame = ttk.Frame(dialog)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        preview_frame = ttk.Frame(dialog)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Info label
        ttk.Label(
            info_frame,
            text=f"A file named '{new_name}' already exists.\nPlease choose which file to keep:",
            justify=tk.LEFT
        ).pack(anchor=tk.W)
        
        # Create preview panels
        left_panel = ttk.LabelFrame(preview_frame, text="Existing File")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        right_panel = ttk.LabelFrame(preview_frame, text="New File")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Load and display previews
        try:
            # Existing file preview
            existing_img = Image.open(existing_path)
            existing_img.thumbnail((350, 350))
            existing_photo = ImageTk.PhotoImage(existing_img)
            
            existing_label = ttk.Label(left_panel, image=existing_photo)
            existing_label.image = existing_photo
            existing_label.pack(pady=5)
            
            ttk.Label(
                left_panel,
                text=f"Path: {existing_path}\nSize: {os.path.getsize(existing_path):,} bytes",
                justify=tk.LEFT
            ).pack(anchor=tk.W, padx=5)
            
            # New file preview
            new_img = Image.open(new_path)
            new_img.thumbnail((350, 350))
            new_photo = ImageTk.PhotoImage(new_img)
            
            new_label = ttk.Label(right_panel, image=new_photo)
            new_label.image = new_photo
            new_label.pack(pady=5)
            
            ttk.Label(
                right_panel,
                text=f"Path: {new_path}\nSize: {os.path.getsize(new_path):,} bytes",
                justify=tk.LEFT
            ).pack(anchor=tk.W, padx=5)
            
        except Exception as e:
            print(f"Error loading previews: {e}")
            ttk.Label(
                preview_frame,
                text=f"Error loading previews: {str(e)}",
                foreground="red"
            ).pack(pady=10)
        
        # Result variable
        result = tk.StringVar(value="skip")
        
        # Buttons
        ttk.Button(
            button_frame,
            text="Keep Existing",
            command=lambda: [setattr(dialog, "choice", "keep_existing"), dialog.destroy()]
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Keep New",
            command=lambda: [setattr(dialog, "choice", "keep_new"), dialog.destroy()]
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Keep Both",
            command=lambda: [setattr(dialog, "choice", "keep_both"), dialog.destroy()]
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Skip",
            command=lambda: [setattr(dialog, "choice", "skip"), dialog.destroy()]
        ).pack(side=tk.LEFT, padx=5)
        
        # Wait for dialog
        dialog.wait_window()
        return getattr(dialog, "choice", "skip")

    def delete_selected(self):
        """Move selected files to the deleted folder."""
        try:
            selected_indices = self.file_listbox.curselection()
            if not selected_indices:
                return
                
            # Create deleted directory if needed
            deleted_dir = os.path.join(self.current_directory, "deleted")
            if not os.path.exists(deleted_dir):
                os.makedirs(deleted_dir)
                
            # Get selected files (accounting for header rows in search results)
            search_text = self.search_var.get()
            header_offset = 2 if search_text else 0
            
            files_to_delete = []
            for idx in selected_indices:
                if search_text and idx < header_offset:
                    continue  # Skip header rows
                file_idx = idx - header_offset
                if 0 <= file_idx < len(self.filtered_files):
                    files_to_delete.append(self.filtered_files[file_idx])
            
            if not files_to_delete:
                return
                
            # Confirm deletion
            count = len(files_to_delete)
            if not messagebox.askyesno(
                "Confirm Delete",
                f"Move {count} file{'s' if count > 1 else ''} to deleted folder?"
            ):
                return
                
            # Move files to deleted folder
            moved_count = 0
            for file_path in files_to_delete:
                try:
                    filename = os.path.basename(file_path)
                    new_path = os.path.join(deleted_dir, filename)
                    
                    # Handle filename conflicts
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(new_path):
                        new_path = os.path.join(deleted_dir, f"{base}_{counter}{ext}")
                        counter += 1
                        
                    os.rename(file_path, new_path)
                    moved_count += 1
                except Exception as e:
                    print(f"Error moving {filename}: {e}")
            
            # Show result
            messagebox.showinfo(
                "Delete Complete",
                f"Moved {moved_count} file{'s' if moved_count > 1 else ''} to:\n{deleted_dir}"
            )
            
            # Refresh the file list
            self.load_files_from_directory(self.current_directory)
            
        except Exception as e:
            print(f"Error during delete: {e}")
            messagebox.showerror("Error", f"Delete failed: {str(e)}")
            
    def on_select(self, event):
        """Handle file selection."""
        if not self.file_listbox.curselection():
            return
            
        selected_index = self.file_listbox.curselection()[0]
        
        # Skip header items when searching
        search_text = self.search_var.get()
        if search_text and selected_index <= 1:  # Skip "Found X matches" and separator
            return
            
        # Adjust index to account for header rows when searching
        file_index = selected_index - 2 if search_text else selected_index
        
        if file_index < 0 or file_index >= len(self.filtered_files):
            return
            
        selected_file = self.filtered_files[file_index]
        print(f"Selected file: {selected_file}")
        
        # Load preview
        if hasattr(self.main_window, 'preview_frame'):
            self.main_window.preview_frame.load_preview(selected_file)

    def print_selected(self):
        """Open selected files in default print dialog."""
        try:
            selected_indices = self.file_listbox.curselection()
            if not selected_indices:
                messagebox.showinfo("Print", "Please select one or more labels to print")
                return
            
            # Get selected files (accounting for header rows in search results)
            search_text = self.search_var.get()
            header_offset = 2 if search_text else 0
            
            for idx in selected_indices:
                if search_text and idx < header_offset:
                    continue  # Skip header rows
                file_idx = idx - header_offset
                if 0 <= file_idx < len(self.filtered_files):
                    file_path = self.filtered_files[file_idx]
                    # Use start command to open with default program
                    os.startfile(file_path, 'print')
            
        except Exception as e:
            print(f"Error during print: {e}")
            messagebox.showerror("Error", f"Print failed: {str(e)}")

class PreviewFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Create preview label frame
        preview_frame = ttk.LabelFrame(self, text="Label Preview",
                                    style='Preview.TLabelframe')
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create canvas for image preview with scrollbars
        canvas_frame = ttk.Frame(preview_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbars
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        
        self.preview_canvas = tk.Canvas(
            canvas_frame,
            bg=THEME['listbox_background'],
            width=400,
            height=400,
            xscrollcommand=h_scrollbar.set,
            yscrollcommand=v_scrollbar.set
        )
        
        # Configure scrollbars
        h_scrollbar.config(command=self.preview_canvas.xview)
        v_scrollbar.config(command=self.preview_canvas.yview)
        
        # Pack everything
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # File info frame
        info_frame = ttk.Frame(preview_frame)
        info_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.info_label = ttk.Label(
            info_frame,
            text="No file selected",
            wraplength=400,
            justify=tk.LEFT,
            style='Info.TLabel'
        )
        self.info_label.pack(fill=tk.X)
        
        # Store references
        self.current_image = None
        self.photo_image = None
        
    def load_preview(self, file_path):
        """Load and display image preview."""
        try:
            # Clear previous image
            self.preview_canvas.delete("all")
            if self.photo_image:
                self.photo_image = None
            
            # Load and resize image
            image = Image.open(file_path)
            
            # Calculate resize ratio while maintaining aspect ratio
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            # Ensure minimum dimensions
            canvas_width = max(canvas_width, 400)
            canvas_height = max(canvas_height, 400)
            
            # Calculate scale factor
            width_ratio = canvas_width / image.width
            height_ratio = canvas_height / image.height
            scale_factor = min(width_ratio, height_ratio)
            
            # Calculate new dimensions
            new_width = int(image.width * scale_factor)
            new_height = int(image.height * scale_factor)
            
            # Resize image
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            self.photo_image = ImageTk.PhotoImage(image)
            
            # Calculate center position
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            
            # Display image
            self.preview_canvas.create_image(x, y, anchor=tk.NW, image=self.photo_image)
            
            # Update info label
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / 1024  # Convert to KB
            self.info_label.config(
                text=f"File: {file_name}\nSize: {file_size:.1f} KB\nDimensions: {image.width}x{image.height}"
            )
            
            # Update canvas scrollregion
            self.preview_canvas.config(scrollregion=self.preview_canvas.bbox("all"))
            
        except Exception as e:
            self.logger.error(f"Error loading preview: {e}")
            self.info_label.config(text=f"Error loading preview: {str(e)}")

def standardize_filename(filename, image_path=None):
    # Implement your filename standardization logic here
    # For now, just return the original filename
    if image_path:
        # Use OCR to extract label info
        text = pytesseract.image_to_string(Image.open(image_path))
        # Extract product name, variant code, and UPC number
        # ...
        # Return the standardized filename
        return f"{product_name}_{variant_code}_label_{upc_number}.png"
    else:
        return filename
