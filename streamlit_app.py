import streamlit as st
import pandas as pd

st.set_page_config(page_title="Meta 廣告數據診斷", layout="wide")
st.title("🎯 Meta 廣告全漏斗關鍵指標大表")

uploaded_file = st.file_uploader("請上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    # --- 1. 精準對齊欄位 ---
    def find_col(keys):
        for col in df.columns:
            clean_col = str(col).strip()
            if any(k in clean_col for k in keys):
                return col
        return None

    # 定義指標對照 (特別加強鉤子率的對應)
    c = {
        "camp": find_col(['行銷活動名稱']),
        "adset": find_col(['廣告組合名稱']),
        "ad": find_col(['廣告名稱']),
        "spend": find_col(['花費金額']),
        # 鉤子率直接對應 3秒播放比率
        "hook": find_col(['影片播放 3 秒以上的比率', '影片播放3秒以上的比率']), 
        "v25": find_col(['影片播放到 25%']),
        "v50": find_col(['影片播放到 50%']),
        "v75": find_col(['影片播放到 75%']),
        "ctr": find_col(['CTR (全部)', 'CTR（連結點閱率）']),
        "cpc": find_col(['CPC (單次連結點擊成本)', 'CPC（單次連結點擊成本）']),
        "pur": find_col(['購買次數', '成果']),
        "pur_rate": find_col(['購買比率']),
        "val": find_col(['購買轉換值']),
        "roas": find_col(['購買 ROAS', '購買ROAS'])
    }

    # --- 2. 數據清洗 ---
    def clean_num(val):
        try:
            if pd.isna(val) or str(val).strip() in ["", "None", "nan"]: return 0.0
            return float(str(val).replace('%', '').replace(',', '').strip())
        except: return 0.0

    numeric_keys = ["spend", "hook", "v25", "v50", "v75", "ctr", "cpc", "pur", "pur_rate", "val", "roas"]
    for k in numeric_keys:
        if c[k]: df[c[k]] = df[c[k]].apply(clean_num)

    if c["camp"]:
        for camp in df[c["camp"]].unique():
            camp_df = df[df[c["camp"]] == camp]
            with st.expander(f"📌 行銷活動：{camp} (總花費: ${camp_df[c['spend']].sum():,.0f})"):
                
                if c["adset"]:
                    for adset in camp_df[c["adset"]].unique():
                        adset_df = camp_df[camp_df[c["adset"]] == adset].copy()
                        st.markdown(f"**📂 廣告組合：{adset}**")

                        # 建立顯示大表格
                        display_map = {
                            c["ad"]: "廣告名稱",
                            c["spend"]: "花費",
                            c["hook"]: "鉤子率(3s)%",
                            c["v25"]: "影片25%",
                            c["v50"]: "影片50%",
                            c["v75"]: "影片75%",
                            c["ctr"]: "CTR%",
                            c["cpc"]: "CPC",
                            c["pur"]: "購買數",
                            c["pur_rate"]: "購買率%",
                            c["val"]: "轉換值",
                            c["roas"]: "ROAS"
                        }
                        
                        valid_cols = [col for col in display_map.keys() if col and col in adset_df.columns]
                        table_df = adset_df[valid_cols].rename(columns=display_map)

                        # --- 3. 診斷邏輯 ---
                        def get_diagnosis(row):
                            h = row.get("鉤子率(3s)%", 0)
                            r = row.get("ROAS", 0)
                            if r >= 2.5: return "🔥 獲利強勁"
                            if h < 20 and h > 0: return "🪝 鉤子太弱 (改開頭)"
                            if h >= 35: return "✅ 抓眼力強"
                            return "✅ 表現穩定"

                        table_df['AI 診斷'] = table_df.apply(get_diagnosis, axis=1)

                        # 格式化
                        fmt = {
                            "花費": "${:,.0f}", "鉤子率(3s)%": "{:.1f}%", "CTR%": "{:.2f}%",
                            "購買率%": "{:.2f}%", "ROAS": "{:.2f}", "轉換值": "${:,.0f}", "CPC": "${:.2f}"
                        }
                        
                        st.dataframe(table_df.style.format(fmt), use_container_width=True, hide_index=True)
    else:
        st.error("欄位匹配失敗，請確認 CSV 標題。")
else:
    st.info("請上傳 CSV 報表開始分析。")
