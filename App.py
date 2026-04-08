import streamlit as st
import asyncio
import edge_tts
import os
import re
import glob
from pydub import AudioSegment

# Page Configuration
st.set_page_config(page_title="Professional Urdu History Narrator", page_icon="📜")

def cleanup_old_files():
    files = glob.glob("*.mp3") + glob.glob("temp/*.mp3")
    for f in files:
        try:
            os.remove(f)
        except:
            pass

if "cleaned" not in st.session_state:
    cleanup_old_files()
    st.session_state.cleaned = True

st.markdown("""
    <style>
    .urdu-text { direction: rtl; text-align: right; font-family: 'Urdu Typesetting', 'Tahoma', sans-serif; }
    textarea { direction: rtl !important; text-align: right !important; font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

if "audio_path" not in st.session_state:
    st.session_state.audio_path = None

async def generate_history_audio(full_script, base_speed, base_pitch, voice_choice, is_kid):
    lines = [l.strip() for l in full_script.split('\n') if l.strip()]
    combined_audio = AudioSegment.empty()
    
    if not os.path.exists("temp"):
        os.makedirs("temp")

    progress_bar = st.progress(0)
    
    # Usman کی آواز کے لیے پچ کو محفوظ حد میں رکھنا
    is_usman = "Imran" in voice_choice
    final_pitch = base_pitch + 15 if is_kid else base_pitch

    for i, line in enumerate(lines):
        pause_match = re.search(r"\[Pause:\s*(\d+)s\]", line)
        clean_text = re.sub(r"\(.*?\)", "", line)
        clean_text = re.sub(r"\[.*?\]", "", clean_text).strip()
        
        if clean_text:
            temp_file = f"temp/part_{i}.mp3"
            
            # ری ٹرائی لاجک: پہلے آپ کی سیٹنگز، پھر ڈیفالٹ
            settings_to_try = [
                {"rate": f"{'+' if base_speed >= 1 else ''}{int((base_speed-1)*100)}%", "pitch": f"{'+' if final_pitch >= 0 else ''}{final_pitch}Hz"},
                {"rate": "+0%", "pitch": "+0Hz"} # اگر فیل ہو تو ڈیفالٹ پر جائے گا
            ]
            
            success = False
            for setting in settings_to_try:
                try:
                    communicate = edge_tts.Communicate(clean_text, voice_choice, rate=setting["rate"], pitch=setting["pitch"])
                    await communicate.save(temp_file)
                    
                    if os.path.exists(temp_file) and os.path.getsize(temp_file) > 500: # 500 bytes سے بڑی فائل ہونی چاہیے
                        segment = AudioSegment.from_mp3(temp_file)
                        combined_audio += segment
                        os.remove(temp_file)
                        success = True
                        break
                except:
                    continue
            
            if not success:
                st.warning(f"لائن {i+1} پر آڈیو نہیں بن سکی۔")

        if pause_match:
            seconds = int(pause_match.group(1))
            combined_audio += AudioSegment.silent(duration=seconds * 1000)
        
        progress_bar.progress((i + 1) / len(lines))

    if len(combined_audio) > 0:
        final_output = f"narrator_{os.urandom(4).hex()}.mp3"
        combined_audio.export(final_output, format="mp3")
        return final_output
    return None

# --- UI ---
st.title("📜 Professional Urdu History Narrator")
st.subheader("پروفیشنل اردو ہسٹری نیریٹر")

st.write("Paste your script below. The app will remove instructions and add pauses automatically.")
st.write("اپنا اسکرپٹ یہاں پیسٹ کریں۔ ایپ خود بخود ہدایات صاف کر کے وقفے شامل کر دے گی۔")

user_input = st.text_area("Urdu Script / اردو اسکرپٹ:", height=300)

# Sidebar
st.sidebar.header("Settings / سیٹنگز")
voice_map = {
    "Asad (Man/مرد)": "ur-PK-AsadNeural",
    "Usman (Deep/جاندار)": "ur-PK-ImranNeural", 
    "Uzma (Woman/خاتون)": "ur-PK-UzmaNeural",
    "Child (Kid/بچہ)": "ur-PK-UzmaNeural"
}
selected_label = st.sidebar.selectbox("Select Narrator / آواز منتخب کریں", list(voice_map.keys()))
selected_code = voice_map[selected_label]

is_kid = "Child" in selected_label
speed = st.sidebar.slider("Speech Rate / بولنے کی رفتار", 0.7, 1.3, 0.9, 0.1)
pitch = st.sidebar.slider("Voice Pitch / آواز کی گہرائی", -20, 20, -8, 1)

if st.button("Generate Voiceover / وائس اوور تیار کریں"):
    if user_input.strip():
        cleanup_old_files()
        with st.spinner("Processing..."):
            try:
                path = asyncio.run(generate_history_audio(user_input, speed, pitch, selected_code, is_kid))
                if path:
                    st.session_state.audio_path = path
                    st.success("Ready! / تیار ہے")
                else:
                    st.error("Fatal Error: Server rejected all attempts.")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.error("Enter Script!")

if st.session_state.audio_path and os.path.exists(st.session_state.audio_path):
    st.markdown("---")
    st.audio(st.session_state.audio_path)
    with open(st.session_state.audio_path, "rb") as f:
        st.download_button("Download MP3 / ڈاؤن لوڈ کریں", f, file_name="Urdu_Narrator.mp3")
