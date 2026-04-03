import streamlit as st
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re

# ================= 1. 網頁基礎設定 =================
st.set_page_config(page_title="元捷 AI 實戰與主管萬事通 V16.5", page_icon="🛡️", layout="wide")

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
    st.title("🛡️ 元捷通訊處：AI 實戰教官系統")
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

# ================= 3. 【元捷大腦：頂規詳盡知識庫】 =================
# 威德教官！這裡封裝了你提供的所有超過 5000 字的教材精華！
YUANJIE_BRAIN = """
### 元捷實戰大百科：深度實戰分析與邏輯庫

#### 一、 職涯與心態建立 (Mindset)
1. 壽險事業觀：核心價值與愛與責任
【深度實戰分析】：壽險事業的本質是建立在對人類「生、老、病、死」這四個普通問題的確定性解決方案之上。在元捷的思維架構中，保險不是支出，而是「防守的錢」，用於保全其他 90% 的努力不被風險吃掉。業務員必須具備「財務醫生」的自覺，深信每個人都需要保險。透過「印鈔機比喻」，將人的經濟價值具象化：如果家裡有一台每天印錢的機器，我們一定會幫它買保險；而人就是那台印鈔機，當風險發生導致機器損壞時，保險理賠金就是替代收入，確保家人能過著「好像我們還在」的生活。這種「因為愛，責任在」的核心價值，是業務員面對拒絕與挫折時最堅實的心靈底層邏輯。
【評分關鍵字】：愛與責任、風險規劃、財務醫生、生老病死、普通問題個人化、確定給付、印鈔機比喻、防守的錢、保全資產、遺愛人間。
【禁忌紅線】：嚴禁僅提及佣金；禁止使用節稅、規避二代健保等名義招攬。

2. 業代增員重點：透明升遷與利潤在自己身上
【深度實戰分析】：增員是從「單兵作業」轉向「組織創業」的關鍵。強調南山「委任辦法」下的公平與透明。核心邏輯在於「利潤在自己身上」，收入不由老闆發放，而是由自己的活動量與組織效能決定。分析其組織發展藍圖，晉升主任、襄理至經理的過程，實際上是個人產能與團隊槓桿的平衡，旨在建立穩定的「非工資收入」，達成時間自由。增員被定義為「幫助他人成功」的利他事業，幫助一個想成功的人，比吃七年素齋更有功德。
【評分關鍵字】：利潤在自己身上、創業家精神、委任辦法、組織發展、非工資收入、成人成己、透明晉升、槓桿原理。

3. 職場倫理與禮儀：三不往來與專業素養
【深度實戰分析】：專業形象是第一張身分證。教材引用 7-38-55 定律，外在裝扮佔 55% 影響力。堅持「三不往來」原則（金錢、人頭、感情）。專業感來自細節，如「減壓行銷」：在餐廳分享理財矩陣時使用「借一張紙」或餐巾紙而非自備白紙，以降低客戶警戒。
【評分關鍵字】：三不往來、7-38-55定律、專業套裝、今日事今日畢、誠信透明、減壓行銷、自律生活。

#### 二、 客戶開發與活動量 (Activity)
4. 名單建立開發：曼陀羅法與 COI
【深度實戰分析】：名單是生產原材料。採用「曼陀羅九宮格法」分類八大客源：親、同、友、隨、鄰、同、付、好。維持「200 個有效名單」活水。透過 SWOT 分析進行市場診斷，鎖定「影響力中心 (COI)」。心態上具備「量大人瀟灑」，反對當「算命師」預設立場，應透過大量開口 (5W1H) 篩選需求。
【評分關鍵字】：曼陀羅法、SWOT分析、200個名單、量大人瀟灑、活水池、影響力中心 (COI)、算命師心態。

6. 活動量管理與計分：339 指標與四星會
【深度實戰分析】：活動量是業績領先指標。標準為「339」：每日 3 訪面談、收集 3 個新名單、打 9 通電訪。遵循 10:5:3:1 漏斗原則：10 次約訪產生 5 次面談，最終產出 1 件成交。提早完成目標即是向前。四星會代表穩定的活動慣性，確保留進流出的名單維持活水。
【評分關鍵字】：339指標、10:5:3:1原則、四星會標準、量變產生質變、活動日誌、提早完成目標、自律管理。

#### 三、 需求挖掘與溝通 (Contact)
7. FACT 需求引導步驟：
【深度解構】：
- F (Fact, 事實)：蒐集客觀背景資料（開銷、家庭、工作），建立資料庫。
- A (Affection, 情感)：探尋感受（生病無法工作，最擔心什麼？），挖掘隱性需求並喚起不安感。
- C (Choice, 選擇)：透過結構化引導（如理財矩陣），暗示問題嚴重性讓客戶抉擇。
- T (To do, 行動)：促使立即決策，預約下次遞送建議書。

8. DISC 與 AIA 應用：特質溝通
【深度實戰分析】：調頻同步的科學。透過三分鐘觀人術判斷 D(支配)、I(影響)、S(穩健)、C(服從)。落實 LISTEN 原則：L(Looking at)觀察、I(Information)資訊、S(Sensation)同理、T(Trust built)信任、E(Encouragement)鼓勵、N(Neutral rephrase)中立覆述。讓客戶說話佔比 > 50%，成為客戶鏡像建立信賴。
【評分關鍵字】：DISC觀人術、LISTEN原則、7-38-55定律、調頻同步、中立覆述、積極聆聽、同步語辭。

#### 四、 商品專業與轉進 (Product)
10. 長照商品銷售：經典長照比喻
【深度實戰分析】：定位為「院外醫療」。醫療險理賠住院一陣子，長照理賠出院一輩子。運用「蕭煌奇全殘比喻」或失智失能具象描述。強調「解決問題而非製造問題」：不讓家人面臨照護費用毀滅性影響，確保病患尊嚴。
【評分關鍵字】：院外醫療、理賠一輩子、蕭煌奇比喻、失智失能、尊嚴照護、十六年給付、解決問題而非製造問題。

12. 高保障期繳商品：退休一桶金邏輯
【深度實戰分析】：退休規劃必須「不能失敗、不能重來、不能後悔」。核心在於「鎖利存本」與「資產配置」。退休無關年紀，與「口袋深度」有關。期繳商品利用「時間換空間」，複利增值保全資產，確保水漲船高，水退了還站在船上。
【評分關鍵字】：不能重來、鎖利存本、時間換空間、口袋深度、一桶金、三不特質、複利增值、資產保全。

15. 理財矩陣：4-3-2-1 原則與財富保全
【深度實戰分析】：35 歲以下客群最強工具。將薪資分配為：40% 生活開銷、30% 理財、20% 債務、10% 保險。核心邏輯：用 10% 的保險預算來「保全」另外 90% 的努力與夢想。強調 10% 不是花費，是資產護衛隊。演示時遵循「借一張紙」降低壓力，先達成生活費 40% 共識。
【評分關鍵字】：理財矩陣、4-3-2-1原則、保全資產、10%保險預算、30%理財配置、生活費共識、減壓行銷、借一張紙。

#### 五、 反對問題標準回覆 (Closing)
1. 不需要：同步觀念好，釐清不需買vs不需再買，導向備胎比喻。
2. 沒興趣：保險非興趣。印鈔機比喻，解決生老病死普通問題。
3. 沒預算：理財矩陣 10% 保全觀念，三五千也可以。
4. 買好了：切入健診確認當初規劃是否解決現在的問題。
5. 朋友做：稱讚朋友，強調元捷系統化服務與專業理賠案例。
6. 想拿底薪：禁止說底薪！強調創業平台，利潤在自己身上，透明晉升。

【威德金句】：觀念若改賓士隨你駛、人生不是得到就是學到、我捨不得客戶沒錢、量大人瀟灑。
【地雷紅線】：嚴禁說底薪、嚴禁私下金流、嚴禁低保額規劃、嚴禁代簽、嚴禁節稅不實招攬。
"""

# ================= 4. 主畫面 AI 邏輯 (防 404 版) =================
with st.sidebar:
    st.title("👤 元捷智慧大腦")
    st.metric("🏆 個人戰績", f"{st.session_state.user_data['exp']} 分")
    st.divider()
    mode = st.radio("🚀 系統選擇：", ["⚔️ 反對問題實戰演練", "🧠 元捷主管萬事通"])
    if mode == "⚔️ 反對問題實戰演練":
        selected_mod = st.selectbox("🎯 選擇情境：", ["不需要", "沒興趣", "沒錢", "已買過", "考慮中", "朋友做", "想拿底薪"])
    if st.button("🔄 清空對話"):
        st.session_state.messages = []
        st.rerun()

st.title(mode)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if user_input := st.chat_input("在此輸入..."):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # 防 404 名稱輪替機制
    model = None
    for name in ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'models/gemini-1.5-flash']:
        try:
            model = genai.GenerativeModel(name)
            model.generate_content("test", generation_config={"max_output_tokens": 1})
            break
        except: continue
    
    if not model:
        st.error("❌ 模型連線異常")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    if mode == "⚔️ 反對問題實戰演練":
        prompt = f"""
        你現在是南山元捷教官。
        你的腦中有最詳盡的元捷教材：{YUANJIE_BRAIN}
        
        針對反對情境「{selected_mod}」，學員回答：「{user_input}」。
        請嚴格按照以下規範：
        1. 【評分】：0-100。
        2. 【深度實戰講評】：字數 400 字以上。分析學員是否命中教材細節（如印鈔機、4321、FACT A環節、同步語辭）。
        3. 【地雷紅線】：若說底薪、節稅名義招攬、私下金流，直接斥責並低分。
        4. 【威德金句】：附上激勵語。
        """
    else:
        prompt = f"""
        你現在是元捷主管萬事通（威德主管分身）。
        你的腦中有最詳盡的元捷教材：{YUANJIE_BRAIN}
        
        同仁問：『{user_input}』
        請熱血且專業地回覆：
        1. 提供教材中的具體 SOP (如 FACT 的四步驟、曼陀羅的八大來源)。
        2. 引用具體比喻 (如備胎、印鈔機、不孝子)。
        3. 結尾用威德金句勉勵。
        """

    with st.chat_message("assistant"):
        with st.spinner("威德主管調閱教材中..."):
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
