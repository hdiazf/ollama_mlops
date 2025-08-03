from pydantic import BaseModel
from typing import List, Optional

class PDFResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str

class ChatRequest(BaseModel):
    query: str
    document_ids: List[str]

class ChatResponse(BaseModel):
    response: str
    status: str

class HealthResponse(BaseModel):
    status: str
    message: str

class DocumentSummary(BaseModel):
    id: str
    filename: str
    summary: str