"""
Local repository management for label files.
"""
import os
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Optional
from config import LABELS_DIR, SUPPORTED_EXTENSIONS

class LocalRepository:
    """Manages local storage and retrieval of label files."""
    
    def __init__(self):
        """Initialize the local repository manager."""
        self.logger = logging.getLogger(__name__)
        self.labels_dir = Path(LABELS_DIR)
        self.labels_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        self.logger.info(f"Initialized local repository at: {self.labels_dir}")
        
    def list_files(self, force_refresh: bool = False) -> List[Dict]:
        """
        List all label files in the repository.
        
        Args:
            force_refresh: Whether to force a refresh of the file list
            
        Returns:
            List of dictionaries containing file information
        """
        try:
            self.logger.info(f"Listing files in: {self.labels_dir}")
            files = []
            
            if not self.labels_dir.exists():
                self.logger.error(f"Labels directory does not exist: {self.labels_dir}")
                return []
                
            for file_path in self.labels_dir.glob('*'):
                if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS['labels']:
                    files.append({
                        'name': file_path.name,
                        'path': str(file_path),  # Use full path
                        'type': 'file',
                        'size': file_path.stat().st_size,
                        'modified': file_path.stat().st_mtime
                    })
            
            files.sort(key=lambda x: x['modified'], reverse=True)
            self.logger.info(f"Found {len(files)} files")
            return files
            
        except Exception as e:
            self.logger.error(f"Error listing files: {e}", exc_info=True)
            return []
            
    def get_file_path(self, file_info: Dict) -> Path:
        """
        Get the full path of a file.
        
        Args:
            file_info: Dictionary containing file information
            
        Returns:
            Path object for the file
        """
        return Path(file_info['path'])
            
    def add_file(self, source_path: str, file_name: Optional[str] = None) -> bool:
        """
        Add a file to the repository.
        
        Args:
            source_path: Path to the source file
            file_name: Optional new name for the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            source_path = Path(source_path)
            if not source_path.is_file():
                self.logger.error(f"Source file not found: {source_path}")
                return False
                
            if file_name is None:
                file_name = source_path.name
                
            if source_path.suffix.lower() not in SUPPORTED_EXTENSIONS['labels']:
                self.logger.error(f"Unsupported file type: {source_path.suffix}")
                return False
                
            # Ensure labels directory exists
            self.labels_dir.mkdir(parents=True, exist_ok=True)
            
            dest_path = self.labels_dir / file_name
            shutil.copy2(source_path, dest_path)
            self.logger.info(f"Added file: {file_name} to {dest_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding file: {e}", exc_info=True)
            return False
            
    def load_files_from_directory(self, directory: str) -> int:
        """
        Load all supported files from a directory.
        
        Args:
            directory: Path to source directory
            
        Returns:
            int: Number of files successfully loaded
        """
        try:
            directory = Path(directory)
            if not directory.is_dir():
                raise ValueError(f"Invalid directory: {directory}")
                
            # Ensure labels directory exists
            self.labels_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Loading files from: {directory}")
            files_loaded = 0
            
            for file_path in directory.glob('*'):
                if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS['labels']:
                    if self.add_file(str(file_path)):
                        files_loaded += 1
            
            self.logger.info(f"Successfully loaded {files_loaded} files")
            return files_loaded
            
        except Exception as e:
            self.logger.error(f"Error loading directory: {e}", exc_info=True)
            raise
            
    def delete_file(self, file_info: Dict) -> bool:
        """
        Delete a file from the repository.
        
        Args:
            file_info: Dictionary containing file information
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_path = self.get_file_path(file_info)
            if file_path.exists():
                file_path.unlink()
                self.logger.info(f"Deleted file: {file_info['name']}")
                return True
            else:
                self.logger.error(f"File not found: {file_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting file: {e}", exc_info=True)
            return False
            
    def cleanup(self):
        """Clean up any temporary resources."""
        pass
