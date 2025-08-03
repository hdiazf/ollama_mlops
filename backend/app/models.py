from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class PDF(Base):
    __tablename__ = "PDF"
    
    id = Column(String, primary_key=True, index=True)
    nombre_archivo = Column(String, nullable=False)
    contenido = Column(Text, nullable=False)  # Resumen de 50 palabras
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PDF(id={self.id}, nombre_archivo={self.nombre_archivo})>"