import sys
import os
import csv
import subprocess

def verify_click_action():
    print("--- Testing Click Action ---")
    
    # Create test actions file
    actions_file = "tests/temp_click_test.csv"
    with open(actions_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["TargetApp", "Key", "Action", "Value"])
        writer.writeheader()
        writer.writerow({"TargetApp": "電卓", "Key": "", "Action": "Launch", "Value": "calc.exe"})
        writer.writerow({"TargetApp": "電卓", "Key": "", "Action": "Wait", "Value": "2"})
        writer.writerow({"TargetApp": "電卓", "Key": "ButtonControl(AutomationId='num7Button')", "Action": "Click", "Value": ""})
        writer.writerow({"TargetApp": "電卓", "Key": "", "Action": "Wait", "Value": "0.5"})
        writer.writerow({"TargetApp": "電卓", "Key": "", "Action": "Exit", "Value": ""})
    
    # Run automator
    result = subprocess.run(
        [sys.executable, "automator.py", actions_file, "--log-level", "INFO"],
        capture_output=True,
        text=True
    )
    
    # Check results
    success = True
    
    # Check if Click action was executed
    if "Clicking element" in result.stdout:
        print("PASS: Click action executed")
    else:
        print("FAIL: 'Clicking element' not found in log")
        success = False
    
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
        print("\n=== Click Action Verification: PASS ===")
        return True
    else:
        print("\n=== Click Action Verification: FAIL ===")
        print(f"Output: {result.stdout[-500:]}")
        return False

if __name__ == "__main__":
    success = verify_click_action()
    sys.exit(0 if success else 1)
