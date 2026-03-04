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

# --- 数据加载与自动去重逻辑 ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            df['日期'] = df['日期'].astype(str)
            # 核心修复：按日期去重，保留最后一次修改的内容，解决 Duplicate Key 报错
            df = df.drop_duplicates(subset=['日期'], keep='last').reset_index(drop=True)
            return df
        except Exception as e:
            st.error(f"加载数据出错: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# 初始化 Session State 数据
if 'data' not in st.session_state:
    st.session_state.data = load_data()

# --- 逻辑控制函数 ---
def delete_record(date_to_del):
    st.session_state.data = st.session_state.data[st.session_state.data['日期'] != date_to_del]
    st.session_state.data.to_csv(DATA_FILE, index=False)
    st.toast(f"已删除 {date_to_del} 的记录", icon="🗑️")
    st.rerun()

def edit_record(row_data):
    st.session_state.edit_mode = True
    st.session_state.edit_date = row_data['日期']
    st.session_state.temp_edit_data = row_data.to_dict()
    st.toast(f"已加载 {row_data['日期']} 的历史数据", icon="📝")

# --- UI 界面渲染 ---
st.title("🍎 每日信息汇总管理")

# 每月1号清理提示
if datetime.now().day == 1:
    st.warning("📅 今天是本月1号！建议清理上个月的照片以节省服务器空间。")
    if st.button("一键清理历史照片"):
        for f in os.listdir(IMAGE_DIR):
            os.remove(os.path.join(IMAGE_DIR, f))
        st.success("清理完毕！")

tab1, tab2 = st.tabs(["✍️ 详细登记", "📊 历史管理"])

with tab1:
    # 状态判断：是否处于编辑模式
    is_editing = st.session_state.get('edit_mode', False)
    default_vals = st.session_state.get('temp_edit_data', {}) if is_editing else {}

    with st.form("comprehensive_form", clear_on_submit=not is_editing):
        st.subheader("1. 基础睡眠与生理指标" + (" (编辑模式)" if is_editing else ""))
        c1, c2, c3 = st.columns(3)
        with c1:
            record_date = st.date_input("记录日期", 
                                       value=datetime.strptime(default_vals['日期'], "%Y-%m-%d") if is_editing else datetime.now(),
                                       disabled=is_editing)
            weight = st.number_input("今日体重 (kg)", value=float(default_vals.get('体重', 84.25)), step=0.01)
            smoke = st.number_input("今日抽烟 (根)", value=int(default_vals.get('抽烟', 10)), step=1)
        with c2:
            s_in = st.text_input("昨日入睡时间", value=default_vals.get('昨日入睡', "1:20"))
            s_out = st.text_input("今早起床时间", value=default_vals.get('今早起床', "8:40"))
            s_dur = st.number_input("昨日睡眠维持时长 (h)", value=float(default_vals.get('睡眠时长', 8.0)), step=0.5)
        with c3:
            s_night = st.selectbox("是否起夜", ["否", "是"], index=0 if default_vals.get('是否起夜') == "否" else 1)
            bowel_opts = ["1", "2", "3", "4", "5", "6", "7"]
            b_val = str(default_vals.get('排便性状', "4"))
            bowel = st.selectbox("排便性状", bowel_opts, index=bowel_opts.index(b_val) if b_val in bowel_opts else 3)
            meds = st.selectbox("药物/补剂是否按时", ["是", "否"], index=0 if default_vals.get('用药按时') == "是" else 1)

        st.divider()
        st.subheader("2. 饮食与运动")
        c4, c5 = st.columns(2)
        with c4:
            water = st.number_input("饮水量 (L)", value=float(default_vals.get('饮水', 2.0)), step=0.1)
            water_extra = st.text_input("其中饮料", value=default_vals.get('其中饮料', "na"))
            breakfast_t = st.text_area("早餐及时间", value=default_vals.get('早餐', ""))
            lunch_t = st.text_area("午餐及时间", value=default_vals.get('午餐', ""))
        with c5:
            snack_t = st.text_area("加餐及时间", value=default_vals.get('加餐', "na"))
            dinner_t = st.text_area("晚餐及时间", value=default_vals.get('晚餐', ""))
            walk_l = st.number_input("午后步行(min)", value=int(default_vals.get('午后步行', 0)))
            walk_d = st.number_input("晚后步行(min)", value=int(default_vals.get('晚后步行', 0)))

        st.divider()
        st.subheader("3. 状态回顾")
        c6, c7 = st.columns(2)
        with c6:
            energy = st.select_slider("精力状态", options=["低", "中", "高"], value=default_vals.get('精力', "中"))
            mood = st.select_slider("情绪状态", options=["低", "中", "高"], value=default_vals.get('情绪', "中"))
        with c7:
            discomfort = st.text_area("不适/特殊情况", value=default_vals.get('不适', "无"))
            review = st.text_area("一天回顾", value=default_vals.get('回顾', ""))

        st.info("📸 饮食照片：系统优先采用新拍的照片，其次为上传的文件。若均留空则保留历史。")
        ci1, ci2 = st.columns(2)
        
        with ci1:
            st.write("**早餐**")
            cam_b = st.camera_input("拍照", key="cam_b")
            up_b = st.file_uploader("或相册上传", type=['jpg','png','jpeg'], key="up_b")
            img_b = cam_b if cam_b else up_b

            st.write("**午餐**")
            cam_l = st.camera_input("拍照", key="cam_l")
            up_l = st.file_uploader("或相册上传", type=['jpg','png','jpeg'], key="up_l")
            img_l = cam_l if cam_l else up_l

        with ci2:
            st.write("**加餐**")
            cam_s = st.camera_input("拍照", key="cam_s")
            up_s = st.file_uploader("或相册上传", type=['jpg','png','jpeg'], key="up_s")
            img_s = cam_s if cam_s else up_s

            st.write("**晚餐**")
            cam_d = st.camera_input("拍照", key="cam_d")
            up_d = st.file_uploader("或相册上传", type=['jpg','png','jpeg'], key="up_d")
            img_d = cam_d if cam_d else up_d

        submit = st.form_submit_button("✅ 确认提交并最终同步" if not is_editing else "💾 保存修改并退出编辑")

        if submit:
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
            st.session_state.edit_mode = False
            st.success("数据已成功保存同步！")
            st.rerun()

with tab2:
    st.subheader("📜 历史数据管理")
    df_view = st.session_state.data
    if not df_view.empty:
        df_view = df_view.sort_values("日期", ascending=False)
        for index, row in df_view.iterrows():
            with st.expander(f"📅 {row['日期']} | 体重: {row['体重']}kg | 回顾: {str(row['回顾'])[:15]}..."):
                b_edit, b_del, _ = st.columns([1, 1, 8])
                if b_edit.button("📝 修改", key=f"btn_edit_{row['日期']}_{index}"):
                    edit_record(row)
                    st.rerun()
                if b_del.button("🗑️ 删除", key=f"btn_del_{row['日期']}_{index}", type="primary"):
                    delete_record(row['日期'])
                
                st.write(f"**睡眠**: {row['昨日入睡']} ~ {row['今早起床']} (持续{row['睡眠时长']}h)")
                st.write(f"**指标**: 抽烟{row['抽烟']}根 | 饮水{row['饮水']}L | 状态:{row['精力']}/{row['情绪']}")
                
                img_cols = st.columns(4)
                for i, img_k in enumerate(["早餐图", "午餐图", "加餐图", "晚餐图"]):
                    path = str(row[img_k])
                    if path != "na" and os.path.exists(path):
                        img_cols[i].image(path, caption=img_k)
                    else:
                        img_cols[i].caption(f"无{img_k}")
    else:
        st.info("暂无记录。")

    if not df_view.empty:
        csv = df_view.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 导出完整 CSV 数据", data=csv, file_name=f"health_backup_{datetime.now().strftime('%Y%m%d')}.csv")
