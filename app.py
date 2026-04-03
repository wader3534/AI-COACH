import streamlit as st
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# ================= 1. 網頁與資料庫初始化 =================
st.set_page_config(page_title="捷出青年班 AI 競賽區", page_icon="🏆", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# 建立試算表連線
conn = st.connection("gsheets", type=GSheetsConnection)

def get_db():
    # 強制所有內容轉文字，且「不留任何小數點」
    df = conn.read(ttl=0)
    df = df.astype(str).replace(r'\.0$', '', regex=True)
    return df

# ================= 2. 登入與註冊邏輯 =================
if not st.session_state.logged_in:
    st.title("🛡️ 捷出青年班實戰系統")
    st.subheader("請登入以開始 AI 訓練挑戰")
    
    tab1, tab2 = st.tabs(["🔑 帳號登入", "📝 新隊員註冊"])
    df = get_db()

    with tab1:
        login_user = st.text_input("帳號 (ID)", key="l_user")
        login_pw = st.text_input("密碼", type="password", key="l_pw")
        if st.button("進入道館", key="login_btn"):
            u_input = str(login_user).strip()
            p_input = str(login_pw).strip()
            match = df[(df['username'].astype(str).str.strip() == u_input) & 
                      (df['password'].astype(str).str.strip() == p_input)]
            
            if not match.empty:
                st.session_state.logged_in = True
                user_info = match.iloc[0].to_dict()
                user_info['exp'] = int(float(user_info.get('exp', 0)))
                st.session_state.user_data = user_info
                st.success(f"🎊 歡迎回來，{user_info['display_name']} 教官！")
                st.rerun()
            else:
                st.error("❌ 帳號或密碼錯誤。")

    with tab2:
        reg_user = st.text_input("設定帳號")
        reg_pw = st.text_input("設定密碼", type="password")
        reg_name = st.text_input("顯示名稱 (暱稱)")
        if st.button("完成註冊"):
            u_reg = str(reg_user).strip()
            if not reg_user or not reg_pw or not reg_name:
                st.warning("請填寫所有欄位！")
            elif u_reg in df['username'].astype(str).values:
                st.error("此帳號已被註冊。")
            else:
                new_row = pd.DataFrame([{"username": u_reg, "password": str(reg_pw).strip(), 
                                        "display_name": str(reg_name).strip(), "exp": "0"}])
                conn.update(data=pd.concat([df, new_row], ignore_index=True))
                st.success("註冊成功！請切換到登入頁面。")
    st.stop()

# ================= 3. 題庫與側邊欄 (登入後才顯示) =================
levels = {
    "1. 開門：沒興趣": {"objection": "我對保險沒興趣。", "hint": "提示：運用「滅火器」或「晚年生活」切入需求。", "logic": "1.目標轉移 2.生活類比 3.時間差"},
    "2. 拒絕：不需要": {"objection": "我有健保就夠了，我不需要保險。", "hint": "提示：運用「鎖門」比喻或「DRGs 制度」。", "logic": "1.鎖門比喻 2.DRGs 現狀 3.國民便當"},
    "3. 預算：沒有錢": {"objection": "我現在開銷很高，真的沒有錢。", "hint": "提示：強調「沒錢才更需要保險」。", "logic": "1.因果論 2.防護網 3.支出微調"},
    "4. 逃避：我很忙": {"objection": "我很忙，你資料寄給我就好。", "hint": "提示：肯定忙碌，強調專業代勞。", "logic": "1.專業代勞 2.面談分析"},
    "5. 系統：已有保險": {"objection": "爸媽幫我買好了。", "hint": "提示：運用「滅火器定期檢視」。", "logic": "1.壓力表檢查 2.獨立負責 3.長期服務"},
    "6. 投資：做投資好": {"objection": "我自己做投資比保險好。", "hint": "提示：強調「投資需要時間」。", "logic": "1.時間複利 2.資產保全"},
    "7. 比較：想跟別家比": {"objection": "我想跟別家比較價錢。", "hint": "提示：強調南山理賠品質。", "logic": "1.理賠糾紛率低 2.品牌價值"},
    "8. 拖延：晚點再買": {"objection": "我現在不想決定，晚一點再買。", "hint": "提示：詢問要買便宜還是貴的？", "logic": "1.年紀成本 2.健康狀況不可逆"}
}

with st.sidebar:
    st.title(f"👤 {st.session_state.user_data['display_name']}")
    try:
        current_exp = int(float(st.session_state.user_data.get('exp', 0)))
    except:
        current_exp = 0
    st.metric("🏆 累積實戰 EXP", current_exp)
    
    if st.button("登出"):
        st.session_state.logged_in = False
        st.session_state.user_data = None
        st.rerun()

    st.divider()
    st.subheader("📊 英雄榜")
    try:
        lb = get_db().sort_values(by="exp", ascending=False).head(5)
        st.table(lb[["display_name", "exp"]])
    except:
        st.write("尚無排名數據")
    
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
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        prompt = f"你是南山人壽實戰教練。學員針對
