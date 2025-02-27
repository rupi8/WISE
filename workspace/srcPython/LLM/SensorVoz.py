from m5stack import *
from m5ui import *
from uiflow import *
import time

# Inicialización del módulo de voz
voice = M5Voice()

# Escuchar comandos de voz
def listen_for_command():
    command = voice.listen()  # Escucha un comando de voz
    return command

# Ejecutar si hay un comando
command = listen_for_command()
if command:
    print(f"Comando de voz recibido: {command}")
else:
    print("No se detectó ningún comando.")
