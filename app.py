import streamlit as st
import google.generativeai as genai

# ================= 1. 網頁與遊戲化設定 =================
st.set_page_config(page_title="捷出青年班 AI 道館", page_icon="⚔️", layout="wide")

if "exp" not in st.session_state:
    st.session_state.exp = 0
if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= 2. 全套反對問題題庫 (整合 PPT 教材) =================
# 根據教材內容，整理出 8 大實戰情境
levels = {
    "1. 開門：沒興趣": {
        "objection": "我對保險沒興趣。",
        "hint": "提示：運用「滅火器」或「晚年生活」來切入需求。",
        "logic": "1.【目標轉移】：強調是對晚年有錢或風險分擔有興趣。 2.【生活類比】：用滅火器、汽車備胎比喻需要大於興趣。 3.【時間差】：強調沒興趣才有機會談，有興趣時已出事。"
    },
    "2. 拒絕：不需要": {
        "objection": "我有健保就夠了，我不需要保險。",
        "hint": "提示：詢問客戶出門鎖門的原因，引導責任觀念。",
        "logic": "1.【安全感比喻】：用出門鎖門怕小偷來比喻保險。 2.【責任引導】：聊三階段四問題的責任。 3.【危機意識】：強調需要時就沒機會談了。"
    },
    "3. 預算：沒有錢": {
        "objection": "我現在開銷很高，真的沒有錢。",
        "hint": "提示：計算理財矩陣，強調沒錢才更需要保險照顧家人。",
        "logic": "1.【因果論】：指出現在沒錢是因為以前沒存，現在不存以後還是沒錢。 2.【理財矩陣】：現場計算開銷。 3.【防護網】：強調沒錢時更不容許風險來臨。"
    },
    "4. 逃避：我很忙 / 寄資料": {
        "objection": "我很忙，你資料寄給我就好。",
        "hint": "提示：肯定客戶的忙碌，強調專業打理的重要性。",
        "logic": "1.【專業代勞】：因為忙才需要專業的人幫忙規劃風險，讓客戶專注事業。 2.【面談價值】：如果不談過需求，無法提供適合的方案。"
    },
    "5. 系統：已有保險 / 父母買": {
        "objection": "爸媽幫我買好了，或者是爸媽的朋友在服務。",
        "hint": "提示：運用「滅火器定期檢視」或「建立個人信任業務」的概念。",
        "logic": "1.【定期檢視】：比喻保險像滅火器，要檢視壓力表(內容)才有效。 2.【獨立負責】：出社會應在能力內為自己規劃。 3.【專業信任】：培養自己年紀相仿、無顧忌溝通的專業業務。"
    },
    "6. 投資：做投資比較好": {
        "objection": "我自己存錢或做投資比保險好。",
        "hint": "提示：詢問客戶投資多久能賺到 500 萬，引導風險不可預估性。",
        "logic": "1.【時間與額度】：投資需要時間，但保險能馬上提供高額度幫助。 2.【資產配置】：強調這不是不買股票，而是透過保險保全剩下 90% 的資產。"
    },
    "7. 比較：我想跟別家比較": {
        "objection": "我想跟別家保險公司比較一下價錢。",
        "hint": "提示：強調「南山理賠糾紛率」是業界最低，這才是最大價值。",
        "logic": "1.【理賠數據】：強調南山理賠糾紛事業界最低(數據公開)。 2.【品質比喻】：Toyota 與賓士只差幾千元時，應選服務品質與安全性高的南山。"
    },
    "8. 拖延：晚一點再買": {
        "objection": "保險很重要，但我現在不想決定，晚一點再買。",
        "hint": "提示：詢問客戶要買便宜的還是貴的？",
        "logic": "1.【保費成本】：趁年輕便宜時買，而非老了變貴才買。 2.【執行力】：強調對的事情要立即做決定，否則工作一忙就不重視了。"
    }
}

# ================= 3. 左側邊欄：玩家面板 =================
with st.sidebar:
    st.title("🔥 捷出青年班 AI 戰鬥面板")
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        st.success("🔑 講師心法已載入！")
    except:
        api_key = st.text_input("輸入 API 金鑰以喚醒教練", type="password")
        
    st.divider()
    st.metric(label="🏆 實戰經驗值 (EXP)", value=f"{st.session_state.exp}")
    st.progress(min(st.session_state.exp / 2000, 1.0))
    
    st.divider()
    st.subheader("🗺️ 選擇挑戰情境")
    selected_level = st.selectbox("請選擇今天要攻克的難題：", list(levels.keys()))

    if st.button("🔄 重啟本關對話"):
        st.session_state.messages = []
        st.rerun()

# ================= 4. 主畫面：對話與評分 =================
st.title(f"⚔️ {selected_level}")
current_objection = levels[selected_level]["objection"]

st.info(f"**👨‍💼 客戶說：** 「{current_objection}」")
st.caption(f"💡 {levels[selected_level]['hint']}")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("請輸入你的話術..."):
    if not api_key:
        st.warning("請先設定 API 金鑰！")
        st.stop()

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 整合教材中的處理原則
    system_instruction = f"""
    你現在是南山人壽「捷出青年班」的首席實戰教練。學員正在處理反對問題：「{current_objection}」。
    
    你的評分標準必須嚴格遵守以下教材原則：
    1. 辨別真假：判斷學員是否在解決「真的問題」 [cite: 499]。
    2. 絕不辯論：回答應釐清原因而非爭勝 [cite: 500]。
    3. 簡單明瞭：鼓勵多用事例說明，或將問題拋回給客戶 [cite: 501, 502]。
    
    具體邏輯：
    {levels[selected_level]['logic']}

    請給出：
    **【辨識邏輯】**：分析學員使用了哪種處理技巧。
    **【教練評分】**：1-100 分。
    **【實戰講評】**：指出優點與缺失，並引用教材金句進行示範。
    """

    with st.chat_message("assistant"):
        with st.spinner("教練正在聽取你的回答..."):
            try:
                response = model.generate_content(system_instruction)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.session_state.exp += 100
                st.balloons()
            except Exception as e:
                st.error(f"連線失敗：{e}")
