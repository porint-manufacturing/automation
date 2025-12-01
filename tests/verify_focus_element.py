import sys
import os
import csv
import subprocess
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from automator import Automator

def verify_focus_element():
    print("--- Testing FocusElement Action ---")
    
    actions_file = "tests/temp_focus_element.csv"
    target_app = "タイトルなし - メモ帳"
    
    with open(actions_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["TargetApp", "Key", "Action", "Value"])
        writer.writeheader()
        writer.writerow({"TargetApp": "", "Key": "", "Action": "Launch", "Value": "notepad.exe"})
        writer.writerow({"TargetApp": target_app, "Key": "", "Action": "Wait", "Value": "2"})
        
        # Test: FocusElement on DocumentControl
        # Then SendKeys "Hello"
        writer.writerow({"TargetApp": target_app, "Key": "DocumentControl(searchDepth=5)", "Action": "FocusElement", "Value": ""})
        writer.writerow({"TargetApp": target_app, "Key": "", "Action": "SendKeys", "Value": "Hello Focus"})
        
        # Verify content
        writer.writerow({"TargetApp": target_app, "Key": "DocumentControl(searchDepth=5)", "Action": "VerifyValue", "Value": "Hello Focus"})
        
    print("Created temp actions file.")
    
    log_file = "tests/verify_focus_element.log"
    # Run with log file
    cmd = [
        sys.executable, "automator.py", 
        actions_file, 
        "--log-file", log_file,
        "--log-level", "INFO"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        
        # Check log for "Focusing element"
        with open(log_file, "r", encoding="utf-8") as f:
            log_content = f.read()
            
        if "Focusing element" in log_content and "DocumentControl" in log_content:
            print("FocusElement Verification: PASS (Log confirmed)")
        else:
            print("FocusElement Verification: FAIL (Log missing expected message)")
            print("Log content snippet:", log_content[-500:])
            
    except subprocess.CalledProcessError as e:
        print(f"FocusElement Verification: FAIL - Process error {e}")
    except Exception as e:
        print(f"FocusElement Verification: FAIL - {e}")
    finally:
        if os.path.exists(actions_file): os.remove(actions_file)
        if os.path.exists(log_file): os.remove(log_file)
        subprocess.run("taskkill /f /im notepad.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    verify_focus_element()
