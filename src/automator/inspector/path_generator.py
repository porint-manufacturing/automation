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
        Generates a robust RPA path for the control.
        Uses chained paths (Parent -> Child) to improve performance and uniqueness.
        """
        root = control.GetTopLevelControl()
        if not root:
            return self._generate_segment(control, None)

        # Collect lineage: [Root, ..., Parent, Control]
        # We don't include Root in the path string (it's the TargetApp).
        
        # Optimization for Modern Mode: Use AutomationId directly if available
        if self.mode == "modern" and control.AutomationId:
             # Check if control is root
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
        
        # Generate path segments
        path_segments = []
        parent = root
        for item in lineage:
            segment = self._generate_segment(item, parent)
            path_segments.append(segment)
            parent = item
            
        return " -> ".join(path_segments)
    
    def _generate_segment(self, control, parent):
        """Generates a single path segment (Type(Props)) relative to parent."""
        control_type = control.ControlTypeName
        name = control.Name
        automation_id = control.AutomationId
        class_name = control.ClassName
        
        criteria = []
        search_params = {"ControlTypeName": control_type}
        
        # 1. Strategy: AutomationId (Modern)
        if self.mode == "modern" and automation_id:
            criteria.append(f"AutomationId='{automation_id}'")
            search_params["AutomationId"] = automation_id
            
        # 2. Strategy: Name (Modern/Legacy if stable)
        # In legacy mode, we might skip Name if it looks dynamic, but for now we include it if present.
        elif name:
            # Escape single quotes
            safe_name = name.replace("'", "\\'")
            criteria.append(f"Name='{safe_name}'")
            search_params["Name"] = name
            
        # 3. Strategy: ClassName (Legacy)
        if self.mode == "legacy" and class_name:
            criteria.append(f"ClassName='{class_name}'")
            search_params["ClassName"] = class_name
            
        # 4. Strategy: Fallback to ClassName if nothing else
        if not criteria and class_name:
            criteria.append(f"ClassName='{class_name}'")
            search_params["ClassName"] = class_name

        # Calculate foundIndex relative to PARENT
        # This is much faster than searching the whole tree.
        found_index = 1
        
        if parent:
            try:
                count = 0
                found = False
                
                # Use WalkControl with maxDepth=1 to search ONLY direct children.
                # This avoids traversing deep subtrees (like massive lists).
                # Note: WalkControl(root, maxDepth=1) yields root, then children.
                # We skip the first one (parent itself).
                
                gen = auto.WalkControl(parent, maxDepth=1)
                next(gen) # Skip parent
                
                for ctrl, depth in gen:
                    # Check match
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
                    # Fallback: It might not be a direct child if the hierarchy changed dynamically?
                    pass

            except Exception as e:
                # This often happens with transient elements (like menus closing).
                # Defaulting to 1 is usually safe for these unique items.
                print(f"    Warning: Index calculation skipped (defaulting to 1). Reason: {e}")
                found_index = 1

        # Construct path string
        props = criteria
        if found_index > 1 or self.mode == "legacy":
             props.append(f"foundIndex={found_index}")
        
        # If we are chaining (parent exists), we enforce searchDepth=1
        if parent:
            props.append("searchDepth=1")
        
        props_str = ", ".join(props)
        return f"{control_type}({props_str})"
