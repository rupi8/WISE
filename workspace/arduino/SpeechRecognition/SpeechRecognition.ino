#include <M5ModuleLLM.h>
#include <SpeechRecognition.h> // Librería para el micrófono y reconocimiento de voz

SpeechRecognition speech; // Instancia para reconocimiento de voz

void setup() {
  M5.begin();
  speech.begin(); // Inicializa el micrófono y el reconocimiento de voz
}

void loop() {
  String command = speech.listen(); // Escucha el comando de voz

  if (command == "Encender") {
    M5.Lcd.print("Comando recibido: Encender");
    // Realiza alguna acción, por ejemplo encender una luz
  }
  else if (command == "Apagar") {
    M5.Lcd.print("Comando recibido: Apagar");
    // Realiza alguna acción, por ejemplo apagar una luz
  }
}
