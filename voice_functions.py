import asyncio
import edge_tts
import tempfile
from langdetect import detect
import os
import speech_recognition as sr
import google.generativeai as genai
from playsound import playsound


genai.configure(api_key="AIzaSyAQSvLsUaeDS_BYFnw9RBUgSNaFf9Q2IEE")  # Replace with your real API key
model = genai.GenerativeModel("gemini-1.5-flash")

def get_voice_for_lang(lang_code):
    voices = {
        "en": "en-IN-NeerjaNeural",
        "hi": "hi-IN-MadhurNeural",
        "mr": "mr-IN-AarohiNeural",
    }
    return voices.get(lang_code, "en-IN-NeerjaNeural")

# Use edge-tts to generate speech
async def speak_edge_tts(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        await communicate.save(tmpfile.name)
        return tmpfile.name

def threaded_speak(text):
    lang = detect(text)
    voice = get_voice_for_lang(lang)
    audio_path = asyncio.run(speak_edge_tts(text, voice))
    return audio_path

def stop_tts():
    pass


def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            text = r.recognize_google(audio)
            print("Heard:", text)
            return text
        except sr.UnknownValueError:
            print("Didn't understand.")
            return "ERROR: Could not understand audio."
        except sr.RequestError as e:
            print(f"Error with speech service: {e}")
            return "ERROR: Speech service unavailable."

def ask_gemini(text, context=None):
    try:
        if context and len(context) > 3000:
            context = context[:3000]

        prompt = f"You are a helpful assistant. Only answer based on the content below:\n\n{context}\n\nQuestion: {text}" if context else text

        lang = detect(text)
        if lang != 'en':
            prompt = f"Respond in language: {lang}\n{prompt}"

        response = model.generate_content(prompt)
        print("Gemini Response:", response.text)
        return response.text

    except Exception as e:
        print(f"Gemini error: {e}")
        lang = detect(text)
        if lang == 'mr':
            return "माफ करा, मला उत्तर देता आले नाही."
        elif lang == 'hi':
            return "क्षमा करें, उत्तर नहीं दे सका।"
        else:
            return "Sorry, Gemini failed to respond."



def speak_response(text):
    stop_tts()
    audio_path = threaded_speak(text)
    try:
        playsound(audio_path)  # Plays the audio silently
    except Exception as e:
        print("Audio playback error:", e)
    finally:
        try:
            os.remove(audio_path)  # Remove the temp file to stay clean
        except Exception as cleanup_error:
            print("Error deleting temp audio file:", cleanup_error)

