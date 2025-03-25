import os
import sys
import re
import json
import argparse
from tkinter import messagebox

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_connection(sheet_url, sheet_name):
    """
    Test connection to Google Sheets
    
    Args:
        sheet_url (str): URL of the Google Sheet
        sheet_name (str): Name of the worksheet
        
    Returns:
        tuple: (success, message)
    """
    try:
        # Import required libraries
        try:
            import gspread
            from oauth2client.service_account import ServiceAccountCredentials
        except ImportError:
            return False, "Required libraries not installed. Please install gspread and oauth2client: pip install gspread oauth2client"
        
        # Check if URL is valid
        sheet_id_pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)'
        match = re.match(sheet_id_pattern, sheet_url)
        if not match:
            return False, "Invalid Google Sheet URL format. URL should be in the format: https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID"
        
        # Check for credentials file
        creds_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'credentials.json')
        if not os.path.exists(creds_file):
            return False, f"Credentials file not found at: {creds_file}"
        
        # Define the scope
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # Add credentials to the account
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        
        # Authorize the clientsheet
        client = gspread.authorize(creds)
        
        # Get the sheet
        sheet_id = match.group(1)
        spreadsheet = client.open_by_key(sheet_id)
        
        # Try to access the specified worksheet
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            
            # If we get here, the connection was successful
            return True, f"Successfully connected to sheet '{sheet_name}'"
            
        except gspread.exceptions.WorksheetNotFound:
            # Sheet not found, show available sheets
            all_sheets = [sheet.title for sheet in spreadsheet.worksheets()]
            sheet_list = "\n".join(all_sheets)
            
            return False, f"Sheet '{sheet_name}' not found. Available sheets:\n{sheet_list}"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Main function"""
    # Force UTF-8 encoding for stdout
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        
    parser = argparse.ArgumentParser(description='Test Google Sheets connection')
    parser.add_argument('--url', help='Google Sheet URL')
    parser.add_argument('--name', help='Worksheet name')
    args = parser.parse_args()
    
    # If no arguments are provided, try to read from settings file
    if not args.url or not args.name:
        settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'label_maker_settings.json')
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    
                    if not args.url:
                        args.url = settings.get('google_sheet_url')
                    
                    if not args.name:
                        args.name = settings.get('google_sheet_name')
            except Exception as e:
                print(f"Error reading settings file: {str(e)}")
    
    # Check if we have the required arguments
    if not args.url:
        print("Error: Google Sheet URL is required")
        return
    
    if not args.name:
        print("Error: Worksheet name is required")
        return
    
    # Test the connection
    success, message = test_connection(args.url, args.name)
    
    # Print the result
    if success:
        print("SUCCESS:", message)
    else:
        print("ERROR:", message)

if __name__ == "__main__":
    main()
