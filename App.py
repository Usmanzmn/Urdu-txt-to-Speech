import streamlit as st
import asyncio
import edge_tts
import os
import re
from pydub import AudioSegment

# پیج کی بنیادی سیٹنگ
st.set_page_config(page_title="Urdu History Narrator", page_icon="📜")

# اردو RTL سپورٹ کے لیے ڈیزائن
st.markdown("""
    <style>
    .urdu-text { direction: rtl; text-align: right; font-family: 'Urdu Typesetting', 'Tahoma', sans-serif; }
    textarea { direction: rtl !important; text-align: right !important; font-size: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

# آڈیو جنریشن کا فنکشن
async def generate_history_audio(full_script, base_speed, base_pitch):
    lines = full_script.split('\n')
    combined_audio = AudioSegment.empty()
    
    if not os.path.exists("temp"):
        os.makedirs("temp")

    progress_bar = st.progress(0)
    total_lines = len(lines)

    for i, line in enumerate(lines):
        if not line.strip():
            continue
        
        # خاموشی (Pause) تلاش کرنا: [Pause: 3s]
        pause_match = re.search(r"\[Pause:\s*(\d+)s\]", line)
        
        # بریکٹس اور ہدایات کو صاف کرنا
        clean_text = re.sub(r"\(.*?\)", "", line)
        clean_text = re.sub(r"\[.*?\]", "", clean_text).strip()
        
        if clean_text:
            temp_file = f"temp/part_{i}.mp3"
            # رفتار اور پچ کی سیٹنگ
            rate_str = f"{'+' if base_speed >= 1 else ''}{int((base_speed-1)*100)}%"
            pitch_str = f"{'+' if base_pitch >= 0 else ''}{base_pitch}Hz"
            
            communicate = edge_tts.Communicate(clean_text, "ur-PK-AsadNeural", rate=rate_str, pitch=pitch_str)
            await communicate.save(temp_file)
            
            segment = AudioSegment.from_mp3(temp_file)
            combined_audio += segment
            os.remove(temp_file)

        if pause_match:
            seconds = int(pause_match.group(1))
            combined_audio += AudioSegment.silent(duration=seconds * 1000)
        
        progress_bar.progress((i + 1) / total_lines)

    final_output = "narrator_final.mp3"
    combined_audio.export(final_output, format="mp3")
    return final_output

# --- UI ---
st.title("📜 پروفیشنل اردو ہسٹری نیریٹر")
st.write("اپنا اسکرپٹ یہاں پیسٹ کریں، ایپ خود بخود بریکٹس صاف کر کے وقفے شامل کر دے گی۔")

user_input = st.text_area("اردو اسکرپٹ یہاں لکھیں:", placeholder="مثال: (سنجیدہ آواز) برلن کی دیوار... [Pause: 3s]", height=300)

st.sidebar.header("سیٹنگز")
speed = st.sidebar.slider("بولنے کی رفتار", 0.7, 1.3, 0.9, 0.1)
pitch = st.sidebar.slider("آواز کی گہرائی (Pitch)", -20, 10, -8, 1)

if st.button("وائس اوور تیار کریں"):
    if user_input.strip():
        with st.spinner("آڈیو پروسیسنگ ہو رہی ہے..."):
            try:
                final_path = asyncio.run(generate_history_audio(user_input, speed, pitch))
                st.success("آپ کا وائس اوور تیار ہے!")
                st.audio(final_path)
                with open(final_path, "rb") as f:
                    st.download_button("ڈاؤن لوڈ کریں MP3", f, file_name="Urdu_Narrator.mp3")
            except Exception as e:
                st.error(f"ایرر: {e}")
    else:
        st.error("پہلے اسکرپٹ درج کریں!")
