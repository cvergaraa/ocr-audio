# =========================
# Archivo: ocr_traductor.py
# =========================

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


# =========================
# Funciones auxiliares
# =========================
def text_to_speech(input_language, output_language, text, tld):
    """Traduce el texto y lo convierte en audio"""
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    file_name = text[:20] if text else "audio"
    file_path = f"temp/{file_name}.mp3"

    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    tts.save(file_path)

    return file_name, trans_text


def remove_files(n):
    """Elimina archivos de audio antiguos"""
    mp3_files = glob.glob("temp/*.mp3")
    if not mp3_files:
        return

    now = time.time()
    n_days = n * 86400
    for f in mp3_files:
        if os.stat(f).st_mtime < now - n_days:
            os.remove(f)
            print("Deleted ", f)



remove_files(7)

st.title("📸 Reconocimiento Óptico de Caracteres (OCR)")
st.subheader("Elige la fuente de la imagen: desde cámara o cargando un archivo")

text = " "


cam_ = st.checkbox("Usar Cámara")
if cam_:
    img_file_buffer = st.camera_input("Toma una foto")
else:
    img_file_buffer = None

with st.sidebar:
    st.subheader("Procesamiento para Cámara")
    filtro = st.radio("Filtro para imagen con cámara", ("Sí", "No"))


bg_image = st.file_uploader("Cargar Imagen:", type=["png", "jpg"])
if bg_image is not None:
    st.image(bg_image, caption="Imagen cargada", use_container_width=True)

  
    with open(bg_image.name, "wb") as f:
        f.write(bg_image.read())

    st.success(f"Imagen guardada como {bg_image.name}")


    img_cv = cv2.imread(bg_image.name)
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)

st.write(text)


if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    if filtro == "Sí":
        cv2_img = cv2.bitwise_not(cv2_img)

    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)
    st.write(text)


with st.sidebar:
    st.subheader("Parámetros de Traducción")

    os.makedirs("temp", exist_ok=True)
    translator = Translator()

    LANGUAGES = {
        "Ingles": "en",
        "Español": "es",
        "Bengali": "bn",
        "Koreano": "ko",
        "Mandarin": "zh-cn",
        "Japones": "ja",
    }

    ACCENTS = {
        "Default": "com",
        "India": "co.in",
        "United Kingdom": "co.uk",
        "United States": "com",
        "Canada": "ca",
        "Australia": "com.au",
        "Ireland": "ie",
        "South Africa": "co.za",
    }

    in_lang = st.selectbox("Lenguaje de entrada", list(LANGUAGES.keys()))
    out_lang = st.selectbox("Lenguaje de salida", list(LANGUAGES.keys()))
    english_accent = st.selectbox("Acento", list(ACCENTS.keys()))

    input_language = LANGUAGES[in_lang]
    output_language = LANGUAGES[out_lang]
    tld = ACCENTS[english_accent]

    display_output_text = st.checkbox("Mostrar texto traducido")

    if st.button("Convertir"):
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown("## Tu audio:")
        st.audio(audio_bytes, format="audio/mp3")

        if display_output_text:
            st.markdown("## Texto de salida:")
            st.write(output_text)





 
    
    
