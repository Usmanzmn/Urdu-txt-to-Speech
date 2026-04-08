import streamlit as st
import asyncio
import edge_tts
import os
import re
from pydub import AudioSegment

# آڈیو فائلیں رکھنے کے لیے فولڈر
TEMP_DIR = "temp_audio"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

async def process_script(full_script, voice_name, base_speed, base_pitch):
    # اسکرپٹ کو لائنوں میں تقسیم کرنا
    lines = full_script.split('\n')
    combined_audio = AudioSegment.empty()
    
    for i, line in enumerate(lines):
        if not line.strip():
            continue
            
        # 1. خاموشی (Pause) چیک کرنا: [Pause: 3s]
        pause_match = re.search(r"\[Pause:\s*(\d+)s\]", line)
        
        # 2. آواز کی ہدایات صاف کرنا: (Low Tone) وغیرہ
        clean_text = re.sub(r"\(.*?\)", "", line) # گول بریکٹ ختم
        clean_text = re.sub(r"\[.*?\]", "", clean_text).strip() # چوکور بریکٹ ختم
        
        if clean_text:
            # آڈیو جنریٹ کریں
            filename = f"{TEMP_DIR}/part_{i}.mp3"
            rate_str = f"{'+' if base_speed >= 1 else ''}{int((base_speed-1)*100)}%"
            pitch_str = f"{'+' if base_pitch >= 0 else ''}{base_pitch}Hz"
            
            communicate = edge_tts.Communicate(clean_text, voice_name, rate=rate_str, pitch=pitch_str)
            await communicate.save(filename)
            
            # آڈیو لوڈ کریں اور مین فائل میں جوڑیں
            segment = AudioSegment.from_mp3(filename)
            combined_audio += segment
            os.remove(filename)

        # اگر لائن میں خاموشی کی ہدایت تھی
        if pause_match:
            seconds = int(pause_match.group(1))
            silence = AudioSegment.silent(duration=seconds * 1000)
            combined_audio += silence

    final_path = "final_documentary.mp3"
    combined_audio.export(final_path, format="mp3")
    return final_path

# --- Streamlit UI ---
st.title("📜 Professional Urdu Documentary Maker")
st.info("یہ ایپ آپ کے بریکٹس [Pause] اور (Tone) کو سمجھ کر پروفیشنل آڈیو بنائے گی۔")

user_script = st.text_area("اپنا اسکرپٹ یہاں پیسٹ کریں:", height=300)

col1, col2 = st.columns(2)
with col1:
    speed = st.slider("رفتار (Speed)", 0.7, 1.3, 0.9)
with col2:
    pitch = st.slider("آواز کی گہرائی (Pitch/Deepness)", -20, 10, -8)

if st.button("پروفیشنل وائس اوور تیار کریں"):
    if user_script:
        with st.spinner("دستاویزی فلم تیار ہو رہی ہے، براہ کرم انتظار کریں..."):
            final_file = asyncio.run(process_script(user_script, "ur-PK-AsadNeural", speed, pitch))
            
            st.success("آپ کا وائس اوور تیار ہے!")
            st.audio(final_file)
            
            with open(final_file, "rb") as f:
                st.download_button("ڈاؤن لوڈ کریں", f, file_name="Berlin_Wall_Urdu.mp3")
    else:
        st.error("پہلے اسکرپٹ لکھیں!")
