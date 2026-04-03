import streamlit as st
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# ================= 1. 網頁基礎設定 =================
st.set_page_config(page_title="捷出青年班 AI 競賽區", page_icon="🏆", layout="wide")

# 初始化 Session State (儲存登入狀態)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# 建立試算表連線
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    """讀取資料庫並強制轉換為字串格式，解決 0 開頭密碼問題"""
    try:
        df = conn.read(ttl=0)
        # 強制轉文字並處理掉 .0 的問題
        df = df.astype(str).replace(r'\.0$', '', regex=True)
        return df
    except Exception as e:
        st.error(f"資料庫讀取失敗：{e}")
        return pd.DataFrame(columns=["username", "password", "display_name", "exp"])

# ================= 2. 登入與註冊介面 =================
if not st.session_state.logged_in:
    st.title("🛡️ 捷出青年班實戰系統")
    st.subheader("請登入以開始 AI 訓練挑戰")
    
    tab1, tab2 = st.tabs(["🔑 帳號登入", "📝 新隊員註冊"])
    db_df = get_db()

    with tab1:
        login_user = st.text_input("帳號 (ID)", key="l_user")
        login_pw = st.text_input("密碼", type="password", key="l_pw")
        if st.button("進入道館", key="login_btn"):
            u_input = str(login_user).strip()
            p_input = str(login_pw).strip()
            
            # 比對資料
            match = db_df[(db_df['username'].str.strip() == u_input) & 
                          (db_df['password'].str.strip() == p_input)]
            
            if not match.empty:
                st.session_state.logged_in = True
                user_info = match.iloc[0].to_dict()
                try:
                    user_info['exp'] = int(float(user_info.get('exp', 0)))
                except:
                    user_info['exp'] = 0
                st.session_state.user_data = user_info
                st.success(f"🎊 歡迎回來，{user_info['display_name']} 教官！")
                st.rerun()
            else:
                st.error("❌ 帳號或密碼錯誤。")

    with tab2:
        st.write("填寫資訊建立戰士檔案：")
        reg_user = st.text_input("設定帳號 (建議用手機)", key="r_user")
        reg_pw = st.text_input("設定密碼", type="password", key="r_pw")
        reg_name = st.text_input("您的暱稱", key="r_name")
        
        # 修正語法錯誤的關鍵行
        if st.button("完成註冊", key="reg_btn"):
            u_reg = str(reg_user).strip()
            if not reg_user or not reg_pw or not reg_name:
                st.warning("請填寫所有欄位！")
            elif u_reg in db_df['username'].astype(str).values:
                st.error("此帳號已被註冊。")
            else:
                new_row = pd.DataFrame([{
                    "username": u_reg,
                    "password": str(reg_pw).strip(),
                    "display_name": str(reg_name).strip(),
                    "exp": "0"
                }])
                updated_df = pd.concat([db_df, new_row], ignore_index=True)
                conn.update(data=updated_df)
                st.success("🎉 註冊成功！請切換到登入頁面。")
    st.stop()

# ================= 3. 題庫與側邊欄 (登入後) =================
levels = {
    "1. 開門：沒興趣": {"objection": "我對保險沒興趣。", "hint": "提示：運用「滅火器」或「晚年生活」切入需求。", "logic": "1.目標轉移 2.生活類比 3.時間差"},
    "2. 拒絕：不需要": {"objection": "我有健保就夠了，我不需要保險。", "hint": "提示：運用「鎖門」比喻或「DRGs 制度」。", "logic": "1.鎖門比喻 2.DRGs 現狀 3.國民便當"},
    "3. 預算：沒有錢": {"objection": "我現在開銷很高，真的沒有錢。", "hint": "提示：強調「沒錢才更需要保險」。", "logic": "1.因果論 2.防護網 3.支出微調"},
    "4. 逃避：我很忙": {"objection": "我很忙，你資料寄給我就好。", "hint": "提示：肯定忙碌，強調專業代勞。", "logic": "1.專業代勞 2.面談分析"},
    "5. 系統：已有保險": {"objection": "爸媽幫我買好了。", "hint": "提示：運用「滅火器定期檢視」。", "logic": "1.壓力表檢查 2.獨立負責 3.長期服務"},
    "6. 投資：做投資好": {"objection": "我自己做投資比保險好。", "hint": "提示：強調「投資需要時間」。", "logic": "1.時間複利 2.資產保全"},
    "7. 比較：想跟別家比": {"objection": "我想跟別家比較價錢。", "hint": "提示：強調南山理賠品質。", "logic": "1.理賠糾紛率低 2.品牌價值"},
    "8. 拖延：晚一點再買": {"objection": "我現在不想決定，晚一點再買。", "hint": "提示：詢問要買便宜還是貴的？", "logic": "1.年紀成本 2.健康狀況不可逆"}
}

with st.sidebar:
    if st.session_state.user_data:
        st.title(f"👤 {st.session_state.user_data['display_name']}")
        st.metric("🏆 累積實戰 EXP", st.session_state.user_data['exp'])
    
    if st.button("登出系統"):
        st.session_state.logged_in = False
        st.session_state.user_data = None
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.subheader("📊 英雄榜")
    try:
        current_db = get_db()
        current_db['exp'] = pd.to_numeric(current_db['exp'], errors='coerce').fillna(0)
        leaderboard = current_db.sort_values(by="exp", ascending=False).head(5)
        st.table(leaderboard[["display_name", "exp"]])
    except:
        st.write("暫無排名數據")
    
    st.divider()
    selected_level = st.selectbox("選擇挑戰關卡：", list(levels.keys()))
    if st.button("重新開始本關"):
        st.session_state.messages = []
        st.rerun()

# ================= 4. 主畫面挑戰區 =================
st.title(f"⚔️ {selected_level}")
curr = levels[selected_level]
st.info(f"**👨‍💼 客戶說：** 「{curr['objection']}」")
st.caption(f"💡 {curr['hint']}")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("請輸入你的實戰話術..."):
    try:
        # 1. 配置 AI
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # 2. 自動尋找目前可用的 Flash 模型 (這招最穩！)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # 優先找包含 'flash' 的模型，找不到就用第一個
        target_model = next((m for m in available_models if 'flash' in m), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        # 3. 顯示玩家話術
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 這裡使用三引號確保 Prompt 格式正確不噴錯
        prompt = f"""
        你現在是南山人壽「捷出青年班」的首席實戰教練。
        學員：{st.session_state.user_data['display_name']}
        目前反對問題：{curr['objection']}
        學員話術：{user_input}
        
        請根據教材邏輯：{curr['logic']}
        給予：1. 辨識邏輯 2. 教練評分(1-100) 3. 實戰講評。
        """

        with st.chat_message("assistant"):
            with st.spinner("教練評分中..."):
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
                # 實戰點數更新
           # --- 1. 從 AI 回覆中精準抓取分數 ---
                import re
                # 尋找回覆中的數字 (例如：78)
                scores = re.findall(r'\d+', response.text)
                # 如果有找到數字，取第一個當作得分；沒找到就保底給 60 分
                earned_exp = int(scores[0]) if scores else 60
                
                # 限定分數區間在 0-100 之間，避免 AI 亂給分
                earned_exp = max(0, min(100, earned_exp))

                # --- 2. 更新 Session 狀態 (讓網頁即時跳動) ---
                st.session_state.user_data['exp'] += earned_exp
                
                # --- 3. 同步回傳 Google 試算表 ---
                all_db = get_db()
                u_id = str(st.session_state.user_data['username'])
                # 確保存進去的是加總後的總分
                all_db.loc[all_db['username'].astype(str) == u_id, 'exp'] = str(st.session_state.user_data['exp'])
                conn.update(data=all_db)
                
                # --- 4. 顯示獲勝訊息並噴氣球 ---
                st.success(f"🎯 本次實戰表現：{earned_exp} 分！經驗值已累加。")
                st.balloons()
                
                # 強制畫面重整，讓側邊欄的分數立刻變動
                st.rerun()
    except Exception as e:
        st.error(f"系統異常：{e}")
