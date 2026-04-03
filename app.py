import streamlit as st
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re

# ================= 1. 網頁基礎設定 =================
st.set_page_config(page_title="元捷通訊處 AI 實戰道館", page_icon="🛡️", layout="wide")

# 初始化 Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# 建立試算表連線
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    """讀取資料庫並強制格式化"""
    try:
        df = conn.read(ttl=0)
        df = df.astype(str).replace(r'\.0$', '', regex=True)
        return df
    except Exception as e:
        st.error(f"資料庫讀取失敗：{e}")
        return pd.DataFrame(columns=["username", "password", "display_name", "exp"])

# ================= 2. 登入與註冊介面 =================
if not st.session_state.logged_in:
    st.title("🛡️ 元捷通訊處：捷出青年班實戰系統")
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
                try:
                    user_info['exp'] = int(float(user_info.get('exp', 0)))
                except:
                    user_info['exp'] = 0
                st.session_state.user_data = user_info
                st.success(f"🎊 歡迎回來元捷道館，{user_info['display_name']} 教官！")
                st.rerun()
            else:
                st.error("❌ 帳號或密碼錯誤。")

    with tab2:
        st.write("填寫資訊建立戰士檔案：")
        reg_user = st.text_input("設定帳號 (建議用手機)", key="r_user")
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
                st.success("🎉 註冊成功！請登入開始修練。")
    st.stop()

# ================= 3. 題庫與側邊欄 =================
levels = {
    "1. 開門：沒興趣": {"objection": "我對保險沒興趣。", "hint": "提示：運用「滅火器」或「晚年生活」切入需求。", "logic": "1.目標轉移 2.生活類比 3.時間差"},
    "2. 拒絕：不需要": {"objection": "我有健保就夠了，我不需要保險。", "hint": "提示：運用「鎖門」比喻或「DRGs 制度」。", "logic": "1.鎖門比喻 2.DRGs 現狀 3.國民便當"},
    "3. 預算：沒有錢": {"objection": "我現在開銷很高，真的沒有錢。", "hint": "提示：強調「沒錢才更需要保險」。", "logic": "1.因果論 2.防護網 3.支出微調"},
    "4. 逃避：我很忙": {"objection": "我很忙，你資料寄給我就好。", "hint": "提示：肯定忙碌，強調專業代勞。", "logic": "1.專業代勞 2.面談分析"},
    "5. 系統：已有保險": {"objection": "爸媽幫我買好了。", "hint": "提示：運用「滅火器定期檢視」。", "logic": "1.壓力表檢查 2.獨立負責 3.長期服務"},
    "6. 投資：做投資好": {"objection": "我自己做投資比保險好。", "hint": "提示：強調「投資需要時間」。", "logic": "1.時間複利 2.資產保全"},
    "7. 比較：想跟別家比": {"objection": "我想跟別家比較價錢。", "hint": "提示": "強調南山理賠品質。", "logic": "1.理賠糾紛率低 2.品牌價值"},
    "8. 拖延：晚一點再買": {"objection": "我現在不想決定，晚一點再買。", "hint": "提示：詢問要買便宜還是貴的？", "logic": "1.年紀成本 2.健康狀況不可逆"}
}

with st.sidebar:
    st.title(f"👤 {st.session_state.user_data['display_name']}")
    st.metric("🏆 最佳戰績 EXP (100滿分)", st.session_state.user_data['exp'])
    if st.button("登出系統"):
        st.session_state.logged_in = False
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.subheader("📊 元捷英雄榜")
    try:
        lb_df = get_db()
        lb_df['exp'] = pd.to_numeric(lb_df['exp'], errors='coerce').fillna(0)
        st.table(lb_df.sort_values(by="exp", ascending=False).head(5)[["display_name", "exp"]])
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

if user_input := st.chat_input("請輸入你的元捷實戰話術..."):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # 自動偵測可用模型
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target_model = next((m for m in available_models if 'flash' in m), 'gemini-1.5-flash')
        except:
            target_model = 'gemini-1.5-flash'
            
        model = genai.GenerativeModel(target_model)
        
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 組合 Prompt (加入元捷系統引導)
        prompt = f"""
        你現在是南山人壽「元捷通訊處」的首席實戰教官。
        學員：{st.session_state.user_data['display_name']}
        反對問題：{curr['objection']}
        學員話術：{user_input}
        
        請根據教材邏輯：{curr['logic']} 進行評分與講評。
        
        輸出格式規範 (嚴格執行)：
        1. 【辨識邏輯】：分析學員使用的技巧。
        2. 【教練評分】：評分：XX (請以 0 到 100 為滿分，嚴禁使用 5 分制)。
        3. 【實戰講評】：指出優缺點，並提供示範金句。
        4. 【元捷進修建議】：以熱血的語氣，引導學員針對表現弱點，回到「元捷教育訓練系統」查看相關教材或課程(如：新人基礎班、反對問題處理文本等)，強調系統化練習的重要性。
        """

        with st.chat_message("assistant"):
            with st.spinner("元捷教練評分中..."):
                response = model.generate_content(prompt)
                res_text = response.text
                st.markdown(res_text)
                st.session_state.messages.append({"role": "assistant", "content": res_text})
                
                # 精準抓取分數
                score_match = re.search(r'評分[:：\s]*(\d+)', res_text)
                earned_exp = int(score_match.group(1)) if score_match else 60
                earned_exp = max(0, min(100, earned_exp))

                # 顯示大字體評分板
                st.markdown(f"""
                    <div style="text-align: center; border: 3px solid #FFA500; padding: 20px; border-radius: 15px; background-color: #FFF5E6; margin-top: 20px;">
                        <h1 style="font-size: 80px; color: #FF4B4B; margin: 0;">{earned_exp} <span style="font-size: 24px;">分</span></h1>
                    </div>
                """, unsafe_allow_html=True)

                # 更新分數 (最高分制)
                if earned_exp > st.session_state.user_data['exp']:
                    st.session_state.user_data['exp'] = earned_exp
                    all_db = get_db()
                    u_id = str(st.session_state.user_data['username'])
                    all_db.loc[all_db['username'].astype(str) == u_id, 'exp'] = str(st.session_state.user_data['exp'])
                    conn.update(data=all_db)
                    st.success("🔥 創下個人最高得分紀錄！")
                
                if earned_exp >= 80: st.balloons()
                st.button("同步至元捷英雄榜", on_click=lambda: st.rerun())

    except Exception as e:
        st.error(f"系統連線異常：{e}")
