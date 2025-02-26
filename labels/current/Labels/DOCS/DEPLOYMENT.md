# Deployment Guide

## Building and Distribution

### Prerequisites
1. Python 3.7+
2. Required packages:
   ```
   pip install pyinstaller
   pip install -r assets/dependencies/requirements.txt
   ```

### Building the Application

1. **Using PyInstaller**
   ```bash
   pyinstaller --name="Label Maker V3" ^
               --windowed ^
               --icon=assets/icons/app.ico ^
               --add-data="assets;assets" ^
               --add-data="fonts;fonts" ^
               --add-data="docs;docs" ^
               main.pyw
   ```

2. **Output Structure**
   ```
   dist/
   └── Label Maker V3/
       ├── Label Maker V3.exe
       ├── assets/
       │   ├── icons/
       │   └── dependencies/
       ├── fonts/
       └── docs/
   ```

### Installation Package

1. **Creating Installer**
   - Use Inno Setup for Windows installer
   - Include all dependencies
   - Configure start menu shortcuts
   - Set up file associations

2. **Installer Options**
   ```
   [Setup]
   AppName=Label Maker V3
   AppVersion=1.0.2
   DefaultDirName={pf}\Label Maker V3
   DefaultGroupName=Label Maker V3
   OutputBaseFilename=LabelMakerV3_Setup
   ```

## System Requirements

### Minimum Requirements
- Windows 10 or later
- 4GB RAM
- 1GB free disk space
- 1280x720 screen resolution

### Recommended
- Windows 11
- 8GB RAM
- 2GB free disk space
- 1920x1080 screen resolution
- SSD storage

## Installation

### Standard Installation
1. Run `LabelMakerV3_Setup.exe`
2. Follow installation wizard
3. Complete printer setup
4. Verify file associations

### Silent Installation
```bash
LabelMakerV3_Setup.exe /VERYSILENT /SUPPRESSMSGBOXES
```

### Network Deployment
1. Share installer on network
2. Use Group Policy for deployment
3. Configure automatic updates

## Configuration

### Initial Setup
1. Configure printer settings
2. Set default save location
3. Configure auto-switch behavior
4. Set preview preferences

### Network Settings
```json
{
    "network": {
        "shared_directory": "\\\\server\\labels",
        "backup_location": "\\\\backup\\labels",
        "update_server": "\\\\updates\\labelmaker"
    }
}
```

## Updates

### Auto-Update Process
1. Check for updates on startup
2. Download updates in background
3. Install on application close
4. Maintain backup of previous version

### Manual Update
1. Download latest version
2. Run installer
3. Preserve user settings
4. Verify functionality

## Troubleshooting

### Common Installation Issues
1. **Permission Errors**
   - Run as administrator
   - Check file permissions
   - Verify user rights

2. **Missing Dependencies**
   - Install Visual C++ Redistributable
   - Update .NET Framework
   - Check Python runtime

3. **Network Issues**
   - Verify network access
   - Check proxy settings
   - Test file shares

## Maintenance

### Regular Tasks
1. Clear temporary files
2. Backup configuration
3. Update printer settings
4. Check log files

### Backup Process
1. Export user settings
2. Backup label templates
3. Save printer configurations
4. Archive log files

## Security

### File Permissions
- Restrict write access
- Secure configuration files
- Protect templates directory

### Network Security
- Use secure file shares
- Implement access control
- Enable audit logging

## Uninstallation

### Clean Uninstall
1. Run uninstaller
2. Remove user data
3. Delete registry entries
4. Clean temporary files

### Data Preservation
1. Backup user settings
2. Export templates
3. Save printer configs
4. Archive logs
