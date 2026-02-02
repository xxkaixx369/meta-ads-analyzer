import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meta 廣告全指標診斷", layout="wide")

st.title("🎯 Meta 廣告全階層指標診斷看板")
st.write("點擊「行銷活動」展開，即可查看下屬廣告組合與廣告素材的**完整指標表格**。")

uploaded_file = st.file_uploader("請上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    # --- 1. 強化版欄位偵測 (對準 12.01.33 截圖清單) ---
    def find_col(keys):
        for col in df.columns:
            clean_col = str(col).replace(" ", "").replace("　", "")
            if any(k in clean_col for k in keys): return col
        return None

    c_camp = find_col(['行銷活動名稱'])
    c_adset = find_col(['廣告組合名稱'])
    c_ad = find_col(['廣告名稱'])
    c_spend = find_col(['花費金額'])
    c_impr = find_col(['曝光次數'])
    c_ctr = find_col(['CTR(全部)'])
    c_hook = find_col(['影片播放3秒以上的比率'])
    c_roas = find_col(['購買ROAS'])

    # --- 2. 深度資料清洗 (解決 0 或 None 的問題) ---
    def clean_val(val):
        try:
            if pd.isna(val) or str(val).strip() in ["", "None", "0"]: return 0.0
            return float(str(val).replace('%', '').replace(',', '').strip())
        except: return 0.0

    if c_camp:
        for col in [c_spend, c_ctr, c_hook, c_roas]:
            if col: df[col] = df[col].apply(clean_val)

        # --- 3. 核心診斷邏輯 (更靈敏的判讀標準) ---
        def get_ai_advice(row):
            h = row.get(c_hook, 0)
            c = row.get(c_ctr, 0)
            r = row.get(c_roas, 0)
            s = row.get(c_spend, 0)
            
            if s == 0: return "⚪️ 尚無數據"
            if h < 25: return "❌ 吸睛度低 (前3秒流失)"
            if c < 0.9: return "⚠️ 連結誘因不足 (點擊弱)"
            if r > 0 and r < 1.2: return "💸 投報率偏低 (轉換差)"
            if r >= 2.5 or (c > 1.5 and h > 35): return "🔥 表現優異：建議加預算"
            return "✅ 表現穩定"

        # --- 4. 數據摘要看板 ---
        st.subheader("📊 帳戶整體成效")
        m1, m2, m3 = st.columns(3)
        m1.metric("總消耗 (TWD)", f"${df[c_spend].sum():,.0f}" if c_spend else "N/A")
        m2.metric("平均 CTR", f"{df[c_ctr].mean():.2f}%" if c_ctr else "N/A")
        m3.metric("平均吸睛率 (Hook)", f"{df[c_hook].mean():.2f}%" if c_hook else "N/A")

        # --- 5. 階層式顯示 (含完整指標表格) ---
        st.divider()
        st.subheader("📋 階層式指標清單")
        
        camps = df[c_camp].unique()
        for camp in camps:
            camp_df = df[df[c_camp] == camp]
            camp_spend = camp_df[c_spend].sum()
            
            with st.expander(f"📌 行銷活動：{camp} | 總花費: ${camp_spend:,.0f}"):
                
                if c_adset in df.columns:
                    adsets = camp_df[c_adset].unique()
                    for adset in adsets:
                        adset_df = camp_df[camp_df[c_adset] == adset]
                        st.markdown(f"**📂 廣告組合：{adset}**")
                        
                        # 整理要顯示的廣告表格資料
                        table_df = adset_df.copy()
                        table_df['AI 診斷建議'] = table_df.apply(get_ai_advice, axis=1)
                        
                        # 格式化顯示
                        display_cols = {
                            c_ad: "廣告素材名稱",
                            c_spend: "花費 (TWD)",
                            c_hook: "吸睛率(%)",
                            c_ctr: "點擊率(%)",
                            c_roas: "ROAS",
                            'AI 診斷建議': "AI 診斷建議"
                        }
                        
                        # 只選取存在的欄位並重新命名
                        actual_cols = [c for c in display_cols.keys() if c in table_df.columns]
                        final_table = table_df[actual_cols].rename(columns=display_cols)
                        
                        # 顯示表格 (使用 dataframe 讓介面更整齊)
                        st.dataframe(
                            final_table.sort_values("花費 (TWD)", ascending=False),
                            use_container_width=True,
                            hide_index=True
                        )
                else:
                    st.warning("報表中缺少『廣告組合名稱』，請在匯出時確認維度。")

        # --- 6. 視覺化分析 ---
        if c_spend and c_ctr:
            st.divider()
            st.subheader("📈 素材效率分佈 (氣泡圖)")
            fig = px.scatter(df, x=c_spend, y=c_ctr, color=c_camp, 
                             size=c_impr if c_impr else None,
                             hover_data=[c_ad], text=c_ad,
                             title="X軸:花費金額 / Y軸:點擊率 (越高代表素材越強)")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("❌ 找不到關鍵欄位，請確認 CSV 標題包含『行銷活動名稱』。")
else:
    st.info("👋 請上傳包含『行銷活動、廣告組合、廣告』三層級的 Meta CSV 報表。")
