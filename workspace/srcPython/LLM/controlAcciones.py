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

def controlar_acciones():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Di un comando: 'encender luz', 'apagar luz', etc.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        texto = recognizer.recognize_google(audio, language='es-ES')
        print(f"Comando recibido: {texto}")

        if 'encender luz' in texto.lower():
            print("¡Luz encendida!")
        elif 'apagar luz' in texto.lower():
            print("¡Luz apagada!")
        else:
            print("Comando no reconocido.")

    except sr.UnknownValueError:
        print("No pude entender lo que dijiste.")
    except sr.RequestError as e:
        print(f"Error de solicitud: {e}")

# Llamar a la función
controlar_acciones()
