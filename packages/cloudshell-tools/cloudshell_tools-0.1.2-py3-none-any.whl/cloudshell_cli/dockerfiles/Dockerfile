# Imagen base ligera
FROM python:3.12-slim

# Evitar bytecode y buffer en logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Crear directorio de la app
WORKDIR /app

# Instalar dependencias del sistema si hicieran falta (opcional)
# RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Copiar requisitos e instalarlos
COPY ../app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY ../app/app.py .

# Exponer puerto (CloudShell suele usar 8080)
EXPOSE 8080

# Ejecutar la aplicación
CMD ["python", "app.py"]
