import speech_recognition as sr

def escuchar_y_mostrar():
    # Crear un reconocedor de voz
    recognizer = sr.Recognizer()
    
    # Usar el micrófono como fuente de entrada
    with sr.Microphone() as source:
        print("Por favor, hable ahora...")
        recognizer.adjust_for_ambient_noise(source)  # Ajuste para el ruido ambiental
        audio = recognizer.listen(source)  # Escucha lo que se diga

    try:
        # Intenta reconocer el audio y convertirlo en texto
        texto = recognizer.recognize_google(audio, language='es-ES')  # Usa Google Speech API
        print("Lo que dijiste: " + texto)
    except sr.UnknownValueError:
        print("No pude entender lo que dijiste.")
    except sr.RequestError as e:
        print(f"No se pudo conectar al servicio de reconocimiento de voz; error: {e}")

# Llamar a la función
escuchar_y_mostrar()
