FROM ollama/ollama:latest AS builder

# Traemos el modelo Gemma3 4B IT QAT
RUN nohup ollama serve > /tmp/ollama.log 2>&1 & \
    sleep 90 && \
    ollama pull qwen2.5:1.5b

# Creamos la imagen final
# que solo contiene el modelo pre-cargado
FROM ollama/ollama:latest

# Copia el modelo pre-cargado desde el builder
COPY --from=builder /root/.ollama /root/.ollama

# Exponemos el puerto por defecto de Ollama
EXPOSE 11434

# Corremos el servidor de Ollama
CMD ["serve"]