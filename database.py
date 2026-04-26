"""
Pulse Lab AI Assistant - 數據庫模塊 (升級版)
加入：修改歷史、刪除驗證、智能導出
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import csv
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 配置
# ============================================================

DELETION_PASSWORD = os.getenv("DELETION_PASSWORD")
DB_PATH = os.getenv("DATABASE_PATH", "experiments.db")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")

# ============================================================
# 初始化數據庫
# ============================================================

def init_database():
    """
    初始化數據庫 - 建立表結構
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 建立 experiments 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            wavelength_nm REAL,
            power_mW REAL,
            speed_mm_s REAL,
            material TEXT,
            other_params TEXT,
            notes TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 建立修改歷史表 (NEW)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS edit_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER NOT NULL,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            field_name TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            FOREIGN KEY(experiment_id) REFERENCES experiments(id)
        )
    """)
    
    # 建立刪除日誌表 (NEW)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deletion_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id INTEGER,
            deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            experiment_data TEXT,
            deleted_by TEXT
        )
    """)
    
    # 建立索引
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp 
        ON experiments(timestamp)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_material 
        ON experiments(material)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_wavelength 
        ON experiments(wavelength_nm)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_experiment_id
        ON edit_history(experiment_id)
    """)
    
    conn.commit()
    conn.close()
    
    return True

# ============================================================
# 保存數據
# ============================================================

def save_experiment(experiment_data):
    """
    保存單個實驗記錄到數據庫
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        timestamp = experiment_data.get("timestamp", datetime.now().isoformat())
        wavelength = experiment_data.get("wavelength_nm")
        power = experiment_data.get("power_mW")
        speed = experiment_data.get("speed_mm_s")
        material = experiment_data.get("material")
        other_params = experiment_data.get("other_params", "N/A")
        notes = experiment_data.get("notes", "N/A")
        source = experiment_data.get("source", "unknown")
        
        cursor.execute("""
            INSERT INTO experiments 
            (timestamp, wavelength_nm, power_mW, speed_mm_s, material, 
             other_params, notes, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, wavelength, power, speed, material, 
              other_params, notes, source))
        
        conn.commit()
        experiment_id = cursor.lastrowid
        conn.close()
        
        return True, experiment_id
    
    except Exception as e:
        return False, str(e)

# ============================================================
# 修改數據 (NEW)
# ============================================================

def update_experiment(experiment_id, updated_data):
    """
    修改實驗記錄，並自動記錄修改歷史
    
    Args:
        experiment_id (int): 實驗ID
        updated_data (dict): 要更新的數據
        
    Returns:
        (bool, str): (成功/失敗, 消息)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 取得原始數據
        cursor.execute("SELECT * FROM experiments WHERE id = ?", (experiment_id,))
        original = cursor.fetchone()
        
        if not original:
            conn.close()
            return False, "實驗不存在"
        
        # 將原始行轉換為字典
        col_names = [description[0] for description in cursor.description]
        original_dict = dict(zip(col_names, original))
        
        # 記錄每個修改
        for field, new_value in updated_data.items():
            if field in original_dict:
                old_value = original_dict[field]
                if old_value != new_value:  # 只記錄真正改變的欄位
                    cursor.execute("""
                        INSERT INTO edit_history 
                        (experiment_id, field_name, old_value, new_value)
                        VALUES (?, ?, ?, ?)
                    """, (experiment_id, field, str(old_value), str(new_value)))
        
        # 更新主表
        set_clause = ", ".join([f"{k} = ?" for k in updated_data.keys()])
        set_clause += ", updated_at = CURRENT_TIMESTAMP"
        values = list(updated_data.values()) + [experiment_id]
        
        cursor.execute(f"""
            UPDATE experiments 
            SET {set_clause}
            WHERE id = ?
        """, values)
        
        conn.commit()
        conn.close()
        
        return True, f"實驗 #{experiment_id} 已更新"
    
    except Exception as e:
        return False, str(e)

def get_edit_history(experiment_id):
    """
    獲取實驗的修改歷史
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM edit_history 
            WHERE experiment_id = ? 
            ORDER BY changed_at DESC
        """, (experiment_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    except Exception as e:
        print(f"查詢失敗：{e}")
        return []

# ============================================================
# 刪除數據（有驗證碼保護）
# ============================================================

def delete_experiment(experiment_id, password):
    """
    刪除實驗記錄（需要正確的驗證碼）
    記錄到刪除日誌防呆
    
    Args:
        experiment_id (int): 實驗ID
        password (str): 刪除驗證碼
        
    Returns:
        (bool, str): (成功/失敗, 消息)
    """
    try:
        # 驗證密碼
        if password != DELETION_PASSWORD:
            return False, "❌ 驗證碼錯誤！刪除失敗"
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 先取得完整數據（保存到刪除日誌）
        cursor.execute("SELECT * FROM experiments WHERE id = ?", (experiment_id,))
        experiment = cursor.fetchone()
        
        if not experiment:
            conn.close()
            return False, "實驗不存在"
        
        # 轉換為字典並記錄到刪除日誌
        col_names = [description[0] for description in cursor.description]
        experiment_dict = dict(zip(col_names, experiment))
        
        cursor.execute("""
            INSERT INTO deletion_log 
            (experiment_id, experiment_data, deleted_by)
            VALUES (?, ?, ?)
        """, (experiment_id, json.dumps(experiment_dict, ensure_ascii=False), "user"))
        
        # 刪除修改歷史
        cursor.execute("DELETE FROM edit_history WHERE experiment_id = ?", (experiment_id,))
        
        # 刪除實驗記錄
        cursor.execute("DELETE FROM experiments WHERE id = ?", (experiment_id,))
        
        conn.commit()
        conn.close()
        
        return True, f"✅ 實驗 #{experiment_id} 已永久刪除"
    
    except Exception as e:
        return False, str(e)

# ============================================================
# 查詢數據
# ============================================================

def get_all_experiments():
    """獲取所有實驗記錄"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM experiments 
            ORDER BY timestamp DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    except Exception as e:
        print(f"查詢失敗：{e}")
        return []

def query_by_material(material):
    """按材料查詢"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM experiments 
            WHERE material = ? 
            ORDER BY timestamp DESC
        """, (material,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    except Exception as e:
        print(f"查詢失敗：{e}")
        return []

def query_by_date_range(start_date, end_date):
    """按日期範圍查詢"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM experiments 
            WHERE timestamp BETWEEN ? AND ? 
            ORDER BY timestamp DESC
        """, (start_date, end_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    except Exception as e:
        print(f"查詢失敗：{e}")
        return []

def query_by_wavelength_range(min_nm, max_nm):
    """按波長範圍查詢"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM experiments 
            WHERE wavelength_nm BETWEEN ? AND ? 
            ORDER BY wavelength_nm
        """, (min_nm, max_nm))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    except Exception as e:
        print(f"查詢失敗：{e}")
        return []

# ============================================================
# 統計數據
# ============================================================

def get_experiment_stats():
    """獲取實驗統計信息"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM experiments")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT material, COUNT(*) as count 
            FROM experiments 
            WHERE material IS NOT NULL
            GROUP BY material
        """)
        material_stats = dict(cursor.fetchall())
        
        cursor.execute("""
            SELECT 
                MIN(wavelength_nm) as min_wavelength,
                MAX(wavelength_nm) as max_wavelength,
                AVG(wavelength_nm) as avg_wavelength
            FROM experiments 
            WHERE wavelength_nm IS NOT NULL
        """)
        wavelength_stats = cursor.fetchone()
        
        # 按日期統計
        cursor.execute("""
            SELECT DATE(timestamp) as date, COUNT(*) as count
            FROM experiments
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        """)
        daily_stats = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "total_experiments": total_count,
            "by_material": material_stats,
            "wavelength": {
                "min": wavelength_stats[0],
                "max": wavelength_stats[1],
                "avg": wavelength_stats[2]
            },
            "by_date": daily_stats
        }
    
    except Exception as e:
        print(f"統計失敗：{e}")
        return {}

# ============================================================
# 數據導出 (升級版 - 智能命名 + 日期篩選)
# ============================================================

def export_to_csv(date_filter=None):
    """
    將數據導出為CSV檔案
    使用時間戳命名，避免覆蓋
    
    Args:
        date_filter (str): 可選的日期過濾 (YYYY-MM-DD format)
        
    Returns:
        (bool, str): (成功/失敗, 檔名或錯誤信息)
    """
    try:
        # 取得數據
        if date_filter:
            # 查詢特定日期的數據
            start = f"{date_filter}T00:00:00"
            end = f"{date_filter}T23:59:59"
            experiments = query_by_date_range(start, end)
        else:
            # 查詢所有數據
            experiments = get_all_experiments()
        
        if not experiments:
            return False, "沒有數據可導出"
        
        # 生成帶時間戳的檔名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if date_filter:
            filename = f"experiments_{date_filter}_export_{timestamp}.csv"
        else:
            filename = f"experiments_all_export_{timestamp}.csv"
        
        # 寫入CSV
        fieldnames = list(experiments[0].keys())
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(experiments)
        
        return True, filename
    
    except Exception as e:
        return False, f"導出失敗：{e}"

def get_available_dates():
    """
    獲取有實驗記錄的所有日期
    用於CSV導出的日期選擇
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT DATE(timestamp) as date
            FROM experiments
            ORDER BY date DESC
        """)
        
        dates = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return dates
    
    except Exception as e:
        print(f"查詢失敗：{e}")
        return []

# ============================================================
# 數據復原（從刪除日誌復原）
# ============================================================

def restore_deleted_experiment(experiment_id):
    """
    從刪除日誌恢復已刪除的實驗
    (防呆機制)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 查詢刪除日誌
        cursor.execute("""
            SELECT experiment_data FROM deletion_log 
            WHERE experiment_id = ?
            ORDER BY deleted_at DESC
            LIMIT 1
        """, (experiment_id,))
        
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False, "找不到刪除記錄"
        
        # 恢復數據
        experiment_data = json.loads(result[0])
        
        cursor.execute("""
            INSERT INTO experiments 
            (timestamp, wavelength_nm, power_mW, speed_mm_s, material, 
             other_params, notes, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            experiment_data.get('timestamp'),
            experiment_data.get('wavelength_nm'),
            experiment_data.get('power_mW'),
            experiment_data.get('speed_mm_s'),
            experiment_data.get('material'),
            experiment_data.get('other_params'),
            experiment_data.get('notes'),
            experiment_data.get('source')
        ))
        
        conn.commit()
        conn.close()
        
        return True, f"實驗已恢復"
    
    except Exception as e:
        return False, str(e)

# ============================================================
# 刪除數據庫（用於測試/重置）
# ============================================================

def reset_database():
    """刪除數據庫（謹慎使用！）"""
    try:
        if Path(DB_PATH).exists():
            Path(DB_PATH).unlink()
            print(f"已刪除 {DB_PATH}")
            return True
        return False
    except Exception as e:
        print(f"刪除失敗：{e}")
        return False

# ============================================================
# 初始化
# ============================================================

if __name__ == "__main__":
    init_database()
    print("✅ 數據庫初始化成功")