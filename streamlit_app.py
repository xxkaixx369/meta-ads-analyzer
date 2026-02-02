import streamlit as st
import pandas as pd
import plotly.express as px

# 頁面基本設定
st.set_page_config(page_title="Meta 廣告診斷看板", layout="wide")

# 強制調整樣式讓看板更漂亮
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e6e9ef; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 Meta 廣告素材自動化診斷看板")
st.write("上傳 Meta 報表 CSV，自動產出數據看板與優化建議。")

# 1. 檔案上傳
uploaded_file = st.file_uploader("請上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    # 嘗試處理不同編碼 (解決中文亂碼問題)
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    st.success("✅ 數據導入成功！")

    # --- 2. 智慧欄位比對 (萬用搜尋法) ---
    def find_col(keywords):
        for col in df.columns:
            if any(k in col.lower() for k in keywords):
                return col
        return None

    c_name = find_col(['廣告名稱', 'ad name'])
    c_spend = find_col(['金額', '花費', 'amount spent', '消耗'])
    c_impr = find_col(['曝光次數', 'impressions', '展現'])
    c_click = find_col(['連結點擊', 'link clicks', '連结點擊'])
    c_hook = find_col(['3 秒', '3秒', '3-second video plays', '三秒'])
    c_roas = find_col(['roas', '廣告投資報酬率'])

    # --- 3. 指標計算 ---
    if c_impr:
        # 計算點擊率 (CTR)
        if c_click:
            df['CTR (%)'] = (df[c_click] / df[c_impr] * 100).round(2)
        # 計算吸睛率 (Hook Rate)
        if c_hook:
            df['Hook Rate (%)'] = (df[c_hook] / df[c_impr] * 100).round(2)

        # --- 4. 頂部總結看板 ---
        st.subheader("📊 帳戶表現摘要")
        m1, m2, m3, m4 = st.columns(4)
        
        total_spent = df[c_spend].sum() if c_spend else 0
        avg_ctr = df['CTR (%)'].mean() if 'CTR (%)' in df.columns else 0
        avg_hook = df['Hook Rate (%)'].mean() if 'Hook Rate (%)' in df.columns else 0
        # 找出 CTR 最高的素材名稱
        best_ad = "N/A"
        if 'CTR (%)' in df.columns and c_name:
            best_ad = df.loc[df['CTR (%)'].idxmax(), c_name]

        m1.metric("總花費金額", f"${total_spent:,.0f}")
        m2.metric("平均 CTR", f"{avg_ctr:.2f}%")
        m3.metric("平均 Hook Rate", f"{avg_hook:.2f}%")
        m4.metric("最佳素材", f"{str(best_ad)[:15]}...")

        # --- 5. 視覺化散佈圖 ---
        st.divider()
        st.subheader("📈 素材效率分佈圖")
        if c_spend and 'CTR (%)' in df.columns:
            fig = px.scatter(df, x=c_spend, y='CTR (%)', 
                             text=c_name if c_name else None,
                             size=c_spend, color='CTR (%)',
                             color_continuous_scale='Viridis',
                             labels={c_spend: "花費金額", 'CTR (%)': "點擊率 (CTR %)"},
                             title="氣泡越大代表花費越多；位置越靠上方代表點擊效率越高")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ 數據不足，無法生成分析圖表。")

        # --- 6. 逐一素材診斷 ---
        st.divider()
        st.subheader("📋 素材診斷與優化建議")
        
        for index, row in df.iterrows():
            name = row.get(c_name, f"素材 {index}")
            with st.expander(f"🔍 查看診斷：{name}"):
                col_a, col_b, col_c = st.columns([1, 1, 2])
                
                h_val = row.get('Hook Rate (%)', 0)
                c_val = row.get('CTR (%)', 0)
                r_val = row.get(c_roas, "N/A")
                
                col_a.metric("Hook Rate", f"{h_val}%")
                col_b.metric("CTR", f"{c_val}%")
                
                with col_c:
                    st.write("**💡 行動建議：**")
                    if h_val < 25 and h_val > 0:
                        st.error("❌ **前3秒沒人看**：吸睛度極低。建議更換開頭前3秒內容，直接點出用戶痛點。")
                    elif c_val < 1.0 and c_val > 0:
                        st.warning("⚠️ **觀眾點不下去**：CTR 偏低。建議強化文案的『限時感』或更換更清楚的產品圖。")
                    elif h_val >= 25 and c_val >= 1.0:
                        st.success("✅ **黃金素材**：表現非常優異。建議增加預算，並以此風格拍攝新系列。")
                    else:
                        st.info("指標尚無異常或數據不足。")
    else:
        st.error("❌ 報表中找不到『曝光次數』欄位，請確認匯出的欄位設定。")

else:
    st.info("👋 歡迎使用！請上傳 Meta
