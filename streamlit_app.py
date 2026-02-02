import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meta 廣告全漏斗診斷", layout="wide")
st.title("🎯 Meta 廣告全漏斗數據診斷看板")

uploaded_file = st.file_uploader("請上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    # --- 1. 萬用欄位偵測邏輯 (解決空格與命名問題) ---
    def get_col(keywords):
        for col in df.columns:
            clean_col = str(col).replace(" ", "").replace("　", "")
            if any(k in clean_col for k in keywords):
                return col
        return None

    # 根據你的截圖清單進行匹配
    c_name = get_col(['行銷活動名稱', '廣告名稱'])
    c_spend = get_col(['花費金額', '金額', 'AmountSpent'])
    c_impr = get_col(['曝光次數', 'Impressions'])
    c_ctr = get_col(['CTR(全部)', '點擊率'])
    c_hook = get_col(['影片播放3秒以上的比率', '3秒播放'])
    c_roas = get_col(['購買ROAS', '廣告投資報酬率'])
    c_cpc = get_col(['CPC', '單次連結點擊成本'])

    if c_name and c_impr:
        # --- 2. 資料強制清洗 (解決 ValueError) ---
        def to_float(val):
            try:
                if pd.isna(val) or str(val).strip() == "": return 0.0
                return float(str(val).replace('%', '').replace(',', '').strip())
            except: return 0.0

        # 清洗數據並確保欄位存在
        active_cols = [c_spend, c_ctr, c_hook, c_roas, c_cpc]
        for col in active_cols:
            if col: df[col] = df[col].apply(to_float)

        # --- 3. 漏斗分類與自動解讀 ---
        def analyze_funnel(row):
            name = str(row[c_name]).lower()
            ctr = row.get(c_ctr, 0)
            hook = row.get(c_hook, 0)
            
            if any(x in name for x in ['con', '轉換', '購買', 'sale']):
                level, advice = '3. 轉換層', "✅ 轉換主力" if ctr >= 1.2 else "❌ 說服力不足"
            elif any(x in name for x in ['tra', '流量', 'vcl', '點擊']):
                level, advice = '2. 流量層', "✅ 導流高效" if ctr >= 1.0 else "⚠️ 誘因較弱"
            else:
                level, advice = '1. 認知層', "✅ 吸睛合格" if hook >= 25 else "❌ 前3秒流失嚴重"
            return pd.Series([level, advice])

        df[['漏斗層級', '診斷建議']] = df.apply(analyze_funnel, axis=1)

        # --- 4. 看板與表格呈現 ---
        st.subheader("📊 帳戶指標概覽")
        m1, m2, m3 = st.columns(3)
        m1.metric("總消耗 (TWD)", f"${df[c_spend].sum():,.0f}" if c_spend else "N/A")
        m2.metric("平均 CTR", f"{df[c_ctr].mean():.2f}%" if c_ctr else "N/A")
        m3.metric("平均 Hook Rate", f"{df[c_hook].mean():.2f}%" if c_hook else "N/A")

        st.subheader("📋 素材分類診斷表格")
        # 組合要顯示的表格
        show_cols = [c_name, '漏斗層級']
        if c_hook: show_cols.append(c_hook)
        if c_ctr: show_cols.append(c_ctr)
        if c_roas: show_cols.append(c_roas)
        show_cols.append('診斷建議')
        
        st.dataframe(df.sort_values('漏斗層級')[show_cols], use_container_width=True, hide_index=True)

        # --- 5. 安全繪圖 (解決 ValueError) ---
        if c_spend and c_ctr:
            st.divider()
            st.subheader("📈 效率分析圖")
            plot_df = df[df[c_impr] > 0].dropna(subset=[c_spend, c_ctr])
            if not plot_df.empty:
                fig = px.scatter(plot_df, x=c_spend, y=c_ctr, color='漏斗層級', 
                                 text=c_name, size=c_spend,
                                 title="氣泡越大代表花費越多；位置越高效率越高")
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"❌ 無法辨識關鍵欄位（行銷活動名稱或曝光）。偵測到的欄位有：{list(df.columns)}")
else:
    st.info("👋 請上傳 Meta 報表 CSV 開始自動診斷。")
