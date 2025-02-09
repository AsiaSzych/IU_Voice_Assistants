import os
import time
import logging
import whisper
import tempfile
import pyttsx3
from google.cloud import texttospeech
from va_helpers import create_session, send_message_to_rasa, save_audio_to_file, speak_text, transcribe_audio, record_audio

#Initialize constant parameters
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "./tts_sa.json"
RASA_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook"
TTS_MODEL = "google"
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("va_main")

# In-memory session store
sessions = {}

# Initialize Whisper for STT
stt_model = whisper.load_model("medium")  # Use the 'base' model for quick transcription
logger.debug(f"STT model loaded")

# Initialize TTS
if TTS_MODEL == 'pyttsx':
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', 150)  # Adjust speaking rate
    tts_engine.setProperty('volume', 0.9)  # Adjust volume
elif TTS_MODEL == 'google':
    tts_engine = texttospeech.TextToSpeechClient()
logger.debug(f"TTS model set")


if __name__ == "__main__":
    logger.info("Starting voice assistant...")
    sessions, session_id = create_session(sessions=sessions)

    while True:
        # Record user input
        audio_data, sample_rate = record_audio(duration=6)

        # Save the audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            save_audio_to_file(audio_data, sample_rate, temp_audio_file.name)
            temp_audio_path = temp_audio_file.name

        # Transcribe the audio to text
        user_input = transcribe_audio(stt_model, temp_audio_path)
        os.remove(temp_audio_path) 

        logger.info(f"You: {user_input}")

        # Send transcribed text to Rasa
        responses = send_message_to_rasa(RASA_SERVER_URL, session_id, user_input)
        logger.debug(f"Amount of responses {len(responses)}")
        
        # Speak and print the assistant's response
        for response in responses:
            logger.info(f"Assistant: {response}")
            speak_text(text=response, tts_model=TTS_MODEL, tts_engine=tts_engine)
        
        time.sleep(1)
