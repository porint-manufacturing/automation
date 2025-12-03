import sys
import os
import csv
import shutil
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from automator import Automator

def reproduce_none_error():
    print("--- Reproducing NoneType Error ---")
    
    actions_file = "tests/temp_none_error.csv"
    log_file = "tests/reproduce_none_error.log"
    
    # Row with missing Value column (3 columns instead of 4)
    # TargetApp, Key, Action
    # ,,EndIf
    
    with open(actions_file, 'w', newline='', encoding='utf-8-sig') as f:
        f.write("TargetApp,Key,Action,Value\n")
        f.write(",,EndIf\n") # Missing Value
        
    app = Automator([actions_file], log_file=log_file, log_level="DEBUG")
    
    try:
        app.load_actions()
        app.run()
        print("FAIL: Did not crash.")
    except TypeError as e:
        print(f"PASS: Caught expected TypeError: {e}")
    except Exception as e:
        print(f"FAIL: Caught unexpected exception: {e}")

    # Cleanup
    for handler in app.logger.handlers[:]:
        handler.close()
        app.logger.removeHandler(handler)
    import logging
    logging.shutdown()
    
    if os.path.exists(actions_file): os.remove(actions_file)
    if os.path.exists(log_file): os.remove(log_file)

if __name__ == "__main__":
    reproduce_none_error()
