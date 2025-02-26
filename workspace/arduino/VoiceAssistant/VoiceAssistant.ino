/*
 * SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
 *
 * SPDX-License-Identifier: MIT
 */
#include <Arduino.h>
#include <M5Unified.h>
#include <M5ModuleLLM.h>

M5ModuleLLM module_llm;  // Instancia del módulo LLM
M5ModuleLLM_VoiceAssistant voice_assistant(&module_llm);  // Instancia del asistente de voz basado en el módulo LLM

/* Callback para los datos de ASR (Reconocimiento Automático de Voz) */
void on_asr_data_input(String data, bool isFinish, int index) {
    M5.Display.setTextColor(TFT_GREEN, TFT_BLACK);  // Establece el color de texto verde para los datos de entrada
    // M5.Display.setFont(&fonts::efontCN_12);  // Puedes habilitar soporte de fuentes chinas si es necesario
    M5.Display.printf(">> %s\n", data.c_str());  // Muestra los datos de la entrada de voz en la pantalla

    /* Si los datos de ASR han finalizado */
    if (isFinish) {
        M5.Display.setTextColor(TFT_YELLOW, TFT_BLACK);  // Cambia el color de texto a amarillo cuando se ha completado la entrada
        M5.Display.print("Completado\n");  // Muestra un mensaje indicando que la entrada de voz ha finalizado
    }
}

void setup() {
    M5.begin();  // Inicializa el M5Stack
    M5.Display.setTextSize(2);  // Establece el tamaño del texto en la pantalla
    M5.Display.setTextScroll(true);  // Activa el desplazamiento de texto en la pantalla

    /* Configura el puerto serial para comunicarte con el módulo LLM */
    Serial2.begin(115200, SERIAL_8N1, 16, 17);  // Configura el puerto Serial2 a 115200 bps

    /* Inicializa el módulo LLM */
    module_llm.begin(&Serial2);  // Inicia la comunicación con el módulo LLM

    /* Verifica la conexión del módulo LLM */
    M5.Display.printf(">> Checking connection to ModuleLLM..\n");
    while (1) {
        if (module_llm.checkConnection()) {  // Si la conexión se establece correctamente
            break;  // Sale del bucle
        }
    }

    /* Restablece el módulo LLM */
    M5.Display.printf(">> Resetting ModuleLLM..\n");
    module_llm.sys.reset();  // Reinicia el módulo LLM para asegurar que todo esté listo

    /* Configura el asistente de voz */
    M5.Display.printf(">> Setting up Voice Assistant..\n");
    voice_assistant.begin();  // Inicia el asistente de voz

    /* Configura la función de callback para el ASR */
    voice_assistant.setOnAsrDataCallback(on_asr_data_input);  // Establece la función de callback cuando se reciba información de voz
}

void loop() {
    /* El asistente de voz escucha comandos de voz en el fondo */
    voice_assistant.listen();  // Escucha los comandos de voz continuamente

    delay(100);  // Espera un breve momento antes de continuar con el ciclo
}
