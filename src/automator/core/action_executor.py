"""
ActionExecutor - アクション実行を担当するクラス

automator.pyのexecute_actionメソッドから抽出。
各アクションタイプを個別メソッドに分割して可読性と保守性を向上。
"""

import time
import subprocess
import re
import uiautomation as auto
from src.automator.utils.screenshot import capture_screenshot


class ActionExecutor:
    """アクション実行を担当するクラス"""
    
    def __init__(self, logger, element_finder, focus_manager, dry_run, force_run, wait_time=None):
        """
        ActionExecutorの初期化
        
        Args:
            logger: ロガーインスタンス
            element_finder: ElementFinderインスタンス
            focus_manager: FocusManagerインスタンス
            dry_run: Dry-runモードフラグ
            force_run: Force-runモードフラグ
            wait_time: アクション後の待機時間（秒）
        """
        self.logger = logger
        self.element_finder = element_finder
        self.focus_manager = focus_manager
        self.dry_run = dry_run
        self.force_run = force_run
        self.wait_time = wait_time
    
    def execute(self, target_app, key, act_type, value, variables):
        """
        アクションを実行する
        
        Args:
            target_app: ターゲットアプリケーション名
            key: 要素を特定するキー（RPAパスまたはエイリアス）
            act_type: アクションタイプ
            value: アクションの値
            variables: 変数辞書（参照渡し）
        """
        # Launch と Wait はウィンドウ不要
        if act_type == "Launch":
            return self._execute_launch(value)
        elif act_type == "Wait":
            return self._execute_wait(value)
        elif act_type == "SetVariable":
            return self._execute_set_variable(value, variables)
        
        # Focus はウィンドウが必要だが要素は不要
        if act_type == "Focus":
            window = self.element_finder.find_window(target_app)
            if not window:
                if self.dry_run:
                    self.logger.warning(f"[Dry-run] Window '{target_app}' not found. Subsequent actions might fail.")
                    return
                raise Exception(f"Window '{target_app}' not found.")
            return self._execute_focus(window, target_app)
        
        # 以下のアクションは要素が必要
        window = self.element_finder.find_window(target_app)
        if not window:
            if self.dry_run:
                self.logger.warning(f"[Dry-run] Window '{target_app}' not found. Subsequent actions might fail.")
                return
            raise Exception(f"Window '{target_app}' not found.")
        
        element = window
        if key:
            element = self.element_finder.find_element_by_path(window, key)
            if not element:
                key_display = self.element_finder.format_path_with_alias(key)
                if self.dry_run:
                    self.logger.warning(f"[Dry-run] Element not found for key: {key_display}")
                    return
                raise Exception(f"Element not found for key: {key_display}")
            if self.dry_run:
                self.logger.info(f"[Dry-run] Element found: {element.Name} ({element.ControlTypeName})")
        
        # アクションタイプに応じて処理
        if act_type == "Click":
            return self._execute_click(element)
        elif act_type == "Input":
            return self._execute_input(element, value, key)
        elif act_type == "Invoke":
            return self._execute_invoke(element, key)
        elif act_type == "SendKeys":
            return self._execute_sendkeys(value)
        elif act_type == "Select":
            return self._execute_select(element, value)
        elif act_type == "GetProperty":
            return self._execute_get_property(element, value, variables)
        elif act_type == "Screenshot":
            return self._execute_screenshot(element, value)
        elif act_type == "FocusElement":
            return self._execute_focus_element(element, key)
        
        # TODO: 他のアクションタイプを実装
        raise NotImplementedError(f"Action type '{act_type}' not yet implemented in ActionExecutor")
    
    def _execute_launch(self, value):
        """Launchアクション - アプリケーションを起動"""
        if self.dry_run:
            self.logger.info(f"[Dry-run] Would launch: {value}")
            return
        self.logger.info(f"Launching {value}...")
        subprocess.Popen(value, shell=True)
    
    def _execute_wait(self, value):
        """Waitアクション - 指定秒数待機"""
        if self.dry_run:
            self.logger.info(f"[Dry-run] Would wait: {value} seconds")
            return
        self.logger.info(f"Waiting {value} seconds...")
        time.sleep(float(value))
    
    def _execute_focus(self, window, target_app):
        """Focusアクション - ウィンドウにフォーカス"""
        if self.dry_run:
            self.logger.info(f"[Dry-run] Would focus window: {target_app}")
            return
        window.SetFocus()
    
    def _execute_set_variable(self, value, variables):
        """SetVariableアクション - 変数を設定"""
        if self.dry_run:
            self.logger.info(f"[Dry-run] Would set variable: {value}")
            return
        
        # Parse "var_name = expression"
        match = re.match(r"(\w+)\s*=\s*(.+)", value)
        if not match:
            raise Exception(f"Invalid SetVariable format: {value}")
        
        var_name = match.group(1)
        expression = match.group(2).strip()
        
        # Replace variables in expression
        for v, val in variables.items():
            expression = expression.replace(f"{{{v}}}", str(val))
        
        # Evaluate expression
        try:
            result = eval(expression)
            variables[var_name] = result
            self.logger.info(f"Set variable '{var_name}' to '{result}'")
        except Exception as e:
            raise Exception(f"Failed to evaluate expression '{expression}': {e}")
    
    def _execute_click(self, element):
        """Clickアクション - 要素をクリック"""
        if self.dry_run:
            self.logger.info(f"[Dry-run] Would click element: {element.Name}")
            return
        
        self.logger.info(f"Clicking element '{element.Name}'...")
        
        # Try InvokePattern first, fallback to Click
        try:
            invoke = element.GetPattern(auto.PatternId.InvokePattern)
            if invoke:
                self.logger.debug("Using InvokePattern...")
                invoke.Invoke()
                if self.wait_time is not None:
                    time.sleep(self.wait_time)
            else:
                if self.wait_time is not None:
                    element.Click(waitTime=self.wait_time)
                else:
                    element.Click()
        except Exception as e:
            self.logger.warning(f"Invoke failed, falling back to Click: {e}")
            if self.wait_time is not None:
                element.Click(waitTime=self.wait_time)
            else:
                element.Click()
    
    def _execute_input(self, element, value, key):
        """Inputアクション - テキスト入力"""
        if self.dry_run:
            self.logger.info(f"[Dry-run] Would input text '{value}' into element: {element.Name}")
            return
        
        self.logger.info(f"Inputting text: {value}")
        success = False
        
        # Try ValuePattern first
        try:
            pattern = element.GetPattern(auto.PatternId.ValuePattern)
            if pattern:
                self.logger.debug("Using ValuePattern.SetValue()...")
                element.SetValue(value)
                success = True
        except Exception as e:
            self.logger.debug(f"SetValue failed: {e}")
        
        if not success:
            self.logger.debug("Fallback to SendKeys...")
            # Set focus with Win32 API fallback
            key_display = self.element_finder.format_path_with_alias(key) if key else element.Name
            self.focus_manager.set_focus_with_fallback(element, key_display)
            auto.SendKeys(value)
    
    def _execute_invoke(self, element, key):
        """Invokeアクション - 要素を実行"""
        if self.dry_run:
            self.logger.info(f"[Dry-run] Would invoke element: {element.Name}")
            return
        
        self.logger.info(f"Invoking element '{element.Name}'...")
        
        # Set focus with Win32 API fallback (legacy app support)
        key_display = self.element_finder.format_path_with_alias(key) if key else element.Name
        self.focus_manager.set_focus_with_fallback(element, key_display)
        
        # Proceed with invoke
        pattern = element.GetPattern(auto.PatternId.InvokePattern)
        if pattern:
            pattern.Invoke()
            if self.wait_time is not None:
                time.sleep(self.wait_time)
        else:
            # Fallback to Toggle if Invoke not supported (e.g. Checkbox)
            toggle = element.GetPattern(auto.PatternId.TogglePattern)
            if toggle:
                self.logger.info("Invoke pattern not found, using Toggle pattern...")
                toggle.Toggle()
                if self.wait_time is not None:
                    time.sleep(self.wait_time)
            else:
                raise Exception("Element does not support Invoke or Toggle pattern")
    
    def _execute_sendkeys(self, value):
        """SendKeysアクション - キー送信"""
        if self.dry_run:
            self.logger.info(f"[Dry-run] Would send keys: {value}")
            return
        
        self.logger.info(f"Sending keys: {value}")
        auto.SendKeys(value)
    
    def _execute_select(self, element, value):
        """Selectアクション - 要素を選択"""
        if self.dry_run:
            self.logger.info(f"[Dry-run] Would select element: {element.Name} (Value: {value})")
            return
        
        if value:
            # Value provided: Treat element as a container and select child item
            self.logger.info(f"Selecting item '{value}' in '{element.Name}'...")
            
            # Try to expand first if it's a combobox
            expand = element.GetPattern(auto.PatternId.ExpandCollapsePattern)
            if expand:
                try:
                    expand.Expand()
                    time.sleep(0.5)  # Wait for expansion
                except:
                    pass
            
            # Find child item
            item = element.ListItemControl(Name=value)
            if not item.Exists(maxSearchSeconds=1):
                item = element.TreeItemControl(Name=value)
            
            if not item.Exists(maxSearchSeconds=1):
                item = element.Control(Name=value, searchDepth=1)
            
            if not item.Exists(maxSearchSeconds=1):
                raise Exception(f"Item '{value}' not found in '{element.Name}'")
            
            # Scroll into view if possible
            scroll = item.GetPattern(auto.PatternId.ScrollItemPattern)
            if scroll:
                scroll.ScrollIntoView()
            
            # Select the item
            sel_item = item.GetPattern(auto.PatternId.SelectionItemPattern)
            if sel_item:
                sel_item.Select()
                if self.wait_time is not None:
                    time.sleep(self.wait_time)
            else:
                self.logger.warning("Item does not support SelectionItemPattern, trying Click...")
                if self.wait_time is not None:
                    item.Click(waitTime=self.wait_time)
                else:
                    item.Click()
        else:
            # No value: Select the element itself
            self.logger.info(f"Selecting element '{element.Name}'...")
            sel_item = element.GetPattern(auto.PatternId.SelectionItemPattern)
            if sel_item:
                sel_item.Select()
                if self.wait_time is not None:
                    time.sleep(self.wait_time)
            else:
                raise Exception("Element does not support SelectionItemPattern")
    
    def _execute_get_property(self, element, value, variables):
        """GetPropertyアクション - 要素のプロパティを取得"""
        if self.dry_run:
            self.logger.info(f"[Dry-run] Would get property from element: {element.Name}")
            variables[value] = "[DryRunValue]"
            return
        
        # Parse "var_name = property_name"
        if "=" in value:
            parts = value.split("=", 1)
            var_name = parts[0].strip()
            prop_name = parts[1].strip()
        else:
            # If no '=', use value as both var name and property name
            var_name = value
            prop_name = "Value"
        
        # Get property value using element_finder
        prop_value = self.element_finder.get_element_property(element, prop_name)
        variables[var_name] = prop_value
        
        elem_desc = element.Name or element.ControlTypeName or "element"
        self.logger.info(f"Got {prop_name} = '{prop_value}' from '{elem_desc}', stored in '{var_name}'")
    
    def _execute_screenshot(self, element, value):
        """Screenshotアクション - スクリーンショット撮影"""
        if self.dry_run:
            self.logger.info(f"[Dry-run] Would take screenshot: {value}")
            return
        
        self.logger.info(f"Taking screenshot: {value}")
        capture_screenshot(value, dry_run=self.dry_run)
    
    def _execute_focus_element(self, element, key):
        """FocusElementアクション - 要素にフォーカス"""
        # 要素の説明を決定
        if element.Name:
            element_desc = element.Name
        else:
            element_desc = key if key else f"{element.ControlTypeName} (AutomationId: {element.AutomationId or 'N/A'})"
        
        if self.dry_run:
            self.logger.info(f"[Dry-run] Would focus element: {element_desc}")
            return
        
        self.logger.info(f"Focusing element '{element_desc}'...")
        
        # Set focus with Win32 API fallback
        success = self.focus_manager.set_focus_with_fallback(element, element_desc)
        
        if success:
            self.logger.info(f"✓ Focus successfully set on '{element_desc}'")

