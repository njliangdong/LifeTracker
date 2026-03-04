import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image
import io

# 页面配置
st.set_page_config(page_title="生活看板Pro", layout="wide")

# 文件夹准备
IMAGE_DIR = "food_images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

DATA_FILE = "health_records.csv"

# --- 逻辑：每月1号清理提醒 ---
today = datetime.now()
if today.day == 1:
    st.warning("📅 今天是本月1号！需要清理上个月的饮食照片以节省空间吗？")
    if st.button("清理过期照片"):
        for f in os.listdir(IMAGE_DIR):
            os.remove(os.path.join(IMAGE_DIR, f))
        st.success("已清空本地照片缓存！")

# --- 函数：图像压缩 ---
def save_compressed_image(image_file, date_str):
    img = Image.open(image_file)
    # 转换为 RGB (防止 PNG 透明位图报错)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    # 路径：food_images/2026-03-04.jpg
    save_path = os.path.join(IMAGE_DIR, f"{date_str}.jpg")
    
    # 压缩：质量设为 30 (大幅节省空间，但能看清食物)
    img.save(save_path, "JPEG", quality=30, optimize=True)
    return save_path

# 加载数据逻辑 (省略部分重复字段以保持简洁，实际使用时请保留之前的全部字段)
def load_data():
    try: return pd.read_csv(DATA_FILE)
    except: return pd.DataFrame(columns=["日期", "体重", "饮食照片路径", "备注"])

data = load_data()

st.title("🍎 生活信息管理 (含饮食拍照)")

tab1, tab2 = st.tabs(["✍️ 登记", "📊 历史记录"])

with tab1:
    with st.form("pro_form"):
        date = st.date_input("记录日期", datetime.now())
        weight = st.number_input("今日体重 (kg)", value=84.25)
        
        st.write("📸 记录今日饮食")
        # 调用摄像头
        img_file = st.camera_input("拍照记录最丰盛的一餐")
        
        review = st.text_area("一天回顾")
        
        if st.form_submit_button("保存"):
            img_path = "无照片"
            if img_file:
                # 压缩并存到本地 food_images 文件夹
                img_path = save_compressed_image(img_file, str(date))
            
            new_row = {
                "日期": str(date), 
                "体重": weight, 
                "饮食照片路径": img_path,
                "备注": review
            }
            # ... 此处连接之前的 pd.concat 保存逻辑 ...
            st.success(f"已保存！照片已压缩存至：{img_path}")

with tab2:
    st.subheader("历史记录与照片回顾")
    for index, row in data.iterrows():
        with st.expander(f"📅 {row['日期']} - 体重: {row['体重']}kg"):
            if row['饮食照片路径'] != "无照片" and os.path.exists(str(row['飲食照片路径'])):
                st.image(row['饮食照片路径'], width=300)
            st.write(f"备注: {row['备注']}")
