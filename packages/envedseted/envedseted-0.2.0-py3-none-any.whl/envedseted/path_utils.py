import os
import platform
import subprocess
import json

BACKUP_FILE = os.path.expanduser("~/.envset_path_backup.json")

def _get_path_list(scope="user"):
    path_var = os.environ.get("PATH", "")
    sep = ";" if platform.system() == "Windows" else ":"
    return path_var.split(sep)

def _set_path_list(path_list, scope="user"):
    sep = ";" if platform.system() == "Windows" else ":"
    new_path = sep.join(path_list)
    if platform.system() == "Windows":
        # User PATH update
        subprocess.run(["setx", "PATH", new_path])
    else:
        shell_file = os.path.expanduser("~/.bashrc") if scope == "user" else "/etc/environment"
        with open(shell_file, "a") as f:
            f.write(f'\nexport PATH="{new_path}"\n')
        print(f"Updated PATH in {shell_file}. Restart shell to apply.")

def add(dir_path, scope="user", position="end"):
    path_list = _get_path_list(scope)
    if dir_path in path_list:
        print(f"{dir_path} already in PATH")
        return
    if position == "start":
        path_list.insert(0, dir_path)
    else:
        path_list.append(dir_path)
    _set_path_list(path_list, scope)
    print(f"Added {dir_path} to PATH")

def remove(dir_path, scope="user"):
    path_list = _get_path_list(scope)
    if dir_path not in path_list:
        print(f"{dir_path} not found in PATH")
        return
    path_list.remove(dir_path)
    _set_path_list(path_list, scope)
    print(f"Removed {dir_path} from PATH")

def list(scope="user"):
    path_list = _get_path_list(scope)
    for idx, dir_path in enumerate(path_list, start=1):
        print(f"{idx}. {dir_path}")

def backup():
    path_list = _get_path_list()
    with open(BACKUP_FILE, "w") as f:
        json.dump(path_list, f)
    print(f"PATH backed up to {BACKUP_FILE}")

def restore():
    if not os.path.exists(BACKUP_FILE):
        print("No backup found")
        return
    with open(BACKUP_FILE, "r") as f:
        path_list = json.load(f)
    _set_path_list(path_list)
    print("PATH restored from backup")
