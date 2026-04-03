import streamlit as st
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# ================= 1. 網頁基礎設定 =================
st.set_page_config(page_title="捷出青年班 AI 競賽區", page_icon="🏆", layout="wide")

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
    """讀取資料庫並強制轉換為字串格式，避免 0 開頭密碼被吃掉"""
    try:
        df = conn.read(ttl=0)
        df = df.astype(str).replace(r'\.0$', '', regex=True)
        return df
    except Exception as e:
        st.error(f"資料庫讀取失敗，請檢查 Secrets 設定：{e}")
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
            
            # 比對帳號密碼
            match = db_df[(db_df['username'].str.strip() == u_input) & 
                          (db_df['password'].str.strip() == p_input)]
            
            if not match.empty:
                st.session_state.logged_in = True
                user_info = match.iloc[0].to_dict()
                # 確保分數是數字
                try:
                    user_info['exp'] = int(float(user_info.get('exp', 0)))
                except:
                    user_info['exp'] = 0
                st.session_state.user_data = user_info
                st.success(f"🎊 歡迎回來，{user_info['display_name']} 教官！")
                st.rerun()
            else:
                st.error("❌ 帳號或密碼錯誤，請重新輸入。")

    with tab2:
        st.write("填寫資訊建立您的戰士檔案：")
        reg_user = st.text_input("設定帳號 (建議用手機)", key="r_user")
        reg_pw = st.text_input("設定密碼", type="password", key="r_pw")
        reg_name = st.text_input("您的暱稱 (顯示在排行榜)", key="r_name")
        
        if st.button("完成
