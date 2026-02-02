import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meta 廣告全漏斗診斷", layout="wide")

st.title("🎯 Meta 廣告全漏斗數據診斷看板")

# 1. 檔案上傳
uploaded_file = st.file_uploader("請上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    try:
        # 自動嘗試多種編碼，解決亂碼問題
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    # 【偵錯區】印出所有欄位名稱，方便確認
    with st.expander("🛠️ 偵錯模式：查看原始欄位名稱"):
        st.write("您的 CSV 包含以下欄位：", list(df.columns))

    # 2. 超強容錯欄位偵測
    def find_col(keys):
        for col in df.columns:
            # 移除空格與符號進行比對
            clean_col = str(col).lower().replace(" ", "").replace("_", "").replace("-", "")
            if any(k in clean_col for k in keys): return col
        return None

    # 關鍵字庫
    c_name = find_col(['廣告名稱', 'adname', '素材名稱'])
    c_spend = find_col(['金額', '花費', 'amountspent', '消耗', 'cost'])
    c_impr = find_col(['曝光', 'impressions', '展現'])
    c_click = find_col(['連結點擊', 'linkclicks', '點擊'])
    c_hook = find_col(['3秒', '3-second', '三秒', 'plays'])

    # 3. 判斷是否具備基本數據
    if c_name and c_impr:
        st.success(f"✅ 成功辨識關鍵欄位：名稱({c_name})、曝光({c_impr})")
        
        # 指標計算
        df['吸睛率(Hook%)'] = ((df[c_hook] / df[c_impr] * 100) if c_hook else 0).round(2)
        df['點擊率(CTR%)'] = ((df[c_click] / df[c_impr] * 100) if c_click else 0).round(2)
        
        # 4. 漏斗分類與解讀
        def analyze_row(row):
            name = str(row[c_name]).lower()
            h = row['吸睛率(Hook%)']
            c = row['點擊率(CTR%)']
            
            if any(x in name for x in ['con', '轉換', 'sale', '購買', 'purchase']):
                level, advice = '3. 轉換層', "✅ 轉換主力" if c >= 1.2 else "❌ 說服力不足"
            elif any(x in name for x in ['tra', '流量', 'vcl', '點擊', 'click']):
                level, advice = '2. 流量層', "✅ 導流高效" if c >= 1.0 else "⚠️ 誘因較弱"
            else:
                level, advice = '1. 認知層', "✅ 吸睛合格" if h >= 25 else "❌ 開頭失敗"
            return pd.Series([level, advice])

        df[['漏斗層級', '診斷建議']] = df.apply(analyze_row, axis=1)

        # 5. 顯示數據摘要
        st.subheader("📊 帳戶指標概覽")
        m1, m2, m3 = st.columns(3)
        m1.metric("總消耗", f"${df[c_spend].sum():,.0f}" if c_spend else "N/A")
        m2.metric("平均 CTR", f"{df['點擊率(CTR%)'].mean():.2f}%")
        m3.metric("平均 Hook Rate", f"{df['吸睛率(Hook%)'].mean():.2f}%")

        # 6. 表格顯示
        st.subheader("📋 素材全漏斗診斷表格")
        display_cols = [c_name, '漏斗層級', '吸睛率(Hook%)', '點擊率(CTR%)', '診斷建議']
        st.dataframe(df.sort_values('漏斗層級')[display_cols], use_container_width=True, hide_index=True)

        # 7. 圖表顯示
        st.divider()
        fig = px.scatter(df, x=c_spend if c_spend else '吸睛率(Hook%)', y='點擊率(CTR%)', 
                         color='漏斗層級', text=c_name, title="廣告成效分佈")
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.error("❌ 無法自動辨識欄位。請點開上方的『偵錯模式』檢查您的 CSV 標題是否有：『廣告名稱』與『曝光次數』。")
else:
    st.info("👋 請上傳 Meta 報表 CSV 開始分析。")
