/*
 * SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
 *
 * SPDX-License-Identifier: MIT
 */
#include <Arduino.h>
#include <M5Unified.h>
#include <M5ModuleLLM.h>

M5ModuleLLM module_llm;  // Instancia del módulo LLM
String camera_work_id;    // ID de trabajo para el módulo de cámara
String yolo_work_id;     // ID de trabajo para el módulo YOLO

// Función para limpiar ciertas áreas de la pantalla
void clearDisplay() {
    M5.Display.fillRect(40, 50, 270, 20, BLACK);  // Borra la zona donde se muestra la clase del objeto
    M5.Display.fillRect(150, 80, 60, 20, BLACK);  // Borra la zona donde se muestra la confianza
    M5.Display.fillRect(40, 110, 40, 20, BLACK);  // Borra la zona donde se muestra la coordenada x1
    M5.Display.fillRect(40, 140, 40, 20, BLACK);  // Borra la zona donde se muestra la coordenada y1
    M5.Display.fillRect(40, 170, 40, 20, BLACK);  // Borra la zona donde se muestra la coordenada x2
    M5.Display.fillRect(40, 200, 40, 20, BLACK);  // Borra la zona donde se muestra la coordenada y2
}

void setup() {
    M5.begin();  // Inicializa el M5Stack
    M5.Display.setTextSize(2);  // Establece el tamaño del texto en la pantalla
    M5.Display.setTextScroll(true);  // Activa el desplazamiento de texto

    /* Configura el puerto serial para la comunicación con el módulo LLM */
    Serial2.begin(115200, SERIAL_8N1, 16, 17);  // Configura el puerto Serial2 a 115200 bps

    /* Inicializa el módulo LLM */
    module_llm.begin(&Serial2);  // Inicia la comunicación con el módulo LLM

    /* Verifica la conexión con el módulo LLM */
    M5.Display.setTextColor(ORANGE, BLACK);  // Establece el color de texto para mostrar el estado
    M5.Display.setTextSize(2);  // Configura el tamaño del texto
    M5.Display.setTextDatum(middle_center);  // Establece la alineación del texto al centro
    M5.Display.drawString("Check ModuleLLM connection..", M5.Display.width() / 2, M5.Display.height() / 2);
    while (1) {
        if (module_llm.checkConnection()) {  // Verifica si la conexión se establece correctamente
            break;  // Sale del bucle si la conexión es exitosa
        }
    }

    /* Reinicia el módulo LLM */
    M5.Display.fillRect(0, (M5.Display.height() / 2) - 10, 320, 25, BLACK);  // Limpia la pantalla
    M5.Display.drawString("Reset ModuleLLM..", M5.Display.width() / 2, M5.Display.height() / 2);
    module_llm.sys.reset();  // Reinicia el módulo LLM

    /* Configura el módulo de cámara */
    M5.Display.fillRect(0, (M5.Display.height() / 2) - 10, 320, 25, BLACK);  // Limpia la pantalla
    M5.Display.drawString("Setup camera..", M5.Display.width() / 2, M5.Display.height() / 2);
    camera_work_id = module_llm.camera.setup();  // Inicializa el módulo de cámara y guarda el ID de trabajo

    /* Configura el módulo YOLO y guarda el ID de trabajo */
    M5.Display.fillRect(0, (M5.Display.height() / 2) - 10, 320, 25, BLACK);  // Limpia la pantalla
    M5.Display.drawString("Setup yolo..", M5.Display.width() / 2, M5.Display.height() / 2);
    m5_module_llm::ApiYoloSetupConfig_t yolo_config;  // Configura el módulo YOLO
    yolo_config.input = {camera_work_id};  // Especifica que el YOLO usará la cámara como entrada
    yolo_work_id      = module_llm.yolo.setup(yolo_config, "yolo_setup");  // Inicializa YOLO y guarda el ID de trabajo

    /* Prepara la pantalla para mostrar los resultados */
    M5.Display.fillRect(0, (M5.Display.height() / 2) - 10, 320, 25, BLACK);  // Limpia la pantalla
    M5.Display.setTextDatum(top_left);  // Establece la alineación del texto en la parte superior izquierda
    M5.Display.drawString("class", 10, 20);  // Etiqueta para la clase del objeto
    M5.Display.drawString("confidence", 10, 80);  // Etiqueta para la confianza
    M5.Display.drawString("x1", 10, 110);  // Etiqueta para la coordenada x1
    M5.Display.drawString("y1", 10, 140);  // Etiqueta para la coordenada y1
    M5.Display.drawString("x2", 10, 170);  // Etiqueta para la coordenada x2
    M5.Display.drawString("y2", 10, 200);  // Etiqueta para la coordenada y2
}

void loop() {
    /* Actualiza el módulo LLM */
    module_llm.update();  // Actualiza el estado del módulo LLM

    /* Maneja los mensajes de respuesta del módulo LLM */
    for (auto& msg : module_llm.msg.responseMsgList) {
        /* Si el mensaje es del módulo YOLO */
        if (msg.work_id == yolo_work_id) {
            /* Verifica el tipo de objeto en el mensaje */
            if (msg.object == "yolo.box.stream") {
                /* Parsea el mensaje en formato JSON y obtiene los resultados de YOLO */
                JsonDocument doc;
                deserializeJson(doc, msg.raw_msg);  // Deserializa el mensaje en formato JSON
                JsonArray delta = doc["data"]["delta"].as<JsonArray>();  // Obtiene los resultados de detección

                if (delta.size() > 0) {
                    JsonObject result = delta[0].as<JsonObject>();  // Obtiene el primer resultado de detección
                    String class_name = result["class"].as<String>();  // Clase del objeto detectado
                    float confidence = result["confidence"].as<float>();  // Confianza de la detección
                    JsonArray bboxArray = result["bbox"].as<JsonArray>();  // Coordenadas del cuadro delimitador (bounding box)

                    if (bboxArray.size() == 4) {
                        // Extrae las coordenadas x1, y1, x2, y2 del cuadro delimitador
                        int x1 = bboxArray[0].as<int>();
                        int y1 = bboxArray[1].as<int>();
                        int x2 = bboxArray[2].as<int>();
                        int y2 = bboxArray[3].as<int>();

                        // Limpia la pantalla antes de mostrar nuevos resultados
                        clearDisplay();

                        // Muestra la clase, la confianza y las coordenadas en la pantalla
                        M5.Display.drawString(class_name, 40, 50);  // Clase del objeto
                        M5.Display.drawFloat(confidence, 2, 150, 80);  // Confianza
                        M5.Display.drawNumber(x1, 40, 110);  // Coordenada x1
                        M5.Display.drawNumber(y1, 40, 140);  // Coordenada y1
                        M5.Display.drawNumber(x2, 40, 170);  // Coordenada x2
                        M5.Display.drawNumber(y2, 40, 200);  // Coordenada y2
                    }
                } else {
                    clearDisplay();  // Si no se detecta nada, limpia la pantalla
                }
            }
        }
    }

    /* Limpia los mensajes manejados */
    module_llm.msg.responseMsgList.clear();  // Borra los mensajes que ya han sido procesados
}
