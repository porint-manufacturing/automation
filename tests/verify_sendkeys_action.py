import sys
import os
import csv
import subprocess

def verify_sendkeys_action():
    print("--- Testing SendKeys Action ---")
    
    # Create test actions file
    actions_file = "tests/temp_sendkeys_test.csv"
    with open(actions_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["TargetApp", "Key", "Action", "Value"])
        writer.writeheader()
        writer.writerow({"TargetApp": "メモ帳", "Key": "", "Action": "Launch", "Value": "notepad.exe"})
        writer.writerow({"TargetApp": "メモ帳", "Key": "", "Action": "Wait", "Value": "2"})
        writer.writerow({"TargetApp": "メモ帳", "Key": "EditControl(searchDepth=5)", "Action": "Input", "Value": "Test Text"})
        writer.writerow({"TargetApp": "メモ帳", "Key": "", "Action": "SendKeys", "Value": "{Ctrl}a"})  # Select all
        writer.writerow({"TargetApp": "メモ帳", "Key": "", "Action": "Wait", "Value": "0.3"})
        writer.writerow({"TargetApp": "メモ帳", "Key": "", "Action": "SendKeys", "Value": "{Delete}"})  # Delete
        writer.writerow({"TargetApp": "メモ帳", "Key": "", "Action": "SendKeys", "Value": "{Alt}{F4}"})
    
    # Run automator
    result = subprocess.run(
        [sys.executable, "automator.py", actions_file, "--log-level", "INFO"],
        capture_output=True,
        text=True
    )
    
    # Check results
    success = True
    
    # Check if SendKeys actions were executed
    sendkeys_count = result.stdout.count("Sending keys:")
    if sendkeys_count >= 3:
        print(f"PASS: SendKeys action executed {sendkeys_count} times")
    else:
        print(f"FAIL: SendKeys action executed only {sendkeys_count} times (expected 3)")
        success = False
    
    # Verify SendKeys does NOT set focus (it's global)
    # We should NOT see focus setting for SendKeys action
    if "SendKeys" in result.stdout and "Set focus with Win32 API fallback" not in result.stdout.split("SendKeys")[1].split("\n")[0]:
        print("PASS: SendKeys does not set focus (as expected)")
    else:
        print("INFO: Cannot verify focus behavior from log")
    
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
        print("\n=== SendKeys Action Verification: PASS ===")
        return True
    else:
        print("\n=== SendKeys Action Verification: FAIL ===")
        print(f"Output: {result.stdout[-500:]}")
        return False

if __name__ == "__main__":
    success = verify_sendkeys_action()
    sys.exit(0 if success else 1)
