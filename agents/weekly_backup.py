# agents/weekly_backup.py

import os
import zipfile
from datetime import datetime

def create_backup():
    date_str = datetime.now().strftime("%Y-%m-%d")
    backup_name = f"backup_{date_str}.zip"
    output_path = os.path.join("backups", backup_name)

    os.makedirs("backups", exist_ok=True)

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as z:
        for folder in ["logs", "memory"]:
            for root, _, files in os.walk(folder):
                for file in files:
                    path = os.path.join(root, file)
                    arcname = os.path.relpath(path, start=".")
                    z.write(path, arcname)

    print(f"✅ Created backup: {output_path}")

if __name__ == "__main__":
    create_backup()
