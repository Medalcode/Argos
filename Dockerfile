# Usamos una imagen ligera de Python oficial (versión coincide con el proyecto)
FROM python:3.13-slim

# Seteamos variables de entorno para evitar .pyc y buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Seteamos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalamos dependencias del sistema si fueran necesarias
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copiamos los requisitos primero (para aprovechar el caché de Docker)
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Creamos directorios para persistencia si no existen
RUN mkdir -p logs data

# Comando para ejecutar el bot
CMD ["python", "main.py"]
