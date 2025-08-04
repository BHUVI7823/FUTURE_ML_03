import streamlit as st
from google.cloud import dialogflow_v2 as dialogflow
from google.oauth2 import service_account
import os
import base64
import tempfile
import json
import uuid

# --- Load credentials from secrets.toml ---
if "dialogflow" in st.secrets:
    credentials = service_account.Credentials.from_service_account_info(st.secrets["dialogflow"])
    session_client = dialogflow.SessionsClient(credentials=credentials)
else:
    st.error("Missing Dialogflow credentials in secrets.toml!")
    st.stop()

# --- Dialogflow Configuration ---
DIALOGFLOW_PROJECT_ID = st.secrets["dialogflow"]["project_id"]
SESSION_ID = str(uuid.uuid4())

def detect_intent_texts(project_id, session_id, text, language_code='en'):
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    return response.query_result.fulfillment_text

# --- Background Styling ---
def set_background(image_path):
    with open(image_path, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            min-height: 100vh;
            
        }}
        .chat-bubble {{
            background-color: rgba(255, 255, 255, 0.7);
            padding: 10px 15px;
            border-radius: 12px;
            margin: 10px 0;
            max-width: 80%;
            font-size: 16px;
            font-weight: 500;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.15);
        }}
        .user-message {{ text-align: right; color: #000; }}
        .bot-message {{ text-align: left; color: #000; }}
        h1 {{
            text-align: center;
            color: black;
            text-shadow: 1px 1px 2px black;
        }}
        @media only screen and (max-width: 600px) {{
        .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}"); 
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        min-height: 100vh;
        }}

            .chat-bubble {{
                font-size: 14px;
                max-width: 95%;
            }}
            h1 {{
                font-size: 28px;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# --- Set the background image ---
set_background("background.jpg")

# --- Page Title ---
st.markdown("<h1>🤖 Customer Support Chatbot</h1>", unsafe_allow_html=True)

# --- Chat History State ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Chat Form ---
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message:")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    with st.spinner("Bot is typing..."):
        response = detect_intent_texts(DIALOGFLOW_PROJECT_ID, SESSION_ID, user_input)
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Bot", response))

# --- Display Messages ---
for sender, msg in st.session_state.chat_history:
    css_class = "user-message" if sender == "You" else "bot-message"
    st.markdown(f'<div class="chat-bubble {css_class}"><strong>{sender}:</strong> {msg}</div>', unsafe_allow_html=True)
