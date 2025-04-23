import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from flask_restx import Api
from repository.database import db  # Importar db desde database.py
from controller.routes.image_routes import ns as image_ns  # Importa el namespace de rutas

# Crear la instancia de la aplicación Flask
app = Flask(__name__)

# Configuración de la base de datos (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///image_service.db'  # Base de datos en el directorio raíz del proyecto
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy con la app
db.init_app(app)

# Importar los modelos para que SQLAlchemy los reconozca (después de inicializar db)
from models.models import User, Image

# Crear la base de datos y las tablas dentro del contexto de la aplicación
with app.app_context():
    db.create_all()

# Configurar la API con Flask-RESTX
api = Api(
    app,
    version='1.0.0',
    title='Microservice API WISE',
    description=(
        'API to control and process images through commands and gestures. '
        'Supports brightness adjustments, image changes, and communication with LCD panels. '
        'Designed to integrate with devices like M5Stack and Raspberry Pi.'
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
    app.run(host='0.0.0.0', port=8080, debug=True)