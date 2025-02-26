import time
import serial

class Camera:
    def __init__(self, port, baudrate):
        self.ser = serial.Serial(port, baudrate, timeout=1)
    
    def begin(self):
        # Inicializa la cámara (envía un comando de inicialización a la cámara)
        self.ser.write(b'INIT_CAMERA\n')
    
    def capture_image(self):
        # Captura una imagen (envía un comando de captura a la cámara)
        self.ser.write(b'CAPTURE_IMAGE\n')
        # Lee la respuesta de la cámara
        response = self.ser.readline().decode('utf-8').strip()
        return response

class M5Stack:
    def __init__(self):
        pass
    
    def begin(self):
        # Inicializa la pantalla (esto es solo un ejemplo, en realidad necesitarías una biblioteca específica para la pantalla)
        print("M5Stack initialized")
    
    def print(self, message):
        # Imprime un mensaje en la pantalla (esto es solo un ejemplo, en realidad necesitarías una biblioteca específica para la pantalla)
        print(message)

def main():
    camera = Camera('/dev/ttyACM0', 115200)
    m5 = M5Stack()
    
    m5.begin()
    camera.begin()
    
    while True:
        # Captura una imagen y la almacena
        image = camera.capture_image()
        
        # Aquí puedes procesar la imagen, como hacer reconocimiento facial o de gestos
        m5.print("Imagen capturada")
        time.sleep(2)  # Espera 2 segundos antes de capturar otra imagen

if __name__ == "__main__":
    main()