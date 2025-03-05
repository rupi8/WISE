import speech_recognition as sr
import pyttsx3
from m5stack import *
from m5ui import *
from uiflow import *
import time

# Inicialización del módulo de voz
voice = M5Voice()

def main_voice_control():
    print("Select an option:")
    print("1. Test microphone")
    print("2. Listen and display")
    print("3. Voice sensor (Sensor de voz)")

    choice = input("Enter your choice (1-3): ")

    if choice == "1":
        test_microphone()
    elif choice == "2":
        listen_and_display()
    elif choice == "3":
        voice_sensor()
    else:
        print("Invalid choice.")

# Función para probar el micrófono
def test_microphone():
    recognizer = sr.Recognizer()
    engine = pyttsx3.init()
    
    with sr.Microphone() as source:
        print("Testing microphone. Please speak...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language='en-US')
        print(f"You said: {text}")
        engine.say(f"You said: {text}")
        engine.runAndWait()
    except sr.UnknownValueError:
        print("Could not understand the audio.")
        engine.say("Could not understand the audio.")
        engine.runAndWait()
    except sr.RequestError as e:
        print(f"Error with the recognition service: {e}")
        engine.say("Error with the recognition service.")
        engine.runAndWait()

# Función para escuchar y mostrar el comando de voz
def listen_and_display():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Please speak now...")
        recognizer.adjust_for_ambient_noise(source)  # Ajusta para ruido de fondo
        audio = recognizer.listen(source)  # Escucha el audio

    try:
        text = recognizer.recognize_google(audio, language='en-US')  # Usa la API de Google Speech
        print("You said: " + text)
    except sr.UnknownValueError:
        print("I could not understand what you said.")
    except sr.RequestError as e:
        print(f"Could not connect to the speech recognition service; error: {e}")

# Función para usar el sensor de voz
def voice_sensor():
    # Aquí, utilizamos el M5Voice para escuchar el sensor de voz
    print("Listening for voice command...")
    command = voice.listen()  # Escucha el comando de voz usando el sensor del M5Stack

    if command:
        print(f"Voice command received: {command}")
    else:
        print("No command detected.")

# Main - Test del sistema
if __name__ == "__main__":
    main_voice_control()
