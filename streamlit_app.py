import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meta 廣告關鍵指標診斷", layout="wide")

st.title("🎯 Meta 廣告全路徑關鍵指標看板")
st.write("此表格集結了行銷漏斗的核心數據，幫助您精確判斷廣告問題點。")

uploaded_file = st.file_uploader("請上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    # --- 1. 精準對應關鍵欄位 ---
    def find_col(keys):
        for col in df.columns:
            clean_col = str(col).replace(" ", "").replace("　", "")
            if any(k in clean_col for k in keys): return col
        return None

    # 定義關鍵指標對照
    c_map = {
        "camp": find_col(['行銷活動名稱']),
        "adset": find_col(['廣告組合名稱']),
        "ad": find_col(['廣告名稱']),
        "spend": find_col(['花費金額']),
        "impr": find_col(['曝光次數']),
        "ctr": find_col(['CTR(全部)']),
        "cpc": find_col(['CPC(單次連結點擊成本)']),
        "hook": find_col(['影片播放3秒以上的比率']),
        "pur": find_col(['購買次數']),
        "roas": find_col(['購買ROAS']),
        "atc": find_col(['加到購物車次數'])
    }

    # --- 2. 數據深度清洗 ---
    def clean_val(val):
        try:
            if pd.isna(val) or str(val).strip() in ["", "None", "0"]: return 0.0
            return float(str(val).replace('%', '').replace(',', '').strip())
        except: return 0.0

    numeric_cols = ["spend", "impr", "ctr", "cpc", "hook", "pur", "roas", "atc"]
    for k in numeric_cols:
        col_name = c_map[k]
        if col_name: df[col_name] = df[col_name].apply(clean_val)

    if c_map["camp"]:
        # --- 3. 頂部關鍵摘要 (Summary Box) ---
        total_spend = df[c_map["spend"]].sum() if c_map["spend"] else 0
        total_pur = df[c_map["pur"]].sum() if c_map["pur"] else 0
        avg_roas = df[c_map["roas"]].mean() if c_map["roas"] else 0
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("總花費 (TWD)", f"${total_spend:,.0f}")
        c2.metric("總購買次數", f"{total_pur:,.0f}")
        c3.metric("平均 ROAS", f"{avg_roas:.2f}")
        c4.metric("CPA (單次購買成本)", f"${(total_spend/total_pur) if total_pur > 0 else 0:,.0f}")

        # --- 4. 階層式表格顯示 ---
        st.divider()
        camps = df[c_map["camp"]].unique()
        
        for camp in camps:
            camp_df = df[df[c_map["camp"]] == camp]
            with st.expander(f"📌 行銷活動：{camp}"):
                
                if c_map["adset"]:
                    for adset in camp_df[c_map["adset"]].unique():
                        adset_df = camp_df[camp_df[c_map["adset"]] == adset].copy()
                        st.markdown(f"**📂 廣告組合：{adset}**")
                        
                        # 計算單次購買成本 (CPA)
                        def calc_cpa(row):
                            s = row.get(c_map["spend"], 0)
                            p = row.get(c_map["pur"], 0)
                            return s / p if p > 0 else 0

                        adset_df['CPA'] = adset_df.apply(calc_cpa, axis=1)

                        # 選取關鍵指標並重新命名
                        table_cols = {
                            c_map["ad"]: "廣告名稱",
                            c_map["spend"]: "花費",
                            c_map["hook"]: "吸睛率%",
                            c_map["ctr"]: "點擊率%",
                            c_map["cpc"]: "CPC",
                            c_map["pur"]: "購買",
                            'CPA': "單次購買成本",
                            c_map["roas"]: "ROAS"
                        }
                        
                        actual_cols = [c for c in table_cols.keys() if c and (c in adset_df.columns or c == 'CPA')]
                        display_df = adset_df[actual_cols].rename(columns=table_cols)
                        
                        # 格式化
                        if "吸睛率%" in display_df.columns: display_df["吸睛率%"] = display_df["吸睛率%"].map("{:.1f}%".format)
                        if "點擊率%" in display_df.columns: display_df["點擊率%"] = display_df["點擊率%"].map("{:.2f}%".format)
                        if "花費" in display_df.columns: display_df["花費"] = display_df["花費"].map("${:,.0f}".format)
                        if "單次購買成本" in display_df.columns: display_df["單次購買成本"] = display_df["單次購買成本"].map("${:,.0f}".format)

                        st.dataframe(display_df, use_container_width=True, hide_index=True)

    else:
        st.error("找不到關鍵欄位，請檢查 CSV。")
else:
    st.info("請上傳 Meta 報表 CSV。")
