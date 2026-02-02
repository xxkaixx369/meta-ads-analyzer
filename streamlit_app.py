import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meta 廣告全漏斗診斷", layout="wide")

st.title("🎯 Meta 廣告全漏斗自動化診斷")
st.write("根據認知、流量、轉換層級，提供精準指標解讀與優化方向。")

# 1. 檔案上傳
uploaded_file = st.file_uploader("上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    st.success("✅ 數據導入成功！")

    # 2. 智慧欄位偵測 (修正：更精準的關鍵字匹配)
    def find_col(keys):
        for col in df.columns:
            clean_col = col.lower().replace(" ", "").replace("_", "")
            if any(k in clean_col for k in keys): return col
        return None

    c_name = find_col(['廣告名稱', 'adname'])
    c_spend = find_col(['金額', '花費', 'amountspent', '消耗'])
    c_impr = find_col(['曝光', 'impressions'])
    c_click = find_col(['連結點擊', 'linkclicks'])
    c_hook = find_col(['3秒', '3-second', '三秒'])

    if c_impr and c_name:
        # 3. 核心指標計算
        df['吸睛率(Hook%)'] = ((df[c_hook] / df[c_impr] * 100) if c_hook else 0).round(2)
        df['點擊率(CTR%)'] = ((df[c_click] / df[c_impr] * 100) if c_click else 0).round(2)
        
        # 4. 漏斗層級分類與解讀邏輯
        def get_funnel_and_advice(row):
            name = str(row[c_name]).lower()
            h = row['吸睛率(Hook%)']
            c = row['點擊率(CTR%)']
            
            # 分類邏輯
            if any(x in name for x in ['con', '轉換', 'sale', '購買', 'purchase']):
                funnel = '3. 轉換層 (Conversion)'
                # 轉換層重點：CTR 與 最終行動
                advice = "✅ 轉換核心：點擊表現良好" if c >= 1.2 else "❌ 轉換疲軟：素材說服力不足，建議強化 Call-to-Action。"
            elif any(x in name for x in ['tra', '流量', 'vcl', 'click', '點擊']):
                funnel = '2. 流量層 (Traffic)'
                # 流量層重點：CTR 與 連結誘因
                advice = "✅ 導流效率高：內容具吸引力" if c >= 1.0 else "⚠️ 流量卡關：文案誘因不足，建議更換 Offer 或標題。"
            else:
                funnel = '1. 認知層 (Awareness)'
                # 認知層重點：Hook Rate (前三秒)
                advice = "✅ 品牌建立中：吸睛度合格" if h >= 25 else "❌ 開頭失敗：前3秒無法留人，建議更換素材視覺重心。"
            
            return pd.Series([funnel, advice])

        df[['行銷層級', '指標解讀建議']] = df.apply(get_funnel_and_advice, axis=1)

        # 5. 數據看板
        st.subheader("📊 帳戶指標摘要")
        m1, m2, m3 = st.columns(3)
        m1.metric("總消耗", f"${df[c_spend].sum():,.0f}" if c_spend else "N/A")
        m2.metric("平均 CTR", f"{df['點擊率(CTR%)'].mean():.2f}%")
        m3.metric("平均 Hook Rate", f"{df['吸睛率(Hook%)'].mean():.2f}%")

        # 6. 表格呈現 (依層級排序)
        st.subheader("📋 素材
