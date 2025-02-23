import os
import uuid
import time
import logging
import requests
import wave
import subprocess
import pyaudio
import webrtcvad
from google.cloud import texttospeech

# Configuration
SAMPLE_RATE = 16000  # 16 kHz sample rate (WebRTC VAD works best with this)
FRAME_DURATION = 30   #ms per frame
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION / 1000)  # Convert ms to samples
CHANNELS = 1
FORMAT = pyaudio.paInt16
VAD_MODE = 2  # WebRTC VAD aggressiveness (0-3, higher = more strict)
SILENCE_DURATION = 2.5 #seconds


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("va_helpers")


voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",  
    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.LINEAR16)

vad = webrtcvad.Vad(VAD_MODE)
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=FRAME_SIZE)


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


def is_speech(frame, sample_rate=SAMPLE_RATE):
    return vad.is_speech(frame, sample_rate)

def clear_audio_buffer():
    for _ in range(5):  # Read and discard a few frames
        stream.read(FRAME_SIZE, exception_on_overflow=False)

def record_audio(sample_rate=SAMPLE_RATE):

    clear_audio_buffer()

    logger.info("Listening... Speak now!")
    frames = []
    silence_start = None

    while True:
        audio_chunk = stream.read(FRAME_SIZE, exception_on_overflow=False)
        
        # Check if the chunk contains speech
        if is_speech(audio_chunk):
            frames.append(audio_chunk)
            silence_start = None  # Reset silence timer
        else:
            if silence_start is None:
                silence_start = time.time()  # Start silence timer
            
            # If silence exceeds the threshold, stop recording
            if time.time() - silence_start > SILENCE_DURATION:
                break

    logger.info("Recording stopped.")
    recorded_audio = b''.join(frames)
    return recorded_audio, sample_rate

def save_audio_to_file(audio_data:bytes, sample_rate:int, filename:str):

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # Mono audio
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data)


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
        subprocess.run(["ffplay", "-nodisp", "-autoexit", output_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.remove(output_file) 

def clean_up_resources():

    stream.stop_stream()
    stream.close()
    audio.terminate()