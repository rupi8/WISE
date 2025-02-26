#include <M5ModuleLLM.h>
#include <Camera.h> // Librería para capturar imágenes

Camera camera; // Instancia para la cámara

void setup() {
  M5.begin();
  camera.begin(); // Inicializa la cámara
}

void loop() {
  // Captura una imagen y la almacena
  camera.captureImage();
  
  // Aquí puedes procesar la imagen, como hacer reconocimiento facial o de gestos
  M5.Lcd.print("Imagen capturada");
  delay(2000); // Espera 2 segundos antes de capturar otra imagen
}

