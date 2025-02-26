import time
from M5Stack import *
from M5ModuleLLM import M5ModuleLLM

module_llm = M5ModuleLLM()  # Instancia del módulo LLM

def setup():
    M5.begin()  # Inicializa el M5Stack
    lcd.print("Generando texto...")  # Muestra el mensaje inicial en la pantalla

def loop():
    # Supongamos que estamos usando una función de LLM para generar texto
    generated_text = module_llm.generateText("Hola, ¿cómo estás?")
    lcd.clear()  # Limpia la pantalla
    lcd.print(generated_text)  # Muestra el texto generado en la pantalla
    time.sleep(5)  # Esperar 5 segundos para que se vea el texto generado

if __name__ == "__main__":
    setup()
    while True:
        loop()
        time.sleep(0.1)  # Añade un pequeño retraso para evitar un bucle demasiado rápido