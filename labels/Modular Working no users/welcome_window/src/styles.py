"""
Centralized style configurations for the welcome window.
Allows easy theming and style management.
"""

# Material Design Inspired Color Palette
COLORS = {
    'user': {
        'primary': '#4CAF50',     # Green
        'secondary': '#A5D6A7'    # Light Green
    },
    'management': {
        'primary': '#2196F3',     # Blue
        'secondary': '#90CAF9'    # Light Blue
    },
    'labels': {
        'primary': '#FF9800',     # Orange
        'secondary': '#FFCC80'    # Light Orange
    },
    'settings': {
        'primary': '#9E9E9E',     # Gray
        'secondary': '#E0E0E0'    # Light Gray
    }
}

BUTTON_STYLES = {
    'font': {
        'family': 'Arial',
        'sizes': {
            'large': 18,
            'normal': 12
        }
    },
    'width': {
        'large': 20,
        'normal': 15
    },
    'height': {
        'large': 4,
        'normal': 2
    }
}

WINDOW_CONFIG = {
    'title': 'Label Maker V3',
    'size': '500x450',
    'version': 'Ver. 1.0.1.1'
}
