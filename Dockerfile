# Usamos una imagen ligera de Python oficial
FROM python:3.10-slim

# Seteamos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos los requisitos primero (para aprovechar el caché de Docker)
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Comando para ejecutar el bot
# Usamos "-u" para que los logs salgan inmediatamente (unbuffered)
CMD ["python", "-u", "main.py"]
