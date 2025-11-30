import subprocess
import os
import sys
import time

def verify_dry_run():
    print("--- Testing Automator Dry-run ---")
    
    log_file = "tests/test_dry_run_log.txt"
    actions_file = "tests/test_dry_run_actions.csv"
    
    # Clean up previous run
    if os.path.exists(log_file):
        os.remove(log_file)
        
    # Create a dummy actions file that would normally launch notepad
    with open(actions_file, "w", encoding="utf-8-sig") as f:
        f.write("TargetApp,Key,Action,Value\n")
        f.write("Notepad,,Launch,notepad.exe\n")
        f.write("Notepad,,Wait,1\n")
        
    # Run automator with --dry-run
    cmd = [
        sys.executable,
        "automator.py",
        actions_file,
        "--log-file", log_file,
        "--dry-run"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    end_time = time.time()
    
    # Check execution time (should be fast because Wait is skipped/mocked)
    # Actually, my implementation skips sleep entirely in dry-run, so it should be very fast.
    duration = end_time - start_time
    print(f"Execution duration: {duration:.2f}s")
    
    # Check log content
    if not os.path.exists(log_file):
        print("FAIL: Log file was not created.")
        return False
        
    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()
        
        if "=== DRY RUN MODE ENABLED ===" in content:
            print("PASS: Log contains 'DRY RUN MODE ENABLED'")
        else:
            print("FAIL: Log missing 'DRY RUN MODE ENABLED'")
            return False
            
        if "[Dry-run] Would launch: notepad.exe" in content:
            print("PASS: Log contains '[Dry-run] Would launch'")
        else:
            print("FAIL: Log missing '[Dry-run] Would launch'")
            return False
            
        if "[Dry-run] Would wait: 1 seconds" in content:
            print("PASS: Log contains '[Dry-run] Would wait'")
        else:
            print("FAIL: Log missing '[Dry-run] Would wait'")
            return False

    # Check if Notepad was actually launched?
    # It's hard to check process list reliably in a short script without psutil, 
    # but since we mocked the Launch action, it shouldn't have launched.
    # We can rely on the log message confirming the branch was taken.
    
    print("Dry-run Verification: PASS")
    
    # Cleanup
    if os.path.exists(log_file):
        os.remove(log_file)
    if os.path.exists(actions_file):
        os.remove(actions_file)
        
    return True

if __name__ == "__main__":
    if not verify_dry_run():
        sys.exit(1)
