# 自動進入目錄
cd "C:\pulse_lab-assistant"

# 啟動虛擬環境
.\venv\Scripts\activate.ps1

# 啟動 Streamlit
streamlit run app.py

# 保持視窗開啟以觀察連線狀態
Read-Host "Press any key to close..."
