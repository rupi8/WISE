import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from flask_restx import Api
from extensions import db  # Importar db desde extensions.py
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
    version='1.0',
    title='Image Microservice API',
    description='API for managing images and brightness'
)

# Registra el namespace de imágenes
api.add_namespace(image_ns)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)