# Utiliser une image Python légère officielle
FROM python:3.9-slim

# Étape critique : Installation de FFmpeg et git (nécessaire pour whisper parfois)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Créer le dossier de travail
WORKDIR /app

# Copier les requirements et installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application
COPY . .

# Commande de lancement (Render attend que l'app écoute sur le port 10000 ou $PORT)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]
