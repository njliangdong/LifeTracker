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

# --- 图像压缩与保存函数 ---
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

# --- 数据加载与自动去重 ---
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

# --- Markdown 导出逻辑 ---
def convert_to_md(selected_df):
    md_text = f"# 生活看板历史记录导出\n*导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n---\n"
    for _, row in selected_df.iterrows():
        md_text += f"## 📅 日期：{row['日期']}\n"
        md_text += f"### 🩺 基础指标\n"
        md_text += f"- **体重**: {row['体重']}kg | **抽烟**: {row['抽烟']}根 | **用药**: {row['用药按时']}\n"
        md_text += f"- **睡眠**: {row['昨日入睡']} ~ {row['今早起床']} (时长: {row['睡眠时长']}h)\n"
        md_text += f"- **生理**: 起夜: {row['是否起夜']} | 排便性状: {row['排便性状']}\n\n"
        
        md_text += f"### 🍲 饮食与运动\n"
        md_text += f"- **饮水**: {row['饮水']}L ({row['其中饮料']})\n"
        md_text += f"- **早餐**: {row['早餐']}\n"
        md_text += f"- **午餐**: {row['午餐']}\n"
        md_text += f"- **加餐**: {row['加餐']}\n"
        md_text += f"- **晚餐**: {row['晚餐']}\n"
        md_text += f"- **步数**: 午后 {row['午后步行']}min | 晚后 {row['晚后步行']}min\n\n"
        
        md_text += f"### 🧠 状态与回顾\n"
        md_text += f"- **精力**: {row['精力']} | **情绪**: {row['情绪']}\n"
        md_text += f"- **不适**: {row['不适']}\n"
        md_text += f"- **回顾**: {row['回顾']}\n\n"
        
        md_text += f"--- \n"
    return md_text

# 初始化数据
if 'data' not in st.session_state:
    st.session_state.data = load_data()

# --- 逻辑控制 ---
def delete_record(date_to_del):
    st.session_state.data = st.session_state.data[st.session_state.data['日期'] != date_to_del]
    st.session_state.data.to_csv(DATA_FILE, index=False)
    st.toast(f"已删除 {date_to_del} 的记录", icon="🗑️")
    st.rerun()

# --- UI 渲染 ---
st.title("🍎 每日信息汇总管理")

tab1, tab2 = st.tabs(["✍️ 详细登记", "📊 历史管理"])

with tab1:
    # 使用 Form 无法直接清除内部组件状态，因此图片组件放在 Form 外部
    # 或者利用 Session State 并在提交后清空。
    st.subheader("1. 基础睡眠与生理指标")
    with st.form("basic_info_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            record_date = st.date_input("记录日期", value=datetime.now())
            weight = st.number_input("今日体重 (kg)", value=84.25, step=0.01)
            smoke = st.number_input("今日抽烟 (根)", value=10, step=1)
        with c2:
            s_in = st.text_input("昨日入睡时间", value="1:20")
            s_out = st.text_input("今早起床时间", value="8:40")
            s_dur = st.number_input("昨日睡眠维持时长 (h)", value=8.0, step=0.5)
        with c3:
            s_night = st.selectbox("是否起夜", ["否", "是"])
            bowel = st.selectbox("排便性状", ["1", "2", "3", "4", "5", "6", "7"], index=3)
            meds = st.selectbox("药物/补剂是否按时", ["是", "否"])

        st.divider()
        st.subheader("2. 饮食与运动")
        c4, c5 = st.columns(2)
        with c4:
            water = st.number_input("饮水量 (L)", value=2.0, step=0.1)
            water_extra = st.text_input("其中饮料", value="na")
            breakfast_t = st.text_area("早餐及时间")
            lunch_t = st.text_area("午餐及时间")
        with c5:
            snack_t = st.text_area("加餐及时间", value="na")
            dinner_t = st.text_area("晚餐及时间")
            walk_l = st.number_input("午后步行(min)", value=0)
            walk_d = st.number_input("晚后步行(min)", value=0)

        st.divider()
        st.subheader("3. 状态回顾")
        c6, c7 = st.columns(2)
        with c6:
            energy = st.select_slider("精力状态", options=["低", "中", "高"], value="中")
            mood = st.select_slider("情绪状态", options=["低", "中", "高"], value="中")
        with c7:
            discomfort = st.text_area("不适/特殊情况", value="无")
            review = st.text_area("一天回顾")
        
        # 提交按钮放在这里
        submit_form = st.form_submit_button("✅ 填写完毕，去上传照片")

    st.divider()
    st.subheader("4. 📸 饮食拍照与上传")
    st.info("提示：拍照或上传后，若不满意可点击下方的“❌ 清除重选”。最终确认提交后才会保存。")
    
    ci1, ci2 = st.columns(2)
    
    # 定义图片处理组件函数
    def image_slot(label, key_prefix):
        st.write(f"**{label}**")
        cam_key = f"{key_prefix}_cam"
        up_key = f"{key_prefix}_up"
        
        cam_img = st.camera_input(f"拍{label}", key=cam_key)
        up_img = st.file_uploader(f"从相册选{label}", type=['jpg','png','jpeg'], key=up_key)
        
        final_img = cam_img if cam_img else up_img
        
        if final_img:
            if st.button(f"❌ 清除当前{label}照片", key=f"clear_{key_prefix}"):
                # 通过改变 key 强制让组件重置（Streamlit 技巧：Key 变了，组件状态就清空）
                # 这里我们简单 rerun 即可，因为 file_uploader 是非持久的
                st.toast(f"已清除{label}，请重新操作")
                st.rerun()
        return final_img

    with ci1:
        img_b = image_slot("早餐", "b")
        img_l = image_slot("午餐", "l")
    with ci2:
        img_s = image_slot("加餐", "s")
        img_d = image_slot("晚餐", "d")

    st.divider()
    # 最终提交按钮
    if st.button("🚀 确认全部数据并最终提交保存", type="primary", use_container_width=True):
        if not submit_form:
            st.warning("请确保先点击上方表单内的『填写完毕』确认文字信息")
        
        dt_str = str(record_date)
        new_data = {
            "日期": dt_str, "昨日入睡": s_in, "今早起床": s_out, "睡眠时长": s_dur,
            "是否起夜": s_night, "排便性状": bowel, "体重": weight, "用药按时": meds,
            "抽烟": smoke, "饮水": water, "其中饮料": water_extra,
            "早餐": breakfast_t, "午餐": lunch_t, "午后步行": walk_l,
            "加餐": snack_t, "晚餐": dinner_t, "晚后步行": walk_d,
            "精力": energy, "情绪": mood, "不适": discomfort, "回顾": review,
            "早餐图": process_and_save(img_b, "breakfast", dt_str),
            "午餐图": process_and_save(img_l, "lunch", dt_str),
            "加餐图": process_and_save(img_s, "snack", dt_str),
            "晚餐图": process_and_save(img_d, "dinner", dt_str)
        }
        
        df = st.session_state.data
        if not df.empty and dt_str in df['日期'].values:
            idx = df[df['日期'] == dt_str].index[0]
            for k, v in new_data.items():
                if "图" in k:
                    if v is not None: df.at[idx, k] = v
                else:
                    df.at[idx, k] = v
        else:
            for k in ["早餐图", "午餐图", "加餐图", "晚餐图"]:
                if new_data[k] is None: new_data[k] = "na"
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

        df.to_csv(DATA_FILE, index=False)
        st.session_state.data = df
        st.success("🎉 数据已成功保存同步！")
        st.rerun()

with tab2:
    st.subheader("📜 历史数据全量管理")
    df_view = st.session_state.data
    
    if not df_view.empty:
        df_view = df_view.sort_values("日期", ascending=False)
        
        st.write("### 📥 批量导出")
        selected_dates = st.multiselect("请勾选需要导出的日期：", options=df_view['日期'].tolist())
        if selected_dates:
            export_df = df_view[df_view['日期'].isin(selected_dates)]
            md_content = convert_to_md(export_df)
            st.download_button(
                label=f"📂 导出选中的 {len(selected_dates)} 条图文记录 (.md)",
                data=md_content,
                file_name=f"health_export_{datetime.now().strftime('%m%d')}.md",
                mime="text/markdown"
            )
        st.divider()

        for index, row in df_view.iterrows():
            with st.expander(f"📅 {row['日期']} | 体重: {row['体重']}kg"):
                if st.button("🗑️ 删除此条全部记录", key=f"del_{row['日期']}_{index}", type="primary"):
                    delete_record(row['日期'])
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**😴 睡眠**: {row['昨日入睡']} - {row['今早起床']} ({row['睡眠时长']}h)")
                    st.markdown(f"**🚽 生理**: 起夜:{row['是否起夜']} | 便性:{row['排便性状']} | 用药:{row['用药按时']}")
                    st.markdown(f"**🚬 生活**: 抽烟:{row['抽烟']}根 | 饮水:{row['饮水']}L ({row['其中饮料']})")
                with col_b:
                    st.markdown(f"**⚡ 状态**: 精力:{row['精力']} | 情绪:{row['情绪']}")
                    st.markdown(f"**🚶 步行**: 午后:{row['午后步行']}min | 晚后:{row['晚后步行']}min")
                    st.markdown(f"**⚠️ 不适**: {row['不适']}")
                
                st.markdown(f"**📝 今日回顾**: {row['回顾']}")
                
                st.divider()
                st.write("**🍱 饮食图文详情**")
                img_c1, img_c2, img_c3, img_c4 = st.columns(4)
                meal_data = [("早餐", "早餐图", img_c1), ("午餐", "午餐图", img_c2), 
                             ("加餐", "加餐图", img_c3), ("晚餐", "晚餐图", img_c4)]
                
                for label, img_key, col in meal_data:
                    with col:
                        st.caption(f"{label}: {row[label] if pd.notna(row[label]) else '未记录'}")
                        path = str(row[img_key])
                        if path != "na" and os.path.exists(path):
                            st.image(path, use_container_width=True)
    else:
        st.info("暂无历史记录。")
