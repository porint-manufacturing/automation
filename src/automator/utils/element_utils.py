"""
要素ユーティリティ

UI要素パスのフォーマットと操作のヘルパー関数。
"""


def format_path_with_alias(path, aliases):
    """
    表示用にエイリアス解決を含む要素パスをフォーマット。
    
    Args:
        path: 要素パス文字列
        aliases: エイリアスマッピングの辞書
        
    Returns:
        str: エイリアス情報を含むフォーマットされたパス
    """
    if not path:
        return path
    
    # パスがエイリアスで始まるかチェック
    for alias_name, alias_path in aliases.items():
        if path.startswith(f"${alias_name}"):
            # エイリアスと解決されたパスの両方を表示
            resolved = path.replace(f"${alias_name}", alias_path, 1)
            return f"{path} (resolved: {resolved})"
    
    return path
