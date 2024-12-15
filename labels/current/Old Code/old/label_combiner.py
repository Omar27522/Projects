import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading

class LabelDuplicateChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("UPC Duplicate Finder")
        self.root.geometry("900x700")
        
        # Set theme and style
        style = ttk.Style()
        style.theme_use('clam')
        self.root.configure(bg='#f0f0f0')
        style.configure('TButton', padding=5)
        style.configure('TFrame', background='#f0f0f0')
        style.configure('Header.TLabel', font=('Helvetica', 16, 'bold'), background='#f0f0f0')
        
        self.create_gui()
        
    def create_gui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = ttk.Label(main_frame, text="UPC Duplicate Finder", style='Header.TLabel')
        header.pack(pady=(0, 10))
        
        # Directory selection
        dir_frame = ttk.Frame(main_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.dir_var = tk.StringVar()
        dir_entry = ttk.Entry(dir_frame, textvariable=self.dir_var, width=60)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(dir_frame, text="Browse", command=self.browse_directory)
        browse_btn.pack(side=tk.LEFT)
        
        # Scan button
        self.scan_btn = ttk.Button(main_frame, text="Find UPC Duplicates", command=self.start_scan)
        self.scan_btn.pack(pady=(0, 10))
        
        # Progress
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.pack(pady=(0, 5))
        
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Results
        results_frame = ttk.LabelFrame(main_frame, text="Duplicate UPCs Found", padding="5")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=25, width=90)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
    def browse_directory(self):
        directory = filedialog.askdirectory(title="Select Labels Directory")
        if directory:
            self.dir_var.set(directory)
            
    def start_scan(self):
        directory = self.dir_var.get()
        if not directory:
            self.show_message("Please select a directory first")
            return
            
        self.scan_btn.configure(state='disabled')
        self.progress.start(10)
        self.progress_var.set("Scanning...")
        self.results_text.delete(1.0, tk.END)
        
        thread = threading.Thread(target=self.scan_directory, args=(directory,))
        thread.daemon = True
        thread.start()
        
    def scan_directory(self, directory):
        if not os.path.exists(directory):
            self.show_message(f"Directory not found: {directory}")
            self.finish_scan()
            return
            
        self.log_message(f"Scanning directory: {directory}\n")
        
        # Get all files and their UPC codes
        files_with_upc = []
        upc_pattern = re.compile(r'\b\d{12}\b')
        
        for root, _, files in os.walk(directory):
            self.progress_var.set(f"Checking: {root}")
            for filename in files:
                upc_matches = upc_pattern.findall(filename)
                if upc_matches:
                    full_path = os.path.join(root, filename)
                    for upc in upc_matches:
                        files_with_upc.append((filename, upc, full_path))
        
        if not files_with_upc:
            self.log_message("No files with 12-digit UPC codes found in filenames.")
            self.finish_scan()
            return
            
        # Group files by UPC
        upc_groups = {}
        for filename, upc, filepath in files_with_upc:
            if upc not in upc_groups:
                upc_groups[upc] = []
            upc_groups[upc].append((filename, filepath))
        
        # Report duplicates
        duplicates_found = False
        
        for upc in sorted(upc_groups.keys()):
            files = upc_groups[upc]
            if len(files) > 1:
                duplicates_found = True
                self.log_message(f"\nDuplicate UPC Found: {upc}")
                self.log_message("Files with this UPC:")
                for filename, filepath in files:
                    self.log_message(f"  • {filename}")
                self.log_message("-" * 80)
        
        if not duplicates_found:
            self.log_message("No duplicate UPC codes found in filenames.")
        
        # Summary
        self.log_message("\nSummary:")
        self.log_message(f"Total files with UPC codes: {len(set(f[0] for f in files_with_upc))}")
        self.log_message(f"Total unique UPC codes found: {len(upc_groups)}")
        self.log_message(f"Number of duplicate UPCs: {sum(1 for files in upc_groups.values() if len(files) > 1)}")
        
        self.finish_scan()
        
    def finish_scan(self):
        self.root.after(0, lambda: self.scan_btn.configure(state='normal'))
        self.root.after(0, self.progress.stop)
        self.root.after(0, lambda: self.progress_var.set("Scan complete"))
        
    def show_message(self, message):
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, message)
        
    def log_message(self, message):
        self.root.after(0, lambda: self.results_text.insert(tk.END, message + "\n"))

if __name__ == "__main__":
    root = tk.Tk()
    app = LabelDuplicateChecker(root)
    root.mainloop()
