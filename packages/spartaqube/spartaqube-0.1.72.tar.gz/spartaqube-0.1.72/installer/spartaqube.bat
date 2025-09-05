@echo off

REM Get the current directory where the .bat file is located
set current_path=%~dp0

REM Set target_path to the current path
set target_path=%current_path%

REM Run the Python script (which is in the current directory)
python "%target_path%spartaqube_launcher.py" %*