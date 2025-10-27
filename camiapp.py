import os
import time
import glob
import cv2
import numpy as np
import pytesseract
import streamlit as st
from PIL import Image
from gtts import gTTS
from googletrans import Translator



def text_to_speech(input_language, output_language, text, tld):
    """Traduce el texto y lo convierte en audio."""
    translation = translator.translate(text, src=input_language, dest=output_language)
    translated_text = translation.text
    file_name = text[:20] if text else "audio"
    file_path = f"temp/{file_name}.mp3"

    tts = gTTS(translated_text, lang=output_language, tld=tld, slow=False)
    tts.save(file_path)

    return file_name, translated_text


def remove_old_files(days):
    """Elimina archivos de audio antiguos según la antigüedad (en días)."""
    mp3_files = glob.glob("temp/*.mp3")
    if not mp3_files:
        return

    now = time.time()
    limit = days * 86400  
    for f in mp3_files:
        if os.stat(f).st_mtime < now - limit:
            os.remove(f)
            print("Eliminado:", f)



remove_old_files(7)


st.title("🧠 Reconocimiento Óptico de Caracteres (OCR)")
st.subheader("Selecciona si deseas usar la cámara o cargar una imagen desde tu dispositivo.")

text = " "


use_camera = st.checkbox("📷 Usar cámara")
if use_camera:
    img_file_buffer = st.camera_input("Toma una foto para analizar")
else:
    img_file_buffer = None


with st.sidebar:
    st.subheader(" Opciones de procesamiento")
    filtro = st.radio("Aplicar filtro de inversión:", ("Sí", "No"))


uploaded_img = st.file_uploader(" Cargar imagen:", type=["png", "jpg", "jpeg"])
if uploaded_img is not None:
    st.image(uploaded_img, caption="Imagen cargada", use_container_width=True)

    with open(uploaded_img.name, "wb") as f:
        f.write(uploaded_img.read())

    st.success(f"Imagen guardada como **{uploaded_img.name}**")

    img_cv = cv2.imread(uploaded_img.name)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    st.subheader("📝 Texto detectado:")
    st.write(text)


if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    if filtro == "Sí":
        cv2_img = cv2.bitwise_not(cv2_img)

    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    st.subheader(" Texto detectado:")
    st.write(text)

# --- Sidebar: parámetros de traducción y voz ---
with st.sidebar:
    st.subheader(" Parámetros de traducción y voz")

    os.makedirs("temp", exist_ok=True)
    translator = Translator()

    LANGUAGES = {
        "Inglés": "en",
        "Español": "es",
        "Bengalí": "bn",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja",
    }

    ACCENTS = {
        "Predeterminado": "com",
        "India": "co.in",
        "Reino Unido": "co.uk",
        "Estados Unidos": "com",
        "Canadá": "ca",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za",
    }

    in_lang = st.selectbox(" Lengua original", list(LANGUAGES.keys()))
    out_lang = st.selectbox(" Lenguaje de salida", list(LANGUAGES.keys()))
    accent = st.selectbox(" Acento del audio", list(ACCENTS.keys()))

    input_language = LANGUAGES[in_lang]
    output_language = LANGUAGES[out_lang]
    tld = ACCENTS[accent]

    display_output_text = st.checkbox("Mostrar texto traducido")

    if st.button("🎤 Transformar texto a voz"):
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown("## 🔈 Tu audio generado:")
        st.audio(audio_bytes, format="audio/mp3")

        if display_output_text:
            st.markdown("## Texto traducido:")
            st.write(output_text)


 
    
    
