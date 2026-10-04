import streamlit as st
from groq import Groq
import talent_business_agent as agent
import rag_backend

st.set_page_config(
    page_title="Talent-to-Business AI Agent",
    page_icon="💼",
    layout="wide"
)

st.title("💼 Talent-to-Business AI Agent")
st.write(
    "Turn your skills into a digital business with AI guidance."
)

api_key = st.secrets["GROQ_API_KEY"]

client = Groq(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_message = st.chat_input(
    "Tell me about your skill or ask a business question..."
)

if user_message:
    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })

    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
           result = agent.run_agent(
    client,
    user_message,
    conversation_history=st.session_state.messages
)

            if isinstance(result, dict):
                response = result.get("answer", str(result))
            else:
                response = result

            st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
