import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import os
from PIL import Image, ImageTk
from io import BytesIO
import webbrowser
import json
import threading
from datetime import datetime
import subprocess
import shutil
import tempfile

class GitHubLabelManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Label Manager - Omar27522/Projects")
        self.root.geometry("1000x700")
        
        # Repository details
        self.repo_owner = "Omar27522"
        self.repo_name = "Projects"
        self.labels_path = "labels/files"
        self.repo_url = f"https://github.com/{self.repo_owner}/{self.repo_name}"
        
        # Local repository path
        self.local_repo_path = None
        
        # Initialize status bar
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initialize repository
        if not self.setup_repository():
            messagebox.showerror("Error", "Failed to initialize repository. Please ensure Git is installed.")
            root.destroy()
            return
        
        # Set window icon (GitHub icon)
        try:
            icon_url = "https://github.com/favicon.ico"
            icon_response = requests.get(icon_url)
            if icon_response.status_code == 200:
                icon_data = BytesIO(icon_response.content)
                icon_image = Image.open(icon_data)
                icon_photo = ImageTk.PhotoImage(icon_image)
                self.root.iconphoto(True, icon_photo)
        except:
            pass  # Ignore icon loading errors
        
        # Configure style
        style = ttk.Style()
        style.configure('Header.TLabel', font=('TkDefaultFont', 10, 'bold'))
        style.configure('FileCount.TLabel', font=('TkDefaultFont', 9))
        style.configure('Action.TButton', padding=5)
        
        # Create main container with padding
        self.main_container = ttk.Frame(root, padding="10")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create header frame
        self.create_header_frame()
        
        # Create main content frame
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Configure grid weights
        self.content_frame.grid_columnconfigure(0, weight=1)  # File list
        self.content_frame.grid_columnconfigure(1, weight=2)  # Preview
        
        # Create left panel (file list)
        self.create_file_list_panel()
        
        # Create right panel (preview)
        self.create_preview_panel()
        
        # Initialize variables
        self.current_image = None
        self.files_data = []
        self.last_refresh = None
        
        # Load initial data
        self.set_status("Loading repository files...")
        self.refresh_files()
    
    def create_header_frame(self):
        """Create the header frame with repository info and controls"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Repository info with clickable link
        repo_text = f"Repository: {self.repo_url}/tree/main/{self.labels_path}"
        repo_label = ttk.Label(header_frame, text=repo_text,
                             style='Header.TLabel', cursor="hand2")
        repo_label.pack(side=tk.LEFT)
        repo_label.bind("<Button-1>", 
                       lambda e: webbrowser.open(f"{self.repo_url}/tree/main/{self.labels_path}"))
        
        # Control buttons frame
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side=tk.RIGHT)
        
        # Refresh button
        refresh_btn = ttk.Button(controls_frame, text="🔄 Refresh",
                               command=self.refresh_files, style='Action.TButton')
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Last refresh time
        self.refresh_label = ttk.Label(controls_frame, text="")
        self.refresh_label.pack(side=tk.RIGHT, padx=5)
    
    def create_file_list_panel(self):
        """Create the left panel with file list and search"""
        left_frame = ttk.Frame(self.content_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Search frame
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_frame, text="🔍", font=('TkDefaultFont', 10)).pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_files)
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var,
                               font=('TkDefaultFont', 9))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # File count label
        self.count_label = ttk.Label(search_frame, text="Files: 0",
                                   style='FileCount.TLabel')
        self.count_label.pack(side=tk.RIGHT)
        
        # Create listbox with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.EXTENDED,
                                     font=('TkDefaultFont', 9),
                                     activestyle='none')
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                command=self.file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        self.file_listbox.bind('<Double-Button-1>', lambda e: self.download_labels())
        
        # Action buttons
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        upload_btn = ttk.Button(btn_frame, text="📤 Upload Files",
                              command=self.upload_files, style='Action.TButton')
        upload_btn.pack(side=tk.LEFT, padx=2)
        
        delete_btn = ttk.Button(btn_frame, text="🗑️ Delete Selected",
                              command=self.delete_files, style='Action.TButton')
        delete_btn.pack(side=tk.LEFT, padx=2)
    
    def create_preview_panel(self):
        """Create the right panel for file preview"""
        preview_frame = ttk.Frame(self.content_frame)
        preview_frame.grid(row=0, column=1, sticky="nsew")
        
        # Preview label
        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # File info frame
        info_frame = ttk.Frame(preview_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        self.info_label = ttk.Label(info_frame, text="", wraplength=400)
        self.info_label.pack(fill=tk.X)
        
        # Action buttons
        buttons_frame = ttk.Frame(preview_frame)
        buttons_frame.pack(fill=tk.X)
        
        download_btn = ttk.Button(buttons_frame, text="Download Labels",
                             command=self.download_labels)
        download_btn.pack(side=tk.LEFT, padx=5)
    
    def set_status(self, message):
        """Update status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()

    def refresh_files(self):
        """Refresh the file list from GitHub"""
        try:
            self.set_status("Fetching repository files...")
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{self.labels_path}"
            response = requests.get(url)
            
            if response.status_code != 200:
                raise Exception(f"Failed to fetch files: HTTP {response.status_code}")
            
            self.files_data = response.json()
            self.update_file_list()
            
            self.last_refresh = datetime.now()
            self.refresh_label.config(
                text=f"Last refresh: {self.last_refresh.strftime('%H:%M:%S')}")
            
            self.set_status(f"Found {len(self.files_data)} files in repository")
            
        except Exception as e:
            self.set_status(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
    
    def update_file_list(self):
        """Update the listbox with files"""
        self.file_listbox.delete(0, tk.END)
        search_term = self.search_var.get().lower()
        
        displayed_files = []
        for file in self.files_data:
            if file['type'] == 'file' and file['name'].lower().endswith(('.png', '.jpg', '.jpeg')):
                if search_term in file['name'].lower():
                    displayed_files.append(file)
                    self.file_listbox.insert(tk.END, file['name'])
        
        self.count_label.config(text=f"Files: {len(displayed_files)}")
    
    def filter_files(self, *args):
        """Filter files based on search term"""
        self.update_file_list()
    
    def on_file_select(self, event):
        """Handle file selection"""
        if not self.file_listbox.curselection():
            self.preview_label.config(image='')
            self.info_label.config(text='')
            return
        
        selection = self.file_listbox.curselection()[0]
        file_name = self.file_listbox.get(selection)
        file_data = next((f for f in self.files_data if f['name'] == file_name), None)
        
        if not file_data:
            return
        
        try:
            # Load and display image
            response = requests.get(file_data['download_url'])
            if response.status_code != 200:
                raise Exception(f"Failed to fetch image: HTTP {response.status_code}")
            
            image = Image.open(BytesIO(response.content))
            
            # Resize for preview
            display_size = (400, 400)
            image.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            self.preview_label.config(image=photo)
            self.preview_label.image = photo
            
            # Update info
            self.info_label.config(
                text=f"File: {file_data['name']}\n"
                     f"Size: {file_data['size']:,} bytes\n"
                     f"SHA: {file_data['sha'][:8]}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading preview: {str(e)}")
    
    def setup_repository(self):
        """Setup local repository"""
        try:
            # Create directory in user's AppData/Local folder
            app_data = os.path.join(os.environ['LOCALAPPDATA'], 'LabelManager')
            repo_dir = os.path.join(app_data, 'Repository')
            
            # Create app directory if it doesn't exist
            if not os.path.exists(app_data):
                os.makedirs(app_data)
            
            # Remove existing repo if it exists
            if os.path.exists(repo_dir):
                try:
                    shutil.rmtree(repo_dir)
                except PermissionError:
                    # If can't remove, try to work with existing repo
                    self.local_repo_path = repo_dir
                    return True
            
            try:
                os.makedirs(repo_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create repository directory: {str(e)}")
                return False
            
            self.local_repo_path = repo_dir
            
            # Clone repository
            self.set_status("Cloning repository...")
            result = subprocess.run(
                ["git", "clone", self.repo_url, self.local_repo_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"Failed to clone repository: {result.stderr}")
            
            # Configure Git
            subprocess.run(["git", "config", "user.name", "Label Manager"], cwd=self.local_repo_path)
            subprocess.run(["git", "config", "user.email", "label.manager@example.com"], 
                         cwd=self.local_repo_path)
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to setup repository: {str(e)}")
            return False

    def git_command(self, command, error_message="Git operation failed"):
        """Run a git command in the repository directory"""
        try:
            result = subprocess.run(
                command,
                cwd=self.local_repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"{error_message}: {result.stderr}")
            
            return result.stdout.strip()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return None

    def upload_files(self):
        """Handle file upload using Git"""
        files = filedialog.askopenfilenames(
            title="Select Label Files to Upload",
            filetypes=[
                ("Label files", "*.png *.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        
        if not files:
            return
        
        # Check file sizes
        large_files = []
        for file in files:
            size_mb = os.path.getsize(file) / (1024 * 1024)
            if size_mb > 25:
                large_files.append(f"{os.path.basename(file)} ({size_mb:.1f} MB)")
        
        if large_files:
            messagebox.showerror(
                "Files Too Large",
                "These files exceed GitHub's 25 MB limit:\n\n" +
                "\n".join(large_files)
            )
            return
        
        try:
            # Pull latest changes
            self.set_status("Pulling latest changes...")
            self.git_command(["git", "pull"], "Failed to pull latest changes")
            
            # Copy files to repository
            target_dir = os.path.join(self.local_repo_path, self.labels_path)
            os.makedirs(target_dir, exist_ok=True)
            
            self.set_status("Copying files...")
            for file in files:
                shutil.copy2(file, target_dir)
            
            # Add files to Git
            self.set_status("Adding files to Git...")
            file_list = [os.path.basename(f) for f in files]
            commit_files = [os.path.join(self.labels_path, f) for f in file_list]
            
            self.git_command(["git", "add"] + commit_files,
                           "Failed to add files to Git")
            
            # Create commit
            commit_msg = f"Added {len(files)} new label file(s)\n\n" + \
                        "\n".join(f"- {f}" for f in file_list)
            
            self.git_command(["git", "commit", "-m", commit_msg],
                           "Failed to create commit")
            
            # Push changes
            self.set_status("Pushing changes to GitHub...")
            self.git_command(["git", "push"], "Failed to push changes")
            
            messagebox.showinfo(
                "Success",
                f"Successfully uploaded {len(files)} file(s) to GitHub"
            )
            
            self.refresh_files()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload files: {str(e)}")

    def delete_files(self):
        """Handle file deletion using Git"""
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select files to delete")
            return
        
        selected_files = [self.file_listbox.get(i) for i in selected_indices]
        
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete these {len(selected_files)} file(s)?\n\n" +
            "\n".join(f"- {f}" for f in selected_files) + "\n\n" +
            "This action cannot be undone!",
            icon='warning'
        ):
            return
        
        try:
            # Pull latest changes
            self.set_status("Pulling latest changes...")
            self.git_command(["git", "pull"], "Failed to pull latest changes")
            
            # Remove files
            self.set_status("Removing files...")
            file_paths = [os.path.join(self.labels_path, f) for f in selected_files]
            
            self.git_command(["git", "rm"] + file_paths,
                           "Failed to remove files from Git")
            
            # Create commit
            commit_msg = f"Deleted {len(selected_files)} label file(s)\n\n" + \
                        "\n".join(f"- {f}" for f in selected_files)
            
            self.git_command(["git", "commit", "-m", commit_msg],
                           "Failed to create commit")
            
            # Push changes
            self.set_status("Pushing changes to GitHub...")
            self.git_command(["git", "push"], "Failed to push changes")
            
            messagebox.showinfo(
                "Success",
                f"Successfully deleted {len(selected_files)} file(s) from GitHub"
            )
            
            self.refresh_files()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete files: {str(e)}")

    def download_labels(self):
        """Download selected labels to a user-specified directory"""
        try:
            # Get selected items
            selected_indices = self.file_listbox.curselection()
            if not selected_indices:
                messagebox.showinfo("Info", "Please select labels to download")
                return

            # Ask user for download directory
            download_dir = filedialog.askdirectory(title="Select Download Directory")
            if not download_dir:
                return

            # Get the labels directory path
            labels_dir = os.path.join(self.local_repo_path, self.labels_path)
            
            # Copy selected files
            copied_files = 0
            for index in selected_indices:
                filename = self.file_listbox.get(index)
                src = os.path.join(labels_dir, filename)
                dst = os.path.join(download_dir, filename)
                
                try:
                    shutil.copy2(src, dst)
                    copied_files += 1
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to copy {filename}: {str(e)}")

            if copied_files > 0:
                messagebox.showinfo("Success", f"Downloaded {copied_files} label files to {download_dir}")
            else:
                messagebox.showerror("Error", "No files were downloaded due to errors")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to download labels: {str(e)}")

    def __del__(self):
        """Cleanup temporary repository"""
        if self.local_repo_path and os.path.exists(self.local_repo_path):
            try:
                shutil.rmtree(self.local_repo_path)
            except:
                pass

def main():
    root = tk.Tk()
    root.title("Label Manager - Omar27522/Projects")
    
    # Set style
    style = ttk.Style()
    style.theme_use('clam')  # or 'vista' on Windows
    
    app = GitHubLabelManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
