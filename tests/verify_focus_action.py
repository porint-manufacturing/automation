import sys
import os
import csv
import subprocess

def verify_focus_action():
    print("--- Testing FocusElement Action ---")
    
    # Create test actions file
    actions_file = "tests/temp_focus_test.csv"
    with open(actions_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["TargetApp", "Key", "Action", "Value"])
        writer.writeheader()
        writer.writerow({"TargetApp": "メモ帳", "Key": "", "Action": "Launch", "Value": "notepad.exe"})
        writer.writerow({"TargetApp": "メモ帳", "Key": "", "Action": "Wait", "Value": "2"})
        writer.writerow({"TargetApp": "メモ帳", "Key": "EditControl(searchDepth=5)", "Action": "FocusElement", "Value": ""})
        writer.writerow({"TargetApp": "メモ帳", "Key": "", "Action": "SendKeys", "Value": "{Alt}{F4}"})
    
    # Run automator
    result = subprocess.run(
        [sys.executable, "automator.py", actions_file, "--log-level", "DEBUG"],
        capture_output=True,
        text=True
    )
    
    # Check results
    success = True
    
    # Check if FocusElement action was executed
    if "Focusing element" in result.stdout:
        print("PASS: FocusElement action executed")
    else:
        print("FAIL: 'Focusing element' not found in log")
        success = False
    
    # Check if focus was successfully set
    if "Focus successfully set" in result.stdout:
        print("PASS: Focus successfully set message found")
    else:
        print("WARNING: 'Focus successfully set' not found")
    
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
        print("\n=== FocusElement Action Verification: PASS ===")
        return True
    else:
        print("\n=== FocusElement Action Verification: FAIL ===")
        print(f"Output: {result.stdout[-500:]}")
        return False

if __name__ == "__main__":
    success = verify_focus_action()
    sys.exit(0 if success else 1)
