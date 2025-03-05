# El Control por comandos de voz es una funcionalidad muy interesante. Con esta funcionalidad, 
# 4puedes hacer que tu sistema reconozca lo que el usuario dice 
# (por ejemplo, comandos específicos) y, en respuesta, el altavoz puede emitir una respuesta 
# o realizar una acción.

# Idioma:
# Español: language='es-ES'
# Ingles: language='en-US'

# La función adjust_for_ambient_noise() es parte de la librería speech_recognition 
# y se utiliza para ajustar el micrófono de manera que pueda distinguir mejor entre 
# el ruido de fondo (sonidos ambientales) y el sonido que deseas capturar (como la voz humana).

import speech_recognition as sr
import pyttsx3
from datetime import datetime

def listen_command():
    # Initialize the recognizer
    recognizer = sr.Recognizer()
    
    # Use the microphone to listen
    with sr.Microphone() as source:
        print("Please say a command...")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        audio = recognizer.listen(source)  # Listen to the command
    
    try:
        # Convert audio to text
        command = recognizer.recognize_google(audio, language='en-US')
        print("Received command: " + command)
        
        # Respond based on the command
        if 'hello' in command.lower():
            response = "Hello, how can I assist you?"
        elif 'time' in command.lower():
            current_time = datetime.now().strftime("%H:%M")
            response = f"The current time is {current_time}."
        elif 'goodbye' in command.lower():
            response = "Goodbye, see you later!"
        else:
            response = "I did not understand the command."

        # Convert the response to speech
        engine = pyttsx3.init()
        engine.say(response)
        engine.runAndWait()  # Play the response
        
    except sr.UnknownValueError:
        print("I could not understand what you said.")
    except sr.RequestError as e:
        print(f"Request error: {e}")

# Call the function to listen to the command
listen_command()
