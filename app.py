import streamlit as st
import pandas as pd
from datetime import datetime

# 页面配置：移动端优化
st.set_page_config(page_title="每日信息管理", layout="wide")

# 数据保存逻辑（简单 CSV 版，部署后建议后续升级数据库）
DATA_FILE = "health_records.csv"

def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except:
        # 定义所有你需要的字段
        columns = [
            "日期", "昨日入睡", "今早起床", "睡眠时长(h)", "是否起夜", "排便性状",
            "体重(kg)", "用药按时", "抽烟(根)", "饮水(L)", "其中饮料",
            "早餐记录", "午餐记录", "午后步行(min)", "加餐记录", "晚餐记录",
            "晚后步行(min)", "有氧运动", "抗阻运动", "呼吸练习",
            "精力", "情绪", "饥饿时间点", "不适/特殊情况", "未完成项", "一天回顾"
        ]
        return pd.DataFrame(columns=columns)

# 加载数据
data = load_data()

st.title("📝 每日健康生活看板")

tab1, tab2 = st.tabs(["✍️ 详细登记", "📊 历史数据"])

with tab1:
    with st.form("detail_form", clear_on_submit=True):
        st.subheader("第一部分：基础指标")
        c1, c2, c3 = st.columns(3)
        with c1:
            date = st.date_input("记录日期", datetime.now())
            weight = st.number_input("今日体重 (kg)", value=84.25, step=0.01)
            water = st.number_input("饮水量 (L)", value=2.0, step=0.1)
        with c2:
            sleep_in = st.text_input("昨日入睡时间", value="1:20")
            wake_up = st.text_input("今早起床时间", value="8:40")
            sleep_hr = st.number_input("睡眠维持时长 (h)", value=8.0, step=0.5)
        with c3:
            bowel = st.selectbox("排便性状", ["1", "2", "3", "4", "5", "6", "7"], index=3)
            smoke = st.number_input("今日抽烟 (根)", value=10, step=1)
            drink_extra = st.text_input("其中饮料", value="na")

        st.divider()
        st.subheader("第二部分：饮食与运动")
        c4, c5 = st.columns(2)
        with c4:
            breakfast = st.text_area("早餐及时间点", placeholder="例如：9:00 粗粮...")
            lunch = st.text_area("午餐及时间点", placeholder="13:30 糙米、苦瓜...")
            dinner = st.text_area("晚餐及时间点", placeholder="19:00...")
            snack = st.text_area("加餐及时间点", value="na")
        with c5:
            walk_l = st.number_input("午饭后步行时长 (min)", value=0)
            walk_d = st.number_input("晚饭后步行时长 (min)", value=0)
            cardio = st.text_input("有氧运动项目及时间", placeholder="跑步 30min")
            strength = st.text_input("抗阻运动项目及时间", placeholder="深蹲 3组")

        st.divider()
        st.subheader("第三部分：状态与回顾")
        c6, c7 = st.columns(2)
        with c6:
            energy = st.select_slider("精力", options=["低", "中", "高"], value="中")
            mood = st.select_slider("情绪", options=["低", "中", "高"], value="中")
            night_wake = st.radio("是否起夜", ["否", "是"], horizontal=True)
            meds = st.radio("用药/补剂按时", ["是", "否"], horizontal=True)
            breath = st.radio("呼吸练习 15min+", ["是", "否", "na"], horizontal=True)
        with c7:
            hunger = st.text_input("饥饿感时间点", value="无")
            discomfort = st.text_area("不适状态/特殊情况", value="无")
            todo_missed = st.text_area("对照方案：未完成项", value="无")
            review = st.text_area("一天回顾", placeholder="今天整体感觉如何？")

        if st.form_submit_button("提交保存并同步"):
            new_record = {
                "日期": str(date), "昨日入睡": sleep_in, "今早起床": wake_up, 
                "睡眠时长(h)": sleep_hr, "是否起夜": night_wake, "排便性状": bowel,
                "体重(kg)": weight, "用药按时": meds, "抽烟(根)": smoke, 
                "饮水(L)": water, "其中饮料": drink_extra,
                "早餐记录": breakfast, "午餐记录": lunch, "午后步行(min)": walk_l,
                "加餐记录": snack, "晚餐记录": dinner, "晚后步行(min)": walk_d,
                "有氧运动": cardio, "抗阻运动": strength, "呼吸练习": breath,
                "精力": energy, "情绪": mood, "饥饿时间点": hunger,
                "不适/特殊情况": discomfort, "未完成项": todo_missed, "一天回顾": review
            }
            # 写入 CSV
            updated_df = pd.concat([data, pd.DataFrame([new_record])], ignore_index=True)
            updated_df.to_csv(DATA_FILE, index=False)
            st.success("✅ 数据已同步！")
            st.rerun()

with tab2:
    st.dataframe(data.sort_values("日期", ascending=False), use_container_width=True)
    csv = data.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 导出完整结果 (CSV)", data=csv, file_name="生活管理历史记录.csv")
