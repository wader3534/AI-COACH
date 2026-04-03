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
    return conn.read(ttl=0)

# ================= 2. 登入與註冊畫面 =================
if not st.session_state.logged_in:
    st.title("🛡️ 捷出青年班實戰系統")
    st.subheader("請登入以開始 AI 訓練挑戰")
    
    tab1, tab2 = st.tabs(["🔑 帳號登入", "📝 新隊員註冊"])
    df = get_db()

    with tab1:
        login_user = st.text_input("帳號 (ID)")
        login_pw = st.text_input("密碼", type="password")
        if st.button("進入道館"):
            match = df[(df['username'].astype(str) == login_user) & (df['password'].astype(str) == str(login_pw))]
            if not match.empty:
                st.session_state.logged_in = True
                st.session_state.user_data = match.iloc[0].to_dict()
                st.success(f"歡迎回來，{st.session_state.user_data['display_name']}！")
                st.rerun()
            else:
                st.error("帳號或密碼錯誤。")

    with tab2:
        reg_user = st.text_input("設定帳號 (建議手機或 Email)")
        reg_pw = st.text_input("設定密碼", type="password")
        reg_name = st.text_input("您的顯示名稱 (暱稱)")
        if st.button("完成註冊"):
            if not reg_user or not reg_pw or not reg_name:
                st.warning("請填寫所有欄位！")
            elif reg_user in df['username'].astype(str).values:
                st.error("此帳號已被註冊。")
            else:
                new_row = pd.DataFrame([{"username": reg_user, "password": str(reg_pw), "display_name": reg_name, "exp": 0}])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=updated_df)
                st.success("註冊成功！請切換到登入分頁。")
    st.stop()

# ================= 3. 題庫設定 (Levels 題庫) =================
levels = {
    "1. 開門：沒興趣": {
        "objection": "我對保險沒興趣。",
        "hint": "提示：運用「滅火器」或「晚年生活」切入需求。",
        "logic": "1.目標轉移(對錢有興趣) 2.生活類比(滅火器) 3.時間差(沒興趣才有機會談)"
    },
    "2. 拒絕：不需要": {
        "objection": "我有健保就夠了，我不需要保險。",
        "hint": "提示：運用「鎖門」比喻或「DRGs 制度」自費現狀。",
        "logic": "1.鎖門比喻責任 2.DRGs 住院短自費多 3.國民便當理論"
    },
    "3. 預算：沒有錢": {
        "objection": "我現在開銷很高，真的沒有錢。",
        "hint": "提示：強調「沒錢才更需要保險」，因為承擔不起風險。",
        "logic": "1.因果論 2.沒錢更需防護網 3.理財支出微調"
    },
    "4. 逃避：我很忙 / 寄資料": {
        "objection": "我很忙，你資料寄給我就好。",
        "hint": "提示：肯定忙碌，強調「專業代勞」價值。",
        "logic": "1.專業代勞節省時間 2.面談才能分析需求"
    },
    "5. 系統：已有保險 / 父母買": {
        "objection": "爸媽幫我買好了，或者是朋友在服務。",
        "hint": "提示：運用「滅火器定期檢視」或「建立個人專業人脈」。",
        "logic": "1.滅火器要看壓力表 2.獨立負責 3.長期服務人脈"
    },
    "6. 投資：做投資比較好": {
        "objection": "我自己做投資比保險好。",
        "hint": "提示：強調「投資需要時間」，保險是「當下的防護」。",
        "logic": "1.投資需時間複利 2.10%保險保全90%資產"
    },
    "7. 比較：我想跟別家比較": {
        "objection": "我想跟別家保險公司比較一下價錢。",
        "hint": "提示：強調南山「理賠糾紛率業界最低」。",
        "logic": "1.理賠品質與安心感 2.品牌安全性優於些微價差"
    },
    "8. 拖延：晚一點再買": {
        "objection": "保險很重要，但我現在不想決定，晚一點再買。",
        "hint": "提示：詢問要買便宜還是貴的？強調健康與年齡成本。",
        "logic": "1.年紀與保費成本 2.健康狀況不可逆"
    }
}

# ================= 4. 側邊欄狀態與排行榜 =================
with st.sidebar:
    st.title(f"👤 {st.session_state.user_data['display_name']}")
    st.metric("🏆 累積實戰 EXP", st.session_state.user_data['exp'])
    
    if st.button("登出"):
        st.session_state.logged_in = False
        st.rerun()

    st.divider()
    st.subheader("📊 英雄榜")
    leaderboard = get_db().sort_values(by="exp", ascending=False).head(5)
    st.table(leaderboard[["display_name", "exp"]])
    
    st.divider()
    selected_level = st.selectbox("選擇挑戰關卡：", list(levels.keys()))
    if st.button("重新開始本關"):
        st.session_state.messages = []
        st.rerun()

# ================= 5. 主畫面：AI 對話框指令 =================
st.title(f"⚔️ {selected_level}")
current_obj = levels[selected_level]["objection"]
st.info(f"**👨‍💼 客戶說：** 「{current_obj}」")
st.caption(f"💡 {levels[selected_level]['hint']}")

# 顯示對話紀錄
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 聊天輸入框
if user_input := st.chat_input("請輸入你的實戰話術..."):
    # 讀取金鑰 (Secrets)
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model = genai.GenerativeModel(next((m for m in model_list if 'flash' in m), model_list[0]))
    except:
        st.error("API 連線失敗，請檢查 Secrets 設定。")
        st.stop()

    # 顯示使用者輸入
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 講師指導指令
    prompt = f"""
    你現在是南山人壽「捷出青年班」實戰教練。學員：{st.session_state.user_data['display_name']}。
    面對問題：{current_obj}
    教材邏輯：{levels[selected_level]['logic']}
    請辨識邏輯、給分(1-100)、並給予實戰講評。
    """

    with st.chat_message("assistant"):
        with st.spinner("教練評分中..."):
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            # 更新分數並存回 Google Sheets
            st.session_state.user_data['exp'] += 100
            db = get_db()
            db.loc[db['username'].astype(str) == str(st.session_state.user_data['username']), 'exp'] = st.session_state.user_data['exp']
            conn.update(data=db)
            st.balloons()
