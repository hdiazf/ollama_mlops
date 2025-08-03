from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
import httpx
import PyPDF2
from io import BytesIO

from app.database import get_db, engine
from app.models import PDF, Base
from app.services.ollama_service import OllamaService
from app.schemas import PDFResponse, ChatRequest, ChatResponse, HealthResponse

# Crear todas las tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MLOps Backend API",
    description="Backend para gestión de PDFs y chat con LLM",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar servicio de Ollama
ollama_service = OllamaService()

# Rutas del API
# Endpoint de salud
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Endpoint de salud del servicio"""
    return HealthResponse(status="healthy", message="Backend running successfully")

# Endpoint para subir y procesar PDFs
@app.post("/documents/upload", response_model=PDFResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Subir y procesar un archivo PDF"""
    
    # Validar que sea un PDF
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
    
    try:
        # Leer contenido del archivo
        contents = await file.read()
        
        # Extraer texto del PDF
        pdf_text = extract_text_from_pdf(contents)
        
        if not pdf_text.strip():
            raise HTTPException(status_code=400, detail="No se pudo extraer texto del PDF")
        
        # Generar resumen con Ollama
        summary = await ollama_service.generate_summary(pdf_text)
        
        # Generar ID único para el documento
        document_id = str(uuid.uuid4())
        
        # Guardar en base de datos
        pdf_record = PDF(
            id=document_id,
            nombre_archivo=file.filename,
            contenido=summary
        )
        
        db.add(pdf_record)
        db.commit()
        db.refresh(pdf_record)
        
        return PDFResponse(
            document_id=document_id,
            filename=file.filename,
            status="success",
            message="PDF procesado y guardado correctamente"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error procesando PDF: {str(e)}")

# Endpoint para listar documentos subidos
@app.get("/documents/list")
async def list_documents(db: Session = Depends(get_db)):
    """Listar todos los documentos subidos"""
    
    try:
        documents = db.query(PDF).all()
        return {
            "documents": [
                {
                    "id": doc.id,
                    "filename": doc.nombre_archivo,
                    "summary": doc.contenido[:100] + "..." if len(doc.contenido) > 100 else doc.contenido
                }
                for doc in documents
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo documentos: {str(e)}")

# Endpoint para eliminar un documento por ID
@app.delete("/documents/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Eliminar un documento por ID"""
    
    try:
        pdf_record = db.query(PDF).filter(PDF.id == document_id).first()
        
        if not pdf_record:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        db.delete(pdf_record)
        db.commit()
        
        return {"message": "Documento eliminado correctamente"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error eliminando documento: {str(e)}")

# Endpoint para procesar consultas de chat con contexto de documentos
@app.post("/chat/query", response_model=ChatResponse)
async def chat_query(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Procesar consulta de chat con contexto de documentos"""
    
    try:
        # Obtener contenido de documentos
        documents = db.query(PDF).filter(PDF.id.in_(request.document_ids)).all()
        
        if not documents:
            raise HTTPException(status_code=400, detail="No se encontraron documentos")
        
        # Construir contexto
        context = "\n".join([
            f"Documento '{doc.nombre_archivo}': {doc.contenido}"
            for doc in documents
        ])
        
        # Generar respuesta con Ollama
        response = await ollama_service.generate_response(request.query, context)
        
        return ChatResponse(
            response=response,
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando consulta: {str(e)}")

# Función para extraer texto de un PDF
def extract_text_from_pdf(pdf_content: bytes) -> str:
    """Extraer texto de un archivo PDF"""
    try:
        pdf_file = BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error leyendo PDF: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)