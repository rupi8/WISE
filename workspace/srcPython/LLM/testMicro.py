# Captura audio y lo reproduce de vuelta, permitiéndote verificar que el 
# micrófono funciona correctamente. La función también muestra el 
# texto reconocido en la terminal para verificar la precisión del reconocimiento de voz.

import speech_recognition as sr
import pyttsx3

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

# Call the function
test_microphone()
