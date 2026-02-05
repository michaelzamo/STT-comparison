import os
import shutil
import aiofiles
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import speech_recognition as sr
import whisper
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# On charge le modèle Whisper au démarrage pour ne pas le recharger à chaque requête
# "tiny" ou "base" sont recommandés pour les serveurs gratuits (peu de RAM)
print("Chargement du modèle Whisper...")
whisper_model = whisper.load_model("base") 

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    # 1. Sauvegarder le fichier temporairement
    temp_filename = f"temp_{file.filename}"
    async with aiofiles.open(temp_filename, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    results = {}

    # 2. Transcription Google (Web Speech API)
    try:
        r = sr.Recognizer()
        # Google préfère parfois le WAV, mais SR gère souvent la conversion si ffmpeg est là
        with sr.AudioFile(temp_filename) as source:
            audio_data = r.record(source)
            # On force le japonais pour la démo, ou on pourrait le passer en paramètre
            text_google = r.recognize_google(audio_data, language="ja-JP")
            results["google"] = text_google
    except Exception as e:
        results["google"] = f"Erreur : {str(e)}"

    # 3. Transcription Whisper (Local)
    try:
        # Whisper gère le fichier directement
        result_whisper = whisper_model.transcribe(temp_filename, language="ja")
        results["whisper"] = result_whisper["text"]
    except Exception as e:
        results["whisper"] = f"Erreur : {str(e)}"

    # 4. Nettoyage
    os.remove(temp_filename)

    return results

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
