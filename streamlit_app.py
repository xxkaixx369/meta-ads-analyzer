import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meta 廣告全漏斗診斷", layout="wide")

st.title("🎯 Meta 廣告全漏斗自動化診斷")
st.write("自動識別認知、流量、轉換層級，並給予對應指標解讀。")

uploaded_file = st.file_uploader("上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    # 1. 智慧欄位偵測 (修正版：增加更多變體關鍵字)
    def find_col(keys):
        for col in df.columns:
            if any(k in col.lower().replace(" ", "") for k in keys): return col
        return None

    c_name = find_col(['廣告名稱', 'adname'])
    c_spend = find_col(['金額', '花費', 'amountspent', '消耗'])
    c_impr = find_col(['曝光', 'impressions'])
    c_click = find_col(['連結點擊', 'linkclicks'])
    c_hook = find_col(['3秒', '3-second'])

    if c_impr and c_name:
        # 2. 計算核心指標
        df['吸睛率(Hook%)'] = ((df[c_hook] / df[c_impr] * 100) if c_hook else 0).round(2)
        df['點擊率(CTR%)'] = ((df[c_click] / df[c_impr] * 100) if c_click else 0).round(2)
        if c_spend and c_click:
            df['點擊成本(CPC)'] = (df[c_spend] / df[c_click]).round(2)
        
        # 3. 行銷漏斗分類邏輯 (判斷廣告名稱關鍵字)
        def classify_funnel(name):
            name = str(name).lower()
            if any(x in name for x in ['con', '轉換', 'sale', '購買', '購買']): return '3. 轉換層 (Conversion)'
            if any(x in name for x in ['tra', '流量', 'vcl', '點擊']): return '2. 流量層 (Traffic)'
            return '1. 認知層 (Awareness)'

        df['行銷漏斗層級'] = df[c_name].apply(classify_funnel)

        # 4. 針對不同層級的診斷建議
        def get_funnel_advice(row):
            funnel = row['行銷漏斗層級']
            h = row['吸睛率(Hook%)']
            c = row['點擊率(CTR%)']
            
            if '認知' in funnel:
                if h < 20: return "❌ 認知層首重吸睛：前3秒視覺太弱，無法留住潛在受眾。"
                return "✅ 表現尚可：品牌印象建立中，可嘗試增加互動引導。"
            elif '流量' in funnel:
                if c < 1.0: return "⚠️ 流量層點擊太低：文案誘因不足，建議更換更有利的 Offer。"
                return "✅ 導流效率高：受眾對內容有興趣，建議測試不同落地頁。"
            else: # 轉換層
                if c < 1.2: return "❌ 轉換層點擊疲軟：素材無法激起購買慾。建議增加『限時』或『見證』。"
                return "✅ 轉換主力：成效穩定，可嘗試放大預算。"

        df['AI 診斷與優化建議'] = df.apply(get_funnel_advice, axis=1)

        # 5. 數據看板
        st.subheader("📊 帳戶概覽")
        m1, m2, m3 = st.columns(3)
        m1.metric("總消耗", f"${df[c_spend].sum():,.0f}" if c_spend else "N/A")
        m2.metric("平均 CTR", f"{df['點擊率(CTR%)'].mean():.2f}%")
        m3.metric("平均 Hook Rate", f"{df['吸睛率(Hook%)'].mean():.2f}%")

        # 6. 表格呈現 (依漏斗排序)
        st.subheader("📋 全素材漏斗診斷表")
        df_display = df.sort_values('行銷漏斗層級')
        
        # 整理要顯示的欄位
        cols = [c_name, '行銷漏斗層級', c_spend, '吸睛率(Hook%)', '點擊率(CTR%)', 'AI 診斷與優化建議']
        # 過濾掉不存在的欄位
        actual_cols = [c for c in cols if c in df_display.columns]
        
        st.dataframe(df_display[actual_cols], use_container_width=True, hide_index=True)

        # 7. 視覺化散
