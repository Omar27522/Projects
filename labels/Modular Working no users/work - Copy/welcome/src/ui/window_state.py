"""Module for managing global window state."""

class WindowState:
    """Singleton class to manage global window state."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WindowState, cls).__new__(cls)
            cls._instance.app_windows = []
        return cls._instance
    
    def add_window(self, window):
        """Add a window to tracking."""
        if window not in self.app_windows:
            self.app_windows.append(window)
    
    def remove_window(self, window):
        """Remove a window from tracking."""
        if window in self.app_windows:
            self.app_windows.remove(window)
    
    def get_window_by_type(self, window_type):
        """Get an existing window instance of the specified type."""
        return next((window for window in self.app_windows 
                    if isinstance(window, window_type) and window.winfo_exists()), None)
    
    def get_all_windows(self):
        """Get all tracked windows."""
        # Return only windows that still exist
        return [window for window in self.app_windows if window.winfo_exists()]
