import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meta 廣告全漏斗診斷", layout="wide")

st.title("Meta 廣告全漏斗數據診斷看板")

# 1. 檔案上傳
uploaded_file = st.file_uploader("請上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    # --- 定義精準欄位名稱 (根據您的截圖) ---
    c_name = "行銷活動名稱"
    c_spend = "花費金額  (TWD)"
    c_impr = "曝光次數"
    c_ctr = "CTR (全部) "
    c_hook = "影片播放 3 秒以上的比率 (每次曝光) "
    c_roas = "購買 ROAS (廣告投資報酬率) "

    if c_name in df.columns:
        # 數據清洗函數
        def clean_num(val):
            try:
                if pd.isna(val): return 0.0
                return float(str(val).replace('%', '').replace(',', ''))
            except: return 0.0

        # 清洗關鍵欄位
        df[c_ctr] = df[c_ctr].apply(clean_num)
        df[c_hook] = df[c_hook].apply(clean_num)
        df[c_spend] = df[c_spend].apply(clean_num)
        if c_roas in df.columns:
            df[c_roas] = df[c_roas].apply(clean_num)

        # 2. 漏斗分類邏輯
        def get_funnel_info(row):
            name = str(row[c_name]).lower()
            ctr = row[c_ctr]
            hook = row[c_hook]
            
            if any(x in name for x in ['con', '轉換', '購買', 'sale']):
                level = '3. 轉換層 (Conversion)'
                advice = "✅ 轉換主力：點擊率合格" if ctr >= 1.2 else "❌ 說服力不足：素材無法觸動購買慾。"
            elif any(x in name for x in ['tra', '流量', 'vcl', '點擊']):
                level = '2. 流量層 (Traffic)'
                advice = "✅ 導流高效" if ctr >= 1.0 else "⚠️ 連結誘因弱：建議強化優惠訊息。"
            else:
                level = '1. 認知層 (Awareness)'
                advice = "✅ 吸睛合格" if hook >= 25 else "❌ 開頭失敗：前3秒內容需優化。"
            return pd.Series([level, advice])

        df[['漏斗層級', '診斷建議']] = df.apply(get_funnel_info, axis=1)

        # 3. 數據看板摘要
        st.subheader("數據概覽")
        m1, m2, m3 = st.columns(3)
        m1.metric("總消耗 (TWD)", f"${df[c_spend].sum():,.0f}")
        m2.metric("平均 CTR", f"{df[c_ctr].mean():.2f}%")
        m3.metric("最高 ROAS", f"{df[c_roas].max() if c_roas in df.columns else 'N/A'}")

        # 4. 表格呈現 (重要指標全入列)
        st.subheader("素材全漏斗診斷清單")
        display_cols = [c_name, '漏斗層級', c_hook, c_ctr, '診斷建議']
        st.dataframe(df.sort_values('漏斗層級')[display_cols], use_container_width=True, hide_index=True)

        # 5. 視覺化分析圖
        st.divider()
        st.subheader("成效效率分佈圖")
        fig = px.scatter(df, x=c_spend, y=c_ctr, color='漏斗層級', text=c_name,
                         title="X軸:花費金額 / Y軸:點擊率 (越往上方代表效率越高)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"找不到關鍵欄位：{c_name}，請檢查 CSV 標題。")
else:
    st.info("👋 請上傳 CSV 檔案開始分析。")
