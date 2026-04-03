import streamlit as st
import google.generativeai as genai

# ================= 1. 網頁與遊戲化設定 =================
st.set_page_config(page_title="捷出青年班 AI 道館", page_icon="⚔️", layout="wide")

# 初始化經驗值與對話紀錄
if "exp" not in st.session_state:
    st.session_state.exp = 0
if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= 2. 全套反對問題題庫 (整合 PPT 實戰教材) =================
levels = {
    "1. 開門：沒興趣": {
        "objection": "我對保險沒興趣。",
        "hint": "提示：運用「滅火器」或「晚年生活」來切入需求。",
        "logic": "1.【目標轉移】：強調是對晚年有錢感興趣。2.【生活類比】：用滅火器、汽車備胎比喻需要大於興趣。3.【時間差】：強調沒興趣才有機會談。"
    },
    "2. 拒絕：不需要": {
        "objection": "我有健保就夠了，我不需要保險。",
        "hint": "提示：運用「鎖門」比喻或「DRGs 制度」下自費增加的現實。",
        "logic": "1.【安全感比喻】：用出門鎖門怕小偷比喻保險。2.【DRGs 現狀】：強調住院短、自費多。3.【國民便當】：健保是吃飽，保險是吃好。"
    },
    "3. 預算：沒有錢": {
        "objection": "我現在開銷很高，真的沒有錢。",
        "hint": "提示：強調「沒錢才更需要保險」，因為承擔不起風險帶來的損失。",
        "logic": "1.【因果論】：指出不存錢以後還是沒錢。2.【防護網】：強調沒錢時更不容許意外發生。3.【理財規劃】：從支出中擠出小額保費。"
    },
    "4. 逃避：我很忙 / 寄資料": {
        "objection": "我很忙，你資料寄給我就好。",
        "hint": "提示：肯定客戶忙碌，強調「專業代勞」節省客戶時間的價值。",
        "logic": "1.【專業代勞】：因為忙才需要專業服務。2.【面談重要性】：資料是死的，需求分析才是活的。"
    },
    "5. 系統：已有保險 / 父母買": {
        "objection": "爸媽幫我買好了，或者是爸媽的朋友在服務。",
        "hint": "提示：運用「滅火器定期檢視」或「建立個人專業人脈」的概念。",
        "logic": "1.【定期檢視】：保險像滅火器要檢查壓力表。2.【獨立負責】：出社會應建立自己的保障。3.【專業信任】：選擇年紀相仿、能長期服務的對象。"
    },
    "6. 投資：做投資比較好": {
        "objection": "我自己做投資比保險好。",
        "hint": "提示：強調「投資需要時間」，保險是「當下的防護」。",
        "logic": "1.【時間與額度】：投資需時間複利，保險立刻生效。2.【資產保全】：用 10% 預算保護剩下 90% 的資產。"
    },
    "7. 比較：我想跟別家比較": {
        "objection": "我想跟別家保險公司比較一下價錢。",
        "hint": "提示：強調南山「理賠糾紛率業界最低」與「專業品牌服務」。",
        "logic": "1.【理賠品質】：南山理賠糾紛率低，買的是安心。2.【品牌價值】：差不多的價錢應選更安全的品牌。"
    },
    "8. 拖延：晚一點再買": {
        "objection": "保險很重要，但我現在不想決定，晚一點再買。",
        "hint": "提示：詢問客戶「想買便宜的還是貴的？」，強調年齡與健康成本。",
        "logic": "1.【保費成本】：年紀越大越貴。2.【健康風險】：現在不買，未來健康狀況改變可能想買也買不到。"
    }
}

# ================= 3. 左側邊欄：玩家面板 =================
with st.sidebar:
    st.title("🔥 捷出青年班 AI 戰鬥面板")
    
    # 讀取金鑰 (支援 secrets.toml 或手動輸入)
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

# ================= 4. 主畫面：對話與評分邏輯 =================
st.title(f"⚔️ {selected_level}")
current_objection = levels[selected_level]["objection"]

st.info(f"**👨‍💼 客戶說：** 「{current_objection}」")
st.caption(f"💡 {levels[selected_level]['hint']}")

# 顯示歷史對話
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 聊天輸入框
if user_input := st.chat_input("請輸入你的話術..."):
    if not api_key:
        st.warning("請先設定 API 金鑰！")
        st.stop()

    # --- 自動偵測模型連線 (修正 404 錯誤) ---
    genai.configure(api_key=api_key)
    try:
        model_list = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # 優先選擇 flash 模型，如果沒有則用第一個
        target_model = next((m for m in model_list if 'flash' in m), model_list[0])
        model = genai.GenerativeModel(target_model)
    except Exception as e:
        st.error(f"連線失敗，請檢查金鑰：{e}")
        st.stop()

    # 顯示學員輸入
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 核心講師指令
    system_instruction = f"""
    你現在是南山人壽「捷出青年班」的首席實戰教練。學員正在練習處理：「{current_objection}」。
    請根據以下教材原則評分：
    1. 辨別真假：判斷是否在解決「真的問題」。
    2. 絕不辯論：回答應釐清原因而非爭勝。
    3. 簡單明瞭：鼓勵用「國民便當」、「鎖門」、「滅火器」等事例說明。
    
    具體邏輯要點：
    {levels[selected_level]['logic']}

    輸出格式：
    **【辨識邏輯】**：分析使用了哪種技巧。
    **【教練評分】**：1-100 分。
    **【實戰講評】**：指出優缺點，並引用教材金句示範。
    """

    with st.chat_message("assistant"):
        with st.spinner("教練評分中..."):
            try:
                response = model.generate_content(system_instruction)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.session_state.exp += 100
                st.balloons()
            except Exception as e:
                st.error(f"生成失敗：{e}")
