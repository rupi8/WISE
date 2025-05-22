import sys
import os
import socket
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controller.shared_state import clients  # Importar la lista de clientes
from flask import Flask
from flask_restx import Api
from extensions import db  # Importar db desde extensions.py
from controller.routes.image_routes import ns as image_ns  # Importa el namespace de rutas

# Locks and shared state
ACK_LOCK = threading.Lock()
ACKED_INDICES = set()


# Configuración
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DB_PATH     = os.path.join(BASE_DIR, "../controller/instance/image_service.db")
NUM_CLIENTS = 10
PORT        = 5000


# Mapeo del último octeto IP → índice de segmento
SEGMENT_ORDER = {
   20: 0, 21: 1, 22: 2, 23: 3, 24: 4,
   25: 5, 26: 6, 27: 7, 28: 8, 29: 9,
}


def prune_dead_clients(clients):
    alive = []
    for conn, addr in clients:
        try:
            conn.sendall(b"")  # zero-byte check
            alive.append((conn, addr))
        except:
            print(f"[S] Removing dead client {addr}")
            try: conn.close()
            except: pass
    return alive


def tcp_server():
    server_sock = socket.socket()
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("", PORT))
    server_sock.listen(NUM_CLIENTS)
    print(f"[S] Listening on port {PORT} for {NUM_CLIENTS} clients…")
    
    try:
       clients = prune_dead_clients(clients)
       while len(clients) < NUM_CLIENTS:
           conn, addr = server_sock.accept()
           print(f"[S] Client connected: {addr}")
           clients.append((conn, addr))

       print("[S] Ready. Commands: LIST | LOAD <name> | SEND <name> | SHOW <name> | INCREASE | DECREASE | TEXT <message>")
    except KeyboardInterrupt:
       print("\n[S] Interrupt received. Shutting down…")
    finally:
       for conn, _ in clients:
           try:
               conn.close()
           except:
               pass
       server_sock.close()
       print("[S] Server closed.")


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
    # Verifica si se ejecuta en modo depuración
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    tcp_thread = threading.Thread(target=tcp_server, daemon=True)
    tcp_thread.start()

    # Ejecuta la aplicación Flask
    app.run(host='0.0.0.0', port=8080, debug=debug_mode, use_reloader=not debug_mode)


