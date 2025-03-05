# Puedes asociar ciertos comandos de voz con acciones específicas, 
# como encender o apagar un dispositivo, ejecutar un programa, etc.

# Idioma:
# Español: language='es-ES'
# Ingles: language='en-US'

# recognize_google() es una función proporcionada por la librería speech_recognition 
# que se utiliza para convertir el audio en texto utilizando el servicio de 
# reconocimiento de voz de Google. Es uno de los métodos más comunes para realizar 
# reconocimiento de voz en Python.
import speech_recognition as sr

def control_actions():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say a command: 'turn on the light', 'turn off the light', etc.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio, language='en-US')
        print(f"Received command: {text}")

        if 'turn on the light' in text.lower(): #fuuck
            print("Light turned on!")
        elif 'turn off the light' in text.lower():
            print("Light turned off!")
        else:
            print("Command not recognized.")

    except sr.UnknownValueError:
        print("I could not understand what you said.")
    except sr.RequestError as e:
        print(f"Request error: {e}")

# Call the function
control_actions()