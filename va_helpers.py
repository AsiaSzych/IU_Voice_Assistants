import os
import uuid
import requests
import logging
import wave
import numpy as np
import sounddevice as sd
from pydub import AudioSegment
from pydub.playback import play
from google.cloud import texttospeech

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("va_helpers")

voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",  
    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16)

def create_session(sessions:dict):
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"context": {}}
    return sessions, session_id


def send_message_to_rasa(url:str,
                         session_id:str,
                         user_message:str):
    payload = {
        "sender": session_id,
        "message": user_message
    }

    response = requests.post(url, json=payload)
    if response.status_code == 200:
        rasa_responses = response.json()
        return [r.get("text", "") for r in rasa_responses]
    else:
        logger.error("Error communicating with Rasa:", response.text)
        return ["Sorry, I couldn't process your request."]


def record_audio(duration:int=7, sample_rate:int=16000):

    logger.info("Recording... Speak now.")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.int16)
    sd.wait() 
    logger.info("Recording complete.")
    return audio_data, sample_rate


def save_audio_to_file(audio_data:any, sample_rate:int, filename:str):

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # Mono audio
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())


def transcribe_audio(stt_model: any, 
                    file_path: str):

    result = stt_model.transcribe(file_path)
    return result['text']


def speak_text(text:str,
               tts_engine:any, 
               tts_model:str='pyttsx',
               output_file:str='temp_response.wav'):

    if tts_model == 'pyttsx':
        tts_engine.say(text)
        tts_engine.runAndWait()
    elif tts_model == 'google':
        synthesis_input = texttospeech.SynthesisInput(text=text)
        response = tts_engine.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config)
        with open(output_file, "wb") as out:
            out.write(response.audio_content)
        audio = AudioSegment.from_wav(output_file)
        play(audio)
        os.remove(output_file) 