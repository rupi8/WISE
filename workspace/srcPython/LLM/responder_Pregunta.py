# Puedes integrar el sistema de TTS con tu procesamiento de lenguaje natural (NLP) 
# para responder preguntas o dar indicaciones en voz alta. Por ejemplo, si el 
# sistema entiende una pregunta del usuario, podría responderla verbalmente.


import pyttsx3

def responder_pregunta(pregunta):
    respuestas = {
        "¿cómo estás?": "Estoy bien, gracias por preguntar.",
        "¿qué hora es?": "Son las tres de la tarde."
    }
    respuesta = respuestas.get(pregunta.lower(), "No estoy seguro de la respuesta.")
    engine = pyttsx3.init()
    engine.say(respuesta)
    engine.runAndWait()

# Probar la función con una pregunta
responder_pregunta("¿cómo estás?")
