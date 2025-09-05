# Imagen base de Python
FROM python:3.11-slim

# Crear carpeta de trabajo
WORKDIR /app

# Copiar archivos de la app
COPY requirements.txt .
COPY app.py .
COPY CRI.geo.json .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer puerto
EXPOSE 8050

# Comando por defecto
CMD ["python", "app.py"]
