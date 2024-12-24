"""
Logger configuration for the Label Manager application.
"""
import logging
import logging.handlers
from config import LOG_CONFIG
from pathlib import Path

def setup_logger(name: str) -> logging.Logger:
    """
    Configure and return a logger instance.
    
    Args:
        name: Name of the logger
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Skip if logger is already configured
    if logger.handlers:
        return logger
        
    logger.setLevel(LOG_CONFIG['level'])
    
    # Ensure log directory exists
    log_file = Path(LOG_CONFIG['filename'])
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(LOG_CONFIG['format']))
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOG_CONFIG['format']))
    logger.addHandler(console_handler)
    
    return logger
