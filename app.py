import streamlit as st
import pandas as pd
from datetime import datetime

# 页面基础设置
st.set_page_config(page_title="生活看板", layout="wide")

# 模拟云端数据库：这里使用本地 CSV 存储（部署后可升级为云存储）
DATA_FILE = "health_records.csv"

def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["日期", "体重", "抽烟", "精力", "情绪", "饮食备注"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# 加载现有数据
data = load_data()

# 界面设计：左侧录入，右侧查看
st.title("📑 每日信息管理")

tab1, tab2 = st.tabs(["✍️ 今日登记", "📊 数据历史"])

with tab1:
    with st.form("my_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("记录日期", datetime.now())
            weight = st.number_input("体重 (kg)", value=84.25, step=0.1)
            smoking = st.number_input("抽烟 (根)", value=10, step=1)
        
        with col2:
            energy = st.select_slider("精力状态", options=["低", "中", "高"], value="中")
            mood = st.select_slider("情绪状态", options=["低", "中", "高"], value="中")
        
        meal_info = st.text_area("饮食与运动备注", placeholder="例如：早餐9:00 粗粮；午饭后步行30min")
        
        if st.form_submit_button("提交保存"):
            new_row = {
                "日期": str(date), "体重": weight, "抽烟": smoking,
                "精力": energy, "情绪": mood, "饮食备注": meal_info
            }
            data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
            save_data(data)
            st.success("✅ 已同步至云端")

with tab2:
    st.dataframe(data.sort_values("日期", ascending=False), use_container_width=True)
    
    # 模仿您图片的导出功能
    csv = data.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 导出结果 (CSV)", data=csv, file_name="健康数据导出.csv")
