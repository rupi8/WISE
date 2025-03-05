# Puedes convertir el texto generado por tu sistema en voz para que el altavoz 
# lo reproduzca. Esto es útil para dar respuestas habladas o feedback al usuario. 
# Puedes usar bibliotecas como pyttsx3 o la API de Google para hacerlo.


import pyttsx3

def hablar(texto):
    engine = pyttsx3.init()  # Inicializa el motor de TTS
    engine.say(texto)  # Lo que se va a decir
    engine.runAndWait()  # Espera hasta que termine de hablar

# Usar la función
hablar("Hola, bienvenido a tu sistema inteligente.")




# import pyttsx3

# def hablar():
#     # Solicitar al usuario que ingrese un texto
#     texto = input("Por favor, ingresa el texto que deseas escuchar: ")
    
#     # Inicializar el motor de TTS
#     engine = pyttsx3.init()
    
#     # Convertir el texto a voz
#     engine.say(texto)
#     engine.runAndWait()  # Esperar hasta que termine de hablar

# # Llamar a la función
# hablar()

