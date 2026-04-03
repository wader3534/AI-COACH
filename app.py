import streamlit as st
import google.generativeai as genai

# ================= 1. 網頁與遊戲化設定 =================
st.set_page_config(page_title="捷出青年班 AI 道館", page_icon="⚔️", layout="wide")

# 初始化經驗值 (EXP) 系統
if "exp" not in st.session_state:
    st.session_state.exp = 0
if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= 2. 建立題庫字典 (未來可無限擴充) =================
# 這裡就像多鄰國的各個小關卡
levels = {
    "關卡 1：開門破冰戰 (沒興趣)": {
        "objection": "我對保險沒興趣。",
        "hint": "提示：試著用「目標轉移」或「生活類比(滅火器)」來卸下防備。",
        "logic": """
        1. 【目標轉移法】：認同沒興趣，轉移到晚年生活/風險分擔。
        2. 【生活類比法】：用生活必需品（如滅火器、備胎）比喻。
        3. 【危機反轉法】：點出沒興趣才能談，有興趣（出事）就來不及了。
        4. 【降壓邀約法】：理解不清楚才沒興趣，請求抽出30分鐘了解。
        """
    },
    "關卡 2：預算攻防戰 (保費太貴)": {
        "objection": "我現在房貸車貸開銷很高，這張 36 萬的終身險保費我負擔起來太吃力了。",
        "hint": "提示：先同理壓力，再帶出 36 萬終身險「打底」的價值。",
        "logic": "請嚴格審查學員是否有先同理客戶的開銷壓力，並且是否有強調這 36 萬保額在『開銷高階段的絕對防護網（打底）』價值。如果有，給予高分。"
    }
}

# ================= 3. 左側邊欄：玩家面板 =================
with st.sidebar:
    st.title("🔥 實戰教練面板")
    
    # 讀取金鑰 (保險箱)
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except:
        api_key = st.text_input("請輸入您的 Gemini API 金鑰", type="password")
        
    st.divider()
    
    # 遊戲化元素：經驗值與等級
    st.metric(label="🏆 累積實戰經驗值 (EXP)", value=f"{st.session_state.exp} / 1000")
    st.progress(min(st.session_state.exp / 1000, 1.0))
    
    st.divider()
    
    # 關卡選擇器
    st.subheader("🗺️ 選擇挑戰關卡")
    selected_level = st.radio("請選擇今天要練哪一關：", list(levels.keys()))

    # 如果切換關卡，清空對話紀錄以重新開始
    if st.button("🔄 重新挑戰此關卡"):
        st.session_state.messages = []
        st.rerun()

# ================= 4. 主畫面：戰鬥擂台 =================
st.title(f"⚔️ {selected_level}")
current_objection = levels[selected_level]["objection"]
current_logic = levels[selected_level]["logic"]

# 顯示客戶台詞與小提示
st.info(f"**👨‍💼 客戶說：** 「{current_objection}」")
st.caption(levels[selected_level]["hint"])

# 顯示歷史對話
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 聊天輸入框
if user_input := st.chat_input("請輸入你的實戰話術..."):
    if not api_key:
        st.warning("請先設定 API 金鑰！")
        st.stop()

    genai.configure(api_key=api_key)
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model = genai.GenerativeModel(available_models[0])
    except Exception as e:
        st.error(f"金鑰驗證失敗：{e}")
        st.stop()

    # 顯示學員輸入
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 準備 AI 系統指令
    system_instruction = f"""
    你現在是「捷出青年班」的頂尖保險實戰 AI 教練。
    學員正在練習處理客戶的反對問題：「{current_objection}」

    請根據以下【通關邏輯】來評分學員的回覆：
    {current_logic}

    學員的回覆是：{user_input}

    請以嚴格但充滿溫度的教練口吻給予回饋，請務必按照以下格式輸出：
    **【教練評分】**：(給予 1-100 分)
    **【實戰講評】**：(給予具體稱讚或改進建議)
    """

    # 呼叫 AI
    with st.chat_message("assistant"):
        with st.spinner("教練評分中..."):
            try:
                response = model.generate_content(system_instruction)
                reply = response.text
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
                # 簡單的遊戲化獎勵：只要有練習就加 50 EXP
                st.session_state.exp += 50
                st.balloons() # 噴發過關氣球特效！
                
            except Exception as e:
                st.error(f"發生錯誤：{e}")