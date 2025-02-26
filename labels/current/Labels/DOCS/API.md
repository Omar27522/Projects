# API Documentation

## Core Modules

### BarcodeGenerator

#### Class: `BarcodeGenerator`
Main class for generating and managing label barcodes.

```python
def generate_label(
    text: str, 
    barcode: str, 
    size: tuple = (600, 310)
) -> PIL.Image:
    """Generate a label with text and barcode."""
```

```python
def validate_barcode(
    barcode: str
) -> bool:
    """Validate barcode format and checksum."""
```

### WindowManager

#### Class: `WindowManager`
Handles window creation and management.

```python
def create_window(
    title: str,
    size: tuple,
    position: str = "center"
) -> tk.Toplevel:
    """Create a new window with specified parameters."""
```

```python
def make_draggable(
    window: tk.Toplevel
) -> None:
    """Add drag functionality to window."""
```

### ConfigManager

#### Class: `ConfigManager`
Manages application configuration and settings.

```python
def load_config() -> dict:
    """Load configuration from file."""
```

```python
def save_config(
    config: dict
) -> bool:
    """Save configuration to file."""
```

## UI Components

### MainWindow

#### Class: `MainWindow`
Primary application window implementation.

```python
def preview_label(
    size: int = 4
) -> None:
    """Generate and display label preview."""
```

```python
def save_label(
    path: str = None
) -> bool:
    """Save current label to file."""
```

### ViewFilesWindow

#### Class: `ViewFilesWindow`
File management and preview window.

```python
def refresh_list(
    directory: str = None
) -> None:
    """Refresh file list view."""
```

```python
def toggle_preview(
    state: bool
) -> None:
    """Toggle preview panel visibility."""
```

## Utility Functions

### CSV Processing

```python
def process_csv(
    file_path: str,
    callback: Callable = None
) -> List[Dict]:
    """Process CSV file and return label data."""
```

### File Management

```python
def sanitize_filename(
    name: str
) -> str:
    """Clean filename for safe saving."""
```

```python
def get_unique_filename(
    base_name: str,
    directory: str
) -> str:
    """Generate unique filename in directory."""
```

## Event System

### Custom Events

```python
class LabelEvent:
    """Base class for label-related events."""
    PREVIEW_UPDATED = "<<PreviewUpdated>>"
    SAVE_COMPLETED = "<<SaveCompleted>>"
    PRINT_STARTED = "<<PrintStarted>>"
    PRINT_COMPLETED = "<<PrintCompleted>>"
```

### Event Handlers

```python
def bind_label_events(
    widget: tk.Widget,
    events: List[str],
    callback: Callable
) -> None:
    """Bind label events to callback."""
```

## Constants and Enums

### Window States
```python
class WindowState(Enum):
    NORMAL = "normal"
    MINIMIZED = "iconic"
    MAXIMIZED = "zoomed"
    HIDDEN = "withdrawn"
```

### Preview Sizes
```python
PREVIEW_SIZES = {
    3: (300, 155),
    4: (400, 207),
    5: (500, 259)
}
```

## Error Handling

### Custom Exceptions
```python
class LabelMakerError(Exception):
    """Base exception for Label Maker."""
    pass

class ConfigError(LabelMakerError):
    """Configuration related errors."""
    pass

class BarcodeError(LabelMakerError):
    """Barcode generation errors."""
    pass
```

## Configuration Schema

### Settings Structure
```json
{
    "window_settings": {
        "font_size_large": int,
        "font_size_medium": int,
        "transparency_level": float,
        "always_on_top": bool
    },
    "label_settings": {
        "barcode_width": int,
        "barcode_height": int,
        "DPI": int
    }
}
```
