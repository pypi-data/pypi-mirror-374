import os
import platform
import subprocess
from . import path_utils

def set_var(name, value, scope="user"):
    system = platform.system()
    if system == "Windows":
        if scope == "user":
            subprocess.run(["setx", name, value])
        else:
            subprocess.run(["setx", name, value, "/M"])
    else:
        shell_file = os.path.expanduser("~/.bashrc") if scope == "user" else "/etc/environment"
        with open(shell_file, "a") as f:
            f.write(f'\nexport {name}="{value}"\n')
        print(f"{name} set in {shell_file}. Restart shell to apply.")

def get_var(name):
    return os.environ.get(name)

def delete_var(name, scope="user"):
    system = platform.system()
    if system == "Windows":
        key = "HKCU\\Environment" if scope == "user" else "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment"
        subprocess.run(["reg", "delete", key, "/F", "/V", name])
    else:
        shell_file = os.path.expanduser("~/.bashrc") if scope == "user" else "/etc/environment"
        with open(shell_file, "r") as f:
            lines = f.readlines()
        with open(shell_file, "w") as f:
            for line in lines:
                if name not in line:
                    f.write(line)
        print(f"{name} removed from {shell_file}. Restart shell to apply.")

def list_vars(scope="user"):
    system_name = platform.system()

    if system_name == "Windows":
        import winreg

        if scope == "user":
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment")
        else:  # system
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment")

        index = 0
        try:
            while True:
                name, value, _ = winreg.EnumValue(key, index)
                print(f"{name}={value}")
                index += 1
        except OSError:
            pass  # No more items

    else:  # Linux/macOS
        shell_file = os.path.expanduser("~/.bashrc") if scope == "user" else "/etc/environment"
        env_vars = {}

        # Try to read current environment first
        for k, v in os.environ.items():
            env_vars[k] = v

        # Optionally merge variables from shell file
        if os.path.exists(shell_file):
            with open(shell_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("export "):
                        parts = line.replace("export ", "", 1).split("=", 1)
                        if len(parts) == 2:
                            env_vars[parts[0]] = parts[1].strip('"')

        for name, value in env_vars.items():
            print(f"{name}={value}")


# PATH utilities shortcut
path = path_utils
