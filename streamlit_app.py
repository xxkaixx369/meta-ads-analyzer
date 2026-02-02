import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meta 全指標漏斗診斷", layout="wide")

st.title("🎯 Meta 廣告全指標漏斗診斷看板")
st.write("表格已更新為**全漏斗模式**，包含從曝光到轉換的所有核心數據。")

uploaded_file = st.file_uploader("請上傳 Meta 原始報表 (CSV)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='big5')

    # --- 1. 自動欄位偵測 (對準您的原始清單) ---
    def find_col(keys):
        for col in df.columns:
            clean_col = str(col).replace(" ", "").replace("　", "")
            if any(k in clean_col for k in keys): return col
        return None

    # 定義所有您需要的指標
    cols_map = {
        "camp": find_col(['行銷活動名稱']),
        "adset": find_col(['廣告組合名稱']),
        "ad": find_col(['廣告名稱']),
        "spend": find_col(['花費金額']),
        "impr": find_col(['曝光次數']),
        "cpc": find_col(['CPC(單次連結點擊成本)']),
        "ctr": find_col(['CTR(全部)']),
        "atc": find_col(['加到購物車次數']),
        "init_check": find_col(['開始結帳次數']),
        "pur": find_col(['購買次數']),
        "roas": find_col(['購買ROAS']),
        "hook": find_col(['影片播放3秒以上的比率']),
        "thru": find_col(['ThruPlay次數'])
    }

    # --- 2. 數據清洗 ---
    def clean_val(val):
        try:
            if pd.isna(val) or str(val).strip() in ["", "None", "0"]: return 0.0
            return float(str(val).replace('%', '').replace(',', '').strip())
        except: return 0.0

    # 排除名稱類欄位，將指標類全部轉為數字
    numeric_keys = ["spend", "impr", "cpc", "ctr", "atc", "init_check", "pur", "roas", "hook", "thru"]
    for k in numeric_keys:
        col_name = cols_map[k]
        if col_name: df[col_name] = df[col_name].apply(clean_val)

    if cols_map["camp"]:
        # --- 3. 診斷建議邏輯 (多維度判斷) ---
        def get_detailed_advice(row):
            s = row.get(cols_map["spend"], 0)
            h = row.get(cols_map["hook"], 0)
            c = row.get(cols_map["ctr"], 0)
            p = row.get(cols_map["pur"], 0)
            r = row.get(cols_map["roas"], 0)
            
            if s == 0: return "⚪️ 暫無消耗"
            if r >= 3.0: return "🔥 獲利強勁：立即加碼"
            if p > 0 and r < 1.5: return "💸 有訂單但虧損：需降成本"
            if p == 0 and s > 500: return "❌ 轉換斷層：檢查落地頁"
            if c < 0.8: return "⚠️ 連結太冷：建議改圖文"
            if h < 20: return "🪝 鉤子不響：改影片前3秒"
            return "✅ 表現穩定"

        # --- 4. 階層式顯示 ---
        camps = df[cols_map["camp"]].unique()
        for camp in camps:
            camp_df = df[df[cols_map["camp"]] == camp]
            camp_spend = camp_df[cols_map["spend"]].sum()
            
            with st.expander(f"📌 行銷活動：{camp} | 總花費: ${camp_spend:,.0f}"):
                if cols_map["adset"]:
                    adsets = camp_df[cols_map["adset"]].unique()
                    for adset in adsets:
                        adset_df = camp_df[camp_df[cols_map["adset"]] == adset]
                        st.markdown(f"**📂 廣告組合：{adset}**")
                        
                        # 整理最終顯示表格
                        final_df = adset_df.copy()
                        final_df['AI 診斷建議'] = final_df.apply(get_detailed_advice, axis=1)
                        
                        # 設定表格欄位名稱對照表 (User Friendly)
                        display_rename = {
                            cols_map["ad"]: "廣告名稱",
                            cols_map["spend"]: "花費",
                            cols_map["hook"]: "吸睛率%",
                            cols_map["ctr"]: "CTR%",
                            cols_map["cpc"]: "CPC",
                            cols_map["atc"]: "購物車",
                            cols_map["pur"]: "購買",
                            cols_map["roas"]: "ROAS",
                            'AI 診斷建議': "AI 診斷建議"
                        }
                        
                        # 過濾並重新命名
                        cols_to_use = [c for c in display_rename.keys() if c and c in final_df.columns]
                        table_to_show = final_df[cols_to_use].rename(columns=display_rename)
                        
                        # 數據格式美化 (加上 %, $)
                        if "吸睛率%" in table_to_show.columns:
                            table_to_show["吸睛率%"] = table_to_show["吸睛率%"].map("{:.1f}%".format)
                        if "CTR%" in table_to_show.columns:
                            table_to_show["CTR%"] = table_to_show["CTR%"].map("{:.2f}%".format)
                        if "ROAS" in table_to_show.columns:
                            table_to_show["ROAS"] = table_to_show["ROAS"].map("{:.2f}".format)

                        st.dataframe(table_to_show, use_container_width=True, hide_index=True)
                else:
                    st.warning("請在 Meta 匯出報表時包含『廣告組合』與『廣告名稱』。")
    else:
        st.error("無法辨識『行銷活動名稱』，請確認 CSV 檔案。")
else:
    st.info("👋 請上傳 CSV 報表。建議匯出包含：行銷活動、廣告組合、廣告、購買、ATC 等指標。")
