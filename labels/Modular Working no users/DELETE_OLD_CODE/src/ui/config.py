class ConfigManager:
    def __init__(self):
        self.default_settings = {
            'always_on_top': False,
            'window_geometry': None,
            'last_used_directory': None
        }
        self.settings = self.default_settings.copy()
    
    def get(self, key, default=None):
        return self.settings.get(key, default)
    
    def set(self, key, value):
        self.settings[key] = value
    
    def save(self):
        # TODO: Implement settings persistence if needed
        pass
    
    def load(self):
        # TODO: Implement settings loading if needed
        pass
