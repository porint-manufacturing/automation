"""
OutputHandler - 出力処理を担当するクラス

inspector.pyから抽出。
CSV/clipboard/alias形式での出力を処理。
"""

import csv
import datetime
import io
import uiautomation as auto


class OutputHandler:
    def __init__(self, output_mode="clipboard"):
        """
        Args:
            output_mode: "csv", "clipboard", "alias", or "interactive_alias"
        """
        self.output_mode = output_mode
    
    def finalize(self, recorded_items):
        """
        出力モードに基づいて記録されたアイテムを処理して出力。
        
        Args:
            recorded_items: 記録されたアイテムのリスト（辞書）
        """
        if not recorded_items:
            print("No items recorded.")
            return

        if self.output_mode == "csv":
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"inspector_{timestamp}.csv"
            with open(filename, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=["TargetApp", "Key", "Action", "Value"])
                writer.writeheader()
                writer.writerows(recorded_items)
            print(f"Saved to {filename}")
            
        elif self.output_mode == "clipboard":
            # CSV文字列を生成
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=["TargetApp", "Key", "Action", "Value"])
            writer.writeheader()
            writer.writerows(recorded_items)
            csv_content = output.getvalue()
            
            auto.SetClipboardText(csv_content)
            print("Copied CSV content to clipboard.")

        elif self.output_mode in ["alias", "interactive_alias"]:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"inspector_{timestamp}_alias.csv"
            with open(filename, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=["AliasName", "RPA_Path"])
                writer.writeheader()
                
                alias_items = []
                for item in recorded_items:
                    if "AliasName" in item:
                        # 対話型モードアイテム
                        alias_items.append(item)
                    else:
                        # 通常モードアイテム（KeyをRPA_Pathに変換）
                        alias_items.append({"AliasName": "", "RPA_Path": item["Key"]})
                
                writer.writerows(alias_items)
            print(f"Saved alias definition to {filename}")
