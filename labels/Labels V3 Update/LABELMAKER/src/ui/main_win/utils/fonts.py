class FontManager:
    """Manages font configuration for the application"""
    def __init__(self, root):
        self.root = root
        self.setup_fonts()

    def setup_fonts(self):
        """Configure default fonts"""
        self.default_font = ('TkDefaultFont', 11)
        self.button_font = ('TkDefaultFont', 11, 'normal')
        self.entry_font = ('TkDefaultFont', 11)
        self.label_font = ('TkDefaultFont', 11)
        self.view_files_font = ('TkDefaultFont', 12, 'bold')

        # Apply fonts globally
        self.root.option_add('*Font', self.default_font)
        self.root.option_add('*Button*Font', self.button_font)
        self.root.option_add('*Entry*Font', self.entry_font)
        self.root.option_add('*Label*Font', self.label_font)
