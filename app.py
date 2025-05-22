import streamlit as st
from voice_functions import listen, threaded_speak, ask_gemini, stop_tts

st.set_page_config(page_title="Kira 31 AI Document QA System", layout="centered")
st.title("Kira 31 AI Document QA System")
st.markdown("Use your voice to ask questions based on the uploaded document.")

if 'doc_content' not in st.session_state:
    st.session_state.doc_content = ""
if 'response' not in st.session_state:
    st.session_state.response = ""
if 'history' not in st.session_state:
    st.session_state.history = []
if 'paused' not in st.session_state:
    st.session_state.paused = False
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

status_placeholder = st.empty()

# Show conversation history
if st.session_state.history:
    st.markdown("### 📝 Conversation History")
    for q, r in reversed(st.session_state.history):
        st.markdown(f"**🗣️ You:** {q}")
        st.markdown(f"**🤖 Gemini:** {r}")
        st.markdown("---")


def speak_response(text):
    stop_tts()
    st.session_state.paused = False
    audio_path = threaded_speak(text)
    st.audio(audio_path, format="audio/mp3", autoplay=True)


if st.button("🎤 Ask"):
    with st.spinner("🎙️ Listening... Please speak now"):
        user_input = listen()

    if "ERROR" not in user_input:
        st.session_state.user_input = user_input
        status_placeholder.markdown(f"**🗣️ You said:** {user_input}")

        if st.session_state.doc_content.strip() == "":
            response = "Please upload a document first."
        else:
            with st.spinner("🤖 Thinking..."):
                context = st.session_state['doc_content']
                response = ask_gemini(user_input, context)

        st.session_state.response = response
        st.session_state.history.append((user_input, response))
        status_placeholder.markdown(f"**🤖 Gemini:** {response}")
        speak_response(response)
    else:
        status_placeholder.warning("Could not understand your voice input.")
        st.session_state.response = ""

if st.button("⏹️ Stop"):
    stop_tts()
    st.session_state.paused = True
    status_placeholder.info("🔇 Speech output stopped.")

# End conversation
st.markdown("### ")
if st.button("🔚 End Conversation"):
    status_placeholder.info("Conversation ended. You may now close the app.")
    st.stop()

st.markdown("""
    <style>
    button[kind="primary"] {
        font-weight: bold;
        border-radius: 8px;
        padding: 0.6em 1.5em;
        font-size: 16px;
        margin: 0.3em;
        background-color: #262730 !important;
        color: #f0f0f5 !important;
        border: 1.5px solid #3a3f51 !important;
        transition: background-color 0.3s ease;
    }

    button[kind="primary"]:hover {
        background-color: #3a3f51 !important;
    }

    button[kind="secondary"] {
        background-color: #1f222d !important;
        color: #f0f0f5 !important;
        border: 1.5px solid #3a3f51 !important;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.6em 1.5em;
        font-size: 16px;
        margin: 0.3em;
        transition: background-color 0.3s ease;
        width: 100%;
    }
    button[kind="secondary"]:hover {
        background-color: #3a3f51 !important;
    }

    .stButton > button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)
