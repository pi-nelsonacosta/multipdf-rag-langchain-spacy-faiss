from app.api.routers.langchain_multipdf_router import enrich_question
import streamlit as st
import requests
import os

# Configuración de la página
st.set_page_config(page_title="📄 MultiPDF RAG - Langchain - FAISS - Spacy", layout="wide")

# Inicializar el historial de chat si no existe
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar para configuración de Azure OpenAI
st.sidebar.title("⚙️ Configuración Azure OpenAI")

api_key = st.sidebar.text_input("Ingrese su AZURE_OPENAI_API_KEY:", type="password")
azure_deployment = st.sidebar.text_input("Ingrese su AZURE_OPENAI_DEPLOYMENT_NAME:", type="default")
azure_endpoint = st.sidebar.text_input("Ingrese su AZURE_OPENAI_ENDPOINT:", type="default")
api_version = st.sidebar.text_input("Ingrese su AZURE_OPENAI_API_VERSION:", value="2024-08-01-preview")

# Guardar configuraciones en variables de entorno
if st.sidebar.button("Guardar Configuración"):
    os.environ["AZURE_OPENAI_API_KEY"] = api_key
    os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = azure_deployment
    os.environ["AZURE_OPENAI_ENDPOINT"] = azure_endpoint
    os.environ["AZURE_OPENAI_API_VERSION"] = api_version
    st.sidebar.success("✅ Configuración guardada con éxito.")
    st.rerun()  # Forzar una recarga para aplicar las variables de entorno

# Configuración de la interfaz principal
st.title("📄 MultiPDF RAG - Langchain - FAISS")
st.write("Sube tus PDFs y realiza consultas a través de una interfaz amigable.")

# Sección para mostrar archivos disponibles
st.header("📂 Archivos Disponibles")

# Obtener la lista de archivos desde el backend
def fetch_pdf_files():
    with st.spinner("Cargando archivos disponibles..."):
        response = requests.get("http://localhost:8000/list-pdfs/")
    return response

response = fetch_pdf_files()

if response.status_code == 200:
    pdf_files = response.json().get("pdf_files", [])
    if pdf_files:
        st.write("Archivos disponibles:")
        for pdf in pdf_files:
            # Ajustar las proporciones de las columnas
            col1, col2 = st.columns([0.85, 0.15])
            
            with col1:
                st.write(f"📄 {pdf}")
            
            with col2:
                # Alinear el botón verticalmente al centro
                st.write("")  # Espacio para centrar el botón
                if st.button("🗑️ Eliminar", key=f"delete_{pdf}"):
                    delete_response = requests.delete("http://localhost:8000/delete-pdf/", params={"filename": pdf})
                    if delete_response.status_code == 200:
                        st.success(f"✅ Archivo '{pdf}' eliminado con éxito.")
                        st.rerun()
                    else:
                        st.error(f"❌ Error al eliminar el archivo: {delete_response.text}")
    else:
        st.write("No hay archivos disponibles.")
else:
    st.error(f"❌ Error al obtener la lista de archivos: {response.text}")
    
# Sección para subir PDFs
st.header("🔼 Subir PDFs")
uploaded_files = st.file_uploader("Selecciona uno o varios archivos PDF", type="pdf", accept_multiple_files=True)

if st.button("Procesar PDFs"):
    if uploaded_files:
        files_to_send = [("files", (file.name, file, "application/pdf")) for file in uploaded_files]

        with st.spinner("Procesando PDFs..."):
            response = requests.post("http://localhost:8000/upload/", files=files_to_send)

        if response.status_code == 200:
            st.success("✅ PDFs procesados y base de datos vectorial creada con éxito.")
            st.rerun()
        else:
            st.error(f"❌ Error al procesar PDFs: {response.text}")
    else:
        st.warning("⚠️ Por favor, sube al menos un archivo PDF.")

# Sección para hacer consultas tipo chat
st.header("💬 Chat con los PDFs")

# Entrada de usuario para nuevas preguntas
user_question = st.chat_input("Escribe tu pregunta sobre los PDFs procesados:")

if user_question:
    # Enriquecer la consulta del usuario
    enriched_question = enrich_question(user_question, st.session_state.chat_history)

    # Agregar la pregunta del usuario al historial de chat
    st.session_state.chat_history.append({"role": "user", "content": user_question})

    # Mostrar la pregunta del usuario en el chat
    with st.chat_message("user"):
        st.markdown(user_question)

    # Mostrar la consulta enriquecida (para depuración)
    with st.expander("🔍 Consulta Enriquecida"):
        st.markdown(enriched_question)

    # Enviar la pregunta enriquecida a la API de FastAPI
    with st.spinner("Buscando respuesta..."):
        response = requests.post("http://localhost:8000/query/", data={"question": enriched_question})

    if response.status_code == 200:
        answer = response.json().get("answer", "No se encontró una respuesta.")
    else:
        answer = f"❌ Error al consultar la API: {response.text}"

    # Agregar la respuesta al historial de chat
    st.session_state.chat_history.append({"role": "assistant", "content": answer})

    # Mostrar la respuesta del asistente en el chat
    with st.chat_message("assistant"):
        st.markdown(answer)

# Mostrar historial de chat
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


