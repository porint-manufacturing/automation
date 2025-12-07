"""
ClickHandler - マウス/キーボード入力処理を担当するクラス

inspector.pyから抽出。
左クリック・右クリックの検出とESCキー検出を処理。
"""

import time
import keyboard
import ctypes
import uiautomation as auto


class ClickHandler:
    def __init__(self):
        """Initialize ClickHandler"""
        pass
    
    def wait_for_click(self):
        """
        Waits for a left or right click and returns (control, x, y). 
        Returns None if ESC is pressed.
        """
        while True:
            if keyboard.is_pressed('esc'):
                return None
            
            # Check for left click (0x01) or right click (0x02)
            if (ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000) or \
               (ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000):
                x, y = auto.GetCursorPos()
                control = auto.ControlFromPoint(x, y)
                # Wait for release to avoid multiple registrations
                while (ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000) or \
                      (ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000):
                    time.sleep(0.05)
                return control, x, y
            
            time.sleep(0.05)
