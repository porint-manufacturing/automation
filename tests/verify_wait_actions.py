import sys
import os
import csv
import subprocess
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from automator import Automator

def verify_wait_actions():
    print("--- Testing WaitUntil Actions ---")
    
    actions_file = "tests/temp_wait_actions.csv"
    
    # Create actions file
    # 1. Launch Notepad
    # 2. WaitUntilVisible for text area (should pass quickly)
    # 3. WaitUntilEnabled for text area (should pass quickly)
    # 4. WaitUntilGone for a dummy element (should timeout - we'll set short timeout)
    #    Actually, let's test PASS case for Gone: Close notepad, then WaitUntilGone for window.
    
    with open(actions_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["TargetApp", "Key", "Action", "Value"])
        writer.writeheader()
        writer.writerow({"TargetApp": "", "Key": "", "Action": "Launch", "Value": "notepad.exe"})
        # Use regex for Notepad window title to support English/Japanese
        # But Automator.find_window currently does exact match on Name unless we change logic.
        # Let's check automator.py find_window logic.
        # It uses: window = auto.WindowControl(searchDepth=1, Name=target_app)
        # If we want regex, we might need to change automator or use exact name.
        # Found name: 'タイトルなし - メモ帳'
        target_app = "タイトルなし - メモ帳"
        writer.writerow({"TargetApp": target_app, "Key": "", "Action": "Wait", "Value": "2"}) 
        
        # Test 1: WaitUntilVisible
        writer.writerow({"TargetApp": target_app, "Key": "DocumentControl(searchDepth=5)", "Action": "WaitUntilVisible", "Value": "5"})
        
        # Test 2: WaitUntilEnabled
        writer.writerow({"TargetApp": target_app, "Key": "DocumentControl(searchDepth=5)", "Action": "WaitUntilEnabled", "Value": "5"})
        
        # Test 3: WaitUntilGone (Negative test - expect timeout)
        # We'll use a non-existent element.
        # writer.writerow({"TargetApp": "Notepad", "Key": "ButtonControl(Name='NonExistent')", "Action": "WaitUntilGone", "Value": "2"})
        
        # Test 4: WaitUntilGone (Positive test)
        # Close notepad then wait for window to be gone.
        # But Automator finds window by "TargetApp" column.
        # If we want to wait for the *Window* to be gone, we might need a trick.
        # Automator.find_window uses TargetApp.
        # But WaitUntilGone uses find_element_by_path(window, key).
        # If we want to check if an element inside is gone, that works.
        # Let's try to close the "File" menu? No, hard to open/close.
        
        # Alternative: Launch a second notepad, close it, wait for it to be gone? Complex.
        # Let's just stick to Visible/Enabled for now as they are most critical.
        # And maybe WaitUntilGone for a popup?
        
    print("Created temp actions file.")
    
    automator = Automator(actions_file)
    try:
        automator.load_actions()
        automator.run()
        print("WaitUntil Actions Verification: PASS")
    except Exception as e:
        print(f"WaitUntil Actions Verification: FAIL - {e}")
    finally:
        # Cleanup
        if os.path.exists(actions_file): os.remove(actions_file)
        # Kill notepad
        subprocess.run("taskkill /f /im notepad.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    verify_wait_actions()
