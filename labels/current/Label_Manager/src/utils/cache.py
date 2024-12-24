"""
Cache utility for the Label Manager application.
"""
import time
import logging
from pathlib import Path
from typing import Any, Optional, Dict
import json
from config import CACHE_DIR, CACHE_TTL, CACHE_ENABLED, MAX_CACHE_SIZE

class Cache:
    """Simple file-based cache implementation."""
    
    def __init__(self):
        """Initialize the cache."""
        self.logger = logging.getLogger(__name__)
        self.cache_dir = Path(CACHE_DIR)
        self.enabled = CACHE_ENABLED
        
    def _get_cache_path(self, key: str) -> Path:
        """Get the cache file path for a key."""
        # Use hash of key as filename to avoid invalid characters
        filename = f"{hash(key)}.cache"
        return self.cache_dir / filename
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        if not self.enabled:
            return default
            
        try:
            cache_path = self._get_cache_path(key)
            if not cache_path.exists():
                return default
                
            with cache_path.open('r') as f:
                data = json.load(f)
                
            # Check if cache has expired
            if time.time() - data['timestamp'] > CACHE_TTL:
                self.delete(key)
                return default
                
            return data['value']
            
        except Exception as e:
            self.logger.error(f"Error reading from cache: {e}")
            return default
            
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.enabled:
            return False
            
        try:
            # Check cache size
            if self._get_cache_size() > MAX_CACHE_SIZE:
                self.clear()
                
            cache_path = self._get_cache_path(key)
            data = {
                'value': value,
                'timestamp': time.time(),
                'ttl': ttl or CACHE_TTL
            }
            
            with cache_path.open('w') as f:
                json.dump(data, f)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error writing to cache: {e}")
            return False
            
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting from cache: {e}")
            return False
            
    def clear(self) -> bool:
        """
        Clear all cached values.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            for cache_file in self.cache_dir.glob('*.cache'):
                cache_file.unlink()
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
            return False
            
    def _get_cache_size(self) -> int:
        """Get the total size of all cache files in bytes."""
        try:
            return sum(f.stat().st_size for f in self.cache_dir.glob('*.cache'))
        except Exception:
            return 0
