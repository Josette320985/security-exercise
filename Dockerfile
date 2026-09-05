FROM python:3.11-alpine

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY app.py .
COPY config.py .
COPY crypto_service.py .
COPY rotate_secret.py .

# Exponer puerto
EXPOSE 3000

# Comando: inicia el rotador en segundo plano y luego Flask
CMD sh -c "python rotate_secret.py & python app.py"