import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meta 廣告 AI 數據診斷室", layout="wide")

# 自定義 CSS 樣式
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Meta 廣告素材自動化診斷看板")
st.write("上傳 Meta 報表，立即獲取視覺化分析與優化建議。")

# 1. 檔案上傳
uploaded_file = st.file_uploader("請上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    # 自動處理不同編碼
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    st.success("✅ 數據導入成功！")

    # --- 2. 智慧欄位偵測邏輯 ---
    col_map = {
        'impressions': next((c for c in df.columns if any(x in c.lower() for x in ['impressions', '曝光', '展現'])), None),
        'clicks': next((c for c in df.columns if any(x in c.lower() for x in ['link clicks', '連結點擊', '連结點擊'])), None),
        'hook_plays': next((c for c in df.columns if any(x in c.lower() for x in ['3-second video plays', '3 秒', '3秒', '三秒'])), None),
        'spend': next((c for c in df.columns if any(x in c.lower() for x in ['amount spent', '金額', '花費', '消耗'])), None),
        'ad_name': next((c for c in df.columns if any(x in c.lower() for x in ['ad name', '廣告名稱'])), None),
        'roas': next((c for c in df.columns if any(x in c.lower() for x in ['roas', '廣告投資報酬率'])), None)
    }

    # 計算核心指標
    if col_map['impressions']:
        if col_map['hook_plays']:
            df['Hook Rate (%)'] = (df[col_map['hook_plays']] / df[col_map['impressions']] * 100).round(2)
        if col_map['clicks']:
            df['CTR (%)'] = (df[col_map['clicks']] / df[col_map['impressions']] * 100).round(2)
        
        # --- 3. 頂部看板 (Dashboard) ---
        st.subheader("📊 帳戶整體表現摘要")
        m1, m2, m3, m4 = st.columns(4)
        
        total_spend = df[col_map['spend']].sum() if col_map['spend'] else 0
        avg_ctr = df['CTR (%)'].mean() if 'CTR (%)' in df.columns else 0
        avg_hook = df['Hook Rate (%)'].mean() if 'Hook Rate (%)' in df.columns else 0
        top_ad = df.loc[df['CTR (%)'].idxmax(), col_map['ad_name']] if 'CTR (%)' in df.columns else "N/A"

        m1.metric("總消耗金額", f"${total_spend:,.0f}")
        m2.metric("平均點擊率 (CTR)", f"{avg_ctr:.2f}%")
        m3.metric("平均吸睛率 (Hook)", f"{avg_hook:.2f}%")
        m4.metric("最佳素材", f"{top_ad[:15]}...")

        # --- 4. 視覺化散佈圖 ---
        st.divider()
        st.subheader("📈 素材成效分佈分析")
        
        if col_map['spend'] and 'CTR (%)' in df.columns:
            fig = px.scatter(df, x=col_map['spend'], y='CTR (%)', 
                             text=col_map['ad_name'],
                             size=col_map['spend'], 
                             color='CTR (%)',
                             color_continuous_scale='Portland',
                             title="氣泡大小代表花費金額，越往上方代表效率越高",
                             labels={col_map['spend']: "消耗金額", 'CTR (%)': "點擊率 (CTR %)"})
            fig.update_traces(textposition='top center')
            st.plotly_chart(fig, use_container_width=True)

        # --- 5. 詳細診斷報告 ---
        st.divider()
        st.subheader("📋 素材逐一診斷建議")
        
        for index, row in df.iterrows():
            name = row.get(col_map['ad_name'], f"素材 {index}")
            with st.expander(f"🔍 診斷：{name}"):
                c1, c2, c3 = st.columns([1, 1, 2])
                
                h_val = row.get('Hook Rate (%)', 0)
                c_val = row.get('CTR (%)', 0)
                r_val = row.get(col_map['roas'], 0) if col_map['roas'] else "N/A"
                
                c1.metric("Hook Rate", f"{h_val}%")
                c2.metric("CTR", f"{c_val}%")
                
                with c3:
                    st.write("**💡 優化動作：**")
                    if h_val < 25 and h_val > 0:
                        st.error("❌ **前 3 秒流失嚴重**：建議更換更吸睛的開頭，例如直接展示產品效果或提出
