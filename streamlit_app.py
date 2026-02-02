import streamlit as st
import pandas as pd
import google.generativeai as genai

# 從 Secrets 抓取 API Key
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("❌ API Key 設定失敗，請檢查 Streamlit Secrets。")

st.title("🚀 Meta 廣告素材 AI 診斷室")

uploaded_file = st.file_uploader("上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("數據導入成功！")
    
    # 選擇分析目標
    goal = st.selectbox("您的優化目標", ["網站流量", "影片觀看", "購買轉換"])
    
    if st.button("🪄 請 Gemini AI 進行深度診斷"):
        with st.spinner('Gemini 正在分析素材並思考對策...'):
            # 簡化數據，只取前幾行和重點欄位給 AI，避免超出限制
            data_context = df.head(10).to_string()
            
            prompt = f"""
            你是一位專業的 Meta 廣告數據分析師。
            目標：{goal}
            數據內容：
            {data_context}
            
            請針對以上素材的數據（如曝光、點擊、觀看、花費）進行分析：
            1. 找出表現最好與最差的素材。
            2. 給予具體的「視覺優化」與「文案調整」建議。
            3. 以繁體中文回覆，條列式呈現，語氣要專業且易懂。
            """
            
            response = model.generate_content(prompt)
            st.markdown("---")
            st.subheader("🤖 Gemini 專家分析報告")
            st.write(response.text)
