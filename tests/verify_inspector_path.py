import uiautomation as auto
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from inspector import Inspector

def verify_inspector():
    print("Launching Calc...")
    import subprocess
    subprocess.Popen("calc.exe", shell=True)
    import time
    time.sleep(2)
    
    win = auto.WindowControl(searchDepth=1, Name='電卓')
    if not win.Exists(maxSearchSeconds=3):
        win = auto.WindowControl(searchDepth=1, Name='Calculator')
        
    if not win.Exists():
        print("FAIL: Calculator window not found.")
        return

    # Find '5' button
    # We use recursive search to find it first
    btn = win.ButtonControl(AutomationId='num5Button', searchDepth=0xFFFFFFFF)
    if not btn.Exists(maxSearchSeconds=2):
        print("FAIL: '5' button not found.")
        return
        
    print(f"Found button: {btn.Name}")
    
    # Test Inspector
    inspector = Inspector(mode="modern")
    path = inspector.get_rpa_path(btn)
    print(f"Generated Path: {path}")
    
    # Verify path is short
    if "->" in path:
        print("FAIL: Path contains '->' (too long)")
    elif "AutomationId='num5Button'" in path:
        print("PASS: Path is short and contains AutomationId")
    else:
        print("FAIL: Path does not contain AutomationId")

if __name__ == "__main__":
    auto.SetProcessDpiAwareness(2)
    verify_inspector()
