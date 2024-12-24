"""
Main entry point for the Label Manager application.
"""
import sys
import logging
import os
from pathlib import Path
from src.gui.main_window import MainWindow
from src.utils.logger import setup_logger
from config import TESSERACT_PATH, APP_NAME, APP_VERSION

def check_dependencies() -> bool:
    """
    Check if all required dependencies are available.
    
    Returns:
        bool: True if all dependencies are available, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    # Check Tesseract installation
    tesseract_path = Path(TESSERACT_PATH)
    if not tesseract_path.exists():
        logger.error(f"Tesseract not found at {tesseract_path}")
        return False
        
    return True

def main():
    """Main application entry point."""
    # Setup logger first
    logger = setup_logger('label_manager')
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    
    try:
        # Check dependencies
        if not check_dependencies():
            logger.error("Required dependencies not found")
            sys.exit(1)
            
        # Test directory access
        test_dir = r"C:\Users\Justin\Documents\Labels"
        if os.path.exists(test_dir):
            logger.info(f"Found labels directory: {test_dir}")
            files = [f for f in os.listdir(test_dir) if f.lower().endswith('.png')]
            logger.info(f"Found {len(files)} PNG files")
            if files:
                logger.info(f"First 5 files: {files[:5]}")
        else:
            logger.error(f"Labels directory not found: {test_dir}")
        
        # Create and run the main window
        app = MainWindow()
        app.run()
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Application shutdown complete")

if __name__ == "__main__":
    main()
