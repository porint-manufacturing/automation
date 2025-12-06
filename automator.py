import sys
import os

# Add current directory to Python path for module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import csv
import time
import subprocess
import re
import argparse
import logging
import datetime
import ctypes
import uiautomation as auto
from src.automator.utils.focus import FocusManager
from src.automator.utils.screenshot import capture_screenshot
from src.automator.core.element_finder import ElementFinder
from src.automator.core.action_executor import ActionExecutor

# Enable High DPI Awareness to ensure correct coordinates
try:
    auto.SetProcessDpiAwareness(2) # Process_PerMonitorDpiAware
except Exception:
    pass # Ignore if not supported (e.g. older Windows)

class Automator:
    def __init__(self, action_files, log_file=None, log_level="INFO", dry_run=False, force_run=False, wait_time=None):
        self.actions = []
        self.variables = {}
        self.aliases = {}  # alias_name -> rpa_path
        self.reverse_aliases = {}  # rpa_path -> alias_name (for error messages)
        self.dry_run = dry_run
        self.force_run = force_run
        self.wait_time = wait_time  # None means use library default
        
        # Configure logging
        level = getattr(logging, log_level.upper(), logging.INFO)
        handlers = [logging.StreamHandler(sys.stdout)]
        if log_file:
            handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
        
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=handlers,
            force=True # Reconfigure if already configured
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize FocusManager
        self.focus_manager = FocusManager(force_run=force_run)
        
        # Initialize ElementFinder
        self.element_finder = ElementFinder(
            logger=self.logger,
            aliases=self.aliases,
            reverse_aliases=self.reverse_aliases
        )
        
        # Initialize ActionExecutor
        self.action_executor = ActionExecutor(
            logger=self.logger,
            element_finder=self.element_finder,
            focus_manager=self.focus_manager,
            dry_run=self.dry_run,
            force_run=self.force_run,
            wait_time=self.wait_time
        )
        
        # Ensure action_files is a list
        if isinstance(action_files, str):
            self.action_files = [action_files]
        else:
            self.action_files = action_files
            
        if self.dry_run:
            self.logger.info("=== DRY RUN MODE ENABLED ===")

    def load_aliases(self, alias_files):
        """Loads aliases from one or more CSV files."""
        if isinstance(alias_files, str):
            alias_files = [alias_files]
            
        for alias_file in alias_files:
            self.logger.info(f"Loading aliases from {alias_file}...")
            try:
                with open(alias_file, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        alias = row.get("AliasName")
                        path = row.get("RPA_Path")
                        if alias and path:
                            if alias in self.aliases:
                                self.logger.warning(f"Duplicate alias '{alias}' found in {alias_file}. Overwriting.")
                            self.aliases[alias] = path
                            self.reverse_aliases[path] = alias  # Build reverse lookup
            except Exception as e:
                self.logger.error(f"Error loading aliases from {alias_file}: {e}")
                sys.exit(1)
        self.logger.info(f"Loaded {len(self.aliases)} aliases total.")

    def load_actions(self):
        for csv_file in self.action_files:
            self.logger.info(f"Loading actions from {csv_file}...")
            try:
                with open(csv_file, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Resolve alias if present
                        key = row.get("Key", "")
                        if key and key in self.aliases:
                            self.logger.debug(f"Resolved alias '{key}' -> '{self.aliases[key]}'")
                            row["Key"] = self.aliases[key]
                        
                        # Normalize action type
                        act_type = row.get("Action", "")
                        if act_type.upper() == "IF": row["Action"] = "If"
                        elif act_type.upper() == "ELSE": row["Action"] = "Else"
                        elif act_type.upper() == "ENDIF": row["Action"] = "EndIf"
                        elif act_type.upper() == "LOOP": row["Action"] = "Loop"
                        elif act_type.upper() == "ENDLOOP": row["Action"] = "EndLoop"
                        
                        self.actions.append(row)
            except FileNotFoundError:
                self.logger.error(f"File not found: {csv_file}")
                sys.exit(1)
            except Exception as e:
                self.logger.error(f"Error loading actions from {csv_file}: {e}")
                sys.exit(1)
        self.logger.info(f"Loaded {len(self.actions)} actions total.")

    def evaluate_condition(self, condition):
        """Evaluates a condition string like '{status} == 'OK''."""
        # Replace variables
        if '{' in condition and '}' in condition:
            for var_name, var_val in self.variables.items():
                condition = condition.replace(f"{{{var_name}}}", str(var_val))
        
        # Safety check: only allow simple comparisons
        # This is a basic implementation. For production, use a safer parser.
        try:
            # We use eval() here for flexibility, but it's risky if inputs are untrusted.
            # Assuming CSVs are trusted.
            return eval(condition)
        except Exception as e:
            self.logger.error(f"Condition evaluation failed: {condition} - {e}")
            return False

    def find_matching_end(self, start_index, start_type):
        """Finds the matching EndIf/Else/EndLoop for a given start action."""
        nesting = 0
        for i in range(start_index + 1, len(self.actions)):
            act = self.actions[i].get('Action', '')
            
            if start_type == 'If':
                if act == 'If':
                    nesting += 1
                elif act == 'EndIf':
                    if nesting == 0:
                        return i
                    nesting -= 1
                elif act == 'Else':
                    if nesting == 0:
                        return i
            
            elif start_type == 'Loop':
                if act == 'Loop':
                    nesting += 1
                elif act == 'EndLoop':
                    if nesting == 0:
                        return i
                    nesting -= 1
        return -1

    def run(self):
        i = 0
        loop_stack = [] # Stores (start_index, loop_info)
        
        while i < len(self.actions):
            action = self.actions[i]
            self.logger.info(f"--- Action {i+1} ---")
            target_app = action.get('TargetApp', '')
            key = action.get('Key', '')
            act_type = action.get('Action', '')
            value = action.get('Value', '')
            if value is None:
                value = ""

            # Variable substitution for Value (except for control flow which handles it specifically)
            if act_type not in ['If', 'Loop', 'SetVariable']:
                 if '{' in value and '}' in value:
                    for var_name, var_val in self.variables.items():
                        value = value.replace(f"{{{var_name}}}", str(var_val))

            self.logger.info(f"Target: {target_app}, Action: {act_type}, Value: {value}")
            
            # --- Control Flow ---
            if act_type == 'If':
                condition = value
                result = self.evaluate_condition(condition)
                self.logger.info(f"Condition '{condition}' evaluated to: {result}")
                
                if result:
                    # Continue to next action (True block)
                    i += 1
                else:
                    # Jump to Else or EndIf
                    jump_to = self.find_matching_end(i, 'If')
                    if jump_to == -1:
                        self.logger.error("Missing matching EndIf/Else for If")
                        break
                    
                    # If we jumped to Else, we need to execute the Else block next (so i = jump_to + 1)
                    # But wait, if we jump to Else, the next iteration will process 'Else' action?
                    # No, 'Else' action itself should just jump to EndIf if encountered naturally.
                    # If we jump TO Else, we want to enter the block AFTER Else.
                    
                    next_act = self.actions[jump_to].get('Action', '')
                    if next_act == 'Else':
                        i = jump_to + 1
                    else: # EndIf
                        i = jump_to + 1
                continue

            elif act_type == 'Else':
                # If we hit Else naturally, it means we executed the True block.
                # So we must skip to EndIf.
                # We need to find the EndIf corresponding to the If that started this block.
                # But we don't have a reference to the start If here easily unless we track stack.
                # Alternatively, we can just scan forward for EndIf, respecting nesting.
                # Since we are inside an Else block (conceptually), we search for EndIf.
                # But wait, 'Else' is at the same nesting level as 'If'.
                
                # Scan forward for EndIf
                jump_to = self.find_matching_end(i, 'If') # Reuse If logic? No, If logic looks for Else/EndIf.
                # We need a finder that looks for EndIf only.
                
                nesting = 0
                found = -1
                for j in range(i + 1, len(self.actions)):
                    act = self.actions[j].get('Action', '')
                    if act == 'If':
                        nesting += 1
                    elif act == 'EndIf':
                        if nesting == 0:
                            found = j
                            break
                        nesting -= 1
                
                if found != -1:
                    i = found + 1
                else:
                    self.logger.error("Missing matching EndIf for Else")
                    break
                continue

            elif act_type == 'EndIf':
                # Just continue
                i += 1
                continue

            elif act_type == 'Loop':
                # Check if this loop is already active
                active_loop = None
                if loop_stack and loop_stack[-1][0] == i:
                    active_loop = loop_stack[-1]
                
                if active_loop:
                    # Re-eval condition
                    condition = value
                    # If value is a number, it's a count loop
                    if value.isdigit():
                         # Count is handled in state
                         pass # Logic below
                    else:
                         # Condition loop
                         pass
                else:
                    # New loop entry
                    pass

                # Unified Loop Logic
                # If value is digit -> Count loop.
                # Else -> Condition loop.
                
                should_loop = False
                
                # Expand variables in value for evaluation
                eval_value = value
                if '{' in eval_value and '}' in eval_value:
                    for var_name, var_val in self.variables.items():
                        eval_value = eval_value.replace(f"{{{var_name}}}", str(var_val))

                if eval_value.isdigit():
                    max_count = int(eval_value)
                    # Check stack
                    if loop_stack and loop_stack[-1][0] == i:
                        # Increment counter
                        loop_stack[-1][1]['current'] += 1
                        if loop_stack[-1][1]['current'] < max_count:
                            should_loop = True
                        else:
                            should_loop = False
                            loop_stack.pop() # Loop finished
                    else:
                        # First entry
                        if max_count > 0:
                            should_loop = True
                            loop_stack.append((i, {'type': 'count', 'current': 0, 'max': max_count}))
                        else:
                            should_loop = False
                else:
                    # Condition loop
                    result = self.evaluate_condition(value) # Use original value with vars
                    if result:
                        should_loop = True
                        if not (loop_stack and loop_stack[-1][0] == i):
                            loop_stack.append((i, {'type': 'condition'}))
                    else:
                        should_loop = False
                        if loop_stack and loop_stack[-1][0] == i:
                            loop_stack.pop()

                if should_loop:
                    i += 1
                else:
                    # Jump to EndLoop
                    jump_to = self.find_matching_end(i, 'Loop')
                    if jump_to == -1:
                        self.logger.error("Missing matching EndLoop")
                        break
                    i = jump_to + 1
                continue

            elif act_type == 'EndLoop':
                # Jump back to Loop start
                if loop_stack:
                    start_index = loop_stack[-1][0]
                    i = start_index
                else:
                    self.logger.error("EndLoop without active Loop")
                    i += 1
                continue

            # --- Normal Action ---
            try:
                self.execute_action(target_app, key, act_type, value)
            except Exception as e:
                self.logger.error(f"Action failed: {e}")
                capture_screenshot(f"error_action_{i+1}", dry_run=self.dry_run)
                if not self.force_run:
                    self.logger.error("Stopping execution due to error. Use --force-run to continue on errors.")
                    sys.exit(1)
            
            i += 1








    def execute_action(self, target_app, key, act_type, value):
        """Execute a single action by delegating to ActionExecutor"""
        return self.action_executor.execute(target_app, key, act_type, value, self.variables)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automator: Execute UI automation from CSV.")
    parser.add_argument("csv_files", nargs='+', default=["actions.csv"], help="Path to the actions CSV file(s).")
    parser.add_argument("--aliases", nargs='+', help="Path to the aliases CSV file(s).")
    parser.add_argument("--log-file", help="Path to the log file.")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level.")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no side effects).")
    parser.add_argument("--force-run", action="store_true", help="Continue execution even if errors occur.")
    parser.add_argument("--wait-time", type=float, help="Wait time (in seconds) after each action. If not specified, uses library default.")
    
    args = parser.parse_args()
    
    app = Automator(args.csv_files, log_file=args.log_file, log_level=args.log_level, dry_run=args.dry_run, force_run=args.force_run, wait_time=args.wait_time)
    
    if args.aliases:
        app.load_aliases(args.aliases)
        
    app.load_actions()
    app.run()
