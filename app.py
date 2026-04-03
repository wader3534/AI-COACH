import streamlit as st
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re

# ================= 1. 網頁基礎設定 =================
st.set_page_config(page_title="捷出青年班 AI 競賽區", page_icon="🏆", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "messages" not in st.session_state:
    st.session_state.messages = []

conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    try:
        df = conn.read(ttl=0)
        df = df.astype(str).replace(r'\.0$', '', regex=True)
        return df
    except Exception as e:
        st.error(f"資料庫連線失敗：{e}")
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
            match = db_df[(db_df['username'].str.strip() == u_input) & 
                          (db_df['password'].str.strip() == p_input)]
            if not match.empty:
                st.session_state.logged_in = True
                user_info = match.iloc[0].to_dict()
                user_info['exp'] = int(float(user_info.get('exp', 0)))
                st.session_state.user_data = user_info
                st.success(f"🎊 歡迎回來，{user_info['display_name']}！")
                st.rerun()
            else:
                st.error("❌ 帳號或密碼錯誤。")

    with tab2:
        st.write("填寫資訊建立戰士檔案：")
        reg_user = st.text_input("設定帳號", key="r_user")
        reg_pw = st.text_input("設定密碼", type="password", key="r_pw")
        reg_name = st.text_input("您的暱稱", key="r_name")
        if st.button("完成註冊", key="reg_btn"):
            u_reg = str(reg_user).strip()
            if not reg_user or not reg_pw or not reg_name:
                st.warning("請填寫所有欄位！")
            elif u_reg in db_df['username'].astype(str).values:
                st.error("此帳號已被註冊。")
            else:
                new_row = pd.DataFrame([{"username": u_reg, "password": str(reg_pw).strip(), 
                                        "display_name": str(reg_name).strip(), "exp": "0"}])
                conn.update(data=pd.concat([db_df, new_row], ignore_index=True))
                st.success("🎉 註冊成功！請切換到登入分頁。")
    st.stop()

# ================= 3. 題庫與側邊欄 =================
levels = {
    "1. 開門：沒興趣": {"objection": "我對保險沒興趣。", "hint": "提示：運用「滅火器」切入需求。", "logic": "1.目標轉移 2.生活類比 3.時間差"},
    "2. 拒絕：不需要": {"objection": "我有健保就夠了，不需要保險。", "hint": "提示：運用「鎖門」比喻。", "logic": "1.鎖門比喻 2.DRGs 現狀"},
    "3. 預算：沒有錢": {"objection": "我現在開銷很高，沒錢。", "hint": "提示：沒錢才更需要保險。", "logic": "1.因果論 2.防護網"},
    "4. 逃避：我很忙": {"objection": "我很忙，資料寄給我就好。", "hint": "提示：肯定忙碌，專業代勞。", "logic": "1.專業代勞 2.面談分析"},
    "5. 系統：已有保險": {"objection": "爸媽幫我買好了。", "hint": "提示：運用「滅火器定期檢視」。", "logic": "1.壓力表檢查 2.獨立負責"},
    "6. 投資：做投資好": {"objection": "我自己做投資比較好。", "hint": "提示：強調「投資需要時間」。", "logic": "1.時間複利 2.資產保全"},
    "7. 比較：想跟別家比": {"objection": "我想跟別家比較價錢。", "hint": "提示：強調南山理賠品質。", "logic": "1.糾紛率低 2.品牌價值"},
    "8. 拖延：晚點再買": {"objection": "我現在不想決定。", "hint": "提示：詢問要買便宜還是貴的？", "logic": "1.年紀成本 2.健康不可逆"}
}

with st.sidebar:
    st.title(f"👤 {st.session_state.user_data['display_name']}")
    st.metric("🏆 累積實戰 EXP", st.session_state.user_data['exp'])
    if st.button("登出系統"):
        st.session_state.logged_in = False
        st.rerun()
    st.divider()
    st.subheader("📊 英雄榜")
    try:
        lb_df = get_db()
        lb_df['exp'] = pd.to_numeric(lb_df['exp'], errors='coerce').fillna(0)
        st.table(lb_df.sort_values(by="exp", ascending=False).head(5)[["display_name", "exp"]])
    except:
        st.write("暫無排名")
    st.divider()
    selected_level = st.selectbox("選擇挑戰關卡：", list(levels.keys()))

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
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # --- 教官建議的萬用兼容大法 (加強版) ---
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target_model = next((m for m in available_models if 'flash' in m), 'gemini-1.5-flash')
        except:
            # 萬一連 list_models 都失敗，直接用最穩定的名稱
            target_model = 'gemini-1.5-flash'
            
        model = genai.GenerativeModel(target_model)
        
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        prompt = f"你是南山人壽教練。學員針對「{curr['objection']}」回答「{user_input}」。根據「{curr['logic']}」評分。務必包含『評分：XX』字樣。"

        with st.chat_message("assistant"):
            with st.spinner("教練評分中..."):
                response = model.generate_content(prompt)
                res_text = response.text
                st.markdown(res_text)
                st.session_state.messages.append({"role": "assistant", "content": res_text})
                
                # 抓取分數
                score_match = re.search(r'評分[:：\s]*(\d+)', res_text)
                earned_exp = int(score_match.group(1)) if score_match else 60
                
                # 顯示大字體評分
                st.markdown(f"""
                    <div style="text-align: center; border: 3px solid #FFA500; padding: 20px; border-radius: 15px; background-color: #FFF5E6;">
                        <h1 style="font-size: 80px; color: #FF4B4B; margin: 0;">{earned_exp} <span style="font-size: 24px;">分</span></h1>
                    </div>
                """, unsafe_allow_html=True)

                # 更新分數並存檔
                st.session_state.user_data['exp'] += earned_exp
                all_db = get_db()
                all_db.loc[all_db['username'].astype(str) == str(st.session_state.user_data['username']), 'exp'] = str(st.session_state.user_data['exp'])
                conn.update(data=all_db)
                if earned_exp >= 80: st.balloons()
                st.button("確認成績並更新排行榜", on_click=lambda: st.rerun())

    except Exception as e:
        st.error(f"系統連線異常：{e}")
