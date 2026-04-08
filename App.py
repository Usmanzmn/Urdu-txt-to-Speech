try:
    import audioop
except ImportError:
    import audioop_lts as audioop
    import sys
    sys.modules['audioop'] = audioop

import streamlit as st

import asyncio
import edge_tts
import os
import re
from pydub import AudioSegment
import io

# پیج کی سیٹنگز
st.set_page_config(page_title="Urdu History Narrator", page_icon="📜")

# اردو کے لیے خاص ڈیزائن (RTL Support)
st.markdown("""
    <style>
    .urdu-text { direction: rtl; text-align: right; font-family: 'Urdu Typesetting', 'Tahoma', sans-serif; }
    textarea { direction: rtl !important; text-align: right !important; font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

# آڈیو پروسیسنگ کا فنکشن
async def generate_documentary_audio(full_script, base_speed, base_pitch):
    # اسکرپٹ کو لائنوں میں توڑنا
    lines = full_script.split('\n')
    combined_audio = AudioSegment.empty()
    
    # عارضی فولڈر بنانا
    if not os.path.exists("temp"):
        os.makedirs("temp")

    progress_bar = st.progress(0)
    total_lines = len(lines)

    for i, line in enumerate(lines):
        if not line.strip():
            continue
        
        # 1. خاموشی (Pause) تلاش کرنا: جیسے [Pause: 3s]
        pause_match = re.search(r"\[Pause:\s*(\d+)s\]", line)
        
        # 2. بریکٹس والی ہدایات کو متن سے صاف کرنا تاکہ وہ بولی نہ جائیں
        clean_text = re.sub(r"\(.*?\)", "", line) # (...) ختم کریں
        clean_text = re.sub(r"\[.*?\]", "", clean_text).strip() # [...] ختم کریں
        
        # اگر لائن میں اردو متن موجود ہے
        if clean_text:
            temp_file = f"temp/part_{i}.mp3"
            rate_str = f"{'+' if base_speed >= 1 else ''}{int((base_speed-1)*100)}%"
            pitch_str = f"{'+' if base_pitch >= 0 else ''}{base_pitch}Hz"
            
            # Asad کی آواز (Male Narrator) استعمال ہو رہی ہے
            communicate = edge_tts.Communicate(clean_text, "ur-PK-AsadNeural", rate=rate_str, pitch=pitch_str)
            await communicate.save(temp_file)
            
            # آڈیو کو مین فائل میں جوڑنا
            segment = AudioSegment.from_mp3(temp_file)
            combined_audio += segment
            os.remove(temp_file) # عارضی فائل ڈیلیٹ کرنا

        # 3. اگر لائن میں Pause کی ہدایت تھی تو خاموشی ڈالنا
        if pause_match:
            seconds = int(pause_match.group(1))
            silence = AudioSegment.silent(duration=seconds * 1000) # milliseconds میں
            combined_audio += silence
        
        progress_bar.progress((i + 1) / total_lines)

    # فائنل آڈیو کو محفوظ کرنا
    final_output = "narrator_final.mp3"
    combined_audio.export(final_output, format="mp3")
    return final_output

# --- انٹر فیس (UI) ---
st.title("📜 پروفیشنل اردو ہسٹری نیریٹر")
st.write("اپنا اسکرپٹ نیچے لکھیں، ایپ خود بخود ہدایات اور وقفوں کو مینیج کر لے گی۔")

# ان پٹ ایریا
user_input = st.text_area("اردو اسکرپٹ یہاں پیسٹ کریں:", placeholder="مثال: (سنجیدہ آواز) برلن کی دیوار... [Pause: 3s]", height=300)

# سیٹنگز
st.sidebar.header("آواز کی سیٹنگز")
speed = st.sidebar.slider("بولنے کی رفتار (Speed)", 0.5, 1.5, 0.9, 0.1)
pitch = st.sidebar.slider("آواز کی گہرائی (Pitch) - کم کریں تو آواز بوڑھی ہوگی", -20, 10, -7, 1)

if st.button("وائس اوور تیار کریں"):
    if user_input.strip() == "":
        st.warning("براہ کرم پہلے اسکرپٹ لکھیں۔")
    else:
        with st.spinner("آپ کی دستاویزی فلم کی آواز تیار ہو رہی ہے..."):
            try:
                final_audio_path = asyncio.run(generate_documentary_audio(user_input, speed, pitch))
                
                # آڈیو پلیئر دکھانا
                st.success("وائس اوور مکمل ہو گیا!")
                with open(final_audio_path, "rb") as audio_file:
                    st.audio(audio_file.read(), format="audio/mp3")
                
                # ڈاؤن لوڈ بٹن
                with open(final_audio_path, "rb") as audio_file:
                    st.download_button("ڈاؤن لوڈ کریں MP3", audio_file, file_name="Urdu_Narrator.mp3")
            
            except Exception as e:
                st.error(f"کوئی غلطی ہوئی ہے: {e}")
# پہلے سے موجود امپورٹس کے ساتھ یہ بھی شامل کریں
import requests

# ٹیبز بنائیں تاکہ ایپ صاف ستھری لگے
tab1, tab2 = st.tabs(["📜 ہسٹری نیریٹر (Asad)", "👥 آواز کلوننگ (Voice Clone)"])

with tab1:
    # یہاں آپ کا پرانا والا اسکرپٹ والا کوڈ آئے گا (Asad Voice)
    pass

with tab2:
    st.header("اپنی آواز کلون کریں")
    st.write("اپنی آواز کا 10 سے 20 سیکنڈ کا کلپ (WAV/MP3) اپ لوڈ کریں اور جادو دیکھیں!")
    
    uploaded_voice = st.file_uploader("اپنی آواز اپ لوڈ کریں", type=["wav", "mp3"])
    clone_text = st.text_area("وہ متن لکھیں جو آپ اپنی آواز میں سننا چاہتے ہیں:")
    
    if st.button("کلون آواز میں تبدیل کریں"):
        if uploaded_voice and clone_text:
            st.info("مفت سرور پر پروسیسنگ ہو رہی ہے، اس میں 1 سے 2 منٹ لگ سکتے ہیں...")
            # یہاں ہم کلوننگ کا لاجک لکھیں گے
        else:
            st.error("براہ کرم آواز کی فائل اور متن دونوں فراہم کریں۔")
