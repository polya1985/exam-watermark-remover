import streamlit as st
import cv2
import numpy as np
from PIL import Image
import fitz  # 這是 PyMuPDF 的套件名稱，用來讀取 PDF

st.set_page_config(layout="wide", page_title="會考 PDF 浮水印去除工具")

st.title("📄 國中會考卷：PDF/圖片浮水印去除工具")
st.write("支援上傳 PDF 或圖片（JPG/PNG）。會自動將 PDF 每一頁轉出來去背。")

# 1. 更新上傳器，加入 pdf 支援
uploaded_file = st.file_uploader("請選擇會考題目檔案...", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    images = []
    
    # 2. 判斷檔案類型並讀取
    if uploaded_file.type == "application/pdf":
        with st.spinner('正在解析 PDF 頁面...'):
            # 使用 fitz (PyMuPDF) 讀取 PDF
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                # dpi=150 可以讓題目文字保持清晰
                pix = page.get_pixmap(dpi=150) 
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images.append(np.array(img))
    else:
        # 處理一般圖片 (已修復 np.uint8 錯誤)
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)
        images.append(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    # 3. 側邊欄控制拉桿
    st.sidebar.header("調整參數")
    sensitivity = st.sidebar.slider("浮水印過濾強度", 0, 100, 30)
    
    # 4. 逐頁處理浮水印
    for idx, image_rgb in enumerate(images):
        st.markdown(f"### 第 {idx+1} 頁")
        
        # 轉換色彩空間來抓取粉紅色
        img_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        
        # 定義粉紅色的範圍
        lower_pink = np.array([140, 20, 20])
        upper_pink = np.array([180, 255, 255])
        
        mask = cv2.inRange(hsv, lower_pink, upper_pink)
        
        if sensitivity > 0:
            # 依據拉桿強度進行遮罩膨脹，確保浮水印邊緣乾淨
            kernel = np.ones((3,3), np.uint8)
            mask = cv2.dilate(mask, kernel, iterations=1)
            
        # 將浮水印位置填成白色
        result = image_rgb.copy()
        result[mask > 0] = [255, 255, 255] 

        # 5. 顯示左右對照圖
        col1, col2 = st.columns(2)
        with col1:
            st.image(image_rgb, caption="原始檔案", use_container_width=True)
        with col2:
            st.image(result, caption="處理結果", use_container_width=True)
