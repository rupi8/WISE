#include <M5ModuleLLM.h>

void setup() {
  // Inicializar el M5Stack LLM
  M5.begin();
  
  // Inicializa la pantalla si está conectada
  M5.Lcd.print("Hello World!");
}

void loop() {
  // El código se queda aquí para que el mensaje sea mostrado
}
