# La función `listen_and_display()` utiliza el micrófono para capturar audio, 
# lo procesa con la API de reconocimiento de voz de Google y muestra el texto 
# reconocido en pantalla. Primero, ajusta el nivel de ruido ambiental para 
# mejorar la precisión, luego escucha la entrada del usuario e intenta 
# transcribirla a texto. Si no puede entender lo dicho, muestra un mensaje de error,
# y si hay un problema de conexión con el servicio de reconocimiento, informa el error correspondiente.

import speech_recognition as sr

def listen_and_display():
    # Create a speech recognizer
    recognizer = sr.Recognizer()
    
    # Use the microphone as input source
    with sr.Microphone() as source:
        print("Please speak now...")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for background noise
        audio = recognizer.listen(source)  # Listen to the speech

    try:
        # Try to recognize the speech and convert it to text
        text = recognizer.recognize_google(audio, language='en-US')  # Use Google Speech API
        print("You said: " + text)
    except sr.UnknownValueError:
        print("I could not understand what you said.")
    except sr.RequestError as e:
        print(f"Could not connect to the speech recognition service; error: {e}")

# Call the function
listen_and_display()
