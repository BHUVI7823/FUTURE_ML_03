import streamlit as st
from google.cloud import dialogflow_v2 as dialogflow
import os
import base64

# Set Google Application Credentials (Service Account)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account.json"

# Dialogflow setup
DIALOGFLOW_PROJECT_ID = "customer-support-chatbot-nmaw"
SESSION_ID = "current-user-id"

# Function to detect intent
def detect_intent_texts(project_id, session_id, text, language_code='en'):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    return response.query_result.fulfillment_text

# Function to set background image
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
            color: white;
            text-shadow: 1px 1px 2px black;
        }}
        @media only screen and (max-width: 600px) {{
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

# Apply background
set_background("background.jpg")

# Title
st.markdown("<h1>🤖 Customer Support Chatbot</h1>", unsafe_allow_html=True)

# Chat history state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat input form
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message:")
    submitted = st.form_submit_button("Send")

# Chat response
if submitted and user_input:
    with st.spinner("Bot is typing..."):
        try:
            response = detect_intent_texts(DIALOGFLOW_PROJECT_ID, SESSION_ID, user_input)
            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("Bot", response))
        except Exception as e:
            st.error(f"Error: {e}")

# Show chat history
for sender, msg in st.session_state.chat_history:
    css_class = "user-message" if sender == "You" else "bot-message"
    st.markdown(f'<div class="chat-bubble {css_class}"><strong>{sender}:</strong> {msg}</div>', unsafe_allow_html=True)
