import streamlit as st
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re

# ================= 1. 網頁基礎設定 =================
st.set_page_config(page_title="元捷 AI 實戰道館 V13.5", page_icon="🛡️", layout="wide")

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
    st.title("🛡️ 元捷通訊處：AI 實戰教官分身 V13.5")
    st.subheader("「觀念若改，賓士隨你駛」— 歡迎進入元捷數位學院")
    tab1, tab2 = st.tabs(["🔑 帳號登入", "📝 新隊員註冊"])
    db_df = get_db()
    with tab1:
        login_user = st.text_input("帳號 (手機或 ID)", key="l_user")
        login_pw = st.text_input("密碼", type="password", key="l_pw")
        if st.button("進入道館", key="login_btn"):
            u_input = str(login_user).strip()
            p_input = str(login_pw).strip()
            match = db_df[(db_df['username'].str.strip() == u_input) & (db_df['password'].str.strip() == p_input)]
            if not match.empty:
                st.session_state.logged_in = True
                user_info = match.iloc[0].to_dict()
                user_info['exp'] = int(float(user_info.get('exp', 0)))
                st.session_state.user_data = user_info
                st.success(f"🎊 歡迎回來，{user_info['display_name']} 夥伴！讓我們成就他人，成就自己！")
                st.rerun()
    with tab2:
        reg_user = st.text_input("設定帳號", key="r_user")
        reg_pw = st.text_input("設定密碼", type="password", key="r_pw")
        reg_name = st.text_input("您的暱稱", key="r_name")
        if st.button("完成註冊", key="reg_btn"):
            if not reg_user or not reg_pw or not reg_name: st.warning("請填寫所有欄位")
            else:
                new_row = pd.DataFrame([{"username": reg_user.strip(), "password": reg_pw.strip(), "display_name": reg_name.strip(), "exp": "0"}])
                conn.update(data=pd.concat([db_df, new_row], ignore_index=True))
                st.success("🎉 註冊成功！請切換到登入分頁。")
    st.stop()

# ================= 3. 元捷 20 大實戰模組完全體資料庫 =================
modules = {
    "1. 壽險事業觀": {
        "analysis": "壽險事業本質是解決生老病死四個普通問題。保險是『防守的錢』，保全另外 90% 的努力。運用印鈔機比喻：人就是印鈔機，故障時需要替代收入確保尊嚴生活。",
        "keywords": "愛與責任、風險規劃、財務醫生、生老病死、確定給付、印鈔機比喻、防守的錢、保全資產、遺愛人間、替代收入。",
        "gold_quote": "因為愛，責任在。保險是為了讓家人在我們不在時，仍能過著好像我們還在的生活。",
        "redlines": "嚴禁僅以高額佣金為訴求；嚴禁使用節稅、規避二代健保名義招攬；禁止缺乏同理心的官僚回應。",
        "ref": "《元捷新人課程：壽險事業觀》"
    },
    "2. 業代增員重點": {
        "analysis": "強調委任辦法下的公平透明，利潤在自己身上。增員是利他事業，建立非工資收入。新人在南山不是做業務，是在創業，透過組織槓桿達成時間自由。",
        "keywords": "利潤在自己身上、創業家精神、委任辦法、組織發展、非工資收入、成人成己、透明晉升、主人翁精神、槓桿原理。",
        "gold_quote": "觀念若改，賓士隨你駛；觀念若不改，一輩子騎歐兜賣。幫助一個想成功的人，比吃七年素齋更有功德。",
        "redlines": "嚴禁提及固定底薪或僱傭關係；不可承諾不勞而獲；嚴禁涉及人頭增員。",
        "ref": "張書豪：增員面談流程 SOP"
    },
    "3. 職場倫理禮儀": {
        "analysis": "專業形象是第一張身分證。落實『三不往來』（金錢、人頭、感情）。遵循 7-38-55 定律，專業套裝與自律行為（今日事今日畢）是贏得信賴的核心。",
        "keywords": "三不往來、7-38-55定律、肢體語言、專業套裝、今日事今日畢、誠信透明、自律生活、服務口碑。",
        "gold_quote": "專業的穿著與嚴謹的自律，是壽險企業家最基本的身分證。今日事，今日畢。",
        "redlines": "嚴禁私下金錢借貸；嚴禁穿著拖鞋或非專業服飾；嚴禁私自代簽要保文件。",
        "ref": "元捷職場倫理與服務規範"
    },
    "4. 名單建立開發": {
        "analysis": "使用曼陀羅法盤點八大來源。維持 200 個有效名單活水。透過 SWOT 診斷個人市場，找出影響力中心 (COI)。心態要量大人瀟灑，不當算命師預設立場。",
        "keywords": "曼陀羅法、SWOT分析、200個名單、量大人瀟灑、活水池、影響力中心 (COI)、算命師心態、10:5:3:1原則。",
        "gold_quote": "再不熟的緣故，都比陌生人熟；一個客戶代表的是背後的一片市場。不要當客戶的算命師。",
        "ref": "元捷開發課程：名單曼陀羅"
    },
    "6. 活動量管理計分": {
        "analysis": "量變產生質變。落實 339 指標（3訪3名單9通電）。遵循 10:5:3:1 漏斗原則。提早完成目標即是向前，確實填寫活動日誌分析轉化率，四星會是穩定標準。",
        "keywords": "339指標、10:5:3:1原則、四星會標準、量變產生質變、活動日誌、漏斗行銷、提早完成目標、自律管理。",
        "gold_quote": "提早才是向前，即使已經落後；量變才會產生質變。量大人瀟灑！",
        "ref": "元捷活動量管理手冊"
    },
    "8. DISC 與 AIA 應用": {
        "analysis": "找對人說對話。透過三分鐘觀人術判斷 D/I/S/C 特質。落實 LISTEN 原則進行積極聆聽。利用同步帶領與鏡像神經元消弭抗拒，讓客戶說話佔比大於 50%。",
        "keywords": "DISC觀人術、LISTEN原則、7-38-55定律、調頻同步、鏡像神經元、中立覆述、積極聆聽、同步語辭。",
        "gold_quote": "您的意思是...？聽比說更有力量。透過調頻同步，進入客戶的共鳴圈。",
        "ref": "元捷溝通科學：DISC 實戰"
    },
    "10. 長照商品銷售": {
        "analysis": "定位為『院外醫療』。醫療險理賠住院一陣子，長照理賠出院一輩子。運用蕭煌奇比喻。解決問題而非製造問題，不讓長壽成為家人的負擔。",
        "keywords": "院外醫療、理賠一輩子、失智失能、蕭煌奇比喻、尊嚴照護、首次給付、長期抗戰、十六年給付、解決問題。",
        "gold_quote": "醫療險理賠住院的一陣子，長照險理賠出院後的一輩子。長期照顧需要的不是親情，而是金錢與專業。",
        "ref": "元捷商品專題：長照險銷售實務"
    },
    "15. 理財矩陣演練": {
        "analysis": "35 歲以下客群最強工具。4-3-2-1 分配原則。核心是 10% 保險保全 90% 資產。遵循減壓行銷，借一張紙自問自答，先達成生活費 40% 共識。",
        "keywords": "理財矩陣、4-3-2-1原則、保全資產、10%保險預算、30%理財配置、生活費共識、債務管理、減壓行銷、借一張紙。",
        "gold_quote": "這 10% 的保險規劃不是多出的花費，而是為了保全你另外 90% 的努力不被風險吃掉。",
        "ref": "元捷理財矩陣教案"
    },
    "17. 三階段四問題": {
        "analysis": "撫育奮鬥養老三階段，對位生老病死四問題。將普通問題個人化。透過引導問句建立風險攸關性。觀念不通不談建議書。建立對責任對象的共鳴。",
        "keywords": "撫育奮鬥養老、走的太早、活得太長、殘廢長年病、收入中斷、生老病死、普通問題個人化、責任對象、需求引導。",
        "gold_quote": "退休無關年紀，跟口袋深度有關。萬一我們提早再見了，目前準備的這些足以照顧您的家人嗎？",
        "ref": "元捷專業技能：三階段四問題"
    },
    "19. 反對問題處理": {
        "analysis": "同步、釐清、轉向三步驟。不與客戶拔河。針對不需要、沒錢、已買等 10 種情境進行標準回覆。將貴轉向為划算，將興趣轉向為解決生老病死的工具。",
        "keywords": "同步語辭、釐清範圍、轉向目標、不拔河、真問題鎖定、扭轉想法、心理橋樑、不需買vs不需再買。",
        "gold_quote": "我知道您覺得保費很貴。您是擔心現在負擔太重，還是擔心以後沒錢治病更昂貴？",
        "ref": "元捷 10 大反對問題標準回覆"
    },
    "20. 激勵成交技巧": {
        "analysis": "成交凌駕一切。運用 A公司B公司法、富蘭克林法、貴人相助法。展現『我捨不得你發生風險沒錢』的使命感。勇於開口，推定成交，一氣呵成簽署。",
        "keywords": "A公司B公司法、富蘭克林法、貴人相助、推定成交、勇於開口、使命感、臨門一腳、成交凌駕一切、決策減壓。",
        "gold_quote": "幫助一個想成功的人比吃七年素齋更有功德。請您做我的貴人，我捨不得您以後沒錢換人工皮。",
        "ref": "元捷成交實務：臨門一腳技巧"
    }
}

# ================= 4. 主畫面邏輯 =================
with st.sidebar:
    st.title(f"👤 {st.session_state.user_data['display_name']}")
    st.metric("🏆 個人最佳戰績", f"{st.session_state.user_data['exp']} 分")
    st.divider()
    selected_mod = st.selectbox("🎯 選擇演練模組：", list(modules.keys()))
    if st.button("🔄 重啟本模組練習"):
        st.session_state.messages = []
        st.rerun()

st.title(f"⚔️ 元捷實戰道館：{selected_mod}")
mod_data = modules[selected_mod]

st.info(f"**📖 核心邏輯：** {mod_data['analysis']}")
with st.expander("💡 威德教官的實戰提示"):
    st.write(f"✅ **評分關鍵字：** {mod_data['keywords']}")
    st.write(f"⭐ **標準金句：** {mod_data['gold_quote']}")
    st.error(f"🚫 **地雷紅線：** {mod_data['redlines']}")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if user_input := st.chat_input("請輸入你的實戰話術..."):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    prompt = f"""
    你現在是南山人壽「元捷通訊處」的首席教官（威德的數位分身）。
    
    【演練模組】：{selected_mod}
    【元捷深度教材分析】：{mod_data['analysis']}
    【加分關鍵字】：{mod_data['keywords']}
    【元捷金句】：{mod_data['gold_quote']}
    【地雷紅線】：{mod_data['redlines']}
    
    學員回覆話術：{user_input}
    
    請依照以下格式進行「威德式」熱血講評：
    1. 【辨識邏輯】：分析學員是否命中元捷教材的核心處理步驟。
    2. 【教練評分】：0-100 分。若觸碰「紅線」（如提及底薪、私下金流、低保額長照、節稅招攬）直接扣 50 分以上。
    3. 【實戰講評】：請用一段 300 字以上的文字進行深度解析，必須包含「優點」、「改進點」以及「實戰建議」。
    4. 【元捷進修建議】：明確要求學員回訓「{mod_data['ref']}」，並送上一句威德金句勉勵。
    """

    with st.chat_message("assistant"):
        with st.spinner("威德教官閱卷中..."):
            response = model.generate_content(prompt)
            res_text = response.text
            st.markdown(res_text)
            st.session_state.messages.append({"role": "assistant", "content": res_text})
            score_match = re.search(r'評分[:：\s]*(\d+)', res_text)
            earned_exp = int(score_match.group(1)) if score_match else 60
            st.markdown(f"""<div style="text-align: center; border: 3px solid #FFA500; padding: 20px; border-radius: 15px; background-color: #FFF5E6; margin-top: 20px;"><h1 style="font-size: 80px; color: #FF4B4B; margin: 0;">{earned_exp} <span style="font-size: 24px;">分</span></h1></div>""", unsafe_allow_html=True)
            if earned_exp > st.session_state.user_data['exp']:
                st.session_state.user_data['exp'] = earned_exp
                all_db = get_db()
                all_db.loc[all_db['username'].astype(str) == str(st.session_state.user_data['username']), 'exp'] = str(st.session_state.user_data['exp'])
                conn.update(data=all_db)
            if earned_exp >= 80: st.balloons()
            if st.button("同步至英雄榜"): st.rerun()
