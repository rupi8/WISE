from m5stack import *
from m5ui import *
from uiflow import *
import json
import time

# Configuración de YOLO
yolo = M5YOLO()

# Inicialización de la cámara
camera = M5Camera()
camera.resolution = (640, 480)  # Resolución de la cámara
camera.flip = False  # No voltear imagen

# Detectar objetos usando YOLO
def detect_objects():
    image = camera.capture()  # Captura una imagen
    detections = yolo.detect(image)  # Detecta los objetos en la imagen
    return detections

# Mostrar los resultados
detections = detect_objects()
for detection in detections:
    print(f"Objeto detectado: {detection['class']} - Confianza: {detection['confidence']:.2f}")
