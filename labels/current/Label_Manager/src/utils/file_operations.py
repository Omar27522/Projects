"""
File system operations for the Label Manager.
"""
import os
import shutil
import tempfile
from datetime import datetime

class FileManager:
    def __init__(self, base_path):
        self.base_path = base_path
        self.ensure_directory_exists()

    def ensure_directory_exists(self):
        """Ensure the base directory exists."""
        os.makedirs(self.base_path, exist_ok=True)

    def get_file_info(self, filepath):
        """Get file information including size and modification date."""
        try:
            stats = os.stat(filepath)
            return {
                'size': self.format_size(stats.st_size),
                'date': datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M'),
                'path': filepath
            }
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None

    @staticmethod
    def format_size(size_bytes):
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def list_files(self, directory=None):
        """List all files in the specified directory."""
        directory = directory or self.base_path
        files = []
        try:
            for entry in os.scandir(directory):
                if entry.is_file():
                    file_info = self.get_file_info(entry.path)
                    if file_info:
                        files.append(file_info)
        except Exception as e:
            print(f"Error listing files: {e}")
        return files

    def create_temp_file(self, content, suffix=None):
        """Create a temporary file with the given content."""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                if isinstance(content, str):
                    content = content.encode()
                tmp.write(content)
                return tmp.name
        except Exception as e:
            print(f"Error creating temp file: {e}")
            return None

    def save_file(self, source_path, destination_name):
        """Save a file to the base directory."""
        try:
            destination_path = os.path.join(self.base_path, destination_name)
            shutil.copy2(source_path, destination_path)
            return destination_path
        except Exception as e:
            print(f"Error saving file: {e}")
            return None
