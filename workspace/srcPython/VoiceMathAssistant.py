import time
from M5Stack import *
from M5ModuleLLM import M5ModuleLLM
import json

module_llm = M5ModuleLLM()  # Instancia del módulo LLM
camera_work_id = None  # ID de trabajo para el módulo de cámara
yolo_work_id = None  # ID de trabajo para el módulo YOLO
tts_work_id = None  # ID de trabajo para el módulo TTS (Text-To-Speech)
language = "en_US"  # Idioma para la síntesis de voz

# Función para limpiar ciertas áreas de la pantalla
def clear_display():
    lcd.fillRect(40, 50, 270, 20, lcd.BLACK)  # Borra la zona donde se muestra la clase del objeto
    lcd.fillRect(150, 80, 60, 20, lcd.BLACK)  # Borra la zona donde se muestra la confianza
    lcd.fillRect(40, 110, 40, 20, lcd.BLACK)  # Borra la zona donde se muestra la coordenada x1
    lcd.fillRect(40, 140, 40, 20, lcd.BLACK)  # Borra la zona donde se muestra la coordenada y1
    lcd.fillRect(40, 170, 40, 20, lcd.BLACK)  # Borra la zona donde se muestra la coordenada x2
    lcd.fillRect(40, 200, 40, 20, lcd.BLACK)  # Borra la zona donde se muestra la coordenada y2

def setup():
    global camera_work_id, yolo_work_id, tts_work_id

    M5.begin()  # Inicializa el M5Stack
    lcd.setTextSize(2)  # Establece el tamaño del texto en la pantalla
    lcd.setTextScroll(True)  # Activa el desplazamiento de texto

    # Configura el puerto serial para la comunicación con el módulo LLM
    Serial2.begin(115200, tx=16, rx=17)  # Configura el puerto Serial2 a 115200 bps

    # Inicializa el módulo LLM
    module_llm.begin(Serial2)  # Inicia la comunicación con el módulo LLM

    # Verifica la conexión con el módulo LLM
    lcd.setTextColor(lcd.ORANGE, lcd.BLACK)  # Establece el color de texto para mostrar el estado
    lcd.setTextSize(2)  # Configura el tamaño del texto
    lcd.setTextDatum(lcd.CENTER)  # Establece la alineación del texto al centro
    lcd.drawString("Check ModuleLLM connection..", lcd.width() // 2, lcd.height() // 2)
    while True:
        if module_llm.checkConnection():  # Verifica si la conexión se establece correctamente
            break  # Sale del bucle si la conexión es exitosa

    # Reinicia el módulo LLM
    lcd.fillRect(0, (lcd.height() // 2) - 10, 320, 25, lcd.BLACK)  # Limpia la pantalla
    lcd.drawString("Reset ModuleLLM..", lcd.width() // 2, lcd.height() // 2)
    module_llm.sys.reset()  # Reinicia el módulo LLM

    # Configura el módulo de cámara
    lcd.fillRect(0, (lcd.height() // 2) - 10, 320, 25, lcd.BLACK)  # Limpia la pantalla
    lcd.drawString("Setup camera..", lcd.width() // 2, lcd.height() // 2)
    camera_work_id = module_llm.camera.setup()  # Inicializa el módulo de cámara y guarda el ID de trabajo

    # Configura el módulo YOLO y guarda el ID de trabajo
    lcd.fillRect(0, (lcd.height() // 2) - 10, 320, 25, lcd.BLACK)  # Limpia la pantalla
    lcd.drawString("Setup yolo..", lcd.width() // 2, lcd.height() // 2)
    yolo_config = {"input": [camera_work_id]}  # Configura el módulo YOLO
    yolo_work_id = module_llm.yolo.setup(yolo_config, "yolo_setup")  # Inicializa YOLO y guarda el ID de trabajo

    # Configura el módulo de audio
    lcd.fillRect(0, (lcd.height() // 2) - 10, 320, 25, lcd.BLACK)  # Limpia la pantalla
    lcd.drawString("Setup audio..", lcd.width() // 2, lcd.height() // 2)
    module_llm.audio.setup()  # Configura el módulo de audio

    # Configura el módulo TTS (Text-to-Speech) y guarda el ID de trabajo
    lcd.fillRect(0, (lcd.height() // 2) - 10, 320, 25, lcd.BLACK)  # Limpia la pantalla
    lcd.drawString("Setup tts..", lcd.width() // 2, lcd.height() // 2)
    tts_config = {}  # Estructura de configuración del módulo TTS
    tts_work_id = module_llm.tts.setup(tts_config, "tts_setup", language)  # Configura el módulo TTS y guarda el ID de trabajo

    # Prepara la pantalla para mostrar los resultados
    lcd.fillRect(0, (lcd.height() // 2) - 10, 320, 25, lcd.BLACK)  # Limpia la pantalla
    lcd.setTextDatum(lcd.TOP_LEFT)  # Establece la alineación del texto en la parte superior izquierda
    lcd.drawString("class", 10, 20)  # Etiqueta para la clase del objeto
    lcd.drawString("confidence", 10, 80)  # Etiqueta para la confianza
    lcd.drawString("x1", 10, 110)  # Etiqueta para la coordenada x1
    lcd.drawString("y1", 10, 140)  # Etiqueta para la coordenada y1
    lcd.drawString("x2", 10, 170)  # Etiqueta para la coordenada x2
    lcd.drawString("y2", 10, 200)  # Etiqueta para la coordenada y2

def loop():
    module_llm.update()  # Actualiza el estado del módulo LLM

    # Maneja los mensajes de respuesta del módulo LLM
    for msg in module_llm.msg.responseMsgList:
        # Si el mensaje es del módulo YOLO
        if msg.work_id == yolo_work_id:
            # Verifica el tipo de objeto en el mensaje
            if msg.object == "yolo.box.stream":
                # Parsea el mensaje en formato JSON y obtiene los resultados de YOLO
                doc = json.loads(msg.raw_msg)  # Deserializa el mensaje en formato JSON
                delta = doc["data"]["delta"]  # Obtiene los resultados de detección

                if len(delta) > 0:
                    result = delta[0]  # Obtiene el primer resultado de detección
                    class_name = result["class"]  # Clase del objeto detectado
                    confidence = result["confidence"]  # Confianza de la detección
                    bboxArray = result["bbox"]  # Coordenadas del cuadro delimitador (bounding box)

                    if len(bboxArray) == 4:
                        # Extrae las coordenadas x1, y1, x2, y2 del cuadro delimitador
                        x1 = bboxArray[0]
                        y1 = bboxArray[1]
                        x2 = bboxArray[2]
                        y2 = bboxArray[3]

                        # Limpia la pantalla antes de mostrar nuevos resultados
                        clear_display()

                        # Muestra la clase, la confianza y las coordenadas en la pantalla
                        lcd.drawString(class_name, 40, 50)  # Clase del objeto
                        lcd.drawFloat(confidence, 2, 150, 80)  # Confianza
                        lcd.drawNumber(x1, 40, 110)  # Coordenada x1
                        lcd.drawNumber(y1, 40, 140)  # Coordenada y1
                        lcd.drawNumber(x2, 40, 170)  # Coordenada x2
                        lcd.drawNumber(y2, 40, 200)  # Coordenada y2
                else:
                    clear_display()  # Si no se detecta nada, limpia la pantalla

    # Crea un texto para que sea pronunciado: {i} plus {i} equals to {i + i}
    static_i = getattr(loop, "i", 0)  # Variable estática que se incrementará en cada ciclo
    static_i += 1
    setattr(loop, "i", static_i)
    text = f"{static_i} plus {static_i} equals {static_i + static_i}."

    lcd.setTextColor(TFT_GREEN)  # Configura el color del texto en la pantalla
    lcd.printf("<< %s\n\n", text)  # Muestra el texto que se va a pronunciar en la pantalla

    # Envía el texto al módulo TTS para que lo pronuncie
    module_llm.tts.inference(tts_work_id, text, 10000)  # Llama al método de inferencia del TTS y espera la respuesta por 10 segundos

    # Limpia los mensajes manejados
    module_llm.msg.responseMsgList.clear()  # Borra los mensajes que ya han sido procesados

    time.sleep(0.5)  # Pausa de medio segundo entre cada ciclo para evitar que el sistema funcione demasiado rápido

if __name__ == "__main__":
    setup()
    while True:
        loop()
        time.sleep(0.1)  # Añade un pequeño retraso para evitar un bucle demasiado rápido