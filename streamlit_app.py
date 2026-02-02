import streamlit as st
import pandas as pd

st.set_page_config(page_title="Meta 廣告數據診斷", layout="wide")
st.title("🎯 Meta 廣告智慧診斷（ROAS > 2 基準）")

uploaded_file = st.file_uploader("請上傳最新的 CSV 報表", type="csv")

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
        "pur": find_col(['購買次數']),
        "roas": find_col(['購買 ROAS', '購買ROAS'])
    }

    def clean_num(val):
        try:
            if pd.isna(val) or str(val).strip() in ["", "None", "nan"]: return 0.0
            return float(str(val).replace('%', '').replace(',', '').strip())
        except: return 0.0

    numeric_keys = ["spend", "hook", "v25", "v50", "v75", "ctr", "pur", "roas"]
    for k in numeric_keys:
        if c[k]: df[c[k]] = df[c[k]].apply(clean_num)

    # 鉤子率轉換
    if c["hook"] and df[c["hook"]].max() <= 1.0:
        df[c["hook"]] = df[c["hook"]] * 100

    if c["camp"]:
        for camp in df[c["camp"]].unique():
            camp_df = df[df[c["camp"]] == camp]
            with st.expander(f"📌 行銷活動：{camp}"):
                for adset in camp_df[c["adset"]].unique():
                    adset_df = camp_df[camp_df[c["adset"]] == adset].copy()
                    
                    # --- 核心邏輯：三大注記 ---
                    def get_comprehensive_advice(row):
                        h = row.get(c["hook"], 0)
                        v25 = row.get(c["v25"], 0)
                        v50 = row.get(c["v50"], 0)
                        v75 = row.get(c["v75"], 0)
                        roas = row.get(c["roas"], 0)
                        
                        # 1. 獲利程度 (ROAS > 2 基準)
                        if roas >= 3.5: profit_status = "💰 高額獲利(加碼)"
                        elif roas >= 2.0: profit_status = "✅ 表現穩定"
                        elif roas > 0: profit_status = "⚠️ 虧損風險"
                        else: profit_status = "❌ 尚無轉換"
                        
                        # 2. 鉤子率 (吸睛度)
                        if h >= 35: hook_status = "🪝 鉤子極強"
                        elif h >= 20: hook_status = "🪝 鉤子正常"
                        else: hook_status = "🪝 鉤子太弱"
                        
                        # 3. 留存流失 (影片漏斗)
                        # 判斷哪一階層掉最多
                        retention = "🎬 留存良好"
                        if v25 > 0:
                            drop_25_50 = v50 / v25
                            drop_50_75 = v75 / v50 if v50 > 0 else 0
                            
                            if drop_25_50 < 0.4: retention = "📉 前段流失嚴重"
                            elif drop_50_75 < 0.4: retention = "📉 中後段乏味"
                        
                        return f"{profit_status} / {hook_status} / {retention}"

                    adset_df['AI 綜合診斷報告'] = adset_df.apply(get_comprehensive_advice, axis=1)

                    # 整理表格顯示
                    display_map = {
                        c["ad"]: "廣告名稱", c["spend"]: "花費", c["hook"]: "鉤子率%",
                        c["v25"]: "25%觀看", c["v50"]: "50%觀看", c["v75"]: "75%觀看",
                        c["roas"]: "ROAS", 'AI 綜合診斷報告': "AI 綜合診斷報告"
                    }
                    
                    final_table = adset_df[list(display_map.keys())].rename(columns=display_map)
                    
                    fmt = {"花費": "${:,.0f}", "鉤子率%": "{:.1f}%", "ROAS": "{:.2f}"}
                    st.dataframe(final_table.style.format(fmt), use_container_width=True, hide_index=True)
else:
    st.info("請上傳最新 CSV 報表進行診斷。")
