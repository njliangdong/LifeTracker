import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
import io

# 页面配置
st.set_page_config(page_title="生活看板Pro", layout="wide")

# 文件夹准备
IMAGE_DIR = "health_images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

DATA_FILE = "health_records.csv"

# --- 核心逻辑：数据加载与去重 ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            df['日期'] = df['日期'].astype(str)
            df = df.drop_duplicates(subset=['日期'], keep='last').reset_index(drop=True)
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()

# 初始化全局数据
if 'data' not in st.session_state:
    st.session_state.data = load_data()

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

# --- Markdown 导出 ---
def convert_to_md(selected_df):
    md_text = f"# 生活看板历史记录导出\n*导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n---\n"
    for _, row in selected_df.iterrows():
        md_text += f"## 📅 日期：{row['日期']}\n"
        md_text += f"### 🩺 基础指标\n"
        md_text += f"- **体重**: {row['体重']}kg | **抽烟**: {row['抽烟']}根 | **用药**: {row['用药按时']}\n"
        md_text += f"- **睡眠**: {row['昨日入睡']} ~ {row['今早起床']} (时长: {row['睡眠时长']}h)\n"
        md_text += f"--- \n"
    return md_text

def delete_record(date_to_del):
    st.session_state.data = st.session_state.data[st.session_state.data['日期'] != date_to_del]
    st.session_state.data.to_csv(DATA_FILE, index=False)
    st.toast(f"已删除 {date_to_del} 的记录", icon="🗑️")
    st.rerun()

# --- UI 渲染 ---
st.title("🍎 每日信息汇总管理")

tab1, tab2 = st.tabs(["✍️ 详细登记", "📊 历史管理"])

with tab1:
    # 1. 日期选择（作为进度加载的 Key）
    # 默认显示今天，用户也可以切换日期来查看/补录历史
    curr_date = st.date_input("选择记录日期", value=datetime.now())
    date_str = str(curr_date)
    
    # 2. 尝试从已有数据中加载该日期的“进度”
    existing_df = st.session_state.data
    record = None
    if not existing_df.empty and date_str in existing_df['日期'].values:
        record = existing_df[existing_df['日期'] == date_str].iloc[0]

    # 3. 渲染表单（如果有历史进度则填充，否则使用默认值）
    st.subheader(f"📝 {date_str} 数据登记")
    
    with st.form("main_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            weight = st.number_input("今日体重 (kg)", value=float(record['体重']) if record is not None else 84.25, step=0.01)
            smoke = st.number_input("今日抽烟 (根)", value=int(record['抽烟']) if record is not None else 10, step=1)
        with c2:
            s_in = st.text_input("昨日入睡时间", value=record['昨日入睡'] if record is not None else "1:20")
            s_out = st.text_input("今早起床时间", value=record['今早起床'] if record is not None else "8:40")
            s_dur = st.number_input("昨日睡眠维持时长 (h)", value=float(record['睡眠时长']) if record is not None else 8.0, step=0.5)
        with c3:
            s_night = st.selectbox("是否起夜", ["否", "是"], index=0 if record is None or record['是否起夜']=="否" else 1)
            bowel = st.selectbox("排便性状", ["1", "2", "3", "4", "5", "6", "7"], index=3 if record is None else ["1","2","3","4","5","6","7"].index(str(record['排便性状'])))
            meds = st.selectbox("药物/补剂是否按时", ["是", "否"], index=0 if record is None or record['用药按时']=="是" else 1)

        st.divider()
        c4, c5 = st.columns(2)
        with c4:
            water = st.number_input("饮水量 (L)", value=float(record['饮水']) if record is not None else 2.0, step=0.1)
            water_extra = st.text_input("其中饮料", value=record['其中饮料'] if record is not None else "na")
            breakfast_t = st.text_area("早餐及时间", value=record['早餐'] if record is not None else "")
            lunch_t = st.text_area("午餐及时间", value=record['午餐'] if record is not None else "")
        with c5:
            snack_t = st.text_area("加餐及时间", value=record['加餐'] if record is not None else "na")
            dinner_t = st.text_area("晚餐及时间", value=record['晚餐'] if record is not None else "")
            walk_l = st.number_input("午后步行(min)", value=int(record['午后步行']) if record is not None else 0)
            walk_d = st.number_input("晚后步行(min)", value=int(record['晚后步行']) if record is not None else 0)

        st.divider()
        c6, c7 = st.columns(2)
        with c6:
            energy = st.select_slider("精力状态", options=["低", "中", "高"], value=record['精力'] if record is not None else "中")
            mood = st.select_slider("情绪状态", options=["低", "中", "高"], value=record['情绪'] if record is not None else "中")
        with c7:
            discomfort = st.text_area("不适/特殊情况", value=record['不适'] if record is not None else "无")
            review = st.text_area("一天回顾", value=record['回顾'] if record is not None else "")

        submit_text = st.form_submit_button("💾 暂存/更新文字信息")

    st.divider()
    st.subheader("📸 饮食照片管理")
    
    # 进度显示：如果当天已有照片，给予提示
    if record is not None:
        cols_pre = st.columns(4)
        for i, k in enumerate(["早餐图", "午餐图", "加餐图", "晚餐图"]):
            if str(record[k]) != "na" and os.path.exists(str(record[k])):
                cols_pre[i].info(f"已存有{k[:2]}图")

    ci1, ci2 = st.columns(2)
    def image_slot(label, key_prefix):
        st.write(f"**{label}**")
        cam_img = st.camera_input(f"拍{label}", key=f"{key_prefix}_cam_{date_str}") # Key随日期变化实现自动重置
        up_img = st.file_uploader(f"上传{label}", type=['jpg','png','jpeg'], key=f"{key_prefix}_up_{date_str}")
        final_img = cam_img if cam_img else up_img
        if final_img and st.button(f"❌ 清除{label}", key=f"clr_{key_prefix}_{date_str}"):
            st.rerun()
        return final_img

    with ci1:
        img_b = image_slot("早餐", "b")
        img_l = image_slot("午餐", "l")
    with ci2:
        img_s = image_slot("加餐", "s")
        img_d = image_slot("晚餐", "d")

    # 4. 最终上传/同步逻辑
    if st.button("🚀 实时同步到数据库", type="primary", use_container_width=True):
        new_data = {
            "日期": date_str, "昨日入睡": s_in, "今早起床": s_out, "睡眠时长": s_dur,
            "是否起夜": s_night, "排便性状": bowel, "体重": weight, "用药按时": meds,
            "抽烟": smoke, "饮水": water, "其中饮料": water_extra,
            "早餐": breakfast_t, "午餐": lunch_t, "午后步行": walk_l,
            "加餐": snack_t, "晚餐": dinner_t, "晚后步行": walk_d,
            "精力": energy, "情绪": mood, "不适": discomfort, "回顾": review
        }
        
        # 处理图片路径：如果有新传的就保存，没传的就尝试保留数据库里的
        for slot, img, tag in [("早餐图", img_b, "breakfast"), ("午餐图", img_l, "lunch"), 
                              ("加餐图", img_s, "snack"), ("晚餐图", img_d, "dinner")]:
            new_path = process_and_save(img, tag, date_str)
            if new_path:
                new_data[slot] = new_path
            elif record is not None:
                new_data[slot] = record[slot] # 保留旧进度
            else:
                new_data[slot] = "na"

        # 更新或追加到内存和文件
        df = st.session_state.data
        if not df.empty and date_str in df['日期'].values:
            idx = df[df['日期'] == date_str].index[0]
            for k, v in new_data.items():
                df.at[idx, k] = v
        else:
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

        df.to_csv(DATA_FILE, index=False)
        st.session_state.data = df
        st.success(f"✅ {date_str} 的数据已同步更新！")
        st.rerun()

with tab2:
    st.subheader("📜 历史数据全量管理")
    df_view = st.session_state.data
    if not df_view.empty:
        df_view = df_view.sort_values("日期", ascending=False)
        
        selected_dates = st.multiselect("勾选导出日期：", options=df_view['日期'].tolist())
        if selected_dates:
            md_content = convert_to_md(df_view[df_view['日期'].isin(selected_dates)])
            st.download_button("📂 导出 Markdown", data=md_content, file_name=f"export_{datetime.now().strftime('%m%d')}.md")

        for index, row in df_view.iterrows():
            with st.expander(f"📅 {row['日期']} | 体重: {row['体重']}kg"):
                if st.button("🗑️ 删除", key=f"del_{row['日期']}"):
                    delete_record(row['日期'])
                st.write(f"**回顾**: {row['回顾']}")
                # 图片预览
                cols = st.columns(4)
                for i, img_k in enumerate(["早餐图", "午餐图", "加餐图", "晚餐图"]):
                    p = str(row[img_k])
                    if p != "na" and os.path.exists(p):
                        cols[i].image(p, caption=img_k[:2])
    else:
        st.info("暂无历史记录。")
