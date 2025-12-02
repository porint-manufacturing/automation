import sys
import os
import csv
import subprocess
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from automator import Automator

def verify_regex_match():
    print("--- Testing Regex Match ---")
    
    actions_file = "tests/temp_regex_actions.csv"
    log_file = "tests/verify_regex_match.log"
    
    # We will use Notepad for testing.
    # Notepad title is usually "Untitled - Notepad" (English) or "無題 - メモ帳" (Japanese).
    # We will try to match it with regex.
    
    # 1. Launch Notepad
    # 2. Match Window with Regex (e.g. regex:.*メモ帳 or regex:.*Notepad)
    # 3. Match Element with RegexName (e.g. DocumentControl with RegexName='.*Editor.*' or similar if applicable, 
    #    but Notepad's main edit control usually has Name 'Text Editor' or similar. 
    #    Let's try to match the "File" menu item which is "ファイル" or "File".
    #    RegexName='(File|ファイル)'
    
    rows = [
        {"TargetApp": "メモ帳", "Key": "", "Action": "Launch", "Value": "notepad.exe"},
        {"TargetApp": "メモ帳", "Key": "", "Action": "Wait", "Value": "2"},
        
        # Test 1: Window Match with Regex
        # "regex:.*メモ帳" should match "無題 - メモ帳"
        # We use a Focus action to test window finding
        {"TargetApp": "regex:.*(メモ帳|Notepad).*", "Key": "", "Action": "Focus", "Value": ""},
        
        # Test 2: Element Match with RegexName
        # Match "File" or "ファイル" menu item
        # Path: Window -> TitleBar -> MenuBar -> MenuItem(Name='ファイル')
        # We will try to find it using RegexName
        # Note: Notepad structure might vary on Win11.
        # Win10: Window -> MenuBar -> MenuItem
        # Let's try a safer one: The main text area.
        # ClassName is 'Edit' (Win10) or 'RichEditD2DPT' (Win11).
        # Name is 'Text Editor' or 'テキスト エディター'.
        # Let's try RegexName='.*Editor.*|.*エディター.*'
        {"TargetApp": "regex:.*(メモ帳|Notepad).*", "Key": "EditControl(RegexName='.*(Editor|エディター).*')", "Action": "Input", "Value": "Regex Test"},
        
        {"TargetApp": "regex:.*(メモ帳|Notepad).*", "Key": "", "Action": "Exit", "Value": ""}
    ]
    
    with open(actions_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["TargetApp", "Key", "Action", "Value"])
        writer.writeheader()
        writer.writerows(rows)
        
    print("Created temp actions file.")
    
    cmd = [
        sys.executable, "automator.py",
        actions_file,
        "--log-file", log_file,
        "--log-level", "DEBUG"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        
        with open(log_file, "r", encoding="utf-8") as f:
            log_content = f.read()
            
        # Checks
        checks = [
            "Using regex pattern: .*(メモ帳|Notepad).*",
            "Searching descendant: {'ControlTypeName': 'EditControl', 'RegexName': '.*(Editor|エディター).*'}"
        ]
        
        all_passed = True
        for check in checks:
            if check in log_content:
                print(f"PASS: Found log '{check}'")
            else:
                print(f"FAIL: Missing log '{check}'")
                all_passed = False
                
        if all_passed:
            print("Regex Verification: PASS")
            if os.path.exists(log_file): os.remove(log_file)
        else:
            print("Regex Verification: FAIL")
            print("--- Log Content ---")
            print(log_content)
            print("-------------------")
            
    except subprocess.CalledProcessError as e:
        print(f"Regex Verification: FAIL - Process error {e}")
    except Exception as e:
        print(f"Regex Verification: FAIL - {e}")
    finally:
        if os.path.exists(actions_file): os.remove(actions_file)

if __name__ == "__main__":
    verify_regex_match()
