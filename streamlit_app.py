import streamlit as st
import pandas as pd

st.set_page_config(page_title="Meta 廣告診斷室", layout="wide")
st.title("🚀 Meta 廣告素材智能診斷工具")

uploaded_file = st.file_uploader("請上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    # 讀取數據
    df = pd.read_csv(uploaded_file)
    
    # 這裡加入一個簡單的側邊欄來選擇目標
    goal = st.sidebar.selectbox("您的優化目標", ["網站流量", "影片觀看", "購買轉換"])
    
    st.success("數據讀取成功！開始進行素材診斷...")

    # --- 核心邏輯開始 ---
    # 自動計算關鍵指標 (假設欄位名稱為 Meta 預設英文)
    if 'Impressions' in df.columns and '3-second video plays' in df.columns:
        df['Hook Rate (%)'] = (df['3-second video plays'] / df['Impressions']) * 100
    
    if 'Link clicks' in df.columns and 'Impressions' in df.columns:
        df['CTR (%)'] = (df['Link clicks'] / df['Impressions']) * 100

    # --- 呈現診斷結果 ---
    st.subheader(f"🎯 目標設定：{goal}")
    
    # 用卡片呈現整體平均表現
    col1, col2, col3 = st.columns(3)
    if 'Hook Rate (%)' in df.columns:
        col1.metric("平均吸睛率 (Hook Rate)", f"{df['Hook Rate (%)'].mean():.2f}%")
    if 'CTR (%)' in df.columns:
        col2.metric("平均點擊率 (CTR)", f"{df['CTR (%)'].mean():.2f}%")
    
    # --- 素材列表與診斷建議 ---
    st.divider()
    st.subheader("📝 單一素材診斷報告")
    
    for index, row in df.iterrows():
        with st.expander(f"素材名稱: {row.get('Ad Name', '未命名素材')}"):
            c1, c2 = st.columns([1, 2])
            
            with c1:
                st.write("**數據表現：**")
                if 'Hook Rate (%)' in df.columns:
                    st.write(f"吸睛率: {row['Hook Rate (%)']:.2f}%")
                if 'CTR (%)' in df.columns:
                    st.write(f"點擊率: {row['CTR (%)']:.2f}%")
            
            with c2:
                st.write("**優化建議：**")
                # 自動建議邏輯
                if 'Hook Rate (%)' in df.columns and row['Hook Rate (%)'] < 25:
                    st.error("⚠️ 吸睛力不足：建議更換影片前 3 秒的視覺，或直接把受眾痛點放在第一句話。")
                elif 'CTR (%)' in df.columns and row['CTR (%)'] < 1.0:
                    st.warning("💡 點擊誘因較弱：建議加強文案中的 Call-to-Action 或調整圖片配色。")
                else:
                    st.success("✅ 表現優異：此素材目前效率良好，建議增加預算或作為後續製作範本。")
