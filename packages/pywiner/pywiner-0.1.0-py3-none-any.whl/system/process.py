import os
import subprocess
import tempfile

def list_processes():
    output = subprocess.check_output("tasklist /fo csv /nh", shell=True, text=True)
    processes = []
    for line in output.strip().split('\n'):
        parts = line.split(',')
        if len(parts) > 0:
            processes.append(parts[0].strip().strip('"'))
    return processes

def find_process(name):
    output = subprocess.check_output(f"tasklist /fo csv /nh /fi \"imagename eq {name}\"", shell=True, text=True)
    if output.strip():
        parts = output.strip().split(',')
        if len(parts) > 1:
            try:
                return int(parts[1].strip().strip('"'))
            except (ValueError, IndexError):
                pass
    return None

def kill_process(pid):
    try:
        subprocess.run(f"taskkill /F /PID {pid}", check=True, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def start_command(command, shell=True):
    subprocess.Popen(command, shell=shell)

def start(exe_path, args=None):
    if args is None:
        args = []
    subprocess.Popen([exe_path] + args)

def exec_batch(batch_code):
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.bat') as temp_file:
            temp_file.write(batch_code)
            temp_batch_path = temp_file.name
        
        subprocess.run(temp_batch_path, shell=True)
    
    finally:
        if os.path.exists(temp_batch_path):
            os.remove(temp_batch_path)