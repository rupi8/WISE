# Puedes programar el sistema para que responda solo a ciertas palabras clave. 
# Esto es útil para crear comandos específicos que inician una acción.

import speech_recognition as sr
import pyttsx3

def feedback_vocal_en_ingles():
    recognizer = sr.Recognizer()
    engine = pyttsx3.init()

    # Configuración para usar una voz en inglés (puedes cambiar a diferentes voces disponibles)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # Cambia el índice para diferentes voces

    with sr.Microphone() as source:
        print("Say a command, for example: 'start' or 'stop'.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        texto = recognizer.recognize_google(audio, language='en-US')  # Usar inglés para el reconocimiento
        print(f"Command received: {texto}")

        if 'start' in texto.lower():
            engine.say("Starting the process.")
            engine.runAndWait()
        elif 'stop' in texto.lower():
            engine.say("Stopping the process.")
            engine.runAndWait()
        else:
            engine.say("Command not recognized.")
            engine.runAndWait()

    except sr.UnknownValueError:
        engine.say("I couldn't understand what you said.")
        engine.runAndWait()
    except sr.RequestError as e:
        engine.say(f"Error with the speech recognition service: {e}")
        engine.runAndWait()

# Call the function
feedback_vocal_en_ingles()

