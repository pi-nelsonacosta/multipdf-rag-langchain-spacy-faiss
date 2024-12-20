from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.spacy_embeddings import SpacyEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools.retriever import create_retriever_tool
from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
import os
import shutil
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="PDF Chat API", description="API para cargar PDFs y realizar consultas mediante RAG", version="1.0.0")

# Configuración para los embeddings
embeddings = SpacyEmbeddings(model_name="en_core_web_sm")

# Directorio para almacenar PDFs y la base de datos FAISS
UPLOAD_DIR = "uploads"
FAISS_DB_DIR = "faiss_db"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(FAISS_DB_DIR, exist_ok=True)


def pdf_read(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    return text


def get_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    return chunks


def vector_store(text_chunks):
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local(FAISS_DB_DIR)


llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    )    


def get_conversational_chain(tools, ques):
        
    # Incluir 'agent_scratchpad' en el prompt
    prompt = ChatPromptTemplate.from_messages([
    ("system", """Eres un asistente útil y riguroso encargado de responder preguntas únicamente utilizando el contexto proporcionado. Sigue estas reglas estrictamente:

    1. **Verifica cuidadosamente** si el término, nombre o información específica mencionada en la pregunta está presente en el contexto antes de dar una respuesta.
    2. Proporciona una **respuesta detallada** solo si la información necesaria está claramente presente en el contexto proporcionado.
    3. Si el término o la información solicitada **no se encuentra explícitamente en el contexto**, responde únicamente con: "La respuesta no está disponible en el contexto".
    4. No inventes, asumas, ni especules respuestas fuera del contexto.
    5. Sé **conciso y directo** en tus respuestas. Evita agregar detalles innecesarios.
    6. Si se solicita información sobre una persona, lugar o entidad, asegúrate de que esté presente en el contexto antes de responder.

    Recuerda: Tu conocimiento se limita al contexto proporcionado. Cualquier información que no esté en el contexto debe ser considerada como no disponible."""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])
   
    agent = create_tool_calling_agent(llm, [tools], prompt)
    agent_executor = AgentExecutor(agent=agent, tools=[tools], verbose=True)
    
    # Invoca el agente proporcionando 'agent_scratchpad' como una cadena vacía
    response = agent_executor.invoke({"input": ques, "agent_scratchpad": ""})
    return response['output']


@app.post("/upload/")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    try:
        pdf_paths = []
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            pdf_paths.append(file_path)

        raw_text = pdf_read(pdf_paths)
        text_chunks = get_chunks(raw_text)
        vector_store(text_chunks)

        return JSONResponse(content={"message": "PDFs processed and vector database created successfully."})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query/")
async def query_pdf(question: str = Form(...)):
    try:
        new_db = FAISS.load_local(FAISS_DB_DIR, embeddings, allow_dangerous_deserialization=True)
        retriever = new_db.as_retriever()
        retrieval_chain = create_retriever_tool(retriever, "pdf_extractor", "This tool is to give answers to queries from the PDF")
        answer = get_conversational_chain(retrieval_chain, question)

        return JSONResponse(content={"answer": answer})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list-pdfs/")
async def list_pdfs():
    try:
        # Listar los archivos en el directorio de uploads
        pdf_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith(".pdf")]
        return JSONResponse(content={"pdf_files": pdf_files})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete-pdf/")
async def delete_pdf(filename: str):
    try:
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return JSONResponse(content={"message": f"Archivo '{filename}' eliminado con éxito."})
        else:
            raise HTTPException(status_code=404, detail=f"Archivo '{filename}' no encontrado.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
