import uiautomation as auto
import subprocess
import time

def reproduce_recursive_fail():
    print("Launching Calc...")
    subprocess.Popen("calc.exe", shell=True)
    time.sleep(2)
    
    print("Searching for Calculator window...")
    win = auto.WindowControl(searchDepth=1, Name='電卓')
    if not win.Exists(maxSearchSeconds=3):
        win = auto.WindowControl(searchDepth=1, Name='Calculator')
        
    if not win.Exists():
        print("FAIL: Calculator window not found.")
        return

    print(f"Window found: {win.Name}")
    
    # Mimic automator.py logic
    # Part: CustomControl(AutomationId='NavView', searchDepth=1)
    
    search_params = {"ControlTypeName": "CustomControl", "AutomationId": "NavView", "searchDepth": 1}
    found_index = 1
    
    print(f"1. Search with params: {search_params}")
    target = win.Control(foundIndex=found_index, **search_params)
    if target.Exists(maxSearchSeconds=1):
        print("PASS: Found at depth 1 (Unexpected)")
    else:
        print("FAIL: Not found at depth 1 (Expected)")
        
        # Fallback 1: Depth + 1
        search_params["searchDepth"] = 2
        print(f"2. Search with params: {search_params}")
        # Force failure to test recursive
        # target = win.Control(foundIndex=found_index, **search_params)
        if False: # target.Exists(maxSearchSeconds=1):
            print("PASS: Found at depth 2")
        else:
            print("FAIL: Not found at depth 2 (Forced failure)")
            
            # Fallback 2: Recursive (remove searchDepth)
            if "searchDepth" in search_params:
                del search_params["searchDepth"]
            print(f"3. Search with params: {search_params}")
            target = win.Control(foundIndex=found_index, **search_params)
            if target.Exists(maxSearchSeconds=1):
                print("PASS: Found recursively (implicit depth)")
            else:
                print("FAIL: Not found recursively (implicit depth)")
                
                # Try explicit max depth
                search_params["searchDepth"] = 0xFFFFFFFF
                print(f"4. Search with params: {search_params}")
                target = win.Control(foundIndex=found_index, **search_params)
                if target.Exists(maxSearchSeconds=1):
                    print("PASS: Found recursively (explicit max depth)")
                else:
                    print("FAIL: Not found recursively (explicit max depth)")

if __name__ == "__main__":
    auto.SetProcessDpiAwareness(2)
    reproduce_recursive_fail()
