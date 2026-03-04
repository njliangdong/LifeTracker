import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# 页面配置
st.set_page_config(page_title="生活看板Pro", layout="wide")

# 文件夹准备
IMAGE_DIR = "health_images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

DATA_FILE = "health_records.csv"

# --- 逻辑：每月1号清理提醒 ---
if datetime.now().day == 1:
    st.warning("📅 今天是本月1号！建议清理上个月的照片以节省空间。")
    if st.button("一键清理历史照片"):
        for f in os.listdir(IMAGE_DIR):
            os.remove(os.path.join(IMAGE_DIR, f))
        st.success("清理完毕！")

# --- 图像压缩函数 ---
def process_and_save(img_file, slot_name, date_str):
    if img_file is None:
        return None  # 返回 None 表示本次没有新上传图片
    img = Image.open(img_file)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    file_name = f"{date_str}_{slot_name}.jpg"
    save_path = os.path.join(IMAGE_DIR, file_name)
    img.save(save_path, "JPEG", quality=30, optimize=True) 
    return save_path

# 数据加载
def load_data():
    try: 
        df = pd.read_csv(DATA_FILE)
        # 确保日期列是字符串方便比对
        df['日期'] = df['日期'].astype(str)
        return df
    except: 
        return pd.DataFrame()

data = load_data()

st.title("🍎 每日信息汇总管理")

tab1, tab2 = st.tabs(["✍️ 详细登记", "📊 数据历史"])

with tab1:
    with st.form("comprehensive_form", clear_on_submit=True):
        st.subheader("1. 基础睡眠与生理指标")
        c1, c2, c3 = st.columns(3)
        with c1:
            date = st.date_input("记录日期", datetime.now())
            weight = st.number_input("今日体重 (kg)", value=84.25, step=0.01)
            smoke = st.number_input("今日抽烟 (根)", value=10, step=1)
        with c2:
            s_in = st.text_input("昨日入睡时间", value="1:20")
            s_out = st.text_input("今早起床时间", value="8:40")
            s_dur = st.number_input("昨日睡眠维持时间 (hours)", value=8.0, step=0.5)
        with c3:
            s_night = st.selectbox("是否起夜", ["否", "是"])
            bowel = st.selectbox("排便性状", ["1", "2", "3", "4", "5", "6", "7"], index=3)
            meds = st.selectbox("药物、补剂是否按时按量", ["是", "否"])

        st.divider()
        st.subheader("2. 饮水与饮食记录 (请在下方拍照)")
        c4, c5 = st.columns(2)
        with c4:
            water = st.number_input("饮水量 (L)", value=2.0, step=0.1)
            water_extra = st.text_input("其中饮料", value="na")
            breakfast_t = st.text_area("早餐及完成时间点", placeholder="9:00, 粗粮等...")
            lunch_t = st.text_area("午餐及完成时间点", placeholder="13:30, 糙米、苦瓜...")
        with c5:
            snack_t = st.text_area("加餐及完成时间点", value="na")
            dinner_t = st.text_area("晚餐及完成时间点", placeholder="19:00, 小排骨等...")

        st.divider()
        st.subheader("3. 运动与呼吸练习")
        c6, c7 = st.columns(2)
        with c6:
            walk_l = st.number_input("午饭后步行时长(min)", value=0)
            walk_d = st.number_input("晚饭后步行时长(min)", value=0)
            cardio = st.text_input("有氧运动项目及时间(min)", placeholder="跑步 30min")
        with c7:
            strength = st.text_input("抗阻运动项目及时间(min)", placeholder="30组...")
            breath = st.selectbox("是否完成呼吸练习15min+", ["na", "是", "否"])

        st.divider()
        st.subheader("4. 状态与回顾")
        c8, c9 = st.columns(2)
        with c8:
            energy = st.select_slider("精力", options=["低", "中", "高"], value="中")
            mood = st.select_slider("情绪", options=["低", "中", "高"], value="中")
            hunger = st.text_input("饥饿感时间点", value="无")
        with c9:
            discomfort = st.text_area("不适状态/特殊情况", value="无")
            unfinished = st.text_area("对照方案，未完成项", value="无")
            review = st.text_area("一天回顾")

        st.info("📸 饮食拍照：若不更新照片请留空，系统将保留原照片。")
        col_img1, col_img2 = st.columns(2)
        with col_img1:
            img_b = st.camera_input("早餐照片")
            img_l = st.camera_input("午餐照片")
        with col_img2:
            img_s = st.camera_input("加餐照片")
            img_d = st.camera_input("晚餐照片")

        submit = st.form_submit_button("✅ 提交并更新今日记录")
        
        if submit:
            dt_str = str(date)
            
            # 准备新输入的数据
            new_data_point = {
                "日期": dt_str, "昨日入睡": s_in, "今早起床": s_out, "睡眠时长": s_dur,
                "是否起夜": s_night, "排便性状": bowel, "体重": weight, "用药按时": meds,
                "抽烟": smoke, "饮水": water, "其中饮料": water_extra,
                "早餐": breakfast_t, "午餐": lunch_t, "午后步行": walk_l,
                "加餐": snack_t, "晚餐": dinner_t, "晚后步行": walk_d,
                "有氧": cardio, "抗阻": strength, "呼吸练习": breath,
                "精力": energy, "情绪": mood, "饥饿点": hunger,
                "不适": discomfort, "未完成": unfinished, "回顾": review,
                "早餐图": process_and_save(img_b, "breakfast", dt_str),
                "午餐图": process_and_save(img_l, "lunch", dt_str),
                "加餐图": process_and_save(img_s, "snack", dt_str),
                "晚餐图": process_and_save(img_d, "dinner", dt_str)
            }

            if not data.empty and dt_str in data['日期'].values:
                # --- 覆盖逻辑：如果日期已存在 ---
                # 获取该行索引
                idx = data[data['日期'] == dt_str].index[0]
                
                for key, value in new_data_point.items():
                    # 如果是图片，只有在新拍了照片（value 不是 None）时才覆盖
                    if "图" in key:
                        if value is not None:
                            data.at[idx, key] = value
                    else:
                        # 对于文字和数字，直接以最后一次提交为准
                        data.at[idx, key] = value
                
                st.info(f"检测到 {dt_str} 已有记录，已完成覆盖更新。")
            else:
                # --- 新增逻辑：如果日期不存在 ---
                # 处理图片路径中的 None，转为 "na"
                for key in ["早餐图", "午餐图", "加餐图", "晚餐图"]:
                    if new_data_point[key] is None:
                        new_data_point[key] = "na"
                
                new_row = pd.DataFrame([new_data_point])
                data = pd.concat([data, new_row], ignore_index=True)
                st.success(f"已创建 {dt_str} 的新纪录！")

            # 保存到本地文件
            data.to_csv(DATA_FILE, index=False)
            st.rerun()

with tab2:
    st.subheader("历史记录回顾")
    if not data.empty:
        # 排序显示
        display_df = data.sort_values("日期", ascending=False)
        st.dataframe(display_df, use_container_width=True)
        
        for _, row in display_df.iterrows():
            with st.expander(f"📅 {row['日期']} 详细记录回顾"):
                pic_cols = st.columns(4)
                img_keys = ["早餐图", "午餐图", "加餐图", "晚餐图"]
                for i, slot in enumerate(img_keys):
                    with pic_cols[i]:
                        path = str(row[slot])
                        if path != "na" and path != "None" and os.path.exists(path):
                            st.image(path, caption=slot)
                        else:
                            st.caption(f"无{slot}")
                st.write(f"**总回顾**: {row['回顾']}")
                
        csv = data.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 导出完整 CSV 结果", data=csv, file_name="健康生活管理导出.csv")
