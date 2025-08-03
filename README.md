# ollama_mlops
Trabajo de MLOPS para la UAI

## Descripción del Proyecto
Este proyecto implementa una plataforma MLOps completa utilizando Ollama para el despliegue de modelos de lenguaje. La arquitectura incluye:

- **Backend**: API REST en FastAPI que gestiona las interacciones con modelos Ollama
- **Frontend**: Interfaz web en Streamlit para interactuar con los modelos
- **Base de Datos**: PostgreSQL para almacenamiento persistente
- **Orquestación**: Docker Compose y Kubernetes para despliegue en contenedores
- **Ollama**: Motor de ejecución de modelos de lenguaje local

## Arquitectura
- **Backend** (FastAPI): Puerto 8000
- **Frontend** (Streamlit): Puerto 8501  
- **PostgreSQL**: Puerto 5432
- **Ollama**: Puerto 11434

## Despliegue

### Docker Compose
```bash
docker-compose up -d
```

### Kubernetes (Minikube)
```bash
deploy.bat
```

## Asistencia de Claude Code

### Configuración de Despliegue
- Creación del script `deploy.bat` para despliegue automatizado en Windows/PowerShell
- Integración automática de apertura del navegador con la URL del frontend

### Resolución de Problemas
- Solución de conectividad entre servicios en Kubernetes
- Configuración de NodePort para acceso externo al frontend
- Optimización del flujo de despliegue con esperas condicionales entre servicios
- Análisis de logs para detectar error de volcado de momoria de LLM Gemma3, cambiandose a Qwen2
