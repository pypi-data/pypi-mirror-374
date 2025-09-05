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

def exec_vbs(vbs_code):
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.vbs') as temp_file:
            temp_file.write(vbs_code)
            temp_vbs_path = temp_file.name

        subprocess.run(["wscript.exe", temp_vbs_path], check=True)
    
    finally:
        if os.path.exists(temp_vbs_path):
            os.remove(temp_vbs_path)

def delete_file(filepath):
    try:
        os.remove(filepath)
        return True
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        return False
    except Exception as e:
        print(f"Error trying to delete file '{filepath}': {e}")
        return False

def create_file(content, extension, pathtocreate="."):
    filename = f"tempfile_{os.getpid()}"
    filepath = os.path.join(pathtocreate, f"{filename}.{extension}")
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath
    except Exception as e:
        print(f"Error trying to create file: {e}")
        return None

def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        return None
    except Exception as e:
        print(f"Error trying to read file '{filepath}': {e}")
        return None