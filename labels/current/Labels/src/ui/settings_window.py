import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .window_icon_manager import WindowIconManager

class SettingsWindow(tk.Toplevel):
    """A class for managing the settings window"""
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.parent = parent
        self.config_manager = config_manager
        
        self.title("Settings")
        self.geometry("400x450")
        self.minsize(350, 400)
        
        # Set window icon
        WindowIconManager.set_window_icon(self, '32', 'settings')
        
        # Configure fonts
        self.default_font = ('TkDefaultFont', 10, 'bold')
        self.option_add('*Font', self.default_font)
        
        # Create settings content
        self._create_settings_content()
        
        # Make window modal
        self.transient(parent)
        self.grab_set()
        
        # Position window relative to parent
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                 parent.winfo_rooty() + 50))
        
        # Bind window close
        self.protocol("WM_DELETE_WINDOW", self.save_settings)
        
        # Focus window
        self.focus_set()

    def _create_settings_content(self):
        """Create settings window content"""
        # Create main frame with padding
        main_frame = tk.Frame(self, bg='SystemButtonFace')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create font size settings
        font_frame = tk.LabelFrame(main_frame, text="Font Sizes", bg='SystemButtonFace', fg='black')
        font_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(font_frame, text="Large Font Size:", bg='SystemButtonFace', anchor='w').pack(fill=tk.X)
        large_font_scale = ttk.Scale(font_frame, from_=12, to=48, 
                                   variable=self.parent.font_size_large,
                                   orient=tk.HORIZONTAL)
        large_font_scale.pack(fill=tk.X)
        
        tk.Label(font_frame, text="Medium Font Size:", bg='SystemButtonFace', anchor='w').pack(fill=tk.X)
        medium_font_scale = ttk.Scale(font_frame, from_=8, to=24, 
                                    variable=self.parent.font_size_medium,
                                    orient=tk.HORIZONTAL)
        medium_font_scale.pack(fill=tk.X)
        
        # Create barcode settings
        barcode_frame = tk.LabelFrame(main_frame, text="Barcode Settings", bg='SystemButtonFace', fg='black')
        barcode_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(barcode_frame, text="Barcode Width:", bg='SystemButtonFace', anchor='w').pack(fill=tk.X)
        width_scale = ttk.Scale(barcode_frame, from_=1, to=3, 
                              variable=self.parent.barcode_width,
                              orient=tk.HORIZONTAL)
        width_scale.pack(fill=tk.X)
        
        tk.Label(barcode_frame, text="Barcode Height:", bg='SystemButtonFace', anchor='w').pack(fill=tk.X)
        height_scale = ttk.Scale(barcode_frame, from_=10, to=30, 
                               variable=self.parent.barcode_height,
                               orient=tk.HORIZONTAL)
        height_scale.pack(fill=tk.X)
        
        # Create window settings
        window_frame = tk.LabelFrame(main_frame, text="Window Settings", bg='SystemButtonFace', fg='black')
        window_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(window_frame, text="Window Transparency:", bg='SystemButtonFace', anchor='w').pack(fill=tk.X)
        transparency_scale = ttk.Scale(window_frame, from_=0.3, to=1.0, 
                                     variable=self.parent.transparency_level,
                                     orient=tk.HORIZONTAL,
                                     command=self.update_transparency)
        transparency_scale.pack(fill=tk.X)
        
        tk.Checkbutton(window_frame, text="Always on Top", 
                      variable=self.parent.always_on_top,
                      bg='SystemButtonFace').pack(anchor=tk.W)
        
        # Create directory settings with button container
        dir_frame = tk.LabelFrame(main_frame, text="Directory Settings", bg='SystemButtonFace', fg='black')
        dir_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Create button container for side-by-side buttons
        button_container = tk.Frame(dir_frame, bg='SystemButtonFace')
        button_container.pack(fill=tk.X, pady=5)
        
        # Folder button
        select_dir_btn = tk.Button(
            button_container,
            text="📁",  # Folder emoji
            bg='#2196F3',  # Blue
            fg='white',
            command=self._select_output_directory,
            width=4  # Make button compact
        )
        select_dir_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # CSV button
        csv_btn = tk.Button(
            button_container,
            text="CSV",
            bg='#2196F3',  # Blue
            fg='white',
            command=self._load_csv_file,
            width=4  # Make button compact
        )
        csv_btn.pack(side=tk.LEFT)
        
        # Create save button
        save_btn = tk.Button(
            main_frame,
            text="Save Settings",
            bg='#4CAF50',  # Green
            fg='white',
            command=self.save_settings
        )
        save_btn.pack(pady=10)

    def update_transparency(self, *args):
        """Update the transparency of the main window"""
        self.parent.update_window_transparency()

    def _select_output_directory(self):
        """Select output directory"""
        directory = filedialog.askdirectory(
            initialdir=self.config_manager.settings.last_directory,
            title="Select Output Directory"
        )
        if directory:
            self.config_manager.settings.last_directory = directory
            self.config_manager.update_label_counter()  # Update counter when directory changes
            self.parent.png_count.set(str(self.config_manager.settings.label_counter))
            self.config_manager.save_settings()
            # Also open the directory viewer
            self.parent.view_directory_files()
            # Close settings window
            self.save_settings()

    def _load_csv_file(self):
        """Load labels from a CSV file"""
        file_path = filedialog.askopenfilename(
            initialdir=self.config_manager.settings.last_directory,
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.parent.load_labels_from_csv(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV file: {str(e)}")

    def save_settings(self):
        """Save settings and close window"""
        # Update settings
        self.config_manager.settings.font_size_large = self.parent.font_size_large.get()
        self.config_manager.settings.font_size_medium = self.parent.font_size_medium.get()
        self.config_manager.settings.barcode_width = self.parent.barcode_width.get()
        self.config_manager.settings.barcode_height = self.parent.barcode_height.get()
        self.config_manager.settings.always_on_top = self.parent.always_on_top.get()
        self.config_manager.settings.transparency_level = self.parent.transparency_level.get()
        
        # Save settings
        self.config_manager.save_settings()
        
        # Destroy window
        self.destroy()
