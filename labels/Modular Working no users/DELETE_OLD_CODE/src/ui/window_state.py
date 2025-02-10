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
        # First clean up any destroyed windows
        self.cleanup_destroyed_windows()
        return next((window for window in self.app_windows 
                    if isinstance(window, window_type) and window.winfo_exists()), None)
    
    def get_all_windows(self):
        """Get all tracked windows."""
        # First clean up any destroyed windows
        self.cleanup_destroyed_windows()
        # Return only windows that still exist
        return [window for window in self.app_windows if window.winfo_exists()]
        
    def cleanup_destroyed_windows(self):
        """Remove any destroyed windows from tracking."""
        try:
            # Use list comprehension to avoid modifying list while iterating
            self.app_windows = [window for window in self.app_windows 
                              if hasattr(window, 'winfo_exists') and window.winfo_exists()]
        except Exception:
            # If there's any error during cleanup, just reset the list
            self.app_windows = []
