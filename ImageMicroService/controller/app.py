import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from flask_restx import Api
from controller.routes.image_routes import ns as image_ns  # Importa el namespace de rutas

app = Flask(__name__)

#API documentación
api = Api(
    app,
    version='1.0.0',
    title='Microservice API WISE',
    description=(
        'API para controlar y procesar imágenes mediante comandos y gestos. '
        'Soporta ajustes de brillo, cambio de imágenes y comunicación con paneles LCD. '
        'Diseñada para integrarse con dispositivos como M5Stack y Raspberry Pi.'
    ),
    contact='upcCia.email@estudiantat.com',
    contact_url='https://tu-sitio-web.com',
    license='MIT',
    license_url='https://opensource.org/licenses/MIT',
    doc='/swagger/'  # Ruta para la interfaz Swagger
)

# Registra el namespace de imágenes
api.add_namespace(image_ns)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)