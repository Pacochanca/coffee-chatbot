
import streamlit as st
import anthropic
import os

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

with open("info.txt", "r") as f:
    document = f.read()

def 判斷意圖(user_input):
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=10,
        system="判斷用戶的意圖，只回答以下其中一個詞：查詢、投訴、再見、其他。詢問過去對話內容也算查詢。查詢包括：詢問店家資料、詢問機器人身份。投訴包括：表達不滿、抱怨。再見包括：bye、goodbye、掰掰等道別語。",
        messages=[{"role": "user", "content": user_input}]
    )
    return message.content[0].text.strip()

def 回答查詢(user_input, history):
    history.append({"role": "user", "content": user_input})
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system=f"重要規則：你必須永遠只用繁體中文回答，絕對不能用英文或其他語言，無論用戶用什麼語言提問。你是小明咖啡客服，只根據以下資料回答問題，資料以外說不知道。\n\n{document}",
        messages=history
    )
    reply = message.content[0].text
    history.append({"role": "assistant", "content": reply})
    return reply

st.title("小明咖啡客服機器人 ☕")

if "history" not in st.session_state:
    st.session_state.history = []

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("請輸入您的問題...")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    意圖 = 判斷意圖(user_input)

    if 意圖 == "查詢":
        reply = 回答查詢(user_input, st.session_state.history)
    elif 意圖 == "投訴":
        reply = "非常抱歉讓您不滿意！我們會盡快安排人員聯絡您。"
        st.session_state.history.append({"role": "user", "content": user_input})
        st.session_state.history.append({"role": "assistant", "content": reply})
    elif 意圖 == "再見":
        reply = "謝謝您的來電，再見！"
        st.session_state.history.append({"role": "user", "content": user_input})
        st.session_state.history.append({"role": "assistant", "content": reply})
    else:
        reply = "您好，請問有什麼可以幫您？"
        st.session_state.history.append({"role": "user", "content": user_input})
        st.session_state.history.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.write(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
