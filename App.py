import streamlit as st
from gtts import gTTS
import os

# Page configuration
st.set_page_config(page_title="Urdu Text to Audio", page_icon="🎤")

# Custom CSS for Urdu (Right-to-Left alignment)
st.markdown("""
    <style>
    .urdu-text {
        direction: rtl;
        text-align: right;
        font-family: 'Urdu Typesetting', 'Tahoma', sans-serif;
        font-size: 20px;
    }
    textarea {
        direction: rtl !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎤 Urdu Text-to-Audio Converter")
st.write("Enter Urdu text below to convert it into speech.")

# Text input with RTL support
user_text = st.text_area("اردو عبارت یہاں لکھیں:", placeholder="مثال کے طور پر: آپ کیسے ہیں؟", height=200)

if st.button("Convert to Audio"):
    if user_text.strip() == "":
        st.warning("Please enter some text first!")
    else:
        with st.spinner("Generating audio..."):
            try:
                # Convert text to speech using gTTS
                tts = gTTS(text=user_text, lang='ur')
                filename = "output.mp3"
                tts.save(filename)

                # Play audio in the app
                audio_file = open(filename, 'rb')
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3')
                
                # Provide download button
                st.download_button(
                    label="Download MP3",
                    data=audio_bytes,
                    file_name="urdu_speech.mp3",
                    mime="audio/mp3"
                )
                
                audio_file.close()
                os.remove(filename) # Clean up the file
            except Exception as e:
                st.error(f"Error: {e}")
