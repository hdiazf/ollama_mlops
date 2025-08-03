import httpx
import asyncio
import os
from typing import Optional

class OllamaService:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = "qwen2.5:1.5b"  # Modelo configurado en el Dockerfile
        
    async def generate_summary(self, text: str) -> str:
        """Generar resumen de 50 palabras usando Ollama"""
        
        prompt = f"Resume este texto en 50 palabras: {text[4000]}"
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "num_predict": 500
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "").strip()
                else:
                    return "Error generando resumen"
                    
        except Exception as e:
            print(f"Error conectando con Ollama: {e}")
            return f"Resumen no disponible - {str(e)[:50]}"
    
    async def generate_response(self, query: str, context: str) -> str:
        """Generar respuesta basada en consulta y contexto de documentos"""
        
        prompt = f"Basándote en este contexto: {context}\n\nResponde esta pregunta: {query}"
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.5,
                            "num_predict": 500
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "").strip()
                else:
                    return "Error generando respuesta del LLM"
                    
        except Exception as e:
            print(f"Error conectando con Ollama: {e}")
            return f"No pude conectar con el modelo de IA. Error: {str(e)}"
    
    async def health_check(self) -> bool:
        """Verificar si Ollama está funcionando"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except:
            return False