# Imagen base de Python
FROM python:3.11-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar los archivos del proyecto
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exponer el puerto (Cloud Run usa 8080)
EXPOSE 8080

# Comando para ejecutar Flask
CMD ["python", "app.py"]
