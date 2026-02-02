import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meta 廣告全漏斗診斷", layout="wide")

st.title("🎯 Meta 廣告全漏斗數據診斷看板")

# 1. 檔案上傳
uploaded_file = st.file_uploader("請上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    # 2. 強化版智慧欄位偵測 (解決名稱消失的問題)
    def find_col(keys):
        for col in df.columns:
            clean_col = str(col).lower().replace(" ", "").replace("_", "")
            if any(k in clean_col for k in keys): return col
        return None

    c_name = find_col(['廣告名稱', 'adname'])
    c_spend = find_col(['金額', '花費', 'amountspent', '消耗'])
    c_impr = find_col(['曝光次數', 'impressions', '展現'])
    c_click = find_col(['連結點擊', 'linkclicks'])
    c_hook = find_col(['3秒', '3-second', '三秒'])

    if c_name and c_impr:
        # 3. 計算重要指標
        df['吸睛率(Hook%)'] = ((df[c_hook] / df[c_impr] * 100) if c_hook else 0).round(2)
        df['點擊率(CTR%)'] = ((df[c_click] / df[c_impr] * 100) if c_click else 0).round(2)
        
        # 4. 漏斗分類與診斷建議
        def analyze_row(row):
            name = str(row[c_name]).lower()
            h = row['吸睛率(Hook%)']
            c = row['點擊率(CTR%)']
            
            # 漏斗層級判斷
            if any(x in name for x in ['con', '轉換', 'sale', '購買']):
                level = '轉換層 (Conversion)'
                advice = "✅ 轉換有力" if c >= 1.2 else "❌ 轉換疲軟：素材說服力不足。"
            elif any(x in name for x in ['tra', '流量', 'vcl', '點擊']):
                level = '流量層 (Traffic)'
                advice = "✅ 導流高效" if c >= 1.0 else "⚠️ 連結誘因弱：建議強化優惠訊息。"
            else:
                level = '認知層 (Awareness)'
