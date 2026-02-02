import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. 增強版 API 配置
try:
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("❌ 找不到 Secrets！請確認 Streamlit Cloud 已填入 GEMINI_API_KEY。")
        st.stop()
        
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # 這裡建議使用最新的 flash 模型名稱
    model = genai.GenerativeModel('gemini-1.5-flash') 
except Exception as e:
    st.error(f"❌ 初始化失敗：{str(e)}")
    st.stop()

st.title("🚀 Meta 廣告素材 AI 診斷室")

uploaded_file = st.file_uploader("上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    # 增加編碼相容性，Meta CSV 有時是 utf-8 或 big5
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')
        
    st.success("數據導入成功！")
    st.dataframe(df.head(5)) # 多秀幾行數據確認欄位
    
    goal = st.selectbox("您的優化目標", ["網站流量", "影片觀看", "購買轉換"])
    
    if st.button("🪄 請 Gemini AI 進行深度診斷"):
        with st.spinner('Gemini 正在分析素材中...'):
            try:
                # 建議加上清理空值的步驟，避免給 AI 亂碼
                data_context = df.head(10).fillna(0).to_string()
                
                prompt = f"""
                你是一位專業的 Meta 廣告分析師。
                目標：{goal}
                數據內容：
                {data_context}
                
                請分析：
                1. 找出表現最好與最差素材。
                2. 具體的視覺與文案建議。
                3. 以繁體中文專業回覆。
                """
                
                response = model.generate_content(prompt)
                st.markdown("---")
                st.subheader("🤖 Gemini 專家分析報告")
                st.write(response.text)
            except Exception as e:
                st.error(f"分析過程發生錯誤：{str(e)}")
