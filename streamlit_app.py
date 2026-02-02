import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meta 廣告 AI 診斷室", layout="wide")

st.title("🎯 Meta 廣告全漏斗數據診斷看板")

uploaded_file = st.file_uploader("上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    # --- 1. 根據您的截圖定義精準欄位名稱 ---
    # 這裡的名稱必須與您截圖中的字串完全一致（包含空格）
    c_name = "行銷活動名稱"
    c_spend = "花費金額  (TWD)"
    c_impr = "曝光次數"
    c_ctr = "CTR (全部) "
    c_hook = "影片播放 3 秒以上的比率 (每次曝光) "
    c_roas = "購買 ROAS (廣告投資報酬率) "
    c_cpc = "CPC (單次連結點擊成本)  (TWD)"

    if c_name in df.columns:
        # --- 2. 資料清洗 (重要：解決 ValueError) ---
        # 轉為字串後移除 %，再轉為浮點數，若失敗則填 0
        def clean_num(val):
            try:
                if pd.isna(val): return 0.0
                return float(str(val).replace('%', '').replace(',', ''))
            except:
                return 0.0

        df[c_ctr] = df[c_ctr].apply(clean_num)
        df[c_hook] = df[c_hook].apply(clean_num)
        df[c_spend] = df[c_spend].apply(clean_num)
        if c_roas in df.columns:
            df[c_roas] = df[c_roas].apply(clean_num)

        # --- 3. 自動分類與解讀建議 ---
        def get_advice(row):
            name = str(row[c_name]).lower()
            ctr = row[c_ctr]
            hook = row[c_hook]
            
            if any(x in name for x in ['con', '轉換', '購買', 'sale']):
                level = '3. 轉換層 (Conversion)'
                advice = "✅ 轉換主力：點擊率合格" if ctr >= 1.2 else "❌ 說服力不足：素材無法觸動購買慾。"
            elif any(x in name for x in ['tra', '流量', 'vcl', '點擊']):
                level = '2. 流量層 (Traffic)'
                advice = "✅ 導流高效" if ctr >= 1.0 else "⚠️ 連結誘因弱：建議更換強吸引力的 Offer。"
            else:
                level = '1. 認知層 (Awareness)'
                advice = "✅ 吸睛合格" if hook >= 25 else "❌ 開頭失敗：前3秒內容需大改。"
            return pd.Series([level, advice])

        df[['行銷層級', '診斷建議']] = df.apply(get_advice, axis=1)

        # --- 4. 數據摘要看板 ---
        st.subheader("📊 帳戶指標摘要")
        m1, m2, m3 = st.columns(3)
        m1.metric("總消耗 (TWD)", f"${df[c_spend].sum():,.0f}")
        m2.metric("平均 CTR", f"{df[c_ctr].mean():.2f}%")
        m3.metric("最高 ROAS", f"{df[c_roas].max() if c_roas in df.columns else 'N/A'}")

        # --- 5. 表格呈現 ---
        st.subheader("📋 素材分類診斷表格")
        display_cols = [c_name, '行銷層級', c_hook, c_ctr, '診斷建議']
        # 確保只顯示存在的欄位且過濾掉數據全為 0 的空行
        df_final = df[df[c_impr] > 0] if c_impr in df.columns else df
        st.dataframe(df_final.sort_values('行銷層級')[display_cols], use_container_width=True, hide_index=True)

        # --- 6. 視覺化分析圖 (增加安全性檢查) ---
        st.divider()
        st.subheader("📈
