# Puedes hacer que el altavoz emita sonidos o mensajes para alertar al usuario de algún 
# evento o para confirmar una acción realizada. Esto puede ser útil en interfaces 
# de usuario o sistemas automatizados.


import pyttsx3

def alerta(texto):
    engine = pyttsx3.init()
    engine.say(texto)
    engine.runAndWait()

# Llamar a la función para dar una alerta
alerta("¡Alerta! Se ha detectado movimiento.")
