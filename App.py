import streamlit as st
import asyncio
import edge_tts
import os
import re
from pydub import AudioSegment

# Page Configuration
st.set_page_config(page_title="Urdu Voice Studio", page_icon="🎤")

# Combined English and Urdu CSS for RTL support
st.markdown("""
    <style>
    .urdu-text { direction: rtl; text-align: right; font-family: 'Urdu Typesetting', 'Tahoma', sans-serif; }
    textarea { direction: rtl !important; text-align: right !important; font-size: 18px !important; }
    .stTitle { text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# Function to generate audio
async def generate_history_audio(full_script, base_speed, base_pitch, voice_choice):
    lines = full_script.split('\n')
    combined_audio = AudioSegment.empty()
    
    if not os.path.exists("temp"):
        os.makedirs("temp")

    progress_bar = st.progress(0)
    total_lines = len(lines)

    for i, line in enumerate(lines):
        if not line.strip():
            continue
        
        # Search for pauses like [Pause: 3s]
        pause_match = re.search(r"\[Pause:\s*(\d+)s\]", line)
        
        # Clean the text from brackets and instructions
        clean_text = re.sub(r"\(.*?\)", "", line)
        clean_text = re.sub(r"\[.*?\]", "", clean_text).strip()
        
        if clean_text:
            temp_file = f"temp/part_{i}.mp3"
            rate_str = f"{'+' if base_speed >= 1 else ''}{int((base_speed-1)*100)}%"
            pitch_str = f"{'+' if base_pitch >= 0 else ''}{base_pitch}Hz"
            
            communicate = edge_tts.Communicate(clean_text, voice_choice, rate=rate_str, pitch=pitch_str)
            await communicate.save(temp_file)
            
            segment = AudioSegment.from_mp3(temp_file)
            combined_audio += segment
            if os.path.exists(temp_file):
                os.remove(temp_file)

        if pause_match:
            seconds = int(pause_match.group(1))
            combined_audio += AudioSegment.silent(duration=seconds * 1000)
        
        progress_bar.progress((i + 1) / total_lines)

    final_output = "narrator_final.mp3"
    combined_audio.export(final_output, format="mp3")
    return final_output

# --- UI Layout ---
st.title("📜 Professional Urdu Voice Studio")
st.subheader("پروفیشنل اردو آواز اسٹوڈیو")

# Main Input
user_input = st.text_area("Urdu Script / اردو اسکرپٹ:", 
                         placeholder="مثال: (سنجیدہ آواز) برلن کی دیوار... [Pause: 3s]", 
                         height=300)

# Sidebar Settings
st.sidebar.header("Voice Settings / آواز کی ترتیبات")

# Voice Selection Dropdown
voice_map = {
    "Asad (Man/مرد)": "ur-PK-AsadNeural",
    "Uzma (Woman/خاتون)": "ur-PK-UzmaNeural",
    "Child (Kid/بچہ)": "ur-IN-GulNeural" # Note: Gul is a softer, high-pitched voice often used for kids/teens
}
selected_voice_label = st.sidebar.selectbox("Select Narrator / آواز منتخب کریں", list(voice_map.keys()))
selected_voice_code = voice_map[selected_voice_label]

speed = st.sidebar.slider("Speech Rate / بولنے کی رفتار", 0.7, 1.3, 0.9, 0.1)
pitch = st.sidebar.slider("Voice Pitch / آواز کی گہرائی", -20, 10, -5, 1)

if st.button("Generate Voiceover / وائس اوور تیار کریں"):
    if user_input.strip():
        with st.spinner("Processing Audio... / آڈیو تیار ہو رہی ہے"):
            try:
                final_path = asyncio.run(generate_history_audio(user_input, speed, pitch, selected_voice_code))
                st.success("Voiceover Ready! / وائس اوور تیار ہے")
                st.audio(final_path)
                with open(final_path, "rb") as f:
                    st.download_button("Download MP3 / ڈاؤن لوڈ کریں", f, file_name="Urdu_Narrator.mp3")
            except Exception as e:
                st.error(f"Error / غلطی: {e}")
    else:
        st.error("Please enter a script! / پہلے اسکرپٹ درج کریں")
# Check if audio exists in memory and display it
if st.session_state.audio_path and os.path.exists(st.session_state.audio_path):
    st.markdown("---")
    st.audio(st.session_state.audio_path)
    
    with open(st.session_state.audio_path, "rb") as f:
        st.download_button(
            label="Download MP3",
            data=f,
            file_name="Urdu_Narrator.mp3",
            mime="audio/mp3"
        )
