import streamlit as st
import requests
import time

# --- سیٹنگز ---
# اپنا ٹوکن یہاں لکھیں
HF_TOKEN = "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"
API_URL = "https://api-inference.huggingface.co/models/coqui/XTTS-v2"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

st.set_page_config(page_title="Urdu Voice Cloner", page_icon="🎤")

# --- UI ---
st.title("🎤 مفت اردو وائس کلوننگ (Hugging Face)")
st.info("نوٹ: پہلی بار ماڈل لوڈ ہونے میں 2 سے 5 منٹ لگ سکتے ہیں۔")

# آواز اپ لوڈ کریں
uploaded_file = st.file_uploader("اپنی آواز کا نمونہ (WAV/MP3) اپ لوڈ کریں", type=["wav", "mp3"])

# متن لکھیں
text_input = st.text_area("اردو اسکرپٹ یہاں لکھیں:", placeholder="مثال: برلن کی دیوار ایک عظیم تاریخ رکھتی ہے۔", height=150)

if st.button("کلون آواز تیار کریں"):
    if not uploaded_file or not text_input:
        st.error("براہ کرم آواز اور متن دونوں فراہم کریں۔")
    else:
        with st.spinner("سرور آواز تیار کر رہا ہے..."):
            # آڈیو فائل کو ریڈ کریں
            audio_data = uploaded_file.read()
            
            # Hugging Face API کو ڈیٹا بھیجنا
            payload = {
                "inputs": text_input,
                "parameters": {"src_audio": audio_data.hex()} 
            }

            try:
                response = requests.post(API_URL, headers=headers, json=payload)
                
                # --- یہاں غلطی تھی، اب یہ ٹھیک ہے ---
                if response.status_code == 503:
                    st.warning("ماڈل ابھی سرور پر لوڈ ہو رہا ہے، براہ کرم 30 سیکنڈ بعد دوبارہ کوشش کریں۔")
                
                elif response.status_code == 200:
                    st.success("آواز تیار ہے!")
                    st.audio(response.content, format="audio/wav")
                    st.download_button("ڈاؤن لوڈ کریں", response.content, "cloned_voice.wav")
                
                else:
                    st.error(f"سرور کا جواب (Error {response.status_code}): {response.text}")
                    
            except Exception as e:
                st.error(f"رابطے میں غلطی: {e}")

# --- ہدایات ---
with st.expander("اگر آواز جنریٹ نہ ہو تو کیا کریں؟"):
    st.write("""
    1. **Error 503:** اس کا مطلب ہے کہ Hugging Face کا سرور ابھی سویا ہوا ہے، وہ ماڈل لوڈ کر رہا ہے۔ 1 منٹ بعد دوبارہ بٹن دبائیں۔
    2. **Error 4xx:** اس کا مطلب ہے کہ ٹوکن یا ماڈل کے لنک میں مسئلہ ہے۔
    3. **بہترین مشورہ:** اگر یہ یہاں کام نہ کرے، تو Hugging Face پر اپنی 'Space' بنائیں، وہاں یہ 100% چلے گا۔
    """)
