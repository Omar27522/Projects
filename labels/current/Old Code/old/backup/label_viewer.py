import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import os
import subprocess
import tempfile
import base64
import json
from PIL import Image, ImageTk
from io import BytesIO

class LabelViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Label Viewer")
        self.root.geometry("800x600")
        
        # Initialize settings variables
        self.local_folder = tk.StringVar()
        self.use_local = tk.BooleanVar(value=False)
        
        # GitHub repository details
        self.repo_owner = "Omar27522"
        self.repo_name = "Projects"
        self.labels_path = "labels/files"
        self.repo_url = f"https://github.com/{self.repo_owner}/{self.repo_name}"
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create top frame for settings button
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill=tk.X)
        
        # Create settings button
        self.settings_button = ttk.Button(self.top_frame, text="⚙", width=3, command=self.open_settings)
        self.settings_button.pack(side=tk.RIGHT)
        
        # Create content frame
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create settings frame
        self.settings_frame = ttk.Frame(self.main_frame)
        
        # Add back button in settings
        self.settings_top_frame = ttk.Frame(self.settings_frame)
        self.settings_top_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.back_button = ttk.Button(self.settings_top_frame, text="← Back", command=self.close_settings)
        self.back_button.pack(side=tk.LEFT)
        
        # Add apply button in settings
        self.apply_button = ttk.Button(self.settings_top_frame, text="Apply", command=self.apply_settings)
        self.apply_button.pack(side=tk.RIGHT)
        
        # Add settings content
        self.settings_content = ttk.Frame(self.settings_frame)
        self.settings_content.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Settings title
        ttk.Label(self.settings_content, text="Settings", font=('TkDefaultFont', 12, 'bold')).pack(pady=(0, 20))
        
        # GitHub settings
        github_frame = ttk.LabelFrame(self.settings_content, text="GitHub Integration", padding=10)
        github_frame.pack(fill=tk.X, pady=5)
        
        # Repository info
        ttk.Label(github_frame, 
                 text=f"Repository: {self.repo_url}/tree/main/{self.labels_path}", 
                 wraplength=300).pack(pady=5)
        
        # Upload button
        upload_button = ttk.Button(github_frame, text="Upload Labels to GitHub", 
                                 command=self.upload_labels)
        upload_button.pack(fill=tk.X, pady=5)
        
        # Local folder settings
        folder_frame = ttk.LabelFrame(self.settings_content, text="Label Source", padding=10)
        folder_frame.pack(fill=tk.X, pady=5)
        
        # Use local folder checkbox
        ttk.Checkbutton(folder_frame, text="Use Local Folder", variable=self.use_local).pack(fill=tk.X)
        
        # Local folder selection
        folder_select_frame = ttk.Frame(folder_frame)
        folder_select_frame.pack(fill=tk.X, pady=5)
        
        self.folder_entry = ttk.Entry(folder_select_frame, textvariable=self.local_folder)
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_button = ttk.Button(folder_select_frame, text="Browse", command=self.browse_local_folder)
        browse_button.pack(side=tk.RIGHT)
        
        # Theme setting
        theme_frame = ttk.Frame(folder_frame)
        theme_frame.pack(fill=tk.X, pady=5)
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value="Light")
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var, values=["Light", "Dark"], state="readonly")
        theme_combo.pack(side=tk.RIGHT)
        
        # Auto-load setting
        autoload_frame = ttk.Frame(folder_frame)
        autoload_frame.pack(fill=tk.X, pady=5)
        ttk.Label(autoload_frame, text="Auto-load first label:").pack(side=tk.LEFT)
        self.autoload_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(autoload_frame, variable=self.autoload_var).pack(side=tk.RIGHT)
        
        # Create left frame for search and listbox
        self.left_frame = ttk.Frame(self.content_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Create search frame
        self.search_frame = ttk.Frame(self.left_frame)
        self.search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create label count
        self.count_label = ttk.Label(self.search_frame, text="Labels: 0")
        self.count_label.pack(side=tk.LEFT, pady=(0, 5))
        
        # Create search entry
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_labels)
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(fill=tk.X)
        
        # Create frame for listbox and scrollbar
        self.list_frame = ttk.Frame(self.left_frame)
        self.list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create listbox for labels
        self.label_listbox = tk.Listbox(self.list_frame, width=40)
        self.label_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create scrollbar for listbox
        scrollbar = ttk.Scrollbar(self.list_frame, orient=tk.VERTICAL, command=self.label_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.label_listbox.config(yscrollcommand=scrollbar.set)
        
        # Create preview frame
        self.preview_frame = ttk.Frame(self.content_frame)
        self.preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create preview label
        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # Create buttons frame
        self.buttons_frame = ttk.Frame(self.preview_frame)
        self.buttons_frame.pack(fill=tk.X, pady=10)
        
        # Create Print and Open buttons
        self.print_button = ttk.Button(self.buttons_frame, text="Print Label", command=self.print_label)
        self.print_button.pack(side=tk.LEFT, padx=5)
        
        self.open_button = ttk.Button(self.buttons_frame, text="Open in Viewer", command=self.open_in_viewer)
        self.open_button.pack(side=tk.LEFT, padx=5)
        
        # Add Delete button
        delete_style = ttk.Style()
        delete_style.configure("Delete.TButton", foreground="red")
        self.delete_button = ttk.Button(self.buttons_frame, text="Delete from GitHub", command=self.delete_labels, style="Delete.TButton")
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        # Bind selection event
        self.label_listbox.bind('<<ListboxSelect>>', self.on_select)
        
        # Store all labels and current image
        self.all_labels = []
        self.current_image = None
        self.temp_file = None
        
        # Load labels
        self.load_labels()
    
    def update_label_count(self):
        total = len(self.all_labels)
        filtered = self.label_listbox.size()
        if total == filtered:
            self.count_label.config(text=f"Labels: {total}")
        else:
            self.count_label.config(text=f"Labels: {filtered}/{total}")
            
    def filter_labels(self, *args):
        search_term = self.search_var.get().lower()
        self.label_listbox.delete(0, tk.END)
        
        for label in self.all_labels:
            if search_term in label.lower():
                self.label_listbox.insert(tk.END, label)
        
        self.update_label_count()
        
        # Auto-select first matching label if auto-load is enabled
        if self.autoload_var.get() and self.label_listbox.size() > 0:
            self.label_listbox.selection_clear(0, tk.END)
            self.label_listbox.selection_set(0)
            self.label_listbox.event_generate('<<ListboxSelect>>')
            
    def load_labels(self):
        # Clear existing labels
        self.label_listbox.delete(0, tk.END)
        self.all_labels = []
        
        if self.use_local.get() and self.local_folder.get():
            # Load from local folder
            try:
                files = os.listdir(self.local_folder.get())
                self.all_labels = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                for label in self.all_labels:
                    self.label_listbox.insert(tk.END, label)
            except Exception as e:
                tk.messagebox.showerror("Error", f"Error loading local labels: {str(e)}")
        else:
            # Load from GitHub
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{self.labels_path}"
            headers = {}
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    files = response.json()
                    self.all_labels = [file['name'] for file in files 
                                     if file['name'].lower().endswith(('.png', '.jpg', '.jpeg'))]
                    for label in self.all_labels:
                        self.label_listbox.insert(tk.END, label)
                else:
                    tk.messagebox.showerror("Error", f"Failed to fetch labels: {response.status_code}")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Error loading labels: {str(e)}")
        
        self.update_label_count()
        
        # Auto-select first label if enabled
        if self.autoload_var.get() and self.label_listbox.size() > 0:
            self.label_listbox.selection_set(0)
            self.label_listbox.event_generate('<<ListboxSelect>>')
    
    def on_select(self, event):
        if not self.label_listbox.curselection():
            return
        
        selected_file = self.label_listbox.get(self.label_listbox.curselection())
        
        try:
            if self.use_local.get() and self.local_folder.get():
                # Load from local folder
                image_path = os.path.join(self.local_folder.get(), selected_file)
                self.current_image = Image.open(image_path)
            else:
                # Load from GitHub
                url = f"https://raw.githubusercontent.com/{self.repo_owner}/{self.repo_name}/main/{self.labels_path}/{selected_file}"
                response = requests.get(url)
                if response.status_code != 200:
                    raise Exception(f"Failed to fetch image: {response.status_code}")
                image_data = BytesIO(response.content)
                self.current_image = Image.open(image_data)
            
            # Save to temporary file for printing/viewing
            if self.temp_file:
                try:
                    os.remove(self.temp_file)
                except:
                    pass
            
            # Create new temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                self.temp_file = tmp.name
                self.current_image.save(self.temp_file)
            
            # Resize image for preview
            display_size = (400, 400)
            preview_image = self.current_image.copy()
            preview_image.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(preview_image)
            self.preview_label.configure(image=photo)
            self.preview_label.image = photo
        except Exception as e:
            self.preview_label.configure(image='')
            self.current_image = None
            tk.messagebox.showerror("Error", f"Error loading image: {str(e)}")
    
    def print_label(self):
        if not self.current_image or not self.temp_file:
            tk.messagebox.showwarning("Warning", "Please select a label first")
            return
        
        try:
            os.startfile(self.temp_file, "print")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error printing label: {str(e)}")
    
    def open_in_viewer(self):
        if not self.current_image or not self.temp_file:
            tk.messagebox.showwarning("Warning", "Please select a label first")
            return
        
        try:
            os.startfile(self.temp_file)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error opening label: {str(e)}")
    
    def open_settings(self):
        # Hide main content and show settings
        self.content_frame.pack_forget()
        self.settings_frame.pack(fill=tk.BOTH, expand=True)
    
    def close_settings(self):
        # Hide settings and show main content
        self.settings_frame.pack_forget()
        self.content_frame.pack(fill=tk.BOTH, expand=True)
    
    def apply_settings(self):
        # Apply the settings and reload labels if needed
        old_use_local = self.use_local.get()
        old_folder = self.local_folder.get()
        
        # If source changed, reload labels
        if old_use_local != self.use_local.get() or old_folder != self.local_folder.get():
            self.load_labels()
        
        self.close_settings()
    
    def browse_local_folder(self):
        folder = filedialog.askdirectory(title="Select Labels Folder")
        if folder:
            self.local_folder.set(folder)
    
    def upload_labels(self):
        if not self.local_folder.get():
            messagebox.showerror("Error", "Please select a local folder first:\n"
                               "1. Check 'Use Local Folder'\n"
                               "2. Click Browse to select your folder")
            return
            
        # Get selected labels
        selected_indices = self.label_listbox.curselection()
        if not selected_indices:
            if not messagebox.askyesno("Upload All", 
                                     "No labels selected. Would you like to upload all labels from the local folder?"):
                return
            selected_labels = self.all_labels
        else:
            selected_labels = [self.label_listbox.get(i) for i in selected_indices]
        
        if not selected_labels:
            messagebox.showwarning("Warning", "No labels to upload")
            return
        
        # Show upload instructions
        upload_url = f"{self.repo_url}/upload/main/{self.labels_path}"
        os.startfile(upload_url)
        
        # Format the list of files for the instructions
        file_list = "\n".join(f"- {label}" for label in selected_labels)
        
        messagebox.showinfo("Upload Instructions", 
            f"Follow these steps to upload the selected labels:\n\n"
            f"1. The GitHub upload page has opened in your browser\n"
            f"2. Your local folder is: {self.local_folder.get()}\n"
            f"3. Drag and drop these files from that folder:\n{file_list}\n\n"
            f"4. Add a descriptive commit message (e.g., 'Added new label files')\n"
            f"5. Click 'Commit changes' to upload them\n\n"
            "Once done, click OK to refresh the label list")
        
        # Reload labels if using GitHub source
        if not self.use_local.get():
            self.load_labels()

    def delete_labels(self):
        # Get selected labels
        selected_indices = self.label_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select labels to delete")
            return
            
        selected_labels = [self.label_listbox.get(i) for i in selected_indices]
        
        # Show warning message
        if not messagebox.askyesno("Warning", 
            f"Are you sure you want to delete these {len(selected_labels)} label(s)?\n\n" +
            "\n".join(selected_labels) + "\n\n" +
            "This action cannot be undone!", icon='warning'):
            return
        
        # Format the list of files for the instructions
        file_list = "\n".join(f"- {label}" for label in selected_labels)
        
        # Open the GitHub repository page
        folder_url = f"{self.repo_url}/tree/main/{self.labels_path}"
        os.startfile(folder_url)
        
        # Show instructions
        messagebox.showinfo("Delete Instructions",
            f"Follow these steps to delete the selected labels:\n\n"
            f"For each file in this list:\n{file_list}\n\n"
            "1. Click on the file name\n"
            "2. Click the trash icon (🗑️) in the top-right\n"
            "3. Add a commit message (e.g., 'Deleted label file')\n"
            "4. Click 'Commit changes' to confirm deletion\n\n"
            "Once you've deleted all files, click OK to refresh the label list")
        
        # Reload labels if using GitHub source
        if not self.use_local.get():
            self.load_labels()
    
    def __del__(self):
        # Clean up temporary file
        if self.temp_file and os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
            except:
                pass

def main():
    root = tk.Tk()
    app = LabelViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
