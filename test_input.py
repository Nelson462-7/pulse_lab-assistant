import pandas as pd
import io
import numpy as np
from processor import HyperspectralProcessor

def run_test():
    processor = HyperspectralProcessor()
    
    print("--- 測試 1：正常數據 ---")
    # 模擬 5 欄數據：波長, 測量1, 背景1, 背景2, 背景3
    normal_data = "400,10,1,1,1\n401,20,2,2,2"
    buffer = io.StringIO(normal_data)
    if processor.read_from_buffer(buffer, bg_count=3):
        processor.normalize()
        print("✅ 正常數據通過")
    
    print("\n--- 測試 2：包含缺失值 (NaN) ---")
    nan_data = "400,10,1,,1\n401,,2,2,2" # 中間有空值
    buffer = io.StringIO(nan_data)
    if processor.read_from_buffer(buffer, bg_count=3):
        print("✅ NaN 自動填補通過")
        
    print("\n--- 測試 3：背景列數設定錯誤 (防呆測試) ---")
    buffer = io.StringIO(normal_data)
    # 總共才 5 欄，如果要求 5 個背景，應該要報錯
    if not processor.read_from_buffer(buffer, bg_count=5):
        print("✅ 防呆機制成功攔截非法 bg_count")

if __name__ == "__main__":
    run_test()