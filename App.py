import streamlit as st
import asyncio
import edge_tts
import os
import re
import requests
from pydub import AudioSegment

# پیج سیٹنگز
st.set_page_config(page_title="Urdu TTS & Clone", page_icon="🎤", layout="wide")

# --- CSS for RTL ---
st.markdown("""
    <style>
    .urdu-text { direction: rtl; text-align: right; font-family: 'Urdu Typesetting', 'Tahoma', sans-serif; }
    textarea { direction: rtl !important; text-align: right !important; }
    </style>
    """, unsafe_allow_html=True)

# --- Functions ---
async def generate_asad_audio(full_script, base_speed, base_pitch):
    lines = full_script.split('\n')
    combined_audio = AudioSegment.empty()
    if not os.path.exists("temp"): os.makedirs("temp")
    
    for i, line in enumerate(lines):
        if not line.strip(): continue
        pause_match = re.search(r"\[Pause:\s*(\d+)s\]", line)
        clean_text = re.sub(r"\(.*?\)", "", line)
        clean_text = re.sub(r"\[.*?\]", "", clean_text).strip()
        
        if clean_text:
            temp_file = f"temp/part_{i}.mp3"
            rate_str = f"{'+' if base_speed >= 1 else ''}{int((base_speed-1)*100)}%"
            pitch_str = f"{'+' if base_pitch >= 0 else ''}{base_pitch}Hz"
            communicate = edge_tts.Communicate(clean_text, "ur-PK-AsadNeural", rate=rate_str, pitch=pitch_str)
            await communicate.save(temp_file)
            combined_audio += AudioSegment.from_mp3(temp_file)
            if os.path.exists(temp_file): os.remove(temp_file)

        if pause_match:
            seconds = int(pause_match.group(1))
            combined_audio += AudioSegment.silent(duration=seconds * 1000)
            
    final_output = "history_voice.mp3"
    combined_audio.export(final_output, format="mp3")
    return final_output

# --- Main UI ---
st.title("🎤 اردو وائس ماسٹر")

tab1, tab2 = st.tabs(["📜 ہسٹری نیریٹر (Asad Voice)", "👥 وائس کلوننگ (AI Clone)"])

# --- Tab 1: Original History Narrator ---
with tab1:
    st.header("پروفیشنل ہسٹری نیریٹر")
    st.info("یہ حصہ آپ کے اسکرپٹ سے بریکٹس نکال کر وقفے (Pauses) شامل کرے گا۔")
    
    user_script = st.text_area("اردو اسکرپٹ یہاں لکھیں:", height=250, key="txt1")
    
    col1, col2 = st.columns(2)
    with col1:
        speed = st.slider("رفتار", 0.5, 1.5, 0.9)
    with col2:
        pitch = st.slider("آواز کی گہرائی", -20, 10, -7)
        
    if st.button("وائس اوور تیار کریں"):
        if user_script:
            with st.spinner("آڈیو تیار ہو رہی ہے..."):
                try:
                    final_path = asyncio.run(generate_asad_audio(user_script, speed, pitch))
                    st.audio(final_path)
                    with open(final_path, "rb") as f:
                        st.download_button("ڈاؤن لوڈ کریں", f, "History_Voice.mp3")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.error("اسکرپٹ لکھیں!")

# --- Tab 2: Voice Cloning ---
with tab2:
    st.header("آواز کلوننگ (Hugging Face)")
    st.warning("اپنا درست ٹوکن نیچے درج کریں۔")
    
    # اپنا ٹوکن یہاں لکھیں
    HF_TOKEN = "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" 
    
    clone_audio = st.file_uploader("اپنی آواز اپ لوڈ کریں (Sample)", type=["wav", "mp3"])
    clone_text = st.text_area("کلون آواز کے لیے متن لکھیں:", height=150, key="txt2")
    
    if st.button("کلون آواز جنریٹ کریں"):
        if clone_audio and clone_text:
            with st.spinner("AI سرور آواز تیار کر رہا ہے..."):
                API_URL = "https://api-inference.huggingface.co/models/coqui/XTTS-v2"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                # آڈیو کو ہیگز یا بیس 64 میں بھیجنا ماڈل پر منحصر ہے، 
                # زیادہ تر انفرنس APIs کو براہ راست بائٹس چاہئیں ہوتی ہیں
                try:
                    audio_bytes = clone_audio.read()
                    # نوٹ: ہر ماڈل کی API پے لوڈ مختلف ہو سکتا ہے
                    response = requests.post(API_URL, headers=headers, json={"inputs": clone_text})
                    
                    if response.status_code == 200:
                        st.success("کلون آواز تیار ہے!")
                        st.audio(response.content)
                    elif response.status_code == 503:
                        st.warning("سرور ماڈل لوڈ کر رہا ہے، 20 سیکنڈ بعد دوبارہ ٹرائی کریں۔")
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"رابطے میں غلطی: {e}")
        else:
            st.error("فائل اور ٹیکسٹ دونوں ضروری ہیں۔")
