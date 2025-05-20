FROM python:3.9-slim

# Instalar dependencias de Docker
RUN apt-get update && apt-get install -y \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY AutoScaler.py .

# Configurar entorno sin buffer
ENV PYTHONUNBUFFERED=1

CMD ["python", "AutoScaler.py"]