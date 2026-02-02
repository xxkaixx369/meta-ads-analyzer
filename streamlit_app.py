import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meta 廣告診斷工具", layout="wide")

st.title("🎯 Meta 廣告素材自動化診斷 (表格匯總版)")

# 1. 檔案上傳
uploaded_file = st.file_uploader("上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    st.success("✅ 數據導入成功！")

    # 2. 自動欄位偵測 (擴大搜尋範圍以確保抓到數據)
    def find_col(keys):
        for col in df.columns:
            if any(k in col.lower() for k in keys): return col
        return None

    c_name = find_col(['廣告名稱', 'ad name'])
    c_spend = find_col(['金額', '花費', 'amount spent', '消耗'])
    c_impr = find_col(['曝光次數', 'impressions', '展現'])
    c_click = find_col(['連結點擊', 'link clicks'])
    c_hook = find_col(['3 秒', '3秒', '3-second', '三秒'])

    # 3. 指標計算與診斷邏輯
    if c_impr:
        # 計算吸睛率與點擊率
        df['吸睛率(Hook %)'] = ((df[c_hook] / df[c_impr] * 100) if c_hook else 0).round(2)
        df['點擊率(CTR %)'] = ((df[c_click] / df[c_impr] * 100) if c_click else 0).round(2)
        
        # 建立自動診斷建議
        def get_advice(row):
            h = row['吸睛率(Hook %)']
            c = row['點擊率(CTR %)']
            if h < 25: return "❌ 吸睛力不足：建議更換前3秒視覺"
            elif c < 1.0: return "⚠️ 點擊力不足：建議強化文案誘因"
            else: return "✅ 表現優異：建議維持或加預算"

        df['AI 診斷建議'] = df.apply(get_advice, axis=1)

        # 4. 數據看板 (Dashboard)
        st.subheader("📊 帳戶成效摘要")
        m1, m2, m3 = st.columns(3)
        m1.metric("總消耗金額", f"${df[c_spend].sum():,.0f}" if c_spend else "N/A")
        m2.metric("平均 CTR", f"{df['點擊率(CTR %)'].mean():.2f}%")
        m3.metric("平均 Hook Rate", f"{df['吸睛率(Hook %)'].mean():.2f}%")

        # 5. 顯示表格 (關鍵優化：直接顯示所有數據)
        st.divider()
        st.subheader("📋 素材全清單診斷表格")
        
        # 整理要顯示的欄位
        display_cols = []
        if c_name: display_cols.append(c_name)
        if c_spend: display_cols.append(c_spend)
        display_cols.extend(['吸睛率(Hook %)', '點擊率(CTR %)', 'AI 診斷建議'])
        
        # 使用 Streamlit 的 dataframe 顯示，並設定寬度自動展開
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)

        # 6. 視覺化散佈圖
        if c_spend:
            st.divider()
            st.subheader("📈 效率分佈圖")
            fig = px.scatter(df, x=c_spend, y='點擊率(CTR %)', text=c_name, size=c_spend, 
                             color='點擊率(CTR %)', color_continuous_scale='Viridis',
                             title="氣泡越大花費越多；位置越靠上方效率越高")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("找不到曝光數據，請檢查 CSV 欄位。")
else:
    st.info("👋 歡迎使用！請上傳 CSV 開始分析。")
