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

    # 1. 根據截圖精準對應欄位
    c_name = "行銷活動名稱"
    c_spend = "花費金額  (TWD)"
    c_impr = "曝光次數"
    c_ctr = "CTR (全部) "  # 注意結尾有空格
    c_hook = "影片播放 3 秒以上的比率 (每次曝光) " # 這是你的吸睛率
    c_roas = "購買 ROAS (廣告投資報酬率) "
    c_cpc = "CPC (單次連結點擊成本)  (TWD)"

    # 檢查核心欄位是否存在
    if c_name in df.columns:
        st.success("✅ 欄位匹配成功！正在產出報告...")

        # 2. 數據清洗：移除數字中的百分比符號並轉為浮點數
        for col in [c_ctr, c_hook]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('%', '').astype(float)

        # 3. 漏斗分類與診斷邏輯
        def analyze_funnel(row):
            name = str(row[c_name]).lower()
            ctr = row[c_ctr] if c_ctr in row else 0
            hook = row[c_hook] if c_hook in row else 0
            
            # 漏斗層級判斷
            if any(x in name for x in ['con', '轉換', '購買', 'sale']):
                level, advice = '3. 轉換層', "✅ 轉換主力" if ctr >= 1.2 else "❌ 說服力不足"
            elif any(x in name for x in ['tra', '流量', 'vcl', '點擊']):
                level, advice = '2. 流量層', "✅ 導流高效" if ctr >= 1.0 else "⚠️ 連結誘因弱"
            else:
                level, advice = '1. 認知層', "✅ 吸睛合格" if hook >= 25 else "❌ 開頭失敗"
            return pd.Series([level, advice])

        df[['漏斗層級', '診斷建議']] = df.apply(analyze_funnel, axis=1)

        # 4. 數據摘要
        st.subheader("📊 帳戶指標概覽")
        m1, m2, m3 = st.columns(3)
        m1.metric("總消耗 (TWD)", f"${df[c_spend].sum():,.0f}" if c_spend in df.columns else "N/A")
        m2.metric("平均 CTR", f"{df[c_ctr].mean():.2f}%" if c_ctr in df.columns else "N/A")
        m3.metric("最高 ROAS", f"{df[c_roas].max()}" if c_roas in df.columns else "N/A")

        # 5. 表格呈現
        st.subheader("📋 全素材漏斗診斷表格")
        # 決定要顯示的欄位清單
        display_cols = [c_name, '漏斗層級', c_hook, c_ctr, c_cpc, '診斷建議']
        # 過濾掉表格中不存在的欄位避免報錯
        actual_display = [c for c in display_cols if c in df.columns or c in ['漏斗層級', '診斷建議']]
        
        st.dataframe(df.sort_values('漏斗層級')[actual_display], use_container_width=True, hide_index=True)

        # 6. 視覺化散佈圖
        st.divider()
        fig = px.scatter(df, x=c_spend if c_spend in df.columns else c_ctr, 
                         y=c_ctr, color='漏斗層級', text=c_name, 
                         hover_data=[c_roas] if c_roas in df.columns else [],
                         title="廣告成效分佈 (氣泡位置越高代表點擊效率越高)")
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.error(f"❌ 關鍵欄位匹配失敗。請確認報表中是否包含『{c_name}』。")
else:
    st.info("👋 請上傳 Meta 報表 CSV 開始分析。")
