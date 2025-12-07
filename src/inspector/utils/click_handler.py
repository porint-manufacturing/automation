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
        """ClickHandler初期化"""
        pass
    
    def wait_for_click(self):
        """
        左または右クリックを待機し、(control, x, y)を返す。
        ESCが押された場合はNoneを返す。
        """
        while True:
            if keyboard.is_pressed('esc'):
                return None
            
            # 左クリック (0x01) または右クリック (0x02) をチェック
            if (ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000) or \
               (ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000):
                x, y = auto.GetCursorPos()
                control = auto.ControlFromPoint(x, y)
                # 複数登録を回避するためにリリースを待つ
                while (ctypes.windll.user32.GetAsyncKeyState(0x01) & 0x8000) or \
                      (ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000):
                    time.sleep(0.05)
                return control, x, y
            
            time.sleep(0.05)
