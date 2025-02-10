import tkinter as tk
from ..utils.ui_helpers import create_styled_button

class ActionButtons(tk.Frame):
    """Frame containing action buttons (Preview, View Files, Import CSV)"""

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        
        self._create_buttons()
        
    def _create_buttons(self):
        """Create action buttons"""
        # Preview button with vibrant blue theme
        preview_btn = create_styled_button(
            self,
            text="Preview",
            command=self.master.preview_label,
            width=10,
            tooltip_text="Show a preview of the label"
        )
        preview_btn.pack(side=tk.LEFT, padx=2)

        # View Files button with vibrant purple theme
        view_files_btn = create_styled_button(
            self,
            text="View Files",
            command=self.master.view_directory_files,
            width=10,
            tooltip_text="Open the directory viewer"
        )
        view_files_btn.pack(side=tk.LEFT, padx=2)

        # Import CSV button with green theme
        csv_colors = {
            'bg': '#27ae60',  # Green
            'fg': 'white',
            'hover_bg': '#219a52',
            'active_bg': '#1e8449'
        }
        csv_btn = create_styled_button(
            self,
            text="Import CSV",
            command=self.master.upload_csv,
            width=10,
            tooltip_text="Import labels from a CSV file",
            color_scheme=csv_colors
        )
        csv_btn.pack(side=tk.LEFT, padx=2)
