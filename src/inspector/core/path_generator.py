"""
PathGenerator - RPAパス生成を担当するクラス

inspector.pyから抽出。
modernモードとlegacyモードでパス生成方法を切り替える。
"""

import uiautomation as auto


class PathGenerator:
    def __init__(self, mode="modern"):
        """
        Args:
            mode: "modern" (AutomationId/Name優先) or "legacy" (ClassName/foundIndex)
        """
        self.mode = mode
    
    def get_rpa_path(self, control):
        """
        コントロールの堅牢なRPAパスを生成する
        パフォーマンスと一意性を向上させるためにチェーンパス（親 -> 子）を使用
        """
        root = control.GetTopLevelControl()
        if not root:
            return self._generate_segment(control, None)

        # 系譜収集: [Root, ..., Parent, Control]
        # パス文字列にはRootを含めない（TargetAppなので）。
        
        # Modernモードの最適化: AutomationIdが利用可能な場合は直接使用
        if self.mode == "modern" and control.AutomationId:
             # controlがrootかどうかをチェック
             if auto.ControlsAreSame(control, root):
                 return ""
             return self._generate_segment(control, None)

        lineage = []
        current = control
        depth_safety = 0
        while current and depth_safety < 50:
            if auto.ControlsAreSame(current, root):
                break
            lineage.insert(0, current)
            try:
                current = current.GetParentControl()
            except Exception as e:
                print(f"Warning: GetParentControl failed: {e}")
                break
            depth_safety += 1
        
        # パスセグメントを生成
        path_segments = []
        parent = root
        for item in lineage:
            segment = self._generate_segment(item, parent)
            path_segments.append(segment)
            parent = item
            
        return " -> ".join(path_segments)
    
    def _generate_segment(self, control, parent):
        """親に相対する単一パスセグメント（Type(Props)）を生成する"""
        control_type = control.ControlTypeName
        name = control.Name
        automation_id = control.AutomationId
        class_name = control.ClassName
        
        criteria = []
        search_params = {"ControlTypeName": control_type}
        
        # 1. 戦略: AutomationId (Modern)
        if self.mode == "modern" and automation_id:
            criteria.append(f"AutomationId='{automation_id}'")
            search_params["AutomationId"] = automation_id
            
        # 2. 戦略: Name (Modern/Legacyで安定している場合)
        # legacyモードでは、Nameが動的に見える場合はスキップするかもしれないが、今のところ存在すれば含める。
        elif name:
            # シングルクォートをエスケープ
            safe_name = name.replace("'", "\\'")
            criteria.append(f"Name='{safe_name}'")
            search_params["Name"] = name
            
        # 3. 戦略: ClassName (Legacy)
        if self.mode == "legacy" and class_name:
            criteria.append(f"ClassName='{class_name}'")
            search_params["ClassName"] = class_name
            
        # 4. 戦略: 他に何もない場合はClassNameにフォールバック
        if not criteria and class_name:
            criteria.append(f"ClassName='{class_name}'")
            search_params["ClassName"] = class_name

        # 親に相対するfoundIndexを計算
        # これはツリー全体を検索するよりもはるかに高速。
        found_index = 1
        
        if parent:
            try:
                count = 0
                found = False
                
                # maxDepth=1でWalkControlを使用し、直接の子ノードのみを検索。
                # これにより、深いサブツリー（大規模なリストなど）の走査を回避。
                # 注: WalkControl(root, maxDepth=1)はroot、その後子ノードを生成する。
                # 最初の1つ（親自身）をスキップする。
                
                gen = auto.WalkControl(parent, maxDepth=1)
                next(gen) # 親をスキップ
                
                for ctrl, depth in gen:
                    # マッチングチェック
                    is_match = (ctrl.ControlTypeName == control_type)
                    if is_match and "AutomationId" in search_params:
                        is_match = (ctrl.AutomationId == search_params["AutomationId"])
                    if is_match and "Name" in search_params:
                        is_match = (ctrl.Name == search_params["Name"])
                    if is_match and "ClassName" in search_params:
                        is_match = (ctrl.ClassName == search_params["ClassName"])
                    
                    if is_match:
                        count += 1
                        if auto.ControlsAreSame(ctrl, control):
                            found_index = count
                            found = True
                            break
                
                if not found:
                    # フォールバック: 階層が動的に変わった場合、直接の子ではないかもしれない？
                    pass

            except Exception as e:
                # これは一時的な要素（メニューが閉じるなど）でよく発生する。
                # デフォルトを1にするのは、これらのユニークなアイテムには無害。
                print(f"    Warning: Index calculation skipped (defaulting to 1). Reason: {e}")
                found_index = 1

        # パス文字列を構築
        props = criteria
        if found_index > 1 or self.mode == "legacy":
             props.append(f"foundIndex={found_index}")
        
        # チェーンしている場合（親が存在）、searchDepth=1を強制
        if parent:
            props.append("searchDepth=1")
        
        props_str = ", ".join(props)
        return f"{control_type}({props_str})"
