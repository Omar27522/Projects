# Troubleshooting Guide

## Common Issues and Solutions

### Print Issues

#### Print Preview Not Showing
**Problem**: Print preview window doesn't appear when clicking print.
**Solution**: 
1. Check if a default printer is set
2. Verify print spooler service is running
3. Restart the application

#### Print Quality Issues
**Problem**: Labels print with poor quality or scaling issues.
**Solution**:
1. Verify DPI settings in configuration
2. Check printer resolution settings
3. Ensure correct label size is selected

### Window Management

#### Auto-Switch Not Working
**Problem**: Windows don't automatically switch as expected.
**Solution**:
1. Verify auto-switch is enabled in settings
2. Check if any windows are pinned
3. Ensure no dialog windows are open

#### Window Position Reset
**Problem**: Windows don't remember their positions.
**Solution**:
1. Check write permissions in app directory
2. Clear window position cache
3. Reset window settings

### Preview Issues

#### Preview Not Updating
**Problem**: Label preview doesn't update with changes.
**Solution**:
1. Check available memory
2. Reduce preview size
3. Clear preview cache

#### Preview Size Issues
**Problem**: Preview appears too large or small.
**Solution**:
1. Cycle through preview sizes (3->4->5)
2. Check display scaling settings
3. Reset preview settings

### File Management

#### CSV Import Failures
**Problem**: CSV files fail to import.
**Solution**:
1. Verify CSV format
2. Check for special characters
3. Ensure required columns exist

#### File Access Errors
**Problem**: Cannot access or save files.
**Solution**:
1. Check file permissions
2. Verify path exists
3. Close files in other applications

### Performance Issues

#### Slow Preview Generation
**Problem**: Label previews generate slowly.
**Solution**:
1. Reduce preview quality
2. Clear temporary files
3. Check available memory

#### Application Freezing
**Problem**: Application becomes unresponsive.
**Solution**:
1. Check system resources
2. Reduce batch size
3. Clear application cache

## Error Messages

### Common Error Messages and Resolutions

#### "Failed to initialize printer"
**Cause**: Printer configuration or access issues
**Resolution**:
1. Check printer connection
2. Verify printer drivers
3. Reset print spooler

#### "Invalid barcode format"
**Cause**: Incorrect barcode input
**Resolution**:
1. Verify barcode format
2. Check input length
3. Remove special characters

#### "Configuration file corrupted"
**Cause**: Settings file issues
**Resolution**:
1. Restore from backup
2. Reset to defaults
3. Check file permissions

## System Requirements

### Minimum Requirements
- Windows 10 or later
- Python 3.7+
- 4GB RAM
- 1GB free disk space

### Recommended Requirements
- Windows 11
- Python 3.9+
- 8GB RAM
- 2GB free disk space
- SSD storage

## Contact Support

If issues persist:
1. Check documentation
2. Search existing issues
3. Create new issue with:
   - Error details
   - Steps to reproduce
   - System information
