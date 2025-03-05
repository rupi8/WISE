from m5stack import *
from m5ui import *
from uiflow import *
import time

# Inicialización de la cámara
camera = M5Camera()

# Configurar la cámara
camera.resolution = (640, 480)  # Resolución de la cámara
camera.flip = False  # No voltear imagen

# Capturar una imagen
def capture_image():
    image = camera.capture()  # Captura una imagen
    return image

# Mostrar la imagen capturada
image = capture_image()
print("Imagen capturada: ", image)
