FROM ollama/ollama:latest

# Descargar el modelo durante el build
RUN ollama serve & \
    sleep 30 && \
    ollama pull qwen2.5:1.5b && \
    pkill ollama

EXPOSE 11434
CMD ["serve"]