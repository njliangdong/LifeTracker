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

# --- 核心逻辑：获取当前日期字符串 ---
def get_now_date_str():
    return datetime.now().strftime("%Y-%m-%d")

# --- 图像处理 ---
def process_and_save(img_file, slot_name, date_str):
    if img_file is None:
        return None
    try:
        img = Image.open(img_file)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        file_name = f"{date_str}_{slot_name}.jpg"
        save_path = os.path.join(IMAGE_DIR, file_name)
        img.save(save_path, "JPEG", quality=30, optimize=True)
        return save_path
    except Exception as e:
        st.error(f"图片保存失败: {e}")
        return None

# --- 数据加载 ---
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df['日期'] = df['日期'].astype(str)
        return df
    return pd.DataFrame()

# 初始化数据
if 'data' not in st.session_state:
    st.session_state.data = load_data()

# --- 逻辑：删除记录 ---
def delete_record(date_to_del):
    st.session_state.data = st.session_state.data[st.session_state.data['日期'] != date_to_del]
    st.session_state.data.to_csv(DATA_FILE, index=False)
    st.rerun()

# --- 逻辑：进入编辑模式 ---
def edit_record(row_data):
    st.session_state.edit_mode = True
    st.session_state.edit_date = row_data['日期']
    # 将要修改的数据暂存，以便填入表单
    st.session_state.temp_edit_data = row_data
    st.toast(f"正在修改 {row_data['日期']} 的记录", icon="📝")

st.title("🍎 每日信息汇总管理")

# 每月1号清理
if datetime.now().day == 1:
    st.warning("📅 今天是本月1号！建议清理旧照片。")
    if st.button("一键清理历史照片"):
        for f in os.listdir(IMAGE_DIR):
            os.remove(os.path.join(IMAGE_DIR, f))
        st.success("清理完毕！")

tab1, tab2 = st.tabs(["✍️ 详细登记", "📊 历史管理"])

with tab1:
    # 自动读取设备时间作为默认值
    current_device_date = datetime.now()
    
    # 检查当前是否处于从历史记录跳转过来的“编辑模式”
    is_editing = st.session_state.get('edit_mode', False)
    default_vals = st.session_state.get('temp_edit_data', {}) if is_editing else {}

    with st.form("comprehensive_form", clear_on_submit=not is_editing):
        st.subheader("1. 基础指标" + (" (修改模式)" if is_editing else ""))
        c1, c2, c3 = st.columns(3)
        with c1:
            # 如果是编辑模式，日期不可更改以防覆盖错误；否则默认为设备今日
            record_date = st.date_input("记录日期", 
                                       value=datetime.strptime(default_vals['日期'], "%Y-%m-%d") if is_editing else current_device_date,
                                       disabled=is_editing)
            weight = st.number_input("今日体重 (kg)", value=float(default_vals.get('体重', 84.25)), step=0.01)
            smoke = st.number_input("今日抽烟 (根)", value=int(default_vals.get('抽烟', 10)), step=1)
        with c2:
            s_in = st.text_input("昨日入睡时间", value=default_vals.get('昨日入睡', "1:20"))
            s_out = st.text_input("今早起床时间", value=default_vals.get('今早起床', "8:40"))
            s_dur = st.number_input("昨日睡眠维持时间 (h)", value=float(default_vals.get('睡眠时长', 8.0)), step=0.5)
        with c3:
            s_night = st.selectbox("是否起夜", ["否", "是"], index=0 if default_vals.get('是否起夜') == "否" else 1)
            bowel_options = ["1", "2", "3", "4", "5", "6", "7"]
            b_val = str(default_vals.get('排便性状', "4"))
            bowel = st.selectbox("排便性状", bowel_options, index=bowel_options.index(b_val) if b_val in bowel_options else 3)
            meds = st.selectbox("药物、补剂是否按时", ["是", "否"], index=0 if default_vals.get('用药按时') == "是" else 1)

        st.divider()
        st.subheader("2. 饮食记录")
        c4, c5 = st.columns(2)
        with c4:
            water = st.number_input("饮水量 (L)", value=float(default_vals.get('饮水', 2.0)), step=0.1)
            water_extra = st.text_input("其中饮料", value=default_vals.get('其中饮料', "na"))
            breakfast_t = st.text_area("早餐及时间", value=default_vals.get('早餐', ""))
            lunch_t = st.text_area("午餐及时间", value=default_vals.get('午餐', ""))
        with c5:
            snack_t = st.text_area("加餐及时间", value=default_vals.get('加餐', "na"))
            dinner_t = st.text_area("晚餐及时间", value=default_vals.get('晚餐', ""))

        st.divider()
        st.subheader("3. 运动与状态")
        c6, c7 = st.columns(2)
        with c6:
            walk_l = st.number_input("午后步行(min)", value=int(default_vals.get('午后步行', 0)))
            walk_d = st.number_input("晚后步行(min)", value=int(default_vals.get('晚后步行', 0)))
            energy = st.select_slider("精力", options=["低", "中", "高"], value=default_vals.get('精力', "中"))
        with c7:
            cardio = st.text_input("有氧项目", value=default_vals.get('有氧', ""))
            strength = st.text_input("抗阻项目", value=default_vals.get('抗阻', ""))
            mood = st.select_slider("情绪", options=["低", "中", "高"], value=default_vals.get('情绪', "中"))

        st.divider()
        review = st.text_area("一天回顾", value=default_vals.get('回顾', ""))
        
        st.info("📸 拍照区域：若不重拍将保留历史照片")
        ci1, ci2 = st.columns(2)
        with ci1:
            img_b = st.camera_input("早餐")
            img_l = st.camera_input("午餐")
        with ci2:
            img_s = st.camera_input("加餐")
            img_d = st.camera_input("晚餐")

        submit = st.form_submit_button("✅ 确认保存记录" if not is_editing else "💾 保存修改并退出")

        if submit:
            dt_str = str(record_date)
            new_record = {
                "日期": dt_str, "昨日入睡": s_in, "今早起床": s_out, "睡眠时长": s_dur,
                "是否起夜": s_night, "排便性状": bowel, "体重": weight, "用药按时": meds,
                "抽烟": smoke, "饮水": water, "其中饮料": water_extra,
                "早餐": breakfast_t, "午餐": lunch_t, "午后步行": walk_l,
                "加餐": snack_t, "晚餐": dinner_t, "晚后步行": walk_d,
                "有氧": cardio, "抗阻": strength, "精力": energy, "情绪": mood, "回顾": review,
                "早餐图": process_and_save(img_b, "breakfast", dt_str),
                "午餐图": process_and_save(img_l, "lunch", dt_str),
                "加餐图": process_and_save(img_s, "snack", dt_str),
                "晚餐图": process_and_save(img_d, "dinner", dt_str)
            }

            # 覆盖/更新逻辑
            df = st.session_state.data
            if not df.empty and dt_str in df['日期'].values:
                idx = df[df['日期'] == dt_str].index[0]
                for k, v in new_record.items():
                    if "图" in k:
                        if v is not None: df.at[idx, k] = v
                    else:
                        df.at[idx, k] = v
            else:
                # 补全图片空值
                for k in ["早餐图", "午餐图", "加餐图", "晚餐图"]:
                    if new_record[k] is None: new_record[k] = "na"
                df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)

            # 落地保存
            df.to_csv(DATA_FILE, index=False)
            st.session_state.data = df
            st.session_state.edit_mode = False # 退出编辑状态
            st.success("今日记录已最终确定并保存！")
            st.rerun()

with tab2:
    st.subheader("📜 历史数据管理")
    df_view = st.session_state.data
    if not df_view.empty:
        df_view = df_view.sort_values("日期", ascending=False)
        
        for _, row in df_view.iterrows():
            with st.expander(f"📅 {row['日期']} | 体重: {row['体重']}kg | 回顾: {str(row['回顾'])[:20]}..."):
                # 操作按钮
                b1, b2, _ = st.columns([1, 1, 8])
                if b1.button("修改", key=f"edit_{row['日期']}"):
                    edit_record(row)
                    st.rerun()
                if b2.button("删除", key=f"del_{row['日期']}", type="primary"):
                    delete_record(row['日期'])
                
                # 内容展示
                st.write(f"**睡眠**: {row['昨日入睡']} ~ {row['今早起床']} (时长: {row['睡眠时长']}h)")
                st.write(f"**饮食**: {row['早餐']} | {row['午餐']} | {row['晚餐']}")
                
                p_cols = st.columns(4)
                for i, img_k in enumerate(["早餐图", "午餐图", "加餐图", "晚餐图"]):
                    path = str(row[img_k])
                    if path != "na" and os.path.exists(path):
                        p_cols[i].image(path, caption=img_k)
    else:
        st.info("暂无历史记录。")
