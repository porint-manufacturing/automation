"""
フォーカス管理ユーティリティ

レガシーアプリケーション用のWin32 APIフォールバックを使用してUI要素のフォーカス設定を処理。
"""

import logging
import ctypes
import uiautomation as auto


class FocusManager:
    """フォールバックメカニズムを使用してUI要素のフォーカスを管理する。"""
    
    def __init__(self, force_run=False, legacy_mode=False):
        """
        FocusManager初期化。
        
        Args:
            force_run: Trueの場合、フォーカス失敗時でも実行を続行
            legacy_mode: Trueの場合、Win32 API SetFocusを優先
        """
        self.force_run = force_run
        self.legacy_mode = legacy_mode
        self.logger = logging.getLogger(__name__)
    
    def set_focus_win32(self, element):
        """
        Win32 APIを使用してフォーカスを設定。
        
        Args:
            element: UI Automation要素
            
        Returns:
            bool: 成功時True、それ以外False
        """
        try:
            hwnd = element.NativeWindowHandle
            if hwnd:
                user32 = ctypes.windll.user32
                user32.SetFocus(hwnd)
                self.logger.info(f"Focus set using Win32 API (HWND: {hwnd})")
                return True
            else:
                self.logger.warning("No NativeWindowHandle available for Win32 SetFocus")
                return False
        except Exception as e:
            self.logger.warning(f"Win32 SetFocus failed: {e}")
            return False
    
    def set_focus_with_fallback(self, element, element_desc="element"):
        """
        UI Automationを使用してフォーカスを設定、失敗時はWin32 APIにフォールバック。
        レガシーモードの場合は逆順。
        
        Args:
            element: UI Automation要素
            element_desc: ログ用の要素説明
            
        Raises:
            RuntimeError: フォーカス失敗かつforce_runがFalseの場合
        """
        
        if self.legacy_mode:
            # レガシーモード: Win32優先
            if self.set_focus_win32(element):
                return
            
            self.logger.warning(f"Win32 SetFocus failed for {element_desc}, falling back to UI Automation")
            try:
                element.SetFocus()
                self.logger.info(f"Focus set on {element_desc} using UI Automation (Fallback)")
                return
            except Exception as e:
                self.logger.warning(f"UI Automation SetFocus failed for {element_desc}: {e}")
                
        else:
            # 標準モード: UI Automation優先
            try:
                element.SetFocus()
                self.logger.info(f"Focus set on {element_desc} using UI Automation")
                return
            except Exception as e:
                self.logger.warning(f"UI Automation SetFocus failed for {element_desc}: {e}")
            
            # Win32 APIにフォールバック
            if self.set_focus_win32(element):
                return
        
        # 両方のメソッドが失敗
        error_msg = f"Failed to set focus on {element_desc} (both UI Automation and Win32 API failed)"
        if self.force_run:
            self.logger.warning(f"{error_msg}. Continuing due to --force-run flag.")
        else:
            raise RuntimeError(error_msg)
