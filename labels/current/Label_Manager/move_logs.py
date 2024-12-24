import os
import shutil
from pathlib import Path

# Get the current log file path
app_data = os.getenv('APPDATA')
app_name = 'Label Manager'
current_log = Path(app_data) / app_name / 'logs' / 'label_manager.log'

# Get the target directory
target_dir = Path(__file__).parent / 'logs'
target_dir.mkdir(exist_ok=True)
target_log = target_dir / 'label_manager.log'

# Move the file if it exists
if current_log.exists():
    print(f"Moving log from {current_log} to {target_log}")
    shutil.move(str(current_log), str(target_log))
    print("Log file moved successfully!")
else:
    print(f"No log file found at {current_log}")
