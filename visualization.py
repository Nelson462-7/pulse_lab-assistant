import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# 設置中文字體
plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows
plt.rcParams['axes.unicode_minus'] = False

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
    ax.set_xlabel('日期')
    ax.set_ylabel('波長 (nm)')
    ax.set_title('波長使用趨勢')
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
    ax.set_xlabel('日期')
    ax.set_ylabel('功率 (mW)')
    ax.set_title('功率使用趨勢')
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
        labels={'x': '材料', 'y': '實驗次數'},
        title='各材料使用頻率',
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
        title='波長 vs 功率（按材料著色）',
        labels={'wavelength': '波長 (nm)', 'power': '功率 (mW)'},
        hover_data=['material']
    )
    
    return fig

def create_statistics_summary(stats):
    """統計摘要表"""
    summary_data = {
        '指標': [
            '總實驗數',
            '平均波長 (nm)',
            '波長範圍 (nm)',
            '使用材料數',
            '平均功率 (mW)'
        ],
        '數值': [
            stats.get('total_experiments', 0),
            f"{stats['wavelength']['avg']:.1f}" if stats.get('wavelength', {}).get('avg') else 'N/A',
            f"{stats['wavelength']['min']:.0f} - {stats['wavelength']['max']:.0f}" 
                if stats.get('wavelength', {}).get('min') else 'N/A',
            len(stats.get('by_material', {})),
            'N/A'  # 後續可加入
        ]
    }
    
    return pd.DataFrame(summary_data)