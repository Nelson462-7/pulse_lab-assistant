import pandas as pd
import numpy as np

def process_hyperspectral_data(df, bg_count=3):
    """
    df: 傳入的原始 DataFrame (第一列為波長)
    bg_count: 背景訊號的數量 (從最後一列往前推)
    """
    # 1. 自動識別列名
    cols = df.columns.tolist()
    wavelength_col = cols[0]
    
    # 2. 自動判斷數據範圍 (不論波長 row 數量，只根據列進行切分)
    # 背景訊號：最後 bg_count 欄
    bg_cols = cols[-bg_count:]
    # 數據點：扣除第一欄(波長)與最後幾欄(背景)[cite: 4]
    data_cols = cols[1:-bg_count]
    
    # 3. 計算背景平均
    df['Background_AVG'] = df[bg_cols].mean(axis=1)
    
    # 4. 進行 Normalize (並防止除以 0)
    norm_cols = []
    for col in data_cols:
        new_col_name = f'{col}_normalized'
        df[new_col_name] = df[col] / (df['Background_AVG'] + 1e-9)
        norm_cols.append(new_col_name)
        
    # 重要修正：必須回傳 3 個值，否則 app.py 會報 ValueError
    # 回傳：處理後的 Dataframe, 數據欄位清單, 背景欄位清單
    return df, data_cols, bg_cols