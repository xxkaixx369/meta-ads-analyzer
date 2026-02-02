import streamlit as st
import pandas as pd

st.set_page_config(page_title="Meta 廣告成效診斷", layout="wide")

st.title("🎯 Meta 廣告素材自動化診斷 (專家邏輯版)")
st.write("此版本無需 API Key，上傳報表後將自動根據廣告指標提供優化建議。")

# 檔案上傳
uploaded_file = st.file_uploader("請上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    # 讀取數據 (自動處理不同編碼)
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    st.success("數據導入成功！")
    
    # 呈現數據清單
    st.subheader("📊 數據診斷列表")
    
    # 診斷邏輯（根據 Meta 常見欄位名稱）
    for index, row in df.iterrows():
        ad_name = row.get('廣告名稱', row.get('Ad Name', f'素材 {index}'))
        
        # 取得關鍵指標 (若無則設為 0)
        impressions = row.get('曝光次數', row.get('Impressions', 0))
        hook_plays = row.get('3 秒影片觀看次數', row.get('3-second video plays', 0))
        clicks = row.get('連結點擊次數', row.get('Link clicks', 0))
        
        # 計算指標
        hook_rate = (hook_plays / impressions * 100) if impressions > 0 else 0
        ctr = (clicks / impressions * 100) if impressions > 0 else 0

        with st.expander(f"🔍 診斷報告：{ad_name}"):
            c1, c2 = st.columns(2)
            with c1:
                st.metric("吸睛率 (Hook Rate)", f"{hook_rate:.2f}%")
                st.metric("點擊率 (CTR)", f"{ctr:.2f}%")
            
            with c2:
                st.write("**💡 優化建議：**")
                if hook_rate < 20 and hook_rate > 0:
                    st.error("❌ **前 3 秒吸引力不足**：觀眾直接滑過。建議更換開頭前 3 秒的視覺，或加入更強烈的痛點文字。")
                elif ctr < 1.0 and ctr > 0:
                    st.warning("⚠️ **內容誘因弱**：雖然有看但不想點。建議強化文案的『行動呼籲 (CTA)』或調整優惠訊息。")
                elif hook_rate >= 20 and ctr >= 1.0:
                    st.success("✅ **優質素材**：各項指標良好，建議增加預算並以此風格製作後續素材。")
                else:
                    st.info("數據不足，無法提供具體建議。")

st.info("💡 提示：本工具目前設定 Hook Rate > 20% 為合格，CTR > 1% 為合格。")
