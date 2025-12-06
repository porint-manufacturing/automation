import sys
import os
import csv
import subprocess
import time

def verify_input_action():
    print("--- Testing Input Action ---")
    
    try:
        # Create test actions file
        actions_file = "tests/temp_input_test.csv"
        with open(actions_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["TargetApp", "Key", "Action", "Value"])
            writer.writeheader()
            writer.writerow({"TargetApp": "メモ帳", "Key": "", "Action": "Launch", "Value": "notepad.exe"})
            writer.writerow({"TargetApp": "メモ帳", "Key": "", "Action": "Wait", "Value": "2"})
            writer.writerow({"TargetApp": "メモ帳", "Key": "EditControl(searchDepth=5)", "Action": "Input", "Value": "Test Input Action"})
            writer.writerow({"TargetApp": "メモ帳", "Key": "", "Action": "Wait", "Value": "0.5"})
            # Close notepad using Exit action (will close without saving)
            writer.writerow({"TargetApp": "メモ帳", "Key": "", "Action": "Exit", "Value": ""})
        
        # Run automator with timeout
        result = subprocess.run(
            [sys.executable, "automator.py", actions_file, "--log-level", "DEBUG"],
            capture_output=True,
            text=True,
            timeout=10  # 10 second timeout
        )
        
        # Check results
        success = True
        
        # Check if Input action was executed
        if "Inputting text: Test Input Action" not in result.stdout:
            print("FAIL: Input action not found in log")
            success = False
        else:
            print("PASS: Input action executed")
        
        # Check if focus was set (UI Automation or Win32 API)
        if "Focus set via UI Automation" in result.stdout or "Win32 SetFocus called" in result.stdout or "Focus successfully set" in result.stdout:
            print("PASS: Focus was set")
        else:
            print("WARNING: Focus setting not clearly confirmed in log")
        
        # Check exit code
        if result.returncode == 0:
            print("PASS: Exit code 0")
        else:
            print(f"FAIL: Exit code {result.returncode}")
            success = False
        
        # Cleanup
        if os.path.exists(actions_file):
            os.remove(actions_file)
        
        if success:
            print("\n=== Input Action Verification: PASS ===")
            return True
        else:
            print("\n=== Input Action Verification: FAIL ===")
            print(f"Output: {result.stdout}")
            print(f"Error: {result.stderr}")
            return False
    
    finally:
        # Ensure notepad is closed
        try:
            subprocess.run(['taskkill', '/F', '/IM', 'notepad.exe'], 
                          capture_output=True, timeout=5)
        except:
            pass

if __name__ == "__main__":
    success = verify_input_action()
    sys.exit(0 if success else 1)
