import uiautomation as auto
import subprocess
import time
import os
import sys

def verify_invoke_select():
    print("=== Invoke and Select Verification ===")
    
    # Launch Calculator
    print("Launching Calculator...")
    subprocess.Popen("calc.exe", shell=True)
    time.sleep(2)
    
    # Find window
    win = auto.WindowControl(searchDepth=1, Name='電卓')
    if not win.Exists(maxSearchSeconds=3):
        win = auto.WindowControl(searchDepth=1, Name='Calculator')
    
    if not win.Exists():
        print("FAIL: Calculator window not found.")
        return False
    
    print(f"Window found: {win.Name}")
    
    # Test Invoke pattern
    print("\n1. Testing Invoke pattern...")
    btn5 = win.ButtonControl(AutomationId='num5Button')
    if not btn5.Exists(maxSearchSeconds=2):
        print("FAIL: Button '5' not found.")
        return False
    
    # Get InvokePattern
    invoke = btn5.GetPattern(auto.PatternId.InvokePattern)
    if invoke:
        print("PASS: InvokePattern found on button '5'")
        invoke.Invoke()
        print("PASS: Invoked button '5'")
    else:
        print("FAIL: InvokePattern not found on button '5'")
        return False
    
    time.sleep(0.5)
    
    # Test with another button
    btnPlus = win.ButtonControl(AutomationId='plusButton')
    if btnPlus.Exists(maxSearchSeconds=1):
        invoke2 = btnPlus.GetPattern(auto.PatternId.InvokePattern)
        if invoke2:
            invoke2.Invoke()
            print("PASS: Invoked button 'Plus'")
        else:
            print("FAIL: InvokePattern not found on 'Plus'")
            return False
    
    time.sleep(0.5)
    
    btn3 = win.ButtonControl(AutomationId='num3Button')
    if btn3.Exists(maxSearchSeconds=1):
        invoke3 = btn3.GetPattern(auto.PatternId.InvokePattern)
        if invoke3:
            invoke3.Invoke()
            print("PASS: Invoked button '3'")
    
    time.sleep(0.5)
    
    # Close calculator
    print("\nClosing Calculator...")
    win.Close()
    
    print("\n=== Invoke Verification: PASS ===")
    return True

if __name__ == "__main__":
    auto.SetProcessDpiAwareness(2)
    success = verify_invoke_select()
    sys.exit(0 if success else 1)
