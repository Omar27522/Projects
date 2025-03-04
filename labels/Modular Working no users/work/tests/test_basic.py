import unittest
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class BasicTests(unittest.TestCase):
    def test_import_main(self):
        """Test that we can import the main module"""
        try:
            import main
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import main module")
            
    def test_config_exists(self):
        """Test that the config directory exists"""
        config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'config')
        self.assertTrue(os.path.exists(config_dir), "Config directory does not exist")

if __name__ == '__main__':
    unittest.main()
