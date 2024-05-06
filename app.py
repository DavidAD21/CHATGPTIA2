import google.generativeai as genai
import os
import io
from PyPDF2 import PdfReader 
from dotenv import load_dotenv
import streamlit as st

# Configurar la página de Streamlit
st.set_page_config(
    page_title="Gemini-Pro Chatbot by HJP7",
    page_icon=":alien:",
    layout="centered",
)

# Cargar variables de entorno
load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')

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

# Barra lateral para cargar archivo PDF
st.sidebar.title("Gemini-Pro Configuration")
pdf_path = st.sidebar.file_uploader("Upload a PDF file", type="pdf")

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
col1.markdown("Preguntas sobre el PDF o cualquier otro tema")
question = col1.text_input("Tu: ")

# Botón para enviar preguntas
if st.button("Enviar pregunta"):
    try:
        if pdf_text and question.strip():
            response = chat.send_message(instruction + pdf_text + question)
            conversation_history.append(("Tú", question))
            conversation_history.append(("Bot", response.text))
        elif question.strip():
            response = chat.send_message(instruction + question)
            conversation_history.append(("Tú", question))
            conversation_history.append(("Bot", response.text))
    except genai.types.generation_types.StopCandidateException:
        st.error("El modelo detuvo la generación de la respuesta. Inténtalo de nuevo con otra pregunta.")

# Mostrar conversación en la interfaz
for sender, message in conversation_history:
    if sender == "Tú":
        col1.markdown(f"{sender}: {message}")
    elif sender == "Bot":
        col1.markdown(f"{sender}: {message}", unsafe_allow_html=True)
