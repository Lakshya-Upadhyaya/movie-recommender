import streamlit as st
import requests
import re
import time

st.title("📽️ Movie Chat Assistant")


def decode_unicode_escapes(text):
    if isinstance(text, str):
        return bytes(text, "utf-8").decode("unicode_escape")
    return text

if "messages" not in st.session_state:
    st.session_state.messages = []

if 'greeted' not in st.session_state:
    st.session_state['greeted'] = True
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hi there! I'm your Movie Assistant. Ask me for recommendations based on your mood, genre, or favorite actors! 🍿"
    })


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask about movies...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        api_url = "ngrok/response"
        response = requests.post(api_url, json={"query": prompt})

        if response.ok:
            raw_output = response.json().get("response", "Sorry, no valid response from API.")

            # Decode any escaped Unicode sequences
            raw_output = decode_unicode_escapes(raw_output)

            # Remove corrupted bullet symbols (if present)
            raw_output = raw_output.replace("â¢", "")

 
            formatted_output = re.sub(r'\s*"(.*?)"', r'\n**\1**', raw_output)


            formatted_output = (
                formatted_output.replace("Title:","**Title:** ")
                                .replace("Release Date:", "\n  **Release Date:**")
                                .replace("Description:", "\n  **Description:**")
                                .replace("Starring:", "\n  **Starring:**")
                                .replace("Directed by:", "\n  **Directed by:**")
                                .replace("Produced by:", "\n  **Produced by:**")
            )
        else:
            formatted_output = "Error: API request failed."

    except Exception as e:
        formatted_output = f"Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": formatted_output})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        display_text = ""
        
        for char in formatted_output:
            display_text += char
            message_placeholder.markdown(display_text)
            time.sleep(0.02)
