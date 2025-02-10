"""
Asset management module for the welcome window application.
Provides paths and utilities for accessing application assets like icons.
"""

import os

# Get the absolute path to the assets directory
ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'assets'
)

# Icon paths
ICONS = {
    'window': {
        'ico': os.path.join(ASSETS_DIR, 'icons', 'window.ico'),
        'png': {
            '16': os.path.join(ASSETS_DIR, 'icons', 'window_16.png'),
            '32': os.path.join(ASSETS_DIR, 'icons', 'window_32.png'),
            '48': os.path.join(ASSETS_DIR, 'icons', 'window_48.png'),
            '64': os.path.join(ASSETS_DIR, 'icons', 'window_64.png'),
            '128': os.path.join(ASSETS_DIR, 'icons', 'window_128.png')
        }
    }
}

def ensure_assets_dir():
    """
    Ensure that the assets directory structure exists.
    Creates the necessary directories if they don't exist.
    """
    os.makedirs(os.path.join(ASSETS_DIR, 'icons'), exist_ok=True)

def get_window_icon(format='png'):
    """Get the path to the window icon file."""
    script_dir = os.path.dirname(os.path.dirname(__file__))
    if format == 'ico':
        icon_path = os.path.join(script_dir, 'assets', 'icons', 'window.ico')
    else:
        # Try PNG files in order of preference
        for size in ['64', '32', '16']:
            icon_path = os.path.join(script_dir, 'assets', 'icons', f'window_{size}.png')
            if os.path.exists(icon_path):
                return icon_path
        # Fallback to ICO if no PNG found
        icon_path = os.path.join(script_dir, 'assets', 'icons', 'window.ico')
    
    return icon_path

# Create the assets directory structure when the module is imported
ensure_assets_dir()
