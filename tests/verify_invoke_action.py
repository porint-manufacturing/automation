import sys
import os
import csv
import subprocess

def verify_invoke_action():
    print("--- Testing Invoke Action ---")
    
    # Create test actions file
    actions_file = "tests/temp_invoke_test.csv"
    with open(actions_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["TargetApp", "Key", "Action", "Value"])
        writer.writeheader()
        writer.writerow({"TargetApp": "電卓", "Key": "", "Action": "Launch", "Value": "calc.exe"})
        writer.writerow({"TargetApp": "電卓", "Key": "", "Action": "Wait", "Value": "2"})
        writer.writerow({"TargetApp": "電卓", "Key": "ButtonControl(AutomationId='num5Button')", "Action": "Invoke", "Value": ""})
        writer.writerow({"TargetApp": "電卓", "Key": "", "Action": "Wait", "Value": "0.5"})
        writer.writerow({"TargetApp": "電卓", "Key": "", "Action": "Exit", "Value": ""})
    
    # Run automator
    result = subprocess.run(
        [sys.executable, "automator.py", actions_file, "--log-level", "DEBUG"],
        capture_output=True,
        text=True
    )
    
    # Check results
    success = True
    
    # Check if Invoke action was executed
    if "Invoking" in result.stdout or "Invoke()" in result.stdout:
        print("PASS: Invoke action executed")
    else:
        print("FAIL: Invoke action not found in log")
        success = False
    
    # Check if focus was set
    if "Focus set" in result.stdout or "Win32 SetFocus" in result.stdout:
        print("PASS: Focus was set")
    else:
        print("WARNING: Focus setting not clearly confirmed")
    
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
        print("\n=== Invoke Action Verification: PASS ===")
        return True
    else:
        print("\n=== Invoke Action Verification: FAIL ===")
        print(f"Output: {result.stdout[-500:]}")
        return False

if __name__ == "__main__":
    success = verify_invoke_action()
    sys.exit(0 if success else 1)
