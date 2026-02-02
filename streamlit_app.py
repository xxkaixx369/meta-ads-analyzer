import streamlit as st
import pandas as pd

st.set_page_config(page_title="Meta 廣告智慧診斷大表", layout="wide")
st.title("🎯 Meta 廣告全鏈路智慧診斷看板")

uploaded_file = st.file_uploader("請上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    def find_col(keys):
        for col in df.columns:
            clean_col = str(col).strip()
            if any(k in clean_col for k in keys): return col
        return None

    c = {
        "camp": find_col(['行銷活動名稱']),
        "adset": find_col(['廣告組合名稱']),
        "ad": find_col(['廣告名稱']),
        "spend": find_col(['花費金額']),
        "hook": find_col(['影片播放3秒以上的比率']), 
        "v25": find_col(['影片播放到 25%']),
        "v50": find_col(['影片播放到 50%']),
        "v75": find_col(['影片播放到 75%']),
        "ctr": find_col(['CTR（連結點閱率）']),
        "cpc": find_col(['CPC（單次連結點擊成本）']),
        "pur": find_col(['購買次數']),
        "roas": find_col(['購買 ROAS', '購買ROAS']),
        "val": find_col(['購買轉換值'])
    }

    def clean_num(val):
        try:
            if pd.isna(val) or str(val).strip() in ["", "None", "nan"]: return 0.0
            return float(str(val).replace('%', '').replace(',', '').strip())
        except: return 0.0

    numeric_keys = ["spend", "hook", "v25", "v50", "v75", "ctr", "cpc", "pur", "roas", "val"]
    for k in numeric_keys:
        if c[k]: df[c[k]] = df[c[k]].apply(clean_num)

    # 鉤子率小數轉百分比格式
    if c["hook"] and df[c["hook"]].max() <= 1.0:
        df[c["hook"]] = df[c["hook"]] * 100

    if c["camp"]:
        for camp in df[c["camp"]].unique():
            camp_df = df[df[c["camp"]] == camp]
            with st.expander(f"📌 行銷活動：{camp} (總花費: ${camp_df[c['spend']].sum():,.0f})"):
                for adset in camp_df[c["adset"]].unique():
                    adset_df = camp_df[camp_df[c["adset"]] == adset].copy()
                    
                    display_map = {
                        c["ad"]: "廣告名稱", c["spend"]: "花費", c["hook"]: "鉤子率%",
                        c["v25"]: "影片25%", c["v50"]: "影片50%", c["v75"]: "影片75%",
                        c["ctr"]: "CTR%", c["cpc"]: "CPC", c["pur"]: "購買", c["roas"]: "ROAS"
                    }
                    
                    valid_cols = [col for col in display_map.keys() if col]
                    table_df = adset_df[valid_cols].rename(columns=display_map)

                    # --- 核心智慧診斷函數 ---
                    def get_smart_advice(row):
                        h = row.get("鉤子率%", 0)
                        v25 = row.get("影片25%", 0)
                        v50 = row.get("影片50%", 0)
                        ctr = row.get("CTR%", 0)
                        roas = row.get("ROAS", 0)
                        
                        advices = []
                        # 1. ROAS 優先判斷
                        if roas >= 2.5: return "🚀 獲利黑馬：直接加預算"
                        
                        # 2. 漏斗分段診斷
                        if h < 20: 
                            advices.append("🪝 鉤子太爛(改前3秒)")
                        elif h > 35 and ctr < 1.0:
                            advices.append("🖱️ 導流弱(改文案/按鈕)")
                            
                        if v25 > 0 and (v50 / v25) < 0.5:
                            advices.append("📉 中段流失(縮短影片)")
                            
                        if ctr > 1.5 and roas < 1.2:
                            advices.append("🛒 轉換阻力(查官網/優惠)")

                        return " | ".join(advices) if advices else "✅ 表現穩定"

                    table_df['AI 複合建議'] = table_df.apply(get_smart_advice, axis=1)

                    fmt = {
                        "花費": "${:,.0f}", "鉤子率%": "{:.1f}%", "CTR%": "{:.2f}%",
                        "ROAS": "{:.2f}", "CPC": "${:.2f}"
                    }
                    st.dataframe(table_df.style.format(fmt), use_container_width=True, hide_index=True)
