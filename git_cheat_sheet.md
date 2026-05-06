1. 啟動開發環境
在進行任何 Git 操作前，請先確保進入專案目錄並啟動虛擬環境：

PowerShell
# 進入專案目錄
cd C:\pulse_lab-assistant

# 啟動虛擬環境
.\venv\Scripts\Activate.ps1
提示：若出現權限錯誤，請先執行 Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process。

2. 標準更新流程 (Daily Workflow)
當你修改了 app.py、processor.py 或新增了實驗數據時，請執行以下步驟：

檢查變動狀態：

PowerShell
git status
加入追蹤：

PowerShell
    git add .
    ```
    *注意：若有不念推上 Git 的大檔案，請先確認 `.gitignore` 已排除該路徑。*
3.  **提交存檔 (Commit)**：
    ```powershell
    git commit -m "feat: 描述你的更新內容 (例如：優化高光譜繪圖顏色)"
    ```
4.  **推送到雲端 (Push)**：
    
```powershell
    git push origin main
    ```

---

### 3. 關鍵檔案說明
*   **`app.py`**: 系統主程式，包含 Streamlit UI 邏輯。
*   **`processor.py`**: 核心數據處理模組（去噪、正規化邏輯）。
*   **`database.py`**: SQLite 資料庫操作與版本控制。
*   **`.env`**: **(禁止上傳)** 存放 API URL 等敏感資訊。
*   **`.gitignore`**: 設定哪些檔案不進版本控制（如 `venv/`, `.env`, `*.db`）。

---

### 4. 常用檢查指令
*   **查看提交歷史**：`git log --oneline -n 5`
*   **撤銷上一次 add**：`git restore --staged <file>`
*   **執行網站測試**：`streamlit run app.py`

---

### 💡 專案備忘 (Phase 2)
*   **繪圖規範**：輸出圖表需保持白底黑字、標題置中，方便黃教授閱覽。
*   **API 規範**：Streamlit 2026 新版本需將 `use_container_width=True` 改為 `width="stretch"`[cite: 6]。

---

**最後更新日期**：2026-05-06
**維護者**：KUO, YAO-JUNG (Nelson)