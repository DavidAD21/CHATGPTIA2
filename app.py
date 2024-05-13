import google.generativeai as genai
import os
import io
from PyPDF2 import PdfReader 
from dotenv import load_dotenv
import streamlit as st

import requests
from bs4 import BeautifulSoup

# Configurar la página de Streamlit
st.set_page_config(
    page_title="DragonNightBot",
    page_icon=":🐉",
    layout="centered",
)

# Cargar variables de entorno
load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')

def contado_de_token(pregunta):
    if pregunta:  
        tokens = model.count_tokens(pregunta)
    else:
        tokens = 0
    return tokens

# Configurar la API de Gemini-Pro
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])
instruction = "responde de manera inteligente en español"
pdf_text = ""
conversation_history = []

# Función para extraer texto de un archivo PDF          
def extract_text_from_pdf(file_contents):
    text = ""
    reader = PdfReader(file_contents)
    for page_num in range(len(reader.pages)):
        text += reader.pages[page_num].extract_text()
    return text

# Función para extraer texto de una página web
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text = '\n'.join([p.get_text() for p in paragraphs])
        return text
    except Exception as e:
        print("Error al extraer texto de la URL:", e)
        return ""

# Barra lateral para cargar archivo PDF
st.sidebar.image("dragon2.png", use_column_width=True)
st.sidebar.title("DragonNightBot")
pdf_path = st.sidebar.file_uploader("Ingresa el Pdf", type="pdf")
button_pdf=st.sidebar.button('pregunta pdf')
# Barra lateral para ingresar enlace
url = st.sidebar.text_input("Ingrese el enlace:")
button_url=st.sidebar.button('pregunta url')
# Comprobar si se ha cargado un archivo PDF
if pdf_path is not None:
    file_contents = pdf_path.getvalue()
    pdf_text = extract_text_from_pdf(io.BytesIO(file_contents))

# Elementos de la interfaz de Streamlit
col1, col2 = st.columns([2, 1])
st.markdown(
    """
    <style>
    .element2 {
        padding: 20px;
        margin: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sección para preguntas
col1.markdown("DragonNightBot Haz tus preguntas")
question= None  
question = col1.text_input("Tu: ")

if question !='':
    resu= contado_de_token(question)
    st.sidebar.markdown(f'Resultado de tokens en la pregunta:  \n {resu}')

# Botón para enviar preguntas
response = None
if button_pdf:
    try:
        if pdf_text and question.strip():
            response = chat.send_message(instruction + pdf_text + question)
            conversation_history.append(("Tú", question))
            conversation_history.append(("Bot", response.text))
        else:
            st.error("No se pudo extraer texto de la URL. Por favor, inténtelo de nuevo con otro enlace.")
    except genai.types.generation_types.StopCandidateException:
        st.error("El modelo detuvo la generación de la respuesta. Inténtalo de nuevo con otra pregunta.")

# Verificar si se proporciona un enlace y extraer texto si está presente
elif button_url:
    url_text = extract_text_from_url(url)
    if url_text:
        response = chat.send_message(instruction + url_text + question)
        conversation_history.append(("You", "URL provided"))
        conversation_history.append(("Bot", response.text))
    else:
        st.error("No se pudo extraer texto de la URL. Por favor, inténtelo de nuevo con otro enlace.")


if question.strip() and not (button_pdf or button_url):
    response = chat.send_message(instruction + question)
    conversation_history.append(("Tú", question))
    conversation_history.append(("Bot", response.text))

for sender, message in conversation_history:

    if sender == "Tú":
        st.empty()
        st.write(f"{sender}: {message}")
        st.empty()
    elif sender == "Bot":
        st.empty()
        st.write("🐉:", message)

    
if response is not None:
    resul= contado_de_token(response.text)
    st.sidebar.markdown(f'Resultado de tokens en la respueta  \n {resul}')
else:
    col1.markdown('No hay datos')