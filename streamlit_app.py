import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meta 廣告三層級診斷", layout="wide")

st.title("🎯 Meta 廣告全階層數據診斷看板")
st.write("點擊「行銷活動」展開，查看內部的「廣告組合」與個別「廣告素材」表現。")

uploaded_file = st.file_uploader("請上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    # --- 1. 強化版欄位偵測 (解決 KeyError) ---
    def find_col(keys):
        for col in df.columns:
            # 移除所有空白比對關鍵字
            clean_col = str(col).replace(" ", "").replace("　", "")
            if any(k in clean_col for k in keys): return col
        return None

    # 精準對應您截圖中的欄位
    c_camp = find_col(['行銷活動名稱'])
    c_adset = find_col(['廣告組合名稱'])
    c_ad = find_col(['廣告名稱'])
    c_spend = find_col(['花費金額', '金額'])
    c_impr = find_col(['曝光次數'])
    c_ctr = find_col(['CTR(全部)'])
    c_hook = find_col(['影片播放3秒以上的比率'])
    c_roas = find_col(['購買ROAS'])

    # --- 2. 資料清洗 ---
    def to_num(val):
        try:
            if pd.isna(val) or str(val).strip() == "": return 0.0
            return float(str(val).replace('%', '').replace(',', '').strip())
        except: return 0.0

    target_cols = [c_spend, c_ctr, c_hook, c_roas]
    for col in target_cols:
        if col: df[col] = df[col].apply(to_num)

    if c_camp:
        # --- 3. 數據看板摘要 ---
        st.subheader("📊 帳戶整體成效")
        m1, m2, m3 = st.columns(3)
        m1.metric("總消耗 (TWD)", f"${df[c_spend].sum():,.0f}" if c_spend else "N/A")
        m2.metric("平均 CTR", f"{df[c_ctr].mean():.2f}%" if c_ctr else "N/A")
        m3.metric("平均吸睛率 (Hook)", f"{df[c_hook].mean():.2f}%" if c_hook else "N/A")

        # --- 4. 三層級階層顯示 (摺疊設計) ---
        st.divider()
        st.subheader("📋 階層式診斷清單")
        
        # 以行銷活動分組
        camps = df[c_camp].unique()
        for camp in camps:
            camp_df = df[df[c_camp] == camp]
            camp_spend = camp_df[c_spend].sum() if c_spend else 0
            
            # 第一層：行銷活動 (Expander)
            with st.expander(f"📌 行銷活動：{camp} (總花費: ${camp_spend:,.0f})"):
                
                # 檢查是否有廣告組合層級
                if c_adset and c_adset in df.columns:
                    adsets = camp_df[c_adset].unique()
                    for adset in adsets:
                        adset_df = camp_df[camp_df[c_adset] == adset]
                        
                        # 第二層：廣告組合 (標題)
                        st.markdown(f"**📂 廣告組合：{adset}**")
                        
                        # 第三層：廣告素材 (表格)
                        if c_ad and c_ad in df.columns:
                            # 整理表格欄位
                            cols_to_show = [c_ad]
                            if c_hook: cols_to_show.append(c_hook)
                            if c_ctr: cols_to_show.append(c_ctr)
                            if c_roas: cols_to_show.append(c_roas)
                            
                            # 診斷 logic
                            def get_label(row):
                                if c_hook and row[c_hook] < 20: return "❌ 前3秒太悶"
                                if c_ctr and row[c_ctr] < 1.0: return "⚠️ 連結不吸引"
                                return "✅ 表現穩定"
                            
                            display_df = adset_df[cols_to_show].copy()
                            display_df['AI 診斷'] = adset_df.apply(get_label, axis=1)
                            
                            st.table(display_df)
                else:
                    # 如果 CSV 沒匯出廣告組合，直接顯示廣告
                    st.info("提示：若需查看廣告組合層級，請在 Meta 匯出報表時勾選『廣告組合名稱』與『廣告名稱』。")
                    if c_ad:
                        st.table(camp_df[[c_ad, c_hook, c_ctr]])

        # --- 5. 視覺化分析圖 (排除錯誤) ---
        if c_spend and c_ctr:
            st.divider()
            st.subheader("📈 素材效率分析圖")
            # 確保資料有效才畫圖
            plot_df = df[df[c_impr] > 0] if c_impr else df
            if not plot_df.empty:
                fig = px.scatter(plot_df, x=c_spend, y=c_ctr, color=c_camp, 
                                 text=c_ad if c_ad else c_camp,
                                 title="氣泡越高代表點擊效率越高")
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"❌ 無法識別『行銷活動名稱』。請檢查 CSV 欄位名稱。")
else:
    st.info("👋 歡迎使用！請上傳 CSV 開始分析。建議匯出時包含『行銷活動、廣告組合、廣告』三種維度。")
