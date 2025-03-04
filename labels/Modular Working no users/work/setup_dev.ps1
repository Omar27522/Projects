# Setup Development Environment Script
Write-Host "Setting up development environment for Label Maker Management Application..." -ForegroundColor Green

# Create virtual environment if it doesn't exist
if (-not (Test-Path -Path ".\venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment. Make sure Python is installed and in your PATH." -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Install development dependencies
Write-Host "Installing development dependencies..." -ForegroundColor Yellow
pip install pylint pytest autopep8 black

# Create tests directory if it doesn't exist
if (-not (Test-Path -Path ".\tests")) {
    Write-Host "Creating tests directory..." -ForegroundColor Yellow
    New-Item -Path ".\tests" -ItemType Directory | Out-Null
    New-Item -Path ".\tests\__init__.py" -ItemType File | Out-Null
}

# Create a basic test file if it doesn't exist
if (-not (Test-Path -Path ".\tests\test_basic.py")) {
    Write-Host "Creating basic test file..." -ForegroundColor Yellow
    @"
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

if __name__ == '__main__':
    unittest.main()
"@ | Out-File -FilePath ".\tests\test_basic.py" -Encoding utf8
}

# Create a pylintrc file if it doesn't exist
if (-not (Test-Path -Path ".\pylintrc")) {
    Write-Host "Creating pylintrc configuration..." -ForegroundColor Yellow
    pylint --generate-rcfile | Out-File -FilePath ".\pylintrc" -Encoding utf8
}

Write-Host "Development environment setup complete!" -ForegroundColor Green
Write-Host "You can now run the following commands:" -ForegroundColor Cyan
Write-Host "  - python main.pyw                  # Run the application" -ForegroundColor White
Write-Host "  - pylint src                       # Run linting" -ForegroundColor White
Write-Host "  - pytest tests                     # Run tests" -ForegroundColor White
Write-Host "  - black src                        # Format code" -ForegroundColor White
