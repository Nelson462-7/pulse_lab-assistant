import streamlit as st
import requests
import json
from datetime import datetime
import re
from database import (
    init_database, save_experiment, get_all_experiments,
    query_by_material, query_by_date_range, get_experiment_stats,
    export_to_csv, get_edit_history,
    delete_experiment, get_available_dates
)

from visualization import (
    plot_wavelength_trend, plot_power_trend,
    plot_material_distribution, plot_parameter_correlation,
    create_statistics_summary
)

st.set_page_config(page_title="Pulse Lab AI Assistant", layout="wide")

# ============================================================
# 初始化
# ============================================================
init_database()

st.title("🧪 Pulse Lab AI 實驗助手 Phase 2")
st.write("智能參數提取 + 數據庫儲存與版本控制")

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MAX_INPUT_LENGTH = 500
REQUIRED_KEYWORDS = ["nm", "mW", "mm/s", "波長", "功率", "速度"]

# ============================================================
# 工具函數 (AI 與 規則提取)
# ============================================================

def validate_input(text):
    """驗證輸入"""
    if not text or not text.strip():
        return False, "輸入不能為空"
    
    if len(text) > MAX_INPUT_LENGTH:
        return False, f"輸入過長 (>{MAX_INPUT_LENGTH}字符)。請使用結構化表單或縮短敘述。"
    
    text_lower = text.lower()
    has_keyword = any(kw.lower() in text_lower for kw in REQUIRED_KEYWORDS)
    if not has_keyword:
        return False, "輸入似乎與實驗參數無關。請提供波長、功率、速度等信息。"
    
    return True, None

def try_rule_based_extraction(text):
    """規則提取 - 快速且穩定"""
    result = {}
    
    wavelength_match = re.search(r'(\d+)\s*nm', text, re.IGNORECASE)
    if wavelength_match:
        result["波長 (nm)"] = wavelength_match.group(1)
    
    power_match = re.search(r'(\d+(?:\.\d+)?)\s*(mW|W|kW)', text, re.IGNORECASE)
    if power_match:
        result["功率"] = f"{power_match.group(1)} {power_match.group(2)}"
    
    speed_match = re.search(r'(\d+(?:\.\d+)?)\s*mm/s', text, re.IGNORECASE)
    if speed_match:
        result["掃描速度 (mm/s)"] = speed_match.group(1)
    
    materials = ["PDMS", "玻璃", "矽", "聚亞醯胺", "PET", "PC"]
    for material in materials:
        if material.lower() in text.lower():
            result["材料"] = material
            break
    
    if len(result) >= 3:
        return result
    
    return None

def extract_with_ai(user_input):
    """AI 提取 - 用於複雜情況"""
    SYSTEM_PROMPT = """你是一個實驗室AI助手。
當用戶描述一個實驗時，你要提取以下參數並用JSON格式回傳：
{
    "波長 (nm)": "值或N/A",
    "功率 (mW)": "值或N/A",
    "掃描速度 (mm/s)": "值或N/A",
    "材料": "值或N/A",
    "其他參數": "值或N/A"
}
只回傳JSON，不要其他文字。"""
    
    payload = {
        "model": "llama2",
        "prompt": f"{SYSTEM_PROMPT}\n\n用戶說：{user_input}",
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result.get("response", "")
            
            json_start = ai_response.find("{")
            json_end = ai_response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_str = ai_response[json_start:json_end]
                return json.loads(json_str), ai_response
        
        return None, None
    
    except Exception as e:
        return None, str(e)

# ============================================================
# UI - 側邊欄
# ============================================================

with st.sidebar:
    st.header("⚙️ 系統設定")
    page = st.radio(
        "選擇功能",
        ["📝 新增實驗", "📊 查看與刪除", "📈 統計與導出"],
        help="在不同功能間切換"
    )
    
    st.divider()
    st.markdown("""
    ### 📋 Phase 2 進度
    - ✅ 刪除防呆驗證
    - ✅ 智能時間戳導出
    - ✅ 修改歷程查看
    - ⏳ Week 2：數據可視化
    
    ### 🎯 系統狀態
    - **數據庫**: SQLite ✅
    - **版本控制**: 刪除日誌 ✅
    - **穩定性**: 70-80%
    """)

# ============================================================
# Page 1：新增實驗
# ============================================================

if page == "📝 新增實驗":
    st.subheader("新增實驗記錄")
    
    input_mode = st.radio(
        "選擇輸入方式",
        ["結構化表單（推薦）", "自由敘述"],
        help="結構化表單最快最準"
    )
    
    if input_mode == "結構化表單（推薦）":
        st.write("✅ 直接填入參數 - 最快、最準確、最穩定")
        
        col1, col2 = st.columns(2)
        
        with col1:
            wavelength = st.number_input(
                "波長 (nm)",
                min_value=100.0,
                max_value=2000.0,
                value=808.0,
                step=1.0
            )
            power = st.number_input(
                "功率 (mW)",
                min_value=1.0,
                max_value=100000.0,
                value=300.0,
                step=10.0
            )
        
        with col2:
            speed = st.number_input(
                "掃描速度 (mm/s)",
                min_value=0.1,
                max_value=100.0,
                value=3.0,
                step=0.1
            )
            material = st.selectbox(
                "材料",
                ["PDMS", "玻璃", "矽", "聚亞醯胺", "PET", "PC", "其他"]
            )
        
        notes = st.text_area(
            "實驗備註",
            placeholder="例如：成功製造微流體通道，質量很好",
            height=80
        )
        
        if st.button("💾 保存實驗", type="primary", use_container_width=True):
            try:
                experiment_data = {
                    "timestamp": datetime.now().isoformat(),
                    "wavelength_nm": wavelength,
                    "power_mW": power,
                    "speed_mm_s": speed,
                    "material": material,
                    "other_params": "N/A",
                    "notes": notes if notes else "N/A",
                    "source": "結構化表單"
                }
                
                success, exp_id = save_experiment(experiment_data)
                
                if success:
                    st.success(f"✅ 實驗已保存！(ID: {exp_id})")
                    st.json(experiment_data)
                else:
                    st.error(f"❌ 保存失敗：{exp_id}")
            
            except Exception as e:
                st.error(f"❌ 發生錯誤：{str(e)}")
    
    else:  # 自由敘述
        st.write("⚠️ 自由敘述依賴AI提取，可能不如結構化表單準確")
        
        user_input = st.text_area(
            "輸入實驗敘述",
            placeholder="例如：今天用808nm雷射，功率300mW，掃描速度3mm/s，材料PDMS",
            height=100
        )
        
        if st.button("🚀 提取並保存", type="primary", use_container_width=True):
            is_valid, error_msg = validate_input(user_input)
            
            if not is_valid:
                st.error(f"❌ {error_msg}")
            else:
                try:
                    st.info("分析中...")
                    
                    # 第1步：嘗試規則提取
                    rule_result = try_rule_based_extraction(user_input)
                    
                    if rule_result:
                        st.success("✅ 規則提取成功")
                        
                        try:
                            experiment_data = {
                                "timestamp": datetime.now().isoformat(),
                                "wavelength_nm": float(rule_result.get("波長 (nm)", 0)) if "波長 (nm)" in rule_result else None,
                                "power_mW": float(rule_result.get("功率", "0").split()[0]) if "功率" in rule_result else None,
                                "speed_mm_s": float(rule_result.get("掃描速度 (mm/s)", 0)) if "掃描速度 (mm/s)" in rule_result else None,
                                "material": rule_result.get("材料"),
                                "other_params": "N/A",
                                "notes": user_input,
                                "source": "規則提取"
                            }
                            
                            success, exp_id = save_experiment(experiment_data)
                            
                            if success:
                                st.success(f"✅ 已保存 (ID: {exp_id})")
                                st.json(rule_result)
                            else:
                                st.error(f"保存失敗：{exp_id}")
                        
                        except ValueError as ve:
                            st.error(f"❌ 數值轉換失敗：{str(ve)}")
                    
                    else:
                        # 第2步：規則失敗，才用AI
                        st.info("嘗試AI詳細分析...")
                        
                        parameters, ai_raw = extract_with_ai(user_input)
                        
                        if parameters:
                            st.success("✅ AI提取成功")
                            
                            try:
                                experiment_data = {
                                    "timestamp": datetime.now().isoformat(),
                                    "wavelength_nm": float(parameters.get("波長 (nm)", 0)) if parameters.get("波長 (nm)") not in ["N/A", None] else None,
                                    "power_mW": float(parameters.get("功率 (mW)", 0)) if parameters.get("功率 (mW)") not in ["N/A", None] else None,
                                    "speed_mm_s": float(parameters.get("掃描速度 (mm/s)", 0)) if parameters.get("掃描速度 (mm/s)") not in ["N/A", None] else None,
                                    "material": parameters.get("材料") if parameters.get("材料") != "N/A" else None,
                                    "other_params": parameters.get("其他參數", "N/A"),
                                    "notes": user_input,
                                    "source": "AI提取"
                                }
                                
                                success, exp_id = save_experiment(experiment_data)
                                
                                if success:
                                    st.success(f"✅ 已保存 (ID: {exp_id})")
                                    st.json(parameters)
                                else:
                                    st.error(f"保存失敗：{exp_id}")
                            
                            except ValueError as ve:
                                st.error(f"❌ 數值轉換失敗：{str(ve)}")
                        
                        else:
                            st.error("❌ 無法解析輸入")
                            if ai_raw:
                                st.warning(f"AI回應：{ai_raw[:200]}")
                
                except Exception as e:
                    st.error(f"❌ 發生未預期的錯誤：{str(e)}")

# ============================================================
# Page 2：查看與刪除
# ============================================================

elif page == "📊 查看與刪除":
    st.subheader("實驗記錄查詢與管理")
    
    query_type = st.radio(
        "查詢方式",
        ["所有記錄", "按材料", "按日期"],
        horizontal=True
    )
    
    experiments = []
    
    try:
        if query_type == "所有記錄":
            experiments = get_all_experiments()
        
        elif query_type == "按材料":
            all_exps = get_all_experiments()
            materials = list(set([exp.get('material') for exp in all_exps if exp.get('material')]))
            
            if materials:
                selected_material = st.selectbox("選擇材料", sorted(materials))
                experiments = query_by_material(selected_material)
            else:
                st.info("還沒有材料記錄")
        
        elif query_type == "按日期":
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("開始日期")
            with col2:
                end_date = st.date_input("結束日期")
            
            if st.button("搜索", use_container_width=True):
                experiments = query_by_date_range(
                    f"{start_date}T00:00:00",
                    f"{end_date}T23:59:59"
                )
        
        # 顯示查詢結果
        if experiments:
            st.write(f"📌 共找到 {len(experiments)} 條記錄")
            
            for exp in experiments:
                with st.expander(
                    f"📁 ID:{exp['id']} | {exp['timestamp'][:16]} | "
                    f"{exp.get('material', 'N/A')} | {exp.get('power_mW', 'N/A')}mW"
                ):
                    col1, col2 = st.columns(2)   
                    
                    with col1:
                        st.write(f"**波長**: {exp.get('wavelength_nm', 'N/A')} nm")
                        st.write(f"**功率**: {exp.get('power_mW', 'N/A')} mW")
                        st.write(f"**速度**: {exp.get('speed_mm_s', 'N/A')} mm/s")
                    
                    with col2:
                        st.write(f"**材料**: {exp.get('material', 'N/A')}")
                        st.write(f"**來源**: {exp.get('source', 'unknown')}")
                        st.write(f"**建立**: {exp.get('created_at', 'N/A')}")
                    
                    st.write(f"**備註**: {exp.get('notes', 'N/A')}")
                    
                    # 顯示修改歷史
                    history = get_edit_history(exp['id'])
                    if history:
                        st.markdown("---")
                        st.markdown("**📝 數據修改歷程:**")
                        for h in history:
                            st.caption(
                                f"🕒 [{h['changed_at'][:16]}] "
                                f"修改了 `{h['field_name']}`: "
                                f"從 `{h['old_value']}` → `{h['new_value']}`"
                            )
                      
                    # 刪除按鈕 DELETION_PASSWORD = "pulse2026"  # 刪除驗證碼
                    st.markdown("---")
                    st.markdown("**⚠️ 危險區域：刪除此實驗**")
                    
                    col_del1, col_del2 = st.columns([2, 1])
                    
                    with col_del1:
                        del_pwd = st.text_input(
                            "輸入驗證碼以確認刪除",
                            type="password",
                            key=f"del_pwd_{exp['id']}"
                        )
                    
                    with col_del2:
                        st.write("")
                        st.write("")
                        if st.button(
                            "🗑️ 確認刪除",
                            type="primary",
                            key=f"del_btn_{exp['id']}",
                            use_container_width=True
                        ):
                            try:
                                success, message = delete_experiment(exp['id'], del_pwd)
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                            except Exception as e:
                                st.error(f"❌ 刪除過程中出錯：{str(e)}")
        
        elif query_type in ["按材料", "按日期"]:
            st.info("請選擇條件後點擊「搜索」")
    
    except Exception as e:
        st.error(f"❌ 查詢失敗：{str(e)}")

# ============================================================
# Page 3：統計與導出
# ============================================================

elif page == "📈 統計與導出":
    st.subheader("實驗統計與數據分析")
    
    try:
        stats = get_experiment_stats()
        experiments = get_all_experiments()
        
        if stats and stats.get('total_experiments', 0) > 0:
            
            # 使用標籤頁組織內容
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 數據摘要",
                "📈 趨勢分析",
                "🎨 分布圖表",
                "📥 數據導出"
            ])
            
            with tab1:
                st.markdown("### 📊 統計摘要")
                summary_df = create_statistics_summary(stats)
                st.dataframe(summary_df, use_container_width=True)
                
                # 按材料統計
                if stats.get('by_material'):
                    st.markdown("### 🧪 按材料分佈")
                    for material, count in sorted(stats['by_material'].items(), 
                                                 key=lambda x: x[1], reverse=True):
                        st.write(f"- **{material}**: {count} 次")
            
            with tab2:
                st.markdown("### 📈 參數趨勢")
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_wavelength = plot_wavelength_trend(experiments)
                    if fig_wavelength:
                        st.pyplot(fig_wavelength)
                    else:
                        st.info("波長數據不足（需至少 2 筆）")
                
                with col2:
                    fig_power = plot_power_trend(experiments)
                    if fig_power:
                        st.pyplot(fig_power)
                    else:
                        st.info("功率數據不足（需至少 2 筆）")
            
            with tab3:
                st.markdown("### 🎨 分布與相關性")
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_material = plot_material_distribution(stats)
                    if fig_material:
                        st.plotly_chart(fig_material, use_container_width=True)
                
                with col2:
                    fig_correlation = plot_parameter_correlation(experiments)
                    if fig_correlation:
                        st.plotly_chart(fig_correlation, use_container_width=True)
                    else:
                        st.info("參數數據不足（需至少 3 筆有波長和功率的記錄）")
            
            with tab4:
                # 保留原有的導出功能
                st.markdown("### 📥 智能導出 CSV")
                
                dates = get_available_dates()
                export_options = ["所有歷史記錄"] + dates
                
                col_exp1, col_exp2 = st.columns([3, 1])
                
                with col_exp1:
                    export_choice = st.selectbox(
                        "選擇要導出的數據範圍",
                        export_options
                    )
                
                with col_exp2:
                    st.write("")
                    st.write("")
                    if st.button("🚀 執行導出", use_container_width=True):
                        try:
                            filter_val = None if export_choice == "所有歷史記錄" else export_choice
                            success, filename = export_to_csv(date_filter=filter_val)
                            
                            if success:
                                st.success(f"✅ 導出成功！\n檔名：`{filename}`")
                            else:
                                st.error(f"❌ 導出失敗：{filename}")
                        
                        except Exception as e:
                            st.error(f"❌ 導出過程中出錯：{str(e)}")
        else:
            st.info("還沒有足夠的數據進行分析")
    
    except Exception as e:
        st.error(f"❌ 統計失敗：{str(e)}")

# ============================================================
# 底部信息
# ============================================================

st.divider()
st.markdown("""
**🎯 Phase 2 完成清單**
- ✅ 刪除防呆驗證碼
- ✅ 智能時間戳導出
- ✅ 修改歷程追蹤
- ⏳ 數據可視化（Week 2）

**下一步**：進入 Week 2，實現數據可視化、趨勢分析、統計圖表
""")