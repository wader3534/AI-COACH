import streamlit as st
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re

# ================= 1. 網頁基礎設定 =================
st.set_page_config(page_title="元捷 AI 實戰與主管萬事通 V16", page_icon="🛡️", layout="wide")

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

# ================= 2. 登入介面 =================
if not st.session_state.logged_in:
    st.title("🛡️ 元捷通訊處：AI 實戰教官系統 V16")
    st.subheader("「觀念若改，賓士隨你駛」— 元捷數位智慧庫")
    tab1, tab2 = st.tabs(["🔑 帳號登入", "📝 新人註冊"])
    db_df = get_db()
    with tab1:
        login_user = st.text_input("帳號 (ID)", key="l_user")
        login_pw = st.text_input("密碼", type="password", key="l_pw")
        if st.button("進入道館"):
            u_input = str(login_user).strip()
            p_input = str(login_pw).strip()
            match = db_df[(db_df['username'].str.strip() == u_input) & (db_df['password'].str.strip() == p_input)]
            if not match.empty:
                st.session_state.logged_in = True
                user_info = match.iloc[0].to_dict()
                user_info['exp'] = int(float(user_info.get('exp', 0)))
                st.session_state.user_data = user_info
                st.rerun()
    st.stop()

# ================= 2. 【元捷大腦：頂規詳盡知識庫】 =================
# 教官！這裡就是你的大腦基地。未來有新教材，直接往這裡面「塞」就對了！
YUANJIE_BRAIN = """
### 一、 職涯與心態建立 (Mindset)
1. 壽險事業觀：核心價值與愛與責任
【深度實戰分析】：壽險事業是建立在對人類「生、老、病、死」這四個普通問題的確定性解決方案。業務員是「財務醫生」，保險是「防守的錢」。
【核心比喻】：印鈔機比喻—人就是印鈔機，保險是替代收入，確保家人能過著「好像我們還在」的生活。
【評分關鍵字】：愛與責任、普通問題個人化、確定給付、印鈔機比喻、財務醫生、防守的錢、保全資產、遺愛人間。

2. 業代增員重點：透明升遷、利潤在自己身上
【深度實戰分析】：增員是組織創業，核心在於「利潤在自己身上」。透過南山公平委任辦法，建立「非工資收入」，實現時間換空間的槓桿原理。
【核心邏輯】：幫助他人成功比吃七年素齋更有功德。你是自己的老闆。
【評分關鍵字】：創業家精神、委任辦法、非工資收入、成人成己、透明晉升、組織發展、槓桿原理、主人翁精神。

3. 職場倫理與禮儀：三不往來、專業素養
【核心邏輯】：專業形象是第一張身分證（7-38-55定律）。落實「三不往來」：金錢、人頭、感情。減壓行銷：借一張紙降低客戶警戒。
【評分關鍵字】：三不往來、7-38-55定律、專業形象、今日事今日畢、誠信透明、減壓行銷。

### 二、 客戶開發與活動量 (Activity)
4. 客戶名單建立與開發：曼陀羅法與 COI
【深度分析】：曼陀羅九宮格法盤點八大客源（親、同、友、隨、鄰、同、付、好）。維持 200 個有效名單。量大人瀟灑，拒當「算命師」。
【評分關鍵字】：曼陀羅法、SWOT分析、200個名單、量大人瀟灑、影響力中心 (COI)。

5. 社區大學經營：萬有引力法
【核心邏輯】：把自己變成磁鐵。固定出席、願意付出、不強出頭。用「健康雜誌」當敲門磚（間接無壓告知）。
【評分關鍵字】：萬有引力法、健康雜誌、間接告知、私交建立、心佔率。

6. 活動量管理與計分：339 指標與四星會
【核心指標】：每日 339（3訪3名單9通）。10:5:3:1 漏斗原則。提早完成目標即是向前。量變產生質變。
【評分關鍵字】：339指標、10:5:3:1原則、四星會、量大人瀟灑、轉化率分析。

### 三、 接職與約訪實戰 (Contact)
8. DISC 與 AIA 應用：特質溝通
【核心邏輯】：三分鐘觀人術判定 D/I/S/C。LISTEN原則（觀察、資訊、同理、信任、鼓勵、中立覆述）。調頻同步與鏡像神經元。
【評分關鍵字】：DISC觀人術、LISTEN原則、7-38-55定律、調頻同步、中立覆述。

### 四、 商品專業與轉進 (Product)
10. 長照商品銷售：經典長照比喻
【深度分析】：院外醫療概念。醫療險理賠住院一陣子，長照理賠出院一輩子。蕭煌奇比喻。解決問題而非製造問題。
【評分關鍵字】：院外醫療、理賠一輩子、蕭煌奇比喻、失智失能、尊嚴照護、十六年給付。

12. 高保障期繳商品：退休一桶金
【核心邏輯】：退休準備「不能失敗、不能重來、不能後悔」。退休無關年紀，與口袋深度有關。鎖利存本。
【評分關鍵字】：不能重來、鎖利存本、一桶金、口袋深度、資產保全。

### 五、 銷售工具與技術 (Tools)
14. 保單健診與條款：從缺口找需求
【核心比喻】：備胎比喻—保單像備胎，要定期檢查。找出新式手術、自費醫材缺口。
【評分關鍵字】：備胎比喻、保單健診、條款缺口、定期檢視、醫療科技缺口。

15. 理財矩陣：4-3-2-1 原則
【核心邏輯】：40%生活、30%理財、20%債務、10%保險。10%保險保全90%資產。資產護衛隊概念。
【評分關鍵字】：理財矩陣、4-3-2-1原則、保全資產、10%預算、減壓行銷。

### 六、 關鍵成交與演練 (Closing)
17. 三階段四問題：結構化問話
【深度分析】：撫育/奮鬥/退休三階段；走太早/活太長/病殘/中斷四問題。普通問題個人化。
【評分關鍵字】：撫育奮鬥退休、責任對象、需求引導、風險預演、危機共鳴。

19. 反對問題處理：10種標準回覆
【核心三步驟】：同步、釐清、轉向。
【標準話術】：不需要、沒興趣、沒錢、已買過、考慮中、朋友做、理財好、繳太長、家人反對、增員底薪。
【紅線】：禁說底薪、禁私下金流、禁低保額規劃、禁節稅名義不實招攬。

### 七、 威德教官靈魂語錄
1. 觀念若改，賓士隨你駛；觀念若不改，一輩子騎歐兜賣。
2. 賺一塊錢不是你的一塊錢，存一塊錢才是你的一塊錢。
3. 人生不是得到，就是學到。
4. 我捨不得我的客戶要裝心臟支架的時候沒有錢。
5. 提早才是向前，即使已經落後。
"""

OBJECTIONS_MAP = {
    "不需要": "健保夠了？同步觀念好，釐清不需買vs不需再買，切入備胎比喻。",
    "沒興趣": "保險非興趣。印鈔機比喻，解決生老病死普通問題。",
    "沒錢": "理財矩陣 10% 保全觀念，三五千也可以，降低門檻。",
    "已買過": "爸媽買好？稱讚觀念好，透過健診確認是否解決現在的問題。",
    "朋友做": "稱讚朋友，強調元捷系統化服務與專業理賠分享。",
    "想拿底薪": "禁止說底薪！強調創業平台與利潤在自己身上。"
}

# ================= 4. 側邊欄與導航 =================
with st.sidebar:
    st.title(f"👤 {st.session_state.user_data['display_name']}")
    st.metric("🏆 最佳戰績", f"{st.session_state.user_data['exp']} 分")
    st.divider()
    mode = st.radio("🚀 系統選擇：", ["⚔️ 反對問題實戰演練", "🧠 元捷主管萬事通"])
    
    if mode == "⚔️ 反對問題實戰演練":
        selected_mod = st.selectbox("🎯 情境選擇：", list(OBJECTIONS_MAP.keys()))
        st.caption(f"💡 教官攻略：{OBJECTIONS_MAP[selected_mod]}")
    else:
        st.success("🤖 已加載元捷詳盡教材庫")

    if st.button("🔄 清空對話"):
        st.session_state.messages = []
        st.rerun()
    if st.button("🚪 登出"):
        st.session_state.logged_in = False
        st.rerun()

# ================= 5. AI 回覆邏輯 =================
st.title(mode)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if user_input := st.chat_input("在此輸入..."):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # 模型防崩潰
        model_name = 'gemini-1.5-flash'
        model = genai.GenerativeModel(model_name)
        
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"): st.markdown(user_input)

        if mode == "⚔️ 反對問題實戰演練":
            prompt = f"""
            你現在是元捷教官。
            【頂規知識庫】：{YUANJIE_BRAIN}
            
            針對反對問題「{selected_mod}」，學員回答：「{user_input}」。
            請嚴格按照以下規範講評：
            1. 【評分】：0-100。
            2. 【深度實戰分析】：字數必須 400 字以上。詳細分析學員是否命中上述知識庫中的具體比喻（如印鈔機、備胎等）及 FACT 步驟。
            3. 【地雷糾錯】：檢測紅線（如底薪、節稅、私下金流）。
            4. 【勉勵】：隨機引用一則威德金句。
            """
        else:
            prompt = f"""
            你現在是元捷處經理數位分身（威德主管萬事通）。
            【全方位大腦知識庫】：{YUANJIE_BRAIN}
            
            同仁現在問你一個問題：『{user_input}』
            
            請以熱血、專業、務實的主管語氣解答：
            1. 【主管解決方案】：必須提供具體的教材 SOP 或話術。如果問到特定領域（如社大、理財矩陣、增員），請背出上述知識庫中的細節。
            2. 【深度比喻對位】：引用教材中相關的比喻（如鎖門比喻、不孝子比喻、4321比例等）。
            3. 【結尾】：附上威德金句，並鼓勵同仁「有意識地生活，量大人瀟灑」。
            """

        with st.chat_message("assistant"):
            with st.spinner("威德主管正在調閱教材中..."):
                response = model.generate_content(prompt)
                res_text = response.text
                st.markdown(res_text)
                st.session_state.messages.append({"role": "assistant", "content": res_text})
                
                if mode == "⚔️ 反對問題實戰演練":
                    score_match = re.search(r'評分[:：\s]*(\d+)', res_text)
                    earned_exp = int(score_match.group(1)) if score_match else 60
                    if earned_exp > st.session_state.user_data['exp']:
                        st.session_state.user_data['exp'] = earned_exp
                        all_db = get_db()
                        all_db.loc[all_db['username'].astype(str) == str(st.session_state.user_data['username']), 'exp'] = str(st.session_state.user_data['exp'])
                        conn.update(data=all_db)
                    if earned_exp >= 80: st.balloons()
                    st.button("同步至英雄榜", on_click=lambda: st.rerun())

    except Exception as e:
        st.error(f"⚠️ 系統異常：{e}")
