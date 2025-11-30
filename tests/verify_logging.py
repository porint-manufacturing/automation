import subprocess
import os
import sys

def verify_logging():
    print("--- Testing Automator Logging ---")
    
    log_file = "tests/test_log.txt"
    actions_file = "tests/test_logging_actions.csv"
    
    # Clean up previous run
    if os.path.exists(log_file):
        os.remove(log_file)
        
    # Create a dummy actions file
    with open(actions_file, "w", encoding="utf-8-sig") as f:
        f.write("TargetApp,Key,Action,Value\n")
        f.write("TestApp,,Wait,0.1\n")
        
    # Run automator with logging
    cmd = [
        sys.executable,
        "automator.py",
        actions_file,
        "--log-file", log_file,
        "--log-level", "DEBUG"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Check if log file exists
    if not os.path.exists(log_file):
        print("FAIL: Log file was not created.")
        return False
        
    # Check log content
    with open(log_file, "r", encoding="utf-8") as f:
        content = f.read()
        print(f"Log content length: {len(content)} bytes")
        
        if "Loading actions from" in content:
            print("PASS: Log contains 'Loading actions from'")
        else:
            print("FAIL: Log missing 'Loading actions from'")
            return False
            
        if "Waiting 0.1 seconds" in content:
            print("PASS: Log contains 'Waiting 0.1 seconds'")
        else:
            print("FAIL: Log missing 'Waiting 0.1 seconds'")
            return False
            
    print("Logging Verification: PASS")
    
    # Cleanup
    if os.path.exists(log_file):
        os.remove(log_file)
    if os.path.exists(actions_file):
        os.remove(actions_file)
        
    return True

if __name__ == "__main__":
    if not verify_logging():
        sys.exit(1)
