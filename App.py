import streamlit as st
import asyncio
import edge_tts
import os

# Page configuration
st.set_page_config(page_title="Urdu History Narrator", page_icon="📜")

# Custom CSS for Urdu RTL
st.markdown("""
    <style>
    .urdu-text { direction: rtl; text-align: right; font-family: 'Urdu Typesetting', 'Tahoma', sans-serif; }
    textarea { direction: rtl !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📜 Urdu Story & History Narrator")
st.write("Convert your scripts into a deep male narrator voice.")

# Sidebar for Voice Tuning
st.sidebar.header("Voice Settings")
speed = st.sidebar.slider("Talking Speed", 0.5, 1.5, 1.0, 0.1)
pitch = st.sidebar.slider("Voice Pitch (Lower = Older)", -20, 20, -5, 1)

# Text input
user_text = st.text_area("اردو اسکرپٹ یہاں لکھیں:", placeholder="ایک دفعہ کا ذکر ہے کہ...", height=250)

# Function to handle the async edge-tts logic
async def generate_audio(text, speed_val, pitch_val):
    # Format speed and pitch for edge-tts (e.g., "+10%", "-5Hz")
    rate_str = f"{'+' if speed_val >= 1 else ''}{int((speed_val-1)*100)}%"
    pitch_str = f"{'+' if pitch_val >= 0 else ''}{pitch_val}Hz"
    
    # ur-PK-AsadNeural is the best Male Urdu voice available
    communicate = edge_tts.Communicate(text, "ur-PK-AsadNeural", rate=rate_str, pitch=pitch_str)
    await communicate.save("output.mp3")

if st.button("Generate Narrator Voice"):
    if user_text.strip() == "":
        st.warning("Please enter your script first!")
    else:
        with st.spinner("The narrator is preparing..."):
            try:
                # Run the async function
                asyncio.run(generate_audio(user_text, speed, pitch))
                
                # Display audio player
                with open("output.mp3", "rb") as f:
                    st.audio(f.read(), format="audio/mp3")
                
                # Download button
                with open("output.mp3", "rb") as f:
                    st.download_button("Download Audio", f, "narrator_voice.mp3")
                
            except Exception as e:
                st.error(f"Error: {e}")
