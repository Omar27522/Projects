"""
Utility functions for Google Sheets operations specific to the Label Maker application.
"""

import os
import re
from src.utils.file_utils import file_exists, get_credentials_file_path
from src.utils.sheets_utils import get_authorized_client, validate_sheet_url

def write_to_google_sheet(config_manager, tracking_number, sku, status_callback=None):
    """
    Write tracking number and SKU to Google Sheets.
    
    Args:
        config_manager: The application's configuration manager
        tracking_number: The tracking number to write
        sku: The SKU to write
        status_callback: Optional callback function to update status messages
        
    Returns:
        tuple: (success, message)
    """
    if not (config_manager.settings.google_sheet_url and 
            config_manager.settings.google_sheet_name):
        if status_callback:
            status_callback("Google Sheets not configured", 'red')
        return False, "Google Sheets not configured"
    
    try:
        # Check for credentials file
        creds_file = get_credentials_file_path()
        if not file_exists(creds_file):
            if status_callback:
                status_callback("Google Sheets credentials file not found", 'red')
            return False, "Google Sheets credentials file not found"
        
        # Validate the sheet URL
        is_valid, result = validate_sheet_url(config_manager.settings.google_sheet_url)
        if not is_valid:
            if status_callback:
                status_callback(f"Invalid Google Sheet URL: {result}", 'red')
            return False, f"Invalid Google Sheet URL: {result}"
        
        sheet_id = result
        
        # Get authorized client
        client = get_authorized_client(creds_file)
        if not client:
            if status_callback:
                status_callback("Failed to authorize Google Sheets client", 'red')
            return False, "Failed to authorize Google Sheets client"
        
        # Open the spreadsheet
        spreadsheet = client.open_by_key(sheet_id)
        
        # Get the worksheet
        worksheet = spreadsheet.worksheet(config_manager.settings.google_sheet_name)
        
        # Get the configured row and column
        tracking_col = config_manager.settings.google_sheet_tracking_column
        tracking_row = config_manager.settings.google_sheet_tracking_row
        sku_col = config_manager.settings.google_sheet_sku_column
        sku_row = config_manager.settings.google_sheet_sku_row
        
        # Write tracking number
        worksheet.update_acell(f"{tracking_col}{tracking_row}", tracking_number)
        
        # Write SKU
        worksheet.update_acell(f"{sku_col}{sku_row}", sku)
        
        # Increment row numbers for next entry
        config_manager.settings.google_sheet_tracking_row += 1
        config_manager.settings.google_sheet_sku_row += 1
        config_manager.save_settings()
        
        if status_callback:
            status_callback("Data written to Google Sheets", 'green')
        
        return True, "Data written to Google Sheets"
        
    except ImportError:
        if status_callback:
            status_callback("Google Sheets libraries not installed", 'red')
        return False, "Google Sheets libraries not installed"
    except Exception as e:
        error_msg = str(e)
        if status_callback:
            status_callback(f"Error writing to Google Sheets: {error_msg}", 'red')
        return False, f"Error writing to Google Sheets: {error_msg}"
