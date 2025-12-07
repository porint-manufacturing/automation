"""
スクリーンショットユーティリティ

スクリーンショット撮影機能を処理。
"""

import logging
import os
import datetime
import uiautomation as auto


def capture_screenshot(name_prefix, dry_run=False):
    """
    画面全体のスクリーンショットを撮影。
    
    Args:
        name_prefix: スクリーンショットファイル名のプレフィックス
        dry_run: Trueの場合、撮影せずにログ出力のみ
        
    Returns:
        str: 保存されたスクリーンショットのパス、失敗/dry-runの場合はNone
    """
    logger = logging.getLogger(__name__)
    
    if dry_run:
        logger.info(f"[Dry-run] Would capture screenshot: {name_prefix}")
        return None
    
    try:
        if not os.path.exists("errors"):
            os.makedirs("errors")
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"errors/{name_prefix}_{timestamp}.png"
        
        # 全画面キャプチャ
        auto.GetRootControl().CaptureToImage(filename)
        logger.info(f"Screenshot saved to: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Failed to capture screenshot: {e}")
        return None
