# Puedes hacer que el altavoz emita sonidos o mensajes para alertar al usuario de algún 
# evento o para confirmar una acción realizada. Esto puede ser útil en interfaces 
# de usuario o sistemas automatizados.

import pyttsx3

def alert(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Call the function to give an alert
alert("Alert! Movement detected.")
