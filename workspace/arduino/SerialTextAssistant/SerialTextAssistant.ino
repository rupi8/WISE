/*
 * SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
 *
 * SPDX-License-Identifier: MIT
 */

#include <Arduino.h>                // Importa la librería base de Arduino
#include <M5Unified.h>              // Librería para interactuar con el M5Stack
#include <M5ModuleLLM.h>            // Librería para interactuar con el M5ModuleLLM (modelo de lenguaje)

#define CommSerialPort Serial       // Define el puerto serie USB como CommSerialPort

M5ModuleLLM module_llm;            // Instancia el objeto que representa el módulo LLM
String llm_work_id;                // Variable para almacenar el ID de trabajo del módulo LLM
String received_question;         // Variable para almacenar la pregunta recibida del puerto serie
bool question_ok;                  // Variable booleana que indica si la pregunta es válida

void setup() {
    M5.begin();                     // Inicializa el M5Stack (pantalla y otros componentes)
    M5.Display.setTextSize(2);      // Configura el tamaño del texto en la pantalla
    M5.Display.setTextScroll(true); // Habilita el desplazamiento de texto en la pantalla

    /* Inicializa la comunicación serial USB */
    CommSerialPort.begin(115200);   // Configura el puerto serie USB a 115200 baudios

    /* Inicializa el puerto serie para el módulo LLM */
    Serial2.begin(115200, SERIAL_8N1, 16, 17);  // Configura el puerto serie 2 para comunicarse con el módulo LLM
    // Serial2.begin(115200, SERIAL_8N1, 13, 14);  // Alternativa para otros modelos
    // Serial2.begin(115200, SERIAL_8N1, 18, 17);  // Alternativa para otros modelos

    /* Inicializa el módulo LLM */
    module_llm.begin(&Serial2);    // Establece la comunicación con el módulo LLM usando Serial2

    /* Asegura que el módulo LLM esté conectado */
    M5.Display.printf(">> Check ModuleLLM connection..\n");
    while (1) {
        if (module_llm.checkConnection()) {   // Verifica la conexión del módulo LLM
            break;  // Sale del bucle si la conexión es exitosa
        }
    }

    /* Reinicia el módulo LLM */
    M5.Display.printf(">> Reset ModuleLLM..\n");
    module_llm.sys.reset();             // Resetea el módulo LLM para asegurar que está listo

    /* Configura el módulo LLM y guarda el ID de trabajo devuelto */
    M5.Display.printf(">> Setup llm..\n");
    m5_module_llm::ApiLlmSetupConfig_t llm_config;  // Estructura de configuración del módulo LLM
    llm_config.max_token_len = 1023;   // Configura el tamaño máximo de los tokens en el modelo de lenguaje
    llm_work_id = module_llm.llm.setup(llm_config);  // Configura el módulo LLM y guarda el ID de trabajo

    M5.Display.printf(">> Setup finish\n");
    M5.Display.printf(">> Try send your question via usb serial port\n");
    M5.Display.setTextColor(TFT_GREEN);
    M5.Display.printf("e.g. \nHi, What's your name?\n");  // Ejemplo de cómo hacer una pregunta
    M5.Display.printf("(end with CRLF \\r\\n)\n\n");
}

void loop() {
    /* Verifica si hay datos disponibles en el puerto serie USB */
    question_ok = false;                // Reinicia la variable que verifica si la pregunta es válida
    if (CommSerialPort.available()) {   // Si hay datos disponibles
        while (CommSerialPort.available()) {
            char in_char = (char)CommSerialPort.read();  // Lee un carácter desde el puerto serie
            received_question += in_char;  // Agrega el carácter a la pregunta

            /* Verifica si la pregunta ha terminado */
            if (received_question.endsWith("\r\n")) {   // Si la pregunta termina con un salto de línea CRLF
                received_question.remove(received_question.length() - 2); // Elimina el CRLF del final
                question_ok = true;  // Marca la pregunta como válida
                break;  // Sale del bucle
            }
        }
    }

    /* Si la pregunta es válida */
    if (question_ok) {
        M5.Display.setTextColor(TFT_GREEN);   // Configura el color del texto en la pantalla
        M5.Display.printf("<< %s\n", received_question.c_str());  // Muestra la pregunta recibida en la pantalla
        M5.Display.setTextColor(TFT_YELLOW);  // Cambia el color del texto para la respuesta
        M5.Display.printf(">> ");
        CommSerialPort.printf("<< \"%s\"\n", received_question.c_str());  // Muestra la pregunta en el puerto serie USB
        CommSerialPort.print(">> ");

        /* Envía la pregunta al módulo LLM y espera el resultado de la inferencia */
        module_llm.llm.inferenceAndWaitResult(llm_work_id, received_question.c_str(), [](String& result) {
            /* Muestra el resultado (respuesta) en la pantalla y en el puerto serie USB */
            M5.Display.printf("%s", result.c_str());
            CommSerialPort.print(result);   // Envia la respuesta al puerto serie USB
        });

        /* Limpia la pregunta para la siguiente */
        received_question.clear();  // Borra la pregunta para preparar el siguiente ciclo

        M5.Display.println();    // Mueve la pantalla para mostrar la siguiente información
        CommSerialPort.println();  // Mueve la línea en el puerto serie USB
    }

    delay(20);  // Pausa breve para evitar sobrecargar el ciclo del loop
}
