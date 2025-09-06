import platform
import os
import shutil

def get_os_info():
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version()
    }

def get_cpu_info():
    return platform.processor()

def get_drives():
    drives = []
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if os.path.exists(f'{letter}:\\'):
            try:
                total, used, free = shutil.disk_usage(f'{letter}:\\')
                drives.append({
                    "drive": f"{letter}:\\",
                    "total_space_gb": round(total / (1024**3), 2),
                    "free_space_gb": round(free / (1024**3), 2)
                })
            except Exception:
                pass
    return drives