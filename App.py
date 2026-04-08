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
            # XTTS v2 عام طور پر JSON میں ٹیکسٹ اور فائل مانگتا ہے
            payload = {
                "inputs": text_input,
                "parameters": {"src_audio": audio_data.hex()} # یہ ماڈل کے حساب سے بدل سکتا ہے
            }

            try:
                response = requests.post(API_URL, headers=headers, json=payload)
                
                # اگر ماڈل ابھی لوڈ ہو رہا ہو (503 Error)
                if response.status_status == 503:
                    st.warning("ماڈل ابھی سرور پر لوڈ ہو رہا ہے، براہ کرم 30 سیکنڈ بعد دوبارہ کوشش کریں۔")
                
                elif response.status_code == 200:
                    st.success("آواز تیار ہے!")
                    st.audio(response.content, format="audio/wav")
                    st.download_button("ڈاؤن لوڈ کریں", response.content, "cloned_voice.wav")
                
                else:
                    st.error(f"سرور نے جواب نہیں دیا: {response.text}")
                    
            except Exception as e:
                st.error(f"رابطے میں غلطی: {e}")

# --- ہدایات ---
with st.expander("یہ کام کیسے کرتا ہے؟"):
    st.write("""
    1. یہ ایپ آپ کا ڈیٹا Hugging Face کے سرور پر بھیجتی ہے۔
    2. وہاں 'XTTS-v2' نامی ماڈل آپ کی آواز کا تجزیہ کرتا ہے۔
    3. اگر آپ کو 'Model Loading' کا میسج ملے تو پریشان نہ ہوں، سرور کو گرم ہونے میں وقت لگتا ہے۔
    """)
