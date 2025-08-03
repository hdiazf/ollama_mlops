from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# URL de conexión a PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/mlops_db"
)

# Crear engine de SQLAlchemy
engine = create_engine(DATABASE_URL)

# Crear SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()