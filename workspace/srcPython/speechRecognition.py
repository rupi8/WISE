import speech_recognition as sr
from m5stack import lcd

class SpeechRecognition:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def listen(self):
        with self.microphone as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
        try:
            command = self.recognizer.recognize_google(audio, language='es-ES')
            print(f"Command received: {command}")
            return command
        except sr.UnknownValueError:
            print("Could not understand the audio")
            return ""
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition service")
            return ""

def main():
    speech = SpeechRecognition()
    lcd.print("Speech Recognition Initialized")

    while True:
        command = speech.listen()

        if command.lower() == "encender":
            lcd.print("Comando recibido: Encender")
            # Realiza alguna acción, por ejemplo encender una luz
        elif command.lower() == "apagar":
            lcd.print("Comando recibido: Apagar")
            # Realiza alguna acción, por ejemplo apagar una luz

if __name__ == "__main__":
    main()