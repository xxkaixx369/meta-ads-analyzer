import streamlit as st
import pandas as pd

st.title("🚀 Meta 廣告素材智能診斷工具")

# 上傳功能
uploaded_file = st.file_uploader("上傳 Meta 報表 (CSV)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("數據導入成功！")
    
    # 簡易數據展示
    st.subheader("數據概覽")
    st.write(df.head())

    # 這裡可以加入我們之前討論的 Hook Rate 等計算邏輯...
    st.info("提示：確保您的 CSV 欄位名稱包含 'Amount spent', 'Impressions' 等官方名稱。")
