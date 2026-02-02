import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meta 廣告診斷看板", layout="wide")

st.title("🎯 Meta 廣告素材自動化診斷看板")

# 1. 檔案上傳
uploaded_file = st.file_uploader("上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    st.success("✅ 數據導入成功！")

    # 2. 自動欄位偵測
    def find_col(keys):
        for col in df.columns:
            if any(k in col.lower() for k in keys): return col
        return None

    c_name = find_col(['廣告名稱', 'ad name'])
    c_spend = find_col(['金額', '花費', 'amount spent', '消耗'])
    c_impr = find_col(['曝光次數', 'impressions', '展現'])
    c_click = find_col(['連結點擊', 'link clicks'])
    c_hook = find_col(['3 秒', '3秒', '3-second'])

    # 3. 計算指標
    if c_impr:
        if c_click: df['CTR (%)'] = (df[c_click] / df[c_impr] * 100).round(2)
        if c_hook: df['Hook Rate (%)'] = (df[c_hook] / df[c_impr] * 100).round(2)

        # 4. 頂部摘要
        st.subheader("📊 數據摘要")
        m1, m2, m3 = st.columns(3)
        m1.metric("總消耗", f"${df[c_spend].sum():,.0f}" if c_spend else "N/A")
        m2.metric("平均 CTR", f"{df['CTR (%)'].mean():.2f}%" if 'CTR (%)' in df.columns else "N/A")
        m3.metric("平均 Hook", f"{df['Hook Rate (%)'].mean():.2f}%" if 'Hook Rate (%)' in df.columns else "N/A")

        # 5. 視覺化圖表
        if c_spend and 'CTR (%)' in df.columns:
            st.divider()
            fig = px.scatter(df, x=c_spend, y='CTR (%)', text=c_name, size=c_spend, 
                             color='CTR (%)', color_continuous_scale='Viridis',
                             title="成效分佈圖 (越往上方越有效率)")
            st.plotly_chart(fig, use_container_width=True)

        # 6. 詳細診斷
        st.divider()
        st.subheader("📋 素材診斷建議")
        for i, row in df.iterrows():
            name = row.get(c_name, f"素材 {i}")
            with st.expander(f"查看：{name}"):
                h = row.get('Hook Rate (%)', 0)
                c = row.get('CTR (%)', 0)
                st.write(f"**吸睛率:** {h}% | **點擊率:** {c}%")
                if h < 25: st.error("❌ 吸睛力不足：建議更換前3秒視覺。")
                elif c < 1.0: st.warning("⚠️ 點擊力不足：建議強化文案誘因。")
                else: st.success("✅ 表現優異：建議維持或加預算。")
    else:
        st.error("找不到曝光數據，請檢查 CSV 欄位。")
else:
    st.info("👋 歡迎使用！請上傳 CSV 開始分析。")
