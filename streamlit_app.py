import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meta 廣告診斷工具", layout="wide")

st.title("🎯 Meta 廣告素材自動化診斷")
st.write("本工具會自動計算 Hook Rate 與 CTR，並提供優化建議。")

# 1. 檔案上傳
uploaded_file = st.file_uploader("請上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    st.success("數據導入成功！")

    # --- 2. 核心指標計算 ---
    col_map = {
        'impressions': next((c for c in df.columns if c.lower() in ['impressions', '曝光次數']), None),
        'clicks': next((c for c in df.columns if c.lower() in ['link clicks', '連結點擊次數']), None),
        'hook_plays': next((c for c in df.columns if '3-second video plays' in c.lower() or '3 秒影片觀看次數' in c), None),
        'spend': next((c for c in df.columns if 'amount spent' in c.lower() or '金額' in c or '花費' in c), None),
        'ad_name': next((c for c in df.columns if 'ad name' in c.lower() or '廣告名稱' in c), None)
    }

    if col_map['impressions']:
        if col_map['hook_plays']:
            df['Hook Rate (%)'] = (df[col_map['hook_plays']] / df[col_map['impressions']] * 100).round(2)
        if col_map['clicks']:
            df['CTR (%)'] = (df[col_map['clicks']] / df[col_map['impressions']] * 100).round(2)

    # --- 3. 視覺化分析圖表 ---
    st.subheader("📊 素材成效分佈圖")
    if col_map['spend'] and 'CTR (%)' in df.columns:
        fig = px.scatter(df, x=col_map['spend'], y='CTR (%)', text=col_map['ad_name'],
                         size=col_map['spend'], color='CTR (%)',
                         color_continuous_scale='RdYlGn',
                         title="成效分佈：越往左上方代表『低成本、高點擊』的優質素材",
                         labels={col_map['spend']: "消耗金額", 'CTR (%)': "點擊率 (CTR %)"})
        st.plotly_chart(fig, use_container_width=True)
    
    # --- 4. 自動化診斷報告 ---
    st.divider()
    st.subheader("📋 單一素材深度診斷")
    
    for index, row in df.iterrows():
        name = row.get(col_map['ad_name'], f"素材 {index}")
        with st.expander(f"🔍 檢查素材：{name}"):
            c1, c2, c3 = st.columns(3)
            
            h_rate = row.get('Hook Rate (%)', 0)
            ctr_rate = row.get('CTR (%)', 0)
            
            c1.metric("吸睛率 (Hook Rate)", f"{h_rate}%")
            c2.metric("點擊率 (CTR)", f"{ctr_rate}%")
            
            with c3:
                st.write("**💡 優化方向：**")
                # 這裡就是修正縮排的地方
                if h_rate < 25 and h_rate > 0:
                    st.error("❌ 開頭太無聊：觀眾滑過率高。建議更換前3秒畫面。")
                elif ctr_rate < 1.0 and ctr_rate > 0:
                    st.warning("⚠️ 內容沒誘因：大家看了但不想點。建議強化文案。")
                elif h_rate >= 25 and ctr_rate >= 1.0:
                    st.success("✅ 黃金素材：表現優異！建議增加預算。")
                else:
                    st.info("數據分析中或欄位不足。")

st.sidebar.info("### 診斷標準\n1. Hook Rate > 25%: 合格\n2. CTR > 1.0%: 合格")
