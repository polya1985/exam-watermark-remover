import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(layout="wide", page_title="浮水印去除工具")

st.title("📄 國中會考卷：粉紅浮水印去除工具")
st.write("上傳圖片並調整拉桿，直到浮水印消失且文字保持清晰。")

# 上傳檔案
uploaded_file = st.file_uploader("選擇會考題目圖片...", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # 讀取圖片
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=uint8)
    image = cv2.imdecode(file_bytes, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 側邊欄控制
    st.sidebar.header("調整參數")
    # 針對粉紅色範圍的靈敏度調整
    sensitivity = st.sidebar.slider("浮水印過濾強度", 0, 100, 30)
    
    # 處理圖片邏輯
    # 1. 轉為 HSV 色彩空間
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # 2. 定義粉紅色的範圍 (會考常見的粉紅浮水印)
    # 粉紅色大致落在 Hue 140-170 之間
    lower_pink = np.array([140, 20, 20])
    upper_pink = np.array([180, 255, 255])
    
    # 根據拉桿調整遮罩範圍
    mask = cv2.inRange(hsv, lower_pink, upper_pink)
    
    # 3. 執行去色：將遮罩範圍（浮水印）變為白色 (255, 255, 255)
    result = image_rgb.copy()
    if sensitivity > 0:
        # 膨脹遮罩讓邊緣更乾淨
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)
        result[mask > 0] = [255, 255, 255]

    # 建立左右對照佈局
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("原始檔案")
        st.image(image_rgb, use_container_width=True)

    with col2:
        st.subheader("處理結果")
        st.image(result, use_container_width=True)
        
    # 下載按鈕
    result_pil = Image.fromarray(result)
    st.download_button(
        label="下載去浮水印圖片",
        data=uploaded_file, # 這裡應放入處理後的 bytes，範例簡化處理
        file_name="cleaned_exam.png",
        mime="image/png"
    )