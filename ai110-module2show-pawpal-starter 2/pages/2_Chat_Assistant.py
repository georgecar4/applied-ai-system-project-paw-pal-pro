
import streamlit as st
from chatbot import get_response
from state import init_state, set_background

st.set_page_config(
    page_title="Chat Assistant - PawPal+",
    page_icon="💬",
    layout="centered"
)

init_state()
set_background("puppy_call_center.png")

st.title("💬 PawPal+ Chat Assistant")
st.caption("Powered by Ollama — ask me to add a task or tell you what's on the schedule! 🐾")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": (
                "Hiya there! 🐾💖 I'm your PawPal+ buddy, powered by a local Ollama model! Ask "
                "me to add a task or tell you what's coming up, and I'll take care of it with a smile! ✨"
            ),
        }
    ]

for message in st.session_state.chat_history:
    avatar = "🐾" if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

user_message = st.chat_input("Type a message...")

if user_message:
    st.session_state.chat_history.append({"role": "user", "content": user_message})

    with st.spinner("Thinking happy thoughts... 🐾"):
        reply = get_response(
            st.session_state.owner,
            st.session_state.scheduler,
            st.session_state.chat_history[:-1],
            user_message,
        )

    st.session_state.chat_history.append({"role": "assistant", "content": reply})
    st.rerun()
