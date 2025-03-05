import speech_recognition as sr
import pyttsx3

def main_voice_control():
    print("Select an option:")
    print("1. Control actions")
    print("2. Voice feedback")
    print("3. Listen and display")
    print("4. Answer a question")
    
    choice = input("Enter your choice (1-4): ")
    
    if choice == "1":
        control_actions()
    elif choice == "2":
        feedback_vocal_en_ingles()
    elif choice == "3":
        listen_and_display()
    elif choice == "4":
        question = input("Enter your question: ")
        answer_question(question)
    else:
        print("Invalid choice.")

def control_actions():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say a command: 'turn on the light', 'turn off the light', etc.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio, language='en-US')
        print(f"Received command: {text}")

        if 'turn on the light' in text.lower():
            print("Light turned on!")
        elif 'turn off the light' in text.lower():
            print("Light turned off!")
        else:
            print("Command not recognized.")

    except sr.UnknownValueError:
        print("I could not understand what you said.")
    except sr.RequestError as e:
        print(f"Request error: {e}")

def feedback_vocal_en_ingles():
    recognizer = sr.Recognizer()
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)

    with sr.Microphone() as source:
        print("Say a command, for example: 'start' or 'stop'.")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        texto = recognizer.recognize_google(audio, language='en-US')
        print(f"Command received: {texto}")

        if 'start' in texto.lower():
            engine.say("Starting the process.")
        elif 'stop' in texto.lower():
            engine.say("Stopping the process.")
        else:
            engine.say("Command not recognized.")
        engine.runAndWait()

    except sr.UnknownValueError:
        engine.say("I couldn't understand what you said.")
        engine.runAndWait()
    except sr.RequestError as e:
        engine.say(f"Error with the speech recognition service: {e}")
        engine.runAndWait()

def listen_and_display():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please speak now...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio, language='en-US')
        print("You said: " + text)
    except sr.UnknownValueError:
        print("I could not understand what you said.")
    except sr.RequestError as e:
        print(f"Could not connect to the speech recognition service; error: {e}")

def answer_question(question):
    responses = {
        "how are you?": "I'm fine, thank you for asking.",
        "what time is it?": "It's three in the afternoon."
    }
    response = responses.get(question.lower(), "I'm not sure about the answer.")
    engine = pyttsx3.init()
    engine.say(response)
    engine.runAndWait()

if __name__ == "__main__":
    main_voice_control()
