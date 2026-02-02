import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meta 廣告階層診斷", layout="wide")
st.title("🎯 Meta 廣告全階層自動化診斷")
st.write("點擊「行銷活動」可展開查看下層的「廣告組合」與「廣告素材」數據。")

uploaded_file = st.file_uploader("上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    # --- 1. 智慧欄位偵測 (支援三層級) ---
    def get_col(keywords):
        for col in df.columns:
            clean_col = str(col).replace(" ", "").replace("　", "")
            if any(k in clean_col for k in keywords): return col
        return None

    c_camp = get_col(['行銷活動名稱', 'CampaignName'])
    c_adset = get_col(['廣告組合名稱', 'AdSetName', '廣告組'])
    c_ad = get_col(['廣告名稱', 'AdName', '素材名稱'])
    c_spend = get_col(['花費金額', '金額', 'AmountSpent'])
    c_impr = get_col(['曝光次數', 'Impressions'])
    c_ctr = get_col(['CTR(全部)', '點擊率'])
    c_hook = get_col(['影片播放3秒以上的比率', '3秒播放'])
    c_roas = get_col(['購買ROAS', '廣告投資報酬率'])

    if c_camp and c_adset and c_ad:
        # --- 2. 資料清洗 ---
        def to_float(val):
            try:
                if pd.isna(val) or str(val).strip() == "": return 0.0
                return float(str(val).replace('%', '').replace(',', '').strip())
            except: return 0.0

        for col in [c_spend, c_ctr, c_hook, c_roas]:
            if col: df[col] = df[col].apply(to_float)

        # --- 3. 漏斗分類邏輯 ---
        def get_level(name):
            name = str(name).lower()
            if any(x in name for x in ['con', '轉換', '購買']): return '3. 轉換層'
            if any(x in name for x in ['tra', '流量', '點擊']): return '2. 流量層'
            return '1. 認知層'

        # --- 4. 階層式顯示介面 ---
        st.subheader("📋 廣告層級診斷看板")
        
        # 依照行銷活動分組
        campaigns = df[c_camp].unique()
        
        for camp in campaigns:
            camp_df = df[df[c_camp] == camp]
            funnel_level = get_level(camp)
            total_spend = camp_df[c_spend].sum()
            avg_ctr = camp_df[c_ctr].mean()
            
            # 第一層：行銷活動 (Expander)
            with st.expander(f"📌 行銷活動：{camp} | 【{funnel_level}】 | 總花費: ${total_spend:,.0f}"):
                
                # 診斷建議 (行銷活動級)
                if avg_ctr < 1.0:
                    st.warning(f"💡 診斷：整體點擊率偏低 ({avg_ctr:.2f}%)，建議檢查受眾精準度。")
                
                # 第二層：廣告組合
                adsets = camp_df[c_adset].unique()
                for adset in adsets:
                    adset_df = camp_df[camp_df[c_adset] == adset]
                    adset_spend = adset_df[c_spend].sum()
                    
                    st.markdown(f"**📂 廣告組合：{adset}** (花費: ${adset_spend:,.0f})")
                    
                    # 第三層：具體廣告 (表格)
                    # 整理要顯示的欄位
                    final_display = adset_df[[c_ad, c_hook, c_ctr, c_roas]].copy()
                    
                    # 加上簡單的診斷建議
                    def quick_advice(row):
                        if row[c_hook] < 25: return "❌ 影片前3秒太無聊"
                        if row[c_ctr] < 1.0: return "⚠️ 連結誘因不足"
                        return "✅ 表現穩定"
                    
                    final_display['素材診斷'] = final_display.apply(quick_advice, axis=1)
                    
                    st.table(final_display)
                    st.divider()

        # --- 5. 視覺化全景圖 ---
        st.divider()
        st.subheader("📈 全素材效率分佈 (氣泡圖)")
        fig = px.scatter(df, x=c_spend, y=c_ctr, color=c_camp, size=c_impr,
                         hover_data=[c_adset, c_ad], text=c_ad,
                         title="越高代表點擊效率越高，氣泡越大曝光越多")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("❌ 報表欄位不足，請確認匯出報表包含：行銷活動名稱、廣告組合名稱、廣告名稱。")
else:
    st.info("👋 請上傳包含『行銷活動、廣告組合、廣告』三層級的 Meta CSV 報表。")
