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
st.title("Preguntas sobre PDF  O URL")

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

if "messages" not in st.session_state:
    st.session_state.messages = []
    
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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
st.sidebar.title("DragonNightBot")
st.sidebar.image("dragon2.png", use_column_width=True)
pdf_path = st.sidebar.file_uploader("Upload a PDF file", type="pdf")
button_pdf=st.sidebar.button('pregunta pdf')
# Barra lateral para ingresar enlace
url = st.sidebar.text_input("Enter URL:")
button_url=st.sidebar.button('pregunta url')
# Comprobar si se ha cargado un archivo PDF
if pdf_path is not None:
    file_contents = pdf_path.getvalue()
    pdf_text = extract_text_from_pdf(io.BytesIO(file_contents))

# Elementos de la interfaz de Streamlit
col1, col2,col3 = st.columns([3, 2, 1])
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
response=None
question =None
# Sección para preguntas
#question = st.text_input("Pregunta")
question= st.text_input("Pregunta" )
if question != '':
    res=contado_de_token(question)
    st.markdown(res) 
if  button_pdf:
    try:    
        if pdf_text:
            response = chat.send_message(instruction + pdf_text +question)
            st.chat_message("user").markdown(question)
            st.session_state.messages.append({"role": "user", "content": question})

            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            question=""

        else:
            st.error("No se pudo encontro infomacion sobre la pregunta en el PDF. Por favor, inténtelo de nuevo.")
    except genai.types.generation_types.StopCandidateException:
        st.error("El modelo detuvo la generación de la respuesta. Inténtalo de nuevo con otra pregunta.")

# Verificar si se proporciona un enlace y extraer texto si está presente
elif button_url:
    url_text = extract_text_from_url(url)
    try:
        if url_text:
            response = chat.send_message(instruction + url_text + question)

            st.chat_message("user").markdown(question)
            st.session_state.messages.append({"role": "user", "content": question})

            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            question=""
        else:
            st.error("No se pudo encontro infomacion sobre la pregunta el URL Por favor, inténtelo de nuevo.")
    except genai.types.generation_types.StopCandidateException:
        st.error("El modelo detuvo la generación de la respuesta. Inténtalo de nuevo con otra pregunta.")

elif question.strip():

    response = chat.send_message(instruction + question)

    st.chat_message("user").markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
    question=""
else:
    st.write("Por favor ingresa una pregunta válida")

if response:
    resul= contado_de_token(response.text)
    st.sidebar.markdown(f'Resultado de tokens en la respueta  \n {resul}')
