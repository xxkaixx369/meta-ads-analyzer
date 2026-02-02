import streamlit as st
import pandas as pd

st.set_page_config(page_title="Meta 全漏斗診斷看板", layout="wide")

st.title("📊 Meta 廣告全漏斗關鍵指標看板")
st.write("表格涵蓋認知(影片留存)、流量(點擊成本)與購買(轉換獲利)指標。")

uploaded_file = st.file_uploader("請上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    # --- 1. 自動辨識與精準對應欄位 (根據您提供的 12.01.33 清單) ---
    def find_col(keys):
        for col in df.columns:
            clean_col = str(col).replace(" ", "").replace("　", "")
            if any(k in clean_col for k in keys): return col
        return None

    # 定義指標對照表
    c = {
        "camp": find_col(['行銷活動名稱']),
        "adset": find_col(['廣告組合名稱']),
        "ad": find_col(['廣告名稱']),
        "spend": find_col(['花費金額']),
        "hook": find_col(['影片播放3秒以上的比率']), # 認知指標
        "v25": find_col(['影片播放到25%']),
        "v50": find_col(['影片播放到50%']),
        "v75": find_col(['影片播放到75%']),
        "ctr": find_col(['CTR(全部)', 'CTR(連結點閱率)']), # 流量指標
        "cpc": find_col(['CPC(單次連結點擊成本)']),
        "pur": find_col(['購買次數']), # 購買指標
        "pur_rate": find_col(['購買比率']),
        "val": find_col(['購買轉換值']),
        "roas": find_col(['購買ROAS'])
    }

    # --- 2. 數據清洗與數字轉換 ---
    def clean_num(val):
        try:
            if pd.isna(val) or str(val).strip() in ["", "None", "nan"]: return 0.0
            return float(str(val).replace('%', '').replace(',', '').strip())
        except: return 0.0

    numeric_keys = ["spend", "hook", "v25", "v50", "v75", "ctr", "cpc", "pur", "pur_rate", "val", "roas"]
    for k in numeric_keys:
        if c[k]: df[c[k]] = df[c[k]].apply(clean_num)

    if c["camp"]:
        # --- 3. 展開階層式表格 ---
        for camp in df[c["camp"]].unique():
            camp_df = df[df[c["camp"]] == camp]
            with st.expander(f"📌 行銷活動：{camp} (總花費: ${camp_df[c['spend']].sum():,.0f})"):
                
                if c["adset"]:
                    for adset in camp_df[c["adset"]].unique():
                        adset_df = camp_df[camp_df[c["adset"]] == adset].copy()
                        st.markdown(f"**📂 廣告組合：{adset}**")

                        # 準備大表格數據
                        display_map = {
                            c["ad"]: "廣告名稱",
                            c["spend"]: "花費",
                            c["hook"]: "鉤子率%",
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
                        
                        # 過濾掉沒抓到的欄位並更名
                        valid_cols = [col for col in display_map.keys() if col and col in adset_df.columns]
                        table_df = adset_df[valid_cols].rename(columns=display_map)

                        # --- 4. 條件診斷建議 (讓「表現穩定」更靈敏) ---
                        def get_diagnosis(row):
                            # 將各欄位轉回數值進行判斷
                            h = row.get("鉤子率%", 0)
                            ctr = row.get("CTR%", 0)
                            roas = row.get("ROAS", 0)
                            
                            if roas >= 2.5: return "🔥 優異:建議加預算"
                            if h < 20 and h > 0: return "🪝 認知弱:改影片前3秒"
                            if ctr < 0.8 and ctr > 0: return "🖱️ 流量弱:改廣告文案"
                            if roas < 1.0 and roas > 0: return "💸 轉換弱:檢查落地頁"
                            return "✅ 表現穩定"

                        table_df['AI 診斷'] = table_df.apply(get_diagnosis, axis=1)

                        # --- 5. 格式化顯示 (美化百分比與金額) ---
                        fmt = {}
                        if "花費" in table_df.columns: fmt["花費"] = "${:,.0f}"
                        if "鉤子率%" in table_df.columns: fmt["鉤子率%"] = "{:.1f}%"
                        if "CTR%" in table_df.columns: fmt["CTR%"] = "{:.2f}%"
                        if "購買率%" in table_df.columns: fmt["購買率%"] = "{:.2f}%"
                        if "ROAS" in table_df.columns: fmt["ROAS"] = "{:.2f}"
                        if "轉換值" in table_df.columns: fmt["轉換值"] = "${:,.0f}"

                        # 顯示完整表格 (不限制行數)
                        st.dataframe(
                            table_df.style.format(fmt),
                            use_container_width=True,
                            hide_index=True
                        )
    else:
        st.error("欄位解析失敗，請確認上傳的是 Meta 原始 CSV 報表。")
else:
    st.info("👋 歡迎！請上傳 CSV 報表。目前設定會自動抓取您報表中的認知、流量與轉換指標。")
