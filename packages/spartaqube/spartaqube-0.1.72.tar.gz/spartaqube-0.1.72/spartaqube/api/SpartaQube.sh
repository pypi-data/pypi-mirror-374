#!/bin/bash

# Navigate to the directory of the script
cd "$(dirname "$0")"

# Run the Python script
python3 spartaqube_launcher.py

# Pause for user input
read -p "Press Enter to continue..."