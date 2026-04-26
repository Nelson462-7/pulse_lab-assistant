# 🏗️ 系統穩定度提升方案

## 📌 現況評估

**當前穩定度**: 70-80%
**潛在風險**: AI 代碼累積、缺乏版本控制、文檔不完整

---

## 🎯 三根支柱方案

### 1️⃣ 數據持久化（已完成 ✅）

**現況：** 已使用 SQLite 數據庫
**優點：**
- 數據不會因為關閉應用而丟失
- 具有事務支持，防止不完整的寫入
- 包含刪除日誌，可以恢復誤刪數據

**建議進階：**
```python
# database.py 中新增備份功能
def backup_database(backup_name=None):
    """每天自動備份數據庫"""
    import shutil
    from datetime import datetime
    
    if backup_name is None:
        backup_name = f"experiments_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    shutil.copy(DB_PATH, f"backups/{backup_name}")
    return backup_name

# app.py 中定期執行
if datetime.now().hour == 0:  # 每天午夜
    backup_database()
```

---

### 2️⃣ 異常處理與防呆（關鍵！）

**現況評估：**
```python
# ❌ 不好的做法（容易崩潰）
def save_data(data):
    power = float(data['power'])  # 如果 data['power'] 是 None，直接錯誤
    wavelength = float(data['wavelength'])
    return power * wavelength

# ✅ 好的做法（健壯）
def save_data(data):
    try:
        power = float(data.get('power', 0))
        if power <= 0:
            raise ValueError("功率必須大於 0")
        
        wavelength = float(data.get('wavelength', 0))
        if wavelength <= 0:
            raise ValueError("波長必須大於 0")
        
        # 驗證通過後再保存
        return power * wavelength
    
    except ValueError as e:
        return None, f"數值錯誤：{str(e)}"
    except Exception as e:
        return None, f"未預期的錯誤：{str(e)}"
```

**Week 2 中實施的改進：**
```python
# 在 app.py 主要操作中加入 try-except
if st.button("💾 保存實驗"):
    try:
        # 驗證輸入
        if wavelength <= 0 or power <= 0:
            st.error("❌ 波長和功率必須大於 0")
            return
        
        # 嘗試保存
        success, exp_id = save_experiment(experiment_data)
        
        if success:
            st.success(f"✅ 已保存 (ID: {exp_id})")
        else:
            st.error(f"❌ 保存失敗：{exp_id}")
    
    except Exception as e:
        st.error(f"❌ 發生未預期的錯誤：{str(e)}")
        # 記錄到日誌，供後續調試
        with open("error_log.txt", "a") as f:
            f.write(f"{datetime.now()}: {str(e)}\n")
```

**建議清單：**
- [ ] 所有用戶輸入都要驗證
- [ ] 所有 API 調用都要 try-except
- [ ] 所有 None 值都要檢查
- [ ] 所有數值轉換都要捕捉 ValueError
- [ ] 每個主要操作都要有成功/失敗的反饋

---

### 3️⃣ 版本控制與變更日誌（最關鍵）

#### **A. Git 版本控制設置**

**為什麼關鍵？** 當你改壞代碼時，可以一鍵倒退到上一個「能用」的版本。

**初始化 Git（只需一次）：**
```powershell
cd pulse_lab-assistant
git init
git config user.name "Nelson"
git config user.email "nelson@nthu.edu.tw"
```

**建立 `.gitignore`（防止不必要的文件進版本庫）：**
```
# 建立檔案：pulse_lab-assistant/.gitignore
venv/
__pycache__/
*.pyc
*.db
backups/
*.csv
.env
.streamlit/
error_log.txt
```

**日常使用（每天工作結束時）：**
```powershell
# 1. 查看改動了哪些文件
git status

# 2. 添加所有改動
git add .

# 3. 提交（寫好提交信息很重要！）
git commit -m "Week 2: 加入波長趨勢圖和材料分布圖"

# 4. 查看提交歷史
git log --oneline
```

**緊急時刻：回到上一個版本**
```powershell
# 查看過去的版本
git log --oneline

# 回到某個版本（例如：回到 3 個提交前）
git reset --hard HEAD~3

# 或回到特定提交
git checkout <commit-id>
```

#### **B. 變更日誌（CHANGELOG.md）**

**建立檔案：** `pulse_lab-assistant/CHANGELOG.md`

```markdown
# 變更日誌 (Changelog)

## Phase 2 - Week 1 (2026-04-26)

### ✅ 新增功能
- 刪除防呆驗證碼系統
- 智能時間戳 CSV 導出（避免覆蓋）
- 修改歷程自動追蹤（記錄 old_value → new_value）
- 按日期範圍導出數據

### 🐛 Bug 修復
- 修復修改歷史查詢時的 None 值錯誤
- 改善中文編碼問題

### ⚠️ 已知限制
- 編輯功能暫不可用（因複雜性）
- CSV 導出時若實驗數 > 500，可能性能下降

### 🔧 技術債
- [ ] 需要加入更完整的錯誤日誌
- [ ] SQLite 索引查詢性能可進一步優化
- [ ] 需要加入事務回滾機制

---

## Phase 2 - Week 2 (2026-05-XX)

### ✅ 新增功能
- 波長/功率趨勢圖（Plotly 互動式）
- 材料分布柱狀圖
- 參數相關性散點圖
- 實驗頻率熱力圖
- 統計摘要表

### 🎯 改進項目
- 使用 @st.cache_data 優化性能
- 實現標籤頁（Tabs）重組 UI
- 中文字體兼容性修復

### 📊 性能改進
- 平均圖表加載時間：10s → 2s
- 數據查詢緩存命中率：~80%
```

**每次更新時的習慣：**
```
工作結束時：
1. 測試功能是否正常
2. 寫一行新增功能描述到 CHANGELOG.md
3. git add . && git commit -m "簡短描述"
4. 檢查 git log 確認提交成功
```

---

## 📋 代碼品質清單

### **每週檢查（Week 1 完成後、Week 2 完成後）**

```markdown
## 代碼審查清單

- [ ] 所有用戶輸入都有驗證
- [ ] 所有外部 API 調用都有超時設定
- [ ] 所有可能的 None 值都被檢查
- [ ] 所有主要操作都有 try-except
- [ ] 所有修改都有清晰的 Git commit message
- [ ] 所有新功能都有在 CHANGELOG.md 中記錄
- [ ] 沒有硬編碼的密鑰或密碼（除了刪除驗證碼）
- [ ] 數據庫備份至少備份一次

## 效能檢查清單

- [ ] 應用啟動時間 < 5 秒
- [ ] 圖表加載時間 < 3 秒
- [ ] CSV 導出時間 < 10 秒（針對 1000+ 筆數據）
- [ ] 記憶體使用量 < 500MB
- [ ] 沒有明顯的 UI 卡頓

## 安全性檢查清單

- [ ] 刪除操作需要驗證碼
- [ ] 沒有日誌中記錄敏感信息
- [ ] 數據庫定期備份
- [ ] 備份保存在安全位置
```

---

## 🚀 「從學生作業到專業工具」的 3 步進階

### **現在的狀況（學生作業級別）**
```
輸入錯誤 → 應用崩潰 → 紅字報錯
```

### **3 個月後的目標（研究原型級別）**
```
輸入錯誤 → 應用自動驗證 → 友善提示「請重新輸入」
```

### **1 年後的願景（專業工具級別）**
```
輸入錯誤 → 應用自動驗證並建議 → 自動記錄到日誌 → 定期生成診斷報告
```

**達成方式：**
1. **現在** → 加強基本的異常處理
2. **Week 2 後** → 加入日誌系統和自動備份
3. **Month 2** → 加入性能監控和自動診斷

---

## 📊 穩定度改進時間表

```
Week 1 (當前)
├─ ✅ 數據庫設計（已完成）
├─ ✅ 刪除驗證（已完成）
└─ ⏳ 強化異常處理

Week 2
├─ 📈 加入數據可視化
├─ 🔄 實現數據緩存優化
└─ 📝 完整的 CHANGELOG.md

Week 3+
├─ 🐛 Bug 收集與修復
├─ 📊 性能監控儀表板
├─ 🔐 備份與恢復系統
└─ 📚 完整的使用文檔

Month 2+
├─ 🤖 機器學習預測
├─ 🔔 異常偵測告警
└─ 📤 自動生成研究報告
```

---

## 🎓 推薦閱讀與實踐

1. **Git 快速入門**
   ```powershell
   git --version  # 檢查是否已安裝
   ```
   如果未安裝，去 [git-scm.com](https://git-scm.com) 下載

2. **Python 錯誤處理最佳實踐**
   - 了解 try-except-finally 語法
   - 學習自定義異常類

3. **Streamlit 應用優化**
   - 使用 @st.cache_data 和 @st.cache_resource
   - 了解 st.session_state 的生命週期

---

## 🎯 行動計劃

### 立刻做（今天）
- [ ] 複製簡化版 app.py
- [ ] 初始化 Git 並建立 .gitignore
- [ ] 建立 CHANGELOG.md 並記錄到現在為止的工作

### 這週做
- [ ] 完成 Week 2 Day 1-2（數據整理）
- [ ] 每天結束時都執行 git commit
- [ ] 更新 CHANGELOG.md 記錄進度

### 下週做
- [ ] 完成 Week 2 圖表功能
- [ ] 進行完整的功能測試
- [ ] 寫一份「用戶指南」（中文）
- [ ] 代碼審查和性能調整

---

## 📞 遇到問題時

如果應用崩潰或出現大問題：

```powershell
# 1. 查看最近的改動
git log --oneline -5

# 2. 回到上一個「能用」的版本
git reset --hard HEAD~1

# 3. 檢查是否恢復正常
streamlit run app.py

# 4. 查看改動了什麼
git diff HEAD~1

# 5. 更仔細地修復問題
# （或重新修改後再提交）
```

這就是版本控制最寶貴的地方：**保險！**

---

## 💡 最後的建議

> 不要害怕改動代碼。有了 Git，你總能倒退。

目前 70-80% 的穩定度已經足夠應付學生研究。關鍵是：
1. ✅ 有數據庫保護你的數據
2. ✅ 有版本控制保護你的代碼
3. ✅ 有異常處理保護你的應用

按照這個方案走，到 Week 2 結束，穩定度會提升到 85-90%。

加油！🚀