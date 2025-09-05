
import os
import sys
import subprocess
import platform

def main_launcher():
    is_windows = platform.system() == "Windows"
    if not os.path.exists('C:\\Users\\benme\\Desktop\\Projects\\spartacloud\\web\\venv'):
        print(f"Virtual environment not found")
        sys.exit(1)

    if not os.path.exists('C:\\Users\\benme\\Desktop\\Projects\\spartacloud\\web\\venv\\Scripts\\python.exe'):
        raise FileNotFoundError(f"Python executable not found")
    if not os.path.exists('C:\\Users\\benme\\Desktop\\Projects\\spartaqube\\web\\spartaqube\\api\\spartaqube_exec.py'):
        raise FileNotFoundError(f"Script not found")

    if is_windows:
        # On Windows: Activate the virtual environment using cmd.exe
        command = f'cmd.exe /k "C:\\Users\\benme\\Desktop\\Projects\\spartacloud\\web\\venv\\Scripts\\activate.bat && python "C:\\Users\\benme\\Desktop\\Projects\\spartaqube\\web\\spartaqube\\api\\spartaqube_exec.py"'
        subprocess.run(command, shell=True)
    else:
        # On macOS/Linux: Use bash to activate the virtual environment
        command = f'source "C:\\Users\\benme\\Desktop\\Projects\\spartacloud\\web\\venv\\Scripts\\activate.bat" && python "C:\\Users\\benme\\Desktop\\Projects\\spartaqube\\web\\spartaqube\\api\\spartaqube_exec.py"'
        subprocess.run(command, shell=True, executable="/bin/bash")

if __name__ == "__main__":
    main_launcher()
