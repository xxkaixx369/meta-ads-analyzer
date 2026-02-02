import streamlit as st
import pandas as pd

st.set_page_config(page_title="Meta 廣告全指標大表", layout="wide")

st.title("📑 Meta 廣告全漏斗數據診斷大表")
st.write("表格支援橫向捲動，涵蓋了認知(影片留存)、流量(點擊)、轉換(業績)的所有核心指標。")

uploaded_file = st.file_uploader("請上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    # --- 1. 自動欄位比對 (精準對應您的報表欄位) ---
    def find_col(keys):
        for col in df.columns:
            clean_col = str(col).replace(" ", "").replace("　", "")
            if any(k in clean_col for k in keys): return col
        return None

    c = {
        "camp": find_col(['行銷活動名稱']),
        "adset": find_col(['廣告組合名稱']),
        "ad": find_col(['廣告名稱']),
        "spend": find_col(['花費金額']),
        "hook": find_col(['影片播放3秒以上的比率']),
        "v25": find_col(['影片播放到25%的次數']),
        "v50": find_col(['影片播放到50%的次_']), # 處理可能的斷字
        "v75": find_col(['影片播放到75%的次_']),
        "ctr": find_col(['CTR(全部)']),
        "cpc": find_col(['CPC(單次連結點擊成本)']),
        "pur": find_col(['購買次數']),
        "pur_rate": find_col(['購買比率']), # 購買比率 (每次連結點擊)
        "roas": find_col(['購買ROAS']),
        "val": find_col(['購買轉換值'])
    }

    # --- 2. 數據清洗 ---
    def clean_val(val):
        try:
            if pd.isna(val) or str(val).strip() in ["", "None"]: return 0.0
            return float(str(val).replace('%', '').replace(',', '').strip())
        except: return 0.0

    for k, col_name in c.items():
        if col_name and k not in ["camp", "adset", "ad"]:
            df[col_name] = df[col_name].apply(clean_val)

    if c["camp"]:
        # --- 3. 階層展開 ---
        for camp in df[c["camp"]].unique():
            camp_df = df[df[c["camp"]] == camp]
            with st.expander(f"📌 行銷活動：{camp} (總花費: ${camp_df[c['spend']].sum():,.0f})"):
                
                if c["adset"]:
                    for adset in camp_df[c["adset"]].unique():
                        adset_df = camp_df[camp_df[c["adset"]] == adset].copy()
                        st.markdown(f"**📂 廣告組合：{adset}**")
                        
                        # --- 4. 建立全指標大表格 ---
                        # 定義顯示名稱對照
                        display_map = {
                            c["ad"]: "廣告名稱",
                            c["spend"]: "花費",
                            # 認知指標
                            c["hook"]: "吸睛率(3s)%",
                            c["v25"]: "25%觀看",
                            c["v50"]: "50%觀看",
                            c["v75"]: "75%觀看",
                            # 流量指標
                            c["ctr"]: "CTR%",
                            c["cpc"]: "CPC",
                            # 轉換指標
                            c["pur"]: "購買",
                            c["pur_rate"]: "購買率%",
                            c["val"]: "轉換值",
                            c["roas"]: "ROAS"
                        }

                        # 只選取報表中有的欄位
                        valid_cols = [col for col in display_map.keys() if col and col in adset_df.columns]
                        table_df = adset_df[valid_cols].rename(columns=display_map)

                        # --- 5. 格式化處理 (美化數據) ---
                        format_dict = {}
                        if "吸睛率(3s)%" in table_df.columns: format_dict["吸睛率(3s)%"] = "{:.2f}%"
                        if "CTR%" in table_df.columns: format_dict["CTR%"] = "{:.2f}%"
                        if "購買率%" in table_df.columns: format_dict["購買率%"] = "{:.2f}%"
                        if "ROAS" in table_df.columns: format_dict["ROAS"] = "{:.2f}"
                        if "花費" in table_df.columns: format_dict["花費"] = "${:,.0f}"
                        if "轉換值" in table_df.columns: format_dict["轉換值"] = "${:,.0f}"
                        if "CPC" in table_df.columns: format_dict["CPC"] = "${:.2f}"
                        
                        # 顯示大表格 (設定高度避免過長)
                        st.dataframe(
                            table_df.style.format(format_dict),
                            use_container_width=True,
                            hide_index=True
                        )
    else:
        st.error("找不到欄位，請確認 CSV 內容。")
else:
    st.info("請上傳 CSV 報表開始分析。")
