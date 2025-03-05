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

def escuchar_comando():
    # Inicializar el reconocedor de voz
    recognizer = sr.Recognizer()
    
    # Usar el micrófono para escuchar
    with sr.Microphone() as source:
        print("Por favor, di un comando...")
        recognizer.adjust_for_ambient_noise(source)  # Ajustar por ruido ambiente
        audio = recognizer.listen(source)  # Escuchar el comando
    
    try:
        # Convertir el audio en texto
        comando = recognizer.recognize_google(audio, language='es-ES')
        print("Comando recibido: " + comando)
        
        # Responder según el comando
        if 'hola' in comando.lower():
            respuesta = "Hola, ¿cómo puedo ayudarte?"
        elif 'hora' in comando.lower():
            from datetime import datetime
            hora_actual = datetime.now().strftime("%H:%M")
            respuesta = f"La hora actual es {hora_actual}"
        elif 'adiós' in comando.lower():
            respuesta = "Adiós, ¡hasta luego!"
        else:
            respuesta = "No entendí el comando."

        # Convertir la respuesta en voz
        engine = pyttsx3.init()
        engine.say(respuesta)
        engine.runAndWait()  # Reproducir la respuesta
        
    except sr.UnknownValueError:
        print("No pude entender lo que dijiste.")
    except sr.RequestError as e:
        print(f"Error de solicitud: {e}")

# Llamar a la función para escuchar el comando
escuchar_comando()
