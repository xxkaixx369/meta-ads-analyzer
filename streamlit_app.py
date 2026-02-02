import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. 強化版配置：直接強制指定模型與版本
try:
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("❌ 找不到 API Key，請檢查 Secrets 設定。")
        st.stop()
        
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # 【關鍵修正】改用明確的 flash-001 或 flash 完整路徑
    # 這是目前最能解決 v1beta 404 報錯的寫法
    model = genai.GenerativeModel(model_name='gemini-1.5-flash-latest')
    
except Exception as e:
    st.error(f"❌ 初始化失敗：{str(e)}")
    st.stop()

st.title("🚀 Meta 廣告素材 AI 診斷室")

# ... (中間上傳 CSV 的代碼保持不變) ...

# 2. 修正按鈕觸發後的呼叫方式
if st.button("🪄 請 Gemini AI 進行深度診斷"):
    with st.spinner('Gemini 正在分析素材中...'):
        try:
            # 確保數據轉成字串，並限制長度避免爆量
            data_context = df.head(15).fillna(0).to_string()
            
            prompt = f"你是一位廣告專家。請分析以下數據並給予優化建議：\n{data_context}"
            
            # 這裡增加一個安全機制
            response = model.generate_content(prompt)
            
            if response.text:
                st.markdown("---")
                st.subheader("🤖 Gemini 專家分析報告")
                st.write(response.text)
            else:
                st.warning("AI 回傳內容為空，請稍後再試。")
                
        except Exception as e:
            # 如果還是 404，這裡會印出更詳細的錯誤資訊
            st.error(f"分析過程發生錯誤：{str(e)}")
            st.info("💡 提示：若持續出現 404，請確認 Google AI Studio 中的 API Key 是否已通過驗證。")
