#!/usr/bin/env python3
import socket
import os
import threading
import time
import numpy as np
import sqlite3  # Para conexión a la base de datos
from subprocess import run, CalledProcessError
from scripts_tcp.fake_clients import FakeConnection  # Importa la clase FakeConnection desde fake_clients.py

# Configuración
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Directorio de Server_Code1.py
DB_PATH = os.path.join(BASE_DIR, "../controller/instance/image_service.db")
NUM_CLIENTS = 10
PORT = 5000
USE_FAKE_CLIENTS = True  # Cambia a True para usar fake_clients en lugar de conexiones reales

# Mapeo del último octeto IP → índice de segmento
SEGMENT_ORDER = {
    161: 0,
    168: 1,
    204: 2,
    221: 3,
    207: 4,
    226: 5,
    193: 6,
    184: 7,
    200: 8,
    214: 9,
}

def load_matrix_from_db(image_name):
    """
    Carga una matriz desde la base de datos.
    :param image_name: Nombre de la imagen en la tabla `images`.
    :return: Matriz NumPy cargada desde la base de datos.
    """
    

    if os.path.exists(DB_PATH):
        print(f"Base de datos encontrada en {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT image_data FROM images WHERE image_name = ?", (image_name,))
        row = cursor.fetchone()
        if row:
            return row
        else:
            raise ValueError(f"No se encontró una imagen con el nombre '{image_name}' en la base de datos.")
    else:
        print(f"Error: No se encontró la base de datos en {DB_PATH}")
def calculate_segments(data_len, parts=10):
    base = data_len // parts
    remainder = data_len % parts
    segments = []
    offset = 0
    for i in range(parts):
        length = base + (1 if i < remainder else 0)
        segments.append((offset, length))
        offset += length
    return segments

def handle_segment_direct(conn, addr, offset, length, data):
    try:
        header = f"SEGMENT:{offset}:{length}\n".encode()
        conn.sendall(header)
        t0 = time.time()
        conn.sendall(data[offset:offset + length])
        t1 = time.time()
        bps = (length * 8) / (t1 - t0)
        print(f"[S]→{addr} SEGMENT {length}B in {t1 - t0:.2f}s → {bps / 1e6:.2f}Mbps")
        conn.settimeout(5.0)
        try:
            ack = conn.recv(1024).decode().strip()
            print(f"[S] ACK from {addr}: {ack}")
        except socket.timeout:
            print(f"[S] No ACK (timeout) from {addr}")
        finally:
            conn.settimeout(None)
    except Exception as e:
        print(f"[S] Error sending segment to {addr}: {e}")

def send_segmented(server_sock, clients, data):
    segments = calculate_segments(len(data), 10)
    ordered_clients = [None] * 10

    for conn, addr in clients:
        ip_last = int(addr[0].split(".")[-1])
        if ip_last in SEGMENT_ORDER:
            idx = SEGMENT_ORDER[ip_last]
            ordered_clients[idx] = (conn, addr)

    threads = []
    for idx, client in enumerate(ordered_clients):
        if client is not None:
            conn, addr = client
            off, ln = segments[idx]
            t = threading.Thread(target=handle_segment_direct,
                                 args=(conn, addr, off, ln, data))
            t.start()
            threads.append(t)
        else:
            print(f"[S] No client for segment #{idx + 1}")
    for t in threads:
        t.join()

def send_full(server_sock, clients, name, data):
    segments = calculate_segments(len(data), 10)
    ordered_clients = [None] * 10

    for conn, addr in clients:
        ip_last = int(addr[0].split(".")[-1])
        if ip_last in SEGMENT_ORDER:
            idx = SEGMENT_ORDER[ip_last]
            ordered_clients[idx] = (conn, addr)

    threads = []
    for idx, client in enumerate(ordered_clients):
        if client is not None:
            conn, addr = client
            off, ln = segments[idx]
            t = threading.Thread(target=handle_segment_direct,
                                 args=(conn, addr, off, ln, data))
            t.start()
            threads.append(t)
        else:
            print(f"[S] No client for LOAD segment #{idx + 1}")
    for t in threads:
        t.join()

def broadcast(clients, cmd):
    for conn, addr in clients:
        try:
            conn.sendall((cmd + "\n").encode())
            print(f"[S]→{addr}: {cmd}")
        except Exception as e:
            print(f"[S] Error sending '{cmd}' to {addr}: {e}")

def main(inputString):
    if USE_FAKE_CLIENTS:
        # Crear una lista falsa de 10 clientes
        fakeClients = [
            (FakeConnection(), (f"192.168.1.{i+1}", 5000 + i)) for i in range(NUM_CLIENTS)
        ]
        print("[S] Using fake clients for testing.")
    else:
        # Configurar el servidor real
        server_sock = socket.socket()
        server_sock.bind(("", PORT))
        server_sock.listen(NUM_CLIENTS)
        print(f"[S] Listening on {PORT} for {NUM_CLIENTS} client(s)…")

        clients = []
        try:
            while len(fakeClients) < NUM_CLIENTS:
                conn, addr = server_sock.accept()
                print(f"[S] Client connected: {addr}")
                clients.append((conn, addr))
                raise KeyboardInterrupt  # Simular la interrupción para evitar el bucle infinito
        except KeyboardInterrupt:
            print("\n[S] Interrupt received. Shutting down server…")
            server_sock.close()
            return

    try:
        while True:
            line = inputString.strip().split()
            cmd = line[0].upper()

            if cmd == "LIST":
                print("[S] LIST command not implemented for database.")

            elif cmd == "LOAD" and len(line) == 2:
                name = line[1]
                try:
                    mat = load_matrix_from_db(name)
                except Exception as e:
                    print(f"[S] Load error: {e}")
                    continue
                data = mat.tobytes()
                print(f"[S] Load & distribute '{name}' → {len(data)}B")
                send_full(None, clients, name, data)

            elif cmd == "SEND" and len(line) == 2:
                name = line[1]
                try:
                    mat = load_matrix_from_db(name)
                except Exception as e:
                    print(f"[S] Load error: {e}")
                    continue
                data = mat.tobytes()
                print(f"[S] Segment send '{name}' → {len(data)}B")
                send_segmented(None, clients, data)
                time.sleep(1)
                broadcast(clients, "SHOW_TEMP")

            elif cmd == "SHOW" and len(line) == 2:
                broadcast(clients, f"SHOW_IMAGE:{line[1]}")

            elif cmd == "INCREASE":
                broadcast(clients, "increase")

            elif cmd == "DECREASE":
                broadcast(clients, "decrease")

            elif cmd == "TEXT" and len(line) >= 2:
                message = " ".join(line[1:])
                print(f"[S] Generating image for text: '{message}'")
                try:
                    run(["python3", "text_to_image.py", message], check=True)
                    mat = load_matrix_from_db("text")
                    data = mat.tobytes()
                    print(f"[S] Segment send 'text' → {len(data)}B")
                    send_segmented(None, clients, data)
                    time.sleep(1)
                    broadcast(clients, "SHOW_TEMP")
                except CalledProcessError as e:
                    print(f"[S] Error running text_to_image.py: {e}")
                except Exception as e:
                    print(f"[S] Error sending text image: {e}")

            else:
                print("Usage: LIST | LOAD <name> | SEND <name> | SHOW <name> | INCREASE | DECREASE | TEXT <message>")

    except KeyboardInterrupt:
        print("\n[S] Interrupt received. Shutting down server…")
    finally:
        for conn, addr in clients:
            try:
                conn.close()
                print(f"[S] Closed connection with {addr}")
            except Exception as e:
                print(f"[S] Error closing connection with {addr}: {e}")

if __name__ == "__main__":
    main()