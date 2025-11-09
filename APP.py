elif choice == "🤖 Ask Nuvora (AI Chat)":
    st.title("💬 Ask Nuvora — Your Career AI Assistant")

    st.markdown("""
    👋 **Hi! I'm Nuvora**, your AI career assistant.  
    Ask about resumes, ATS score improvement, interview prep, or project suggestions!
    """)

    if "OPENAI_API_KEY" not in st.secrets:
        st.error("⚠️ AI unavailable. Please set your OpenAI API key in Streamlit Secrets.")
        st.stop()

    openai_api_key = st.secrets["OPENAI_API_KEY"]

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Chat display
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"<div style='background-color:#F1F1F1;padding:10px;border-radius:10px;margin:5px 0;text-align:right'><b>👤 You:</b> {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background-color:#E6F0FF;padding:10px;border-radius:10px;margin:5px 0'><b>🤖 Nuvora:</b> {msg['content']}</div>", unsafe_allow_html=True)

    # Input box
    user_input = st.chat_input("Ask Nuvora anything...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_api_key)

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are Nuvora, a friendly AI career assistant who helps with resumes, job prep, ATS optimization, and interview questions."},
                    *st.session_state.chat_history
                ]
            )

            ai_reply = response.choices[0].message.content
            st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
            st.rerun()

        except Exception as e:
            st.error(f"⚠️ Error: {e}")

    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()
