import streamlit as st
import asyncio
import edge_tts
import os
import re
import glob
from pydub import AudioSegment

# Page Configuration
st.set_page_config(page_title="Urdu History Narrator", page_icon="📜")

# 1. فنکشن: پرانی فائلیں ڈیلیٹ کرنے کے لیے
def cleanup_old_files():
    # تمام عارضی فائلیں اور فائنل آڈیو فائلیں ڈھونڈ کر ڈیلیٹ کرنا
    files = glob.glob("*.mp3") + glob.glob("temp/*.mp3")
    for f in files:
        try:
            os.remove(f)
        except:
            pass

# ایپ اسٹارٹ ہوتے ہی صفائی کرنا
if "cleaned" not in st.session_state:
    cleanup_old_files()
    st.session_state.cleaned = True

# CSS for RTL and Styling
st.markdown("""
    <style>
    .urdu-text { direction: rtl; text-align: right; font-family: 'Urdu Typesetting', 'Tahoma', sans-serif; }
    textarea { direction: rtl !important; text-align: right !important; font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

if "audio_path" not in st.session_state:
    st.session_state.audio_path = None

async def generate_history_audio(full_script, base_speed, base_pitch, voice_choice, is_kid):
    lines = full_script.split('\n')
    combined_audio = AudioSegment.empty()
    
    if not os.path.exists("temp"):
        os.makedirs("temp")

    progress_bar = st.progress(0)
    total_lines = len(lines)

    # بچے کے لیے پچ ایڈجسٹمنٹ
    final_pitch = base_pitch + 15 if is_kid else base_pitch

    for i, line in enumerate(lines):
        if not line.strip(): continue
        
        pause_match = re.search(r"\[Pause:\s*(\d+)s\]", line)
        clean_text = re.sub(r"\(.*?\)", "", line)
        clean_text = re.sub(r"\[.*?\]", "", clean_text).strip()
        
        if clean_text:
            temp_file = f"temp/part_{i}.mp3"
            rate_str = f"{'+' if base_speed >= 1 else ''}{int((base_speed-1)*100)}%"
            pitch_str = f"{'+' if final_pitch >= 0 else ''}{final_pitch}Hz"
            
            communicate = edge_tts.Communicate(clean_text, voice_choice, rate=rate_str, pitch=pitch_str)
            await communicate.save(temp_file)
            
            segment = AudioSegment.from_mp3(temp_file)
            combined_audio += segment
            if os.path.exists(temp_file): os.remove(temp_file)

        if pause_match:
            seconds = int(pause_match.group(1))
            combined_audio += AudioSegment.silent(duration=seconds * 1000)
        
        progress_bar.progress((i + 1) / total_lines)

    # ہر یوزر کے لیے منفرد نام تاکہ اوور لیپ نہ ہو
    final_output = f"narrator_{os.urandom(4).hex()}.mp3"
    combined_audio.export(final_output, format="mp3")
    return final_output

# --- UI ---
st.title("📜 Professional Urdu History Narrator")
st.subheader("پروفیشنل اردو ہسٹری نیریٹر")

st.write("Paste your script below. The app will remove instructions and add pauses automatically.")

user_input = st.text_area("Urdu Script / اردو اسکرپٹ:", height=300)

# Sidebar Settings
st.sidebar.header("Settings / سیٹنگز")
voice_map = {
    "Asad (Man/مرد)": "ur-PK-AsadNeural",
    "Uzma (Woman/خاتون)": "ur-PK-UzmaNeural",
    "Child (Kid/بچہ)": "ur-PK-UzmaNeural"
}
selected_voice_label = st.sidebar.selectbox("Select Narrator / آواز منتخب کریں", list(voice_map.keys()))
selected_voice_code = voice_map[selected_voice_label]

is_kid = True if "Child" in selected_voice_label else False

speed = st.sidebar.slider("Speech Rate / بولنے کی رفتار", 0.7, 1.3, 0.9, 0.1)
pitch = st.sidebar.slider("Voice Pitch / آواز کی گہرائی", -20, 20, -8, 1)

if st.button("Generate Voiceover / وائس اوور تیار کریں"):
    if user_input.strip():
        # نیا جنریشن شروع کرنے سے پہلے پرانی فائلیں صاف کرنا
        cleanup_old_files()
        with st.spinner("Processing... / آڈیو تیار ہو رہی ہے"):
            try:
                st.session_state.audio_path = asyncio.run(generate_history_audio(user_input, speed, pitch, selected_voice_code, is_kid))
                st.success("Ready! / تیار ہے")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.error("Enter Script!")

if st.session_state.audio_path and os.path.exists(st.session_state.audio_path):
    st.markdown("---")
    st.audio(st.session_state.audio_path)
    with open(st.session_state.audio_path, "rb") as f:
        st.download_button("Download MP3 / ڈاؤن لوڈ کریں", f, file_name="Urdu_Narrator.mp3")
