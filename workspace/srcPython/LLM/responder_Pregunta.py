# Puedes integrar el sistema de TTS con tu procesamiento de lenguaje natural (NLP) 
# para responder preguntas o dar indicaciones en voz alta. Por ejemplo, si el 
# sistema entiende una pregunta del usuario, podría responderla verbalmente.

import pyttsx3

def answer_question(question):
    responses = {
        "how are you?": "I'm fine, thank you for asking.",
        "what time is it?": "It's three in the afternoon."
    }
    response = responses.get(question.lower(), "I'm not sure about the answer.")
    engine = pyttsx3.init()
    engine.say(response)
    engine.runAndWait()

# Test the function with a question
answer_question("how are you?")