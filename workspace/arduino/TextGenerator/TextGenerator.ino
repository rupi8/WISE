#include <M5ModuleLLM.h>

void setup() {
  M5.begin();
  M5.Lcd.print("Generando texto...");
}

void loop() {
  // Supongamos que estamos usando una función de LLM para generar texto
  String generatedText = M5ModuleLLM.generateText("Hola, ¿cómo estás?");
  M5.Lcd.clear();
  M5.Lcd.print(generatedText);
  delay(5000); // Esperar 5 segundos para que se vea el texto generado
}
