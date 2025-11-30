import uiautomation as auto

import subprocess
import time

print("Launching Notepad...")
subprocess.Popen("notepad.exe")
time.sleep(2)

print("--- Top Level Windows ---")
root = auto.GetRootControl()
for window in root.GetChildren():
    if window.Name:
        print(f"Name: '{window.Name}', Class: '{window.ClassName}'")
