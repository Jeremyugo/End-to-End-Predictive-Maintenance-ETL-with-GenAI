import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
from ai_agent.agent import interact_with_agent

st.set_page_config(
    page_title="Predictive Maintenance Agent 🤖",
    layout="wide",
)

def run_app():
    st.title("Predictive Maintenance AI Agent 🤖")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_query := st.chat_input("Ask a question:"):
        with st.chat_message("user"):
            st.markdown(user_query)
        st.session_state.messages.append({"role": "user", "content": user_query})

        with st.spinner("The agent is thinking..."):
            response = interact_with_agent(user_query)

        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
    return 


if __name__ == '__main__':
    run_app()