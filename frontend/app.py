import streamlit as st
import requests
import os
from typing import List, Optional
import io
import base64
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="MLOps Chat con PDFs",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Variables de configuración
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Funciones auxiliares
def upload_pdf_to_backend(uploaded_file) -> Optional[str]:
    """Sube un PDF al backend y retorna el ID del documento"""
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
        response = requests.post(f"{BACKEND_URL}/documents/upload", files=files)
        
        if response.status_code == 200:
            return response.json().get("document_id")
        else:
            st.error(f"Error al subir PDF: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")
        return None

def send_query_to_llm(query: str, document_ids: List[str]) -> Optional[str]:
    """Envía una consulta al LLM con contexto de documentos"""
    try:
        payload = {
            "query": query,
            "document_ids": document_ids
        }
        response = requests.post(f"{BACKEND_URL}/chat/query", json=payload)
        
        if response.status_code == 200:
            return response.json().get("response")
        else:
            st.error(f"Error en consulta: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")
        return None

def get_document_list() -> List[dict]:
    """Obtiene la lista de documentos subidos"""
    try:
        response = requests.get(f"{BACKEND_URL}/documents/list")
        if response.status_code == 200:
            return response.json().get("documents", [])
        return []
    except Exception as e:
        st.error(f"Error al obtener documentos: {str(e)}")
        return []

# Inicializar estado de la sesión
if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_documents" not in st.session_state:
    st.session_state.uploaded_documents = []

# SIDEBAR - Panel lateral para subir PDFs
with st.sidebar:
    st.header("📄 Gestión de Documentos")
    
    # Subida de archivos
    uploaded_files = st.file_uploader(
        "Subir PDFs",
        type=['pdf'],
        accept_multiple_files=True,
        help="Sube uno o más archivos PDF para hacer preguntas sobre su contenido"
    )
    
    # Procesar archivos subidos
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Verificar si el archivo ya está en la sesión
            if uploaded_file.name not in [doc["name"] for doc in st.session_state.uploaded_documents]:
                with st.spinner(f"Procesando {uploaded_file.name}..."):
                    document_id = upload_pdf_to_backend(uploaded_file)
                    
                    if document_id:
                        st.session_state.uploaded_documents.append({
                            "name": uploaded_file.name,
                            "id": document_id,
                            "upload_time": datetime.now()
                        })
                        st.success(f"✅ {uploaded_file.name} subido correctamente")
    
    # Mostrar documentos actuales
    if st.session_state.uploaded_documents:
        st.subheader("📚 Documentos Cargados")
        for doc in st.session_state.uploaded_documents:
            with st.expander(f"📄 {doc['name']}", expanded=False):
                st.write(f"**ID:** {doc['id']}")
                st.write(f"**Subido:** {doc['upload_time'].strftime('%H:%M:%S')}")
                
                # Botón para eliminar documento
                if st.button(f"🗑️ Eliminar", key=f"del_{doc['id']}"):
                    try:
                        response = requests.delete(f"{BACKEND_URL}/documents/{doc['id']}")
                        if response.status_code == 200:
                            st.session_state.uploaded_documents = [
                                d for d in st.session_state.uploaded_documents if d['id'] != doc['id']
                            ]
                            st.rerun()
                        else:
                            st.error("Error al eliminar documento")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    
    # Botón para limpiar chat
    if st.button("🧹 Limpiar Chat"):
        st.session_state.messages = []
        st.rerun()
    
    # Estado de conexión
    st.divider()
    with st.spinner("Verificando conexión..."):
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if response.status_code == 200:
                st.success("🟢 Backend conectado")
            else:
                st.error("🔴 Backend no responde")
        except:
            st.error("🔴 Backend desconectado")

# ÁREA PRINCIPAL - Chat con el LLM
st.title("🤖 Chat MLOps con Documentos PDF")
st.markdown("Haz preguntas sobre los documentos PDF que has subido")

# Mostrar mensajes del chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del chat
if prompt := st.chat_input("Escribe tu pregunta aquí..."):
    # Verificar que hay documentos subidos
    if not st.session_state.uploaded_documents:
        st.warning("⚠️ Sube al menos un documento PDF antes de hacer preguntas")
    else:
        # Agregar mensaje del usuario
        user_message = {
            "role": "user", 
            "content": prompt,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        st.session_state.messages.append(user_message)
        
        # Mostrar mensaje del usuario
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"⏰ {user_message['timestamp']}")
        
        # Generar respuesta del asistente
        with st.chat_message("assistant"):
            with st.spinner("🤔 Pensando... Me tomará un momento porque estoy sin GPU..."):
                document_ids = [doc["id"] for doc in st.session_state.uploaded_documents]
                response = send_query_to_llm(prompt, document_ids)
                
                if response:
                    st.markdown(response)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    st.caption(f"⏰ {timestamp}")
                    
                    # Agregar respuesta al historial
                    assistant_message = {
                        "role": "assistant",
                        "content": response,
                        "timestamp": timestamp
                    }
                    st.session_state.messages.append(assistant_message)
                else:
                    error_msg = "❌ No pude procesar tu pregunta. Verifica la conexión con el backend."
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "timestamp": datetime.now().strftime("%H:%M:%S")
                    })

# Footer con información
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📄 Documentos", len(st.session_state.uploaded_documents))

with col2:
    st.metric("💬 Mensajes", len(st.session_state.messages))

with col3:
    if st.session_state.uploaded_documents:
        total_size = sum([len(doc["name"]) for doc in st.session_state.uploaded_documents])
        st.metric("📊 Estado", "✅ Listo")
    else:
        st.metric("📊 Estado", "⏳ Sin docs")