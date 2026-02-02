import streamlit as st
import pandas as pd

# --- 設定頁面 ---
st.set_page_config(page_title="Meta 廣告全指標診斷", layout="wide")
st.title("🎯 Meta 廣告全漏斗關鍵指標大表")

uploaded_file = st.file_uploader("請上傳包含『影片指標』的 Meta 報表 (CSV)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    # --- 欄位自動匹配函數 ---
    def find_col(keys):
        for col in df.columns:
            clean_col = str(col).strip()
            if any(k in clean_col for k in keys):
                return col
        return None

    # 關鍵欄位對應
    c = {
        "camp": find_col(['行銷活動名稱']),
        "ad": find_col(['廣告名稱']),
        "spend": find_col(['花費金額']),
        "hook": find_col(['影片播放 3 秒以上的比率', '影片播放3秒']), # 鉤子率
        "v25": find_col(['影片播放到 25%']),
        "ctr": find_col(['CTR（連結點閱率）', 'CTR']),
        "pur": find_col(['購買次數', '成果']),
        "roas": find_col(['購買 ROAS', '購買ROAS'])
    }

    # 檢查是否缺少關鍵指標
    missing_cols = [k for k, v in c.items() if v is None and k in ['hook', 'v25', 'roas']]
    if missing_cols:
        st.warning(f"⚠️ 偵測到報表缺少以下指標，請重新導出：{', '.join(missing_cols)}")

    # --- 數據清洗 ---
    def clean_val(val):
        try:
            if pd.isna(val) or str(val).strip() in ["", "None"]: return 0.0
            return float(str(val).replace('%', '').replace(',', '').strip())
        except: return 0.0

    for k, col_name in c.items():
        if col_name and k not in ['camp', 'ad']:
            df[col_name] = df[col_name].apply(clean_val)

    # --- 表格顯示 ---
    if c["camp"]:
        # 建立顯示用的 DataFrame
        table_df = df.copy()
        
        # 重新命名以便閱讀
        display_map = {
            c["ad"]: "廣告名稱",
            c["spend"]: "花費",
            c["hook"]: "鉤子率(3s)%",
            c["v25"]: "影片25%",
            c["ctr"]: "CTR%",
            c["pur"]: "購買數",
            c["roas"]: "ROAS"
        }
        
        show_cols = [v for v in display_map.values() if v is not None]
        final_df = table_df.rename(columns={v: k for k, v in display_map.items() if v})[show_cols]

        # 格式化顯示
        fmt = {"花費": "${:,.0f}", "鉤子率(3s)%": "{:.2f}%", "CTR%": "{:.2f}%", "ROAS": "{:.2f}"}
        st.dataframe(final_df.style.format(fmt, na_rep='-'), use_container_width=True)

else:
    st.info("💡 您的目前報表欄位僅有：觸及、曝光、點擊、花費。請重新從 Meta 匯出包含『影片比率』與『ROAS』的報表。")
