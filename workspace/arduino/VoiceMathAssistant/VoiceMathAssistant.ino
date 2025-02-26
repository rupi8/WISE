/*
 * SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
 *
 * SPDX-License-Identifier: MIT
 */
#include <Arduino.h>                // Librería base de Arduino
#include <M5Unified.h>              // Librería para interactuar con el M5Stack
#include <M5ModuleLLM.h>            // Librería para interactuar con el M5ModuleLLM (modelo de lenguaje)

M5ModuleLLM module_llm;            // Instancia un objeto que representa el módulo LLM
String tts_work_id;                // Variable para almacenar el ID de trabajo del módulo TTS (Text-To-Speech)
String language;                   // Variable para almacenar el idioma para la síntesis de voz

void setup() {
    M5.begin();                     // Inicializa el M5Stack (pantalla y otros componentes)
    M5.Display.setTextSize(2);      // Configura el tamaño del texto en la pantalla
    M5.Display.setTextScroll(true); // Habilita el desplazamiento de texto en la pantalla

    language = "en_US";             // Configura el idioma para la síntesis de voz a inglés (US)
    // language = "zh_CN";           // Alternativa para configurar el idioma a chino (CN)

    /* Inicializa el puerto serie para el módulo LLM */
    Serial2.begin(115200, SERIAL_8N1, 16, 17);  // Configura el puerto serie 2 para comunicarse con el módulo LLM
    // Serial2.begin(115200, SERIAL_8N1, 13, 14);  // Alternativa para otros modelos
    // Serial2.begin(115200, SERIAL_8N1, 18, 17);  // Alternativa para otros modelos

    /* Inicializa el módulo LLM */
    module_llm.begin(&Serial2);    // Establece la comunicación con el módulo LLM usando Serial2

    /* Verifica que el módulo LLM esté conectado */
    M5.Display.printf(">> Check ModuleLLM connection..\n");
    while (1) {
        if (module_llm.checkConnection()) {   // Verifica la conexión del módulo LLM
            break;  // Sale del bucle si la conexión es exitosa
        }
    }

    /* Reinicia el módulo LLM */
    M5.Display.printf(">> Reset ModuleLLM..\n");
    module_llm.sys.reset();             // Resetea el módulo LLM para asegurar que está listo

    /* Configura el módulo de audio */
    M5.Display.printf(">> Setup audio..\n");
    module_llm.audio.setup();          // Configura el módulo de audio

    /* Configura el módulo TTS (Text-to-Speech) y guarda el ID de trabajo */
    M5.Display.printf(">> Setup tts..\n\n");
    m5_module_llm::ApiTtsSetupConfig_t tts_config;  // Estructura de configuración del módulo TTS
    tts_work_id = module_llm.tts.setup(tts_config, "tts_setup", language);  // Configura el módulo TTS y guarda el ID de trabajo
}

void loop() {
    /* Crea un texto para que sea pronunciado: {i} plus {i} equals to {i + i} */
    static int i = 0;                   // Variable estática que se incrementará en cada ciclo
    i++;                                // Incrementa el valor de i
    std::string text = std::to_string(i) + " plus " + std::to_string(i) + " equals " + std::to_string(i + i) + ".";  // Crea el texto de la operación

    // También puedes cambiarlo a chino:
    // std::string text = std::to_string(i) + " 加 " + std::to_string(i) + " 等于 " + std::to_string(i + i) + ".";

    M5.Display.setTextColor(TFT_GREEN);  // Configura el color del texto en la pantalla
    M5.Display.printf("<< %s\n\n", text.c_str());  // Muestra el texto que se va a pronunciar en la pantalla

    /* Envía el texto al módulo TTS para que lo pronuncie */
    module_llm.tts.inference(tts_work_id, text.c_str(), 10000);  // Llama al método de inferencia del TTS y espera la respuesta por 10 segundos

    delay(500);  // Pausa de medio segundo entre cada ciclo para evitar que el sistema funcione demasiado rápido
}
