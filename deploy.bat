@echo off
echo Desplegando aplicación en Minikube para TESTING...

REM Construir imágenes en el contexto de Minikube
echo Construyendo imágenes...
FOR /f "tokens=*" %%i IN ('minikube docker-env --shell cmd') DO %%i

docker build -t ollama-mlops-backend:latest ./backend
docker build -t ollama-mlops-frontend:latest ./frontend
docker build -t ollama-mlops-ollama:latest ./ollama

REM Aplicar manifiestos en orden
echo Aplicando manifiestos de Kubernetes...

kubectl apply -f k8s/postgres-deployment.yaml
echo PostgreSQL deployado

kubectl apply -f k8s/ollama-deployment.yaml
echo Ollama deployado

REM Esperar a que PostgreSQL y Ollama estén listos
echo ⏳ Esperando a que los servicios base estén listos...
kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s
kubectl wait --for=condition=ready pod -l app=ollama --timeout=600s

kubectl apply -f k8s/backend-deployment.yaml
echo Backend deployado

REM Esperar a que el backend esté listo
kubectl wait --for=condition=ready pod -l app=backend --timeout=300s

kubectl apply -f k8s/frontend-deployment.yaml
REM Esperar a que el frontend esté listo                                                                                                                                                                          │ │
echo ⏳ Esperando a que el frontend esté listo...
kubectl wait --for=condition=ready pod -l app=frontend --timeout=300s
echo Frontend deployado

echo Despliegue completado!
echo Para ver el estado: kubectl get pods
echo.
echo Obteniendo URL del frontend y abriendola...
minikube service frontend-service