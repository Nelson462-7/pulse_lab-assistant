import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import warnings

# 抑制 matplotlib 字體警告
warnings.filterwarnings('ignore', category=UserWarning)

# ============================================================
# 中文字體設置（Windows 相容）
# ============================================================

def setup_chinese_font():
    """設置中文字體 - 自動偵測可用字體"""
    try:
        # Windows 優先使用
        plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    except:
        # 如果沒有中文字體，使用備選方案
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

setup_chinese_font()

# ============================================================
# 繪圖函數
# ============================================================

def plot_wavelength_trend(experiments):
    """波長趨勢圖"""
    import matplotlib.dates as mdates
    
    # 過濾有波長數據的實驗
    valid_exps = [e for e in experiments if e.get('wavelength_nm')]
    if len(valid_exps) < 2:
        return None
    
    dates = [datetime.fromisoformat(e['timestamp']) for e in valid_exps]
    wavelengths = [e['wavelength_nm'] for e in valid_exps]
    
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(dates, wavelengths, marker='o', linestyle='-', linewidth=2, color='blue')
    ax.set_xlabel('Date')  # 改用英文以避免字體問題
    ax.set_ylabel('Wavelength (nm)')
    ax.set_title('Wavelength Trend')
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return fig

def plot_power_trend(experiments):
    """功率趨勢圖"""
    import matplotlib.dates as mdates
    
    valid_exps = [e for e in experiments if e.get('power_mW')]
    if len(valid_exps) < 2:
        return None
    
    dates = [datetime.fromisoformat(e['timestamp']) for e in valid_exps]
    powers = [e['power_mW'] for e in valid_exps]
    
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(dates, powers, marker='s', linestyle='-', linewidth=2, color='red')
    ax.set_xlabel('Date')
    ax.set_ylabel('Power (mW)')
    ax.set_title('Power Trend')
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return fig

def plot_material_distribution(stats):
    """材料分布圖"""
    materials = list(stats['by_material'].keys())
    counts = list(stats['by_material'].values())
    
    fig = px.bar(
        x=materials,
        y=counts,
        labels={'x': 'Material', 'y': 'Count'},
        title='Material Distribution',
        color=materials,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    
    return fig

def plot_parameter_correlation(experiments):
    """參數相關性散點圖"""
    valid_exps = [e for e in experiments 
                  if e.get('wavelength_nm') and e.get('power_mW')]
    
    if len(valid_exps) < 3:
        return None
    
    data = {
        'wavelength': [e['wavelength_nm'] for e in valid_exps],
        'power': [e['power_mW'] for e in valid_exps],
        'material': [e.get('material', 'N/A') for e in valid_exps]
    }
    
    df = pd.DataFrame(data)
    
    fig = px.scatter(
        df,
        x='wavelength',
        y='power',
        color='material',
        title='Wavelength vs Power',
        labels={'wavelength': 'Wavelength (nm)', 'power': 'Power (mW)'},
        hover_data=['material']
    )
    
    return fig

def create_statistics_summary(stats):
    """統計摘要表"""
    summary_data = {
        'Metric': [
            'Total Experiments',
            'Average Wavelength (nm)',
            'Wavelength Range (nm)',
            'Material Types',
        ],
        'Value': [
            stats.get('total_experiments', 0),
            f"{stats['wavelength']['avg']:.1f}" if stats.get('wavelength', {}).get('avg') else 'N/A',
            f"{stats['wavelength']['min']:.0f} - {stats['wavelength']['max']:.0f}" 
                if stats.get('wavelength', {}).get('min') else 'N/A',
            len(stats.get('by_material', {})),
        ]
    }
    
    return pd.DataFrame(summary_data)

# ============================================================
# 驗證函數已加載
# ============================================================

if __name__ == "__main__":
    print("✅ All visualization functions loaded successfully")