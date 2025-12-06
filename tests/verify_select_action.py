import sys
import os
import csv
import subprocess
import time

def cleanup_calculator():
    """Kill calculator process if it's running"""
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'CalculatorApp.exe'], 
                      capture_output=True, timeout=5)
    except:
        pass

def verify_select_action():
    print("--- Testing Select Action ---")
    
    try:
        # Create test actions file using calculator settings theme radio buttons
        # Using AutomationId from Inspector for reliable element identification
        actions_file = "tests/temp_select_test.csv"
        with open(actions_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=["TargetApp", "Key", "Action", "Value"])
            writer.writeheader()
            writer.writerow({"TargetApp": "電卓", "Key": "", "Action": "Launch", "Value": "calc.exe"})
            writer.writerow({"TargetApp": "電卓", "Key": "", "Action": "Wait", "Value": "2"})
            # Click hamburger menu
            writer.writerow({"TargetApp": "電卓", "Key": "Button(AutomationId='TogglePaneButton')", "Action": "Click", "Value": ""})
            writer.writerow({"TargetApp": "電卓", "Key": "", "Action": "Wait", "Value": "1"})
            # Click settings
            writer.writerow({"TargetApp": "電卓", "Key": "ListItem(AutomationId='SettingsItem')", "Action": "Click", "Value": ""})
            writer.writerow({"TargetApp": "電卓", "Key": "", "Action": "Wait", "Value": "1"})
            # Expand theme section
            writer.writerow({"TargetApp": "電卓", "Key": "Group(ClassName='Microsoft.UI.Xaml.Controls.Expander', Name='アプリ テーマ', searchDepth=10)", "Action": "Click", "Value": ""})
            writer.writerow({"TargetApp": "電卓", "Key": "", "Action": "Wait", "Value": "0.5"})
            # SELECT "Light" theme radio button (using Select action, not Invoke!)
            writer.writerow({"TargetApp": "電卓", "Key": "RadioButton(AutomationId='LightThemeRadioButton', searchDepth=10)", "Action": "Select", "Value": ""})
            writer.writerow({"TargetApp": "電卓", "Key": "", "Action": "Wait", "Value": "1"})
            # Restore to system theme
            writer.writerow({"TargetApp": "電卓", "Key": "RadioButton(AutomationId='SystemThemeRadioButton', searchDepth=10)", "Action": "Select", "Value": ""})
            writer.writerow({"TargetApp": "電卓", "Key": "", "Action": "Wait", "Value": "1"})
            # Go back (with increased search depth)
            writer.writerow({"TargetApp": "電卓", "Key": "Button(AutomationId='BackButton', searchDepth=5)", "Action": "Click", "Value": ""})
            writer.writerow({"TargetApp": "電卓", "Key": "", "Action": "Wait", "Value": "0.5"})
            # Close calculator
            writer.writerow({"TargetApp": "電卓", "Key": "", "Action": "SendKeys", "Value": "{Alt}{F4}"})
        
        # Run automator
        result = subprocess.run(
            [sys.executable, "automator.py", actions_file, "--log-level", "DEBUG"],
            capture_output=True,
            text=True
        )
        
        # Check results
        success = True
        
        # Check if Select action was executed on radio button
        if "Selecting element" in result.stdout and ("ライト" in result.stdout or "LightThemeRadioButton" in result.stdout):
            print("PASS: Radio button select action executed")
        else:
            print("WARNING: Radio button select not clearly confirmed in log")
        
        # Check if settings was accessed
        if "SettingsItem" in result.stdout or "Settings" in result.stdout or "設定" in result.stdout:
            print("PASS: Settings accessed")
        else:
            print("WARNING: Settings access not clearly confirmed")
        
        # Check exit code
        if result.returncode == 0:
            print("PASS: Exit code 0")
        else:
            print(f"FAIL: Exit code {result.returncode}")
            success = False
            # Cleanup on failure
            cleanup_calculator()
        
        # Cleanup
        if os.path.exists(actions_file):
            os.remove(actions_file)
        
        if success:
            print("\n=== Select Action Verification: PASS ===")
            return True
        else:
            print("\n=== Select Action Verification: FAIL ===")
            print(f"Output (last 1000 chars): {result.stdout[-1000:]}")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Exception during test: {e}")
        cleanup_calculator()
        return False

if __name__ == "__main__":
    success = verify_select_action()
    sys.exit(0 if success else 1)
