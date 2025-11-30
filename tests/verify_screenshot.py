import subprocess
import os
import sys
import glob

def verify_screenshot():
    print("--- Testing Automator Screenshot ---")
    
    log_file = "tests/test_screenshot_log.txt"
    actions_file = "tests/test_screenshot_actions.csv"
    errors_dir = "errors"
    
    # Clean up previous run
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # Clean up errors dir (optional, maybe just check for new files)
    # For verification, let's count files before and after
    if not os.path.exists(errors_dir):
        os.makedirs(errors_dir)
    
    initial_screenshots = len(glob.glob(os.path.join(errors_dir, "*.png")))
    print(f"Initial screenshots: {initial_screenshots}")
        
    # Create a dummy actions file that fails
    with open(actions_file, "w", encoding="utf-8-sig") as f:
        f.write("TargetApp,Key,Action,Value\n")
        f.write("NonExistentWindow,,Click,\n")
        
    # Run automator (expecting failure)
    cmd = [
        sys.executable,
        "automator.py",
        actions_file,
        "--log-file", log_file
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Check log content
    if not os.path.exists(log_file):
        print("FAIL: Log file was not created.")
        return False
        
    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()
        
        if "Action failed:" in content:
            print("PASS: Log contains 'Action failed'")
        else:
            print("FAIL: Log missing 'Action failed'")
            return False
            
        if "Screenshot saved to:" in content:
            print("PASS: Log contains 'Screenshot saved to'")
        else:
            print("FAIL: Log missing 'Screenshot saved to'")
            return False

    # Check if new screenshot exists
    final_screenshots = len(glob.glob(os.path.join(errors_dir, "*.png")))
    print(f"Final screenshots: {final_screenshots}")
    
    if final_screenshots > initial_screenshots:
        print("PASS: New screenshot created in errors/ directory")
    else:
        print("FAIL: No new screenshot created")
        return False
    
    print("Screenshot Verification: PASS")
    
    # Cleanup
    if os.path.exists(log_file):
        os.remove(log_file)
    if os.path.exists(actions_file):
        os.remove(actions_file)
        
    return True

if __name__ == "__main__":
    if not verify_screenshot():
        sys.exit(1)
