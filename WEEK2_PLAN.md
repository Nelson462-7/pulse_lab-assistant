# 🎯 Week 2 計劃：數據可視化 + 統計分析

## 📊 週目標
從「數據儲存系統」升級到「數據分析儀表板」

**預期成果：**
- ✅ 波長 vs 功率趨勢圖
- ✅ 材料成功率分布
- ✅ 每日實驗次數統計
- ✅ 參數範圍可視化
- ✅ 自動生成分析報告

---

## 🏗️ 架構設計

```
新增模塊 (visualization.py)
    ↓
    ├─ 折線圖：波長/功率趨勢
    ├─ 柱狀圖：材料分布
    ├─ 散點圖：參數相關性
    ├─ 日曆熱力圖：實驗頻率
    └─ 統計摘要：平均值、標準差

整合到 app.py
    ↓
在「📈 統計與導出」頁面加入可視化區塊
```

---

## 📅 Day-by-Day 計劃

### **Day 1-2：基礎數據整理與繪圖設置**

**目標：** 準備數據，設置繪圖庫

**任務清單：**
1. 在 `database.py` 中新增函數：
   ```python
   def get_time_series_data() -> list
       """返回按日期排列的 (日期, 波長, 功率, 速度, 材料) 元組"""
   
   def get_parameter_statistics() -> dict
       """計算每個參數的平均值、標準差、最小值、最大值"""
   
   def get_daily_experiment_count() -> dict
       """返回 {日期: 實驗次數}"""
   ```

2. 建立 `visualization.py` 模塊：
   ```python
   import matplotlib.pyplot as plt
   import plotly.express as px
   import plotly.graph_objects as go
   
   # 設置中文字體
   plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows: 黑體
   # 或 Mac: plt.rcParams['font.sans-serif'] = ['PingFang SC']
   # 或 Linux: plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
   
   def plot_wavelength_trend(experiments):
       """波長隨時間的變化趨勢"""
       pass
   
   def plot_power_trend(experiments):
       """功率隨時間的變化趨勢"""
       pass
   
   def plot_material_distribution(stats):
       """材料分佈柱狀圖"""
       pass
   ```

3. 在 `requirements.txt` 中確保有：
   ```
   matplotlib>=3.5.0
   plotly>=5.0.0
   pandas>=1.3.0
   numpy>=1.20.0
   ```

**檢查清單：**
- [ ] `database.py` 新增三個統計函數
- [ ] `visualization.py` 建立完成
- [ ] 相關套件已安裝

---

### **Day 3-4：實現具體的圖表**

**目標：** 完成 5 種基本圖表

**實現 1：趨勢圖（Matplotlib）**
```python
def plot_wavelength_trend(experiments):
    """波長趨勢 - 折線圖"""
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime
    
    # 提取數據
    dates = [datetime.fromisoformat(exp['timestamp']) for exp in experiments]
    wavelengths = [exp['wavelength_nm'] for exp in experiments if exp['wavelength_nm']]
    
    # 繪圖
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(dates[:len(wavelengths)], wavelengths, marker='o', linestyle='-', linewidth=2)
    ax.set_xlabel('日期')
    ax.set_ylabel('波長 (nm)')
    ax.set_title('波長使用趨勢')
    ax.grid(True, alpha=0.3)
    
    # 格式化日期軸
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return fig
```

**實現 2：材料分布圖（Plotly - 互動）**
```python
def plot_material_distribution(stats):
    """材料分布 - 互動柱狀圖"""
    import plotly.express as px
    
    materials = list(stats['by_material'].keys())
    counts = list(stats['by_material'].values())
    
    fig = px.bar(
        x=materials,
        y=counts,
        labels={'x': '材料', 'y': '實驗次數'},
        title='各材料使用頻率'
    )
    
    return fig
```

**實現 3：散點圖（參數相關性）**
```python
def plot_parameter_correlation(experiments):
    """波長 vs 功率散點圖"""
    import plotly.express as px
    import pandas as pd
    
    data = {
        'wavelength': [e['wavelength_nm'] for e in experiments if e['wavelength_nm']],
        'power': [e['power_mW'] for e in experiments if e['power_mW']],
        'material': [e['material'] for e in experiments if e['material']]
    }
    
    df = pd.DataFrame(data)
    
    fig = px.scatter(
        df,
        x='wavelength',
        y='power',
        color='material',
        title='波長 vs 功率（按材料著色）',
        labels={'wavelength': '波長 (nm)', 'power': '功率 (mW)'}
    )
    
    return fig
```

**實現 4：日曆熱力圖（實驗頻率）**
```python
def plot_experiment_heatmap(daily_stats):
    """實驗頻率熱力圖"""
    import plotly.figure_factory as ff
    import pandas as pd
    
    # 準備數據：(日期, 實驗次數)
    dates = list(daily_stats.keys())
    counts = list(daily_stats.values())
    
    df = pd.DataFrame({
        'Date': dates,
        'Count': counts
    })
    
    fig = ff.create_annotated_heatmap(
        z=[counts],
        x=dates,
        y=['實驗次數'],
        colorscale='Blues'
    )
    
    return fig
```

**實現 5：統計摘要表**
```python
def create_statistics_summary(stats):
    """生成統計摘要表"""
    import pandas as pd
    
    summary_data = {
        '指標': ['總實驗數', '平均波長 (nm)', '波長範圍', '使用材料數'],
        '數值': [
            stats['total_experiments'],
            f"{stats['wavelength']['avg']:.1f}",
            f"{stats['wavelength']['min']:.0f} - {stats['wavelength']['max']:.0f}",
            len(stats['by_material'])
        ]
    }
    
    return pd.DataFrame(summary_data)
```

**檢查清單：**
- [ ] 趨勢圖可以正常顯示
- [ ] 材料分布圖互動正常
- [ ] 散點圖顏色正確
- [ ] 所有圖表中文正常顯示

---

### **Day 5-6：整合到主應用**

**目標：** 在 `app.py` 的「📈 統計與導出」頁面中加入可視化

**修改 app.py（在「📈 統計與導出」頁面中新增）：**

```python
from visualization import (
    plot_wavelength_trend, plot_power_trend,
    plot_material_distribution, plot_parameter_correlation,
    plot_experiment_heatmap, create_statistics_summary
)

elif page == "📈 統計與導出":
    st.subheader("實驗統計與數據分析")
    
    stats = get_experiment_stats()
    experiments = get_all_experiments()
    
    if stats and stats.get('total_experiments', 0) > 0:
        
        # --- 標籤頁 ---
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 數據摘要",
            "📈 趨勢分析",
            "🎨 分布圖表",
            "📥 數據導出"
        ])
        
        with tab1:
            # 統計摘要
            summary_df = create_statistics_summary(stats)
            st.dataframe(summary_df, use_container_width=True)
        
        with tab2:
            # 趨勢圖
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(
                    plot_wavelength_trend(experiments),
                    use_container_width=True
                )
            with col2:
                st.plotly_chart(
                    plot_power_trend(experiments),
                    use_container_width=True
                )
        
        with tab3:
            # 分布圖
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(
                    plot_material_distribution(stats),
                    use_container_width=True
                )
            with col2:
                st.plotly_chart(
                    plot_parameter_correlation(experiments),
                    use_container_width=True
                )
        
        with tab4:
            # 導出功能（保持原有）
            ...
```

**檢查清單：**
- [ ] 所有圖表顯示在正確的標籤頁中
- [ ] 互動功能正常（縮放、懸停等）
- [ ] 中文標籤正常顯示

---

### **Day 7：測試、優化、文檔**

**目標：** 確保系統穩定且易用

**測試清單：**
1. **功能測試**
   - [ ] 添加新實驗後，圖表自動更新
   - [ ] 刪除實驗後，圖表數值正確
   - [ ] 日期篩選可以正常工作

2. **邊界案例測試**
   - [ ] 只有 1 條記錄時，系統不崩潰
   - [ ] 所有參數為 None 時，圖表正常
   - [ ] 時間跨度很大時，性能可接受

3. **UI/UX 測試**
   - [ ] 圖表大小合理
   - [ ] 顏色配置清晰
   - [ ] 加載時間 < 3 秒

**性能優化：**
```python
# 在 app.py 中使用 Streamlit 的緩存機制
import streamlit as st

@st.cache_data(ttl=300)  # 5分鐘更新一次
def get_cached_experiments():
    return get_all_experiments()

@st.cache_data(ttl=300)
def get_cached_stats():
    return get_experiment_stats()
```

**文檔更新：**
建立 `CHANGELOG.md`
```markdown
# 變更日誌

## Phase 2 - Week 2 (2026-05-XX)

### 新增功能
- [x] 波長趨勢圖
- [x] 功率趨勢圖
- [x] 材料分布圖
- [x] 參數相關性散點圖
- [x] 實驗頻率熱力圖
- [x] 統計摘要表

### Bug 修復
- [x] 中文字體顯示問題
- [x] 圖表加載性能優化

### 已知限制
- 圖表需要至少 3 條數據才能完整顯示
- 時間跨度超過 1 年可能性能下降
```

**檢查清單：**
- [ ] 所有測試案例通過
- [ ] 性能優化完成
- [ ] 文檔更新完成

---

## 🛠️ 技術細節

### **安裝所需套件**

```powershell
.\venv\Scripts\activate.ps1
pip install matplotlib plotly pandas numpy --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

### **解決中文字體問題**

**Windows:**
```python
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
```

**Mac:**
```python
plt.rcParams['font.sans-serif'] = ['PingFang SC']
```

**Linux:**
```python
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
```

### **提升性能的關鍵技巧**

1. **使用 Plotly 代替 Matplotlib**（互動且快速）
2. **實現數據緩存**（使用 `@st.cache_data`）
3. **延遲加載**（用標籤頁避免一次性加載所有圖表）
4. **數據採樣**（超過 1000 筆數據時採樣顯示）

---

## 📊 預期成果

完成 Week 2 後，你會有一個完整的「數據分析儀表板」：

```
┌─────────────────────────────────┐
│  📈 統計與分析儀表板             │
├─────────────────────────────────┤
│  📊 數據摘要 | 📈 趨勢分析       │
│  🎨 分布圖表 | 📥 數據導出       │
├─────────────────────────────────┤
│ [波長趨勢圖]  [功率趨勢圖]       │
│ [材料分布圖]  [相關性散點圖]     │
│ [實驗頻率熱力圖]                │
│ [統計摘要表]                     │
└─────────────────────────────────┘
```

---

## 🎓 學習成果

完成 Week 2，你會掌握：

| 技能 | 詳情 |
|------|------|
| **數據視覺化** | Matplotlib + Plotly 的實踐 |
| **交互式圖表** | 用戶可以縮放、過濾、懸停查看詳情 |
| **性能優化** | 緩存、採樣、異步加載 |
| **統計分析** | 均值、標準差、相關性計算 |
| **系統集成** | 多模塊應用的架構設計 |

---

## 🚀 下一步（Phase 3 預告）

Week 3 可以考慮：
- 機器學習預測（某個參數組合的成功率）
- 異常檢測（發現異常的實驗記錄）
- 自動報告生成（每周的研究摘要）
- 數據備份與恢復機制

---

## 📝 問題排查

**Q: 圖表顯示空白？**
A: 確認有足夠的數據（至少 3 筆），檢查 `get_all_experiments()` 是否返回正確數據

**Q: 中文亂碼？**
A: 檢查 `plt.rcParams['font.sans-serif']` 的字體是否已安裝

**Q: 圖表加載很慢？**
A: 使用 `@st.cache_data` 緩存數據，或減少圖表數量

**Q: Plotly 互動功能不工作？**
A: 確認 Plotly 版本 >= 5.0，更新：`pip install --upgrade plotly`