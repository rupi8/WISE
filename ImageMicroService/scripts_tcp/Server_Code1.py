#!/usr/bin/env python3
import socket
import threading
import os
import time
import numpy as np
import sqlite3  # Para conexión a la base de datos
import io
from subprocess import run, CalledProcessError
from scripts_tcp.fake_clients import FakeConnection  # Importa la clase FakeConnection desde fake_clients.py

# Locks and shared state
ACK_LOCK = threading.Lock()
ACKED_INDICES = set()

# Configuración
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Directorio de Server_Code1.py
DB_PATH = os.path.join(BASE_DIR, "../controller/instance/image_service.db")
NUM_CLIENTS = 10
PORT = 5000

# Mapeo del último octeto IP → índice de segmento
SEGMENT_ORDER = {
    20: 0, 21: 1, 22: 2, 23: 3, 24: 4,
    25: 5, 26: 6, 27: 7, 28: 8, 29: 9,
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
    rem  = data_len % parts
    segs = []
    off  = 0
    for i in range(parts):
        ln = base + (1 if i < rem else 0)
        segs.append((off, ln))
        off += ln
    return segs

def handle_segment_direct(conn, addr, idx, offset, length, data):
    """
    Envia el segmento a un cliente particular y registra su ACK
    """
    global ACKED_INDICES
    try:
        header = f"SEGMENT:{offset}:{length}\n".encode()
        conn.sendall(header)
        t0 = time.time()
        conn.sendall(data[offset:offset+length])
        t1 = time.time()
        bps = (length*8)/(t1-t0)
        print(f"[S]→{addr} idx={idx} {length}B in {t1-t0:.2f}s → {bps/1e6:.2f}Mbps")

        conn.settimeout(10.0)
        try:
            ack = conn.recv(1024).decode().strip()
            print(f"[S] ACK from {addr} idx={idx}: {ack}")
            if ack == "ACK":
                with ACK_LOCK:
                    ACKED_INDICES.add(idx)  # ← NUEVO
        except socket.timeout:
            print(f"[S] No ACK (timeout) from {addr} idx={idx}")
        finally:
            conn.settimeout(None)

    except Exception as e:
        print(f"[S] Error sending segment to {addr} idx={idx}: {e}")

def send_segmented(server_sock, clients, data):
    """
    Envia todos los segmentos, espera ACKs, reintenta faltantes, handshake READY/GO,
    y finalmente envía SHOW_TEMP y CLEAR_BUFFER
    """
    global ACKED_INDICES
    ACKED_INDICES.clear()  # ← NUEVO

    segments       = calculate_segments(len(data), NUM_CLIENTS)
    ordered_clients= [None]*NUM_CLIENTS

    # Ordena clientes según SEGMENT_ORDER
    for conn, addr in clients:
        last = int(addr[0].split('.')[-1])
        if last in SEGMENT_ORDER:
            ordered_clients[SEGMENT_ORDER[last]] = (conn, addr)

    # 1) Envío inicial de segmentos
    threads = []
    for idx, cli in enumerate(ordered_clients):
        if cli:
            conn, addr = cli
            off, ln = segments[idx]
            t = threading.Thread(
                target=handle_segment_direct,
                args=(conn, addr, idx, off, ln, data)
            )
            t.start()
            threads.append(t)
        else:
            print(f"[S] No client para idx={idx}")
    for t in threads: t.join()

    # 2) Reintentos para faltantes (hasta 2 veces)
    for retry in range(2):
        with ACK_LOCK:
            missing = [i for i in range(NUM_CLIENTS) if i not in ACKED_INDICES]
        if not missing:
            break
        print(f"[S] Retry {retry+1} para índices faltantes: {missing}")
        threads = []
        for idx in missing:
            cli = ordered_clients[idx]
            if cli:
                conn, addr = cli
                off, ln = segments[idx]
                t = threading.Thread(
                    target=handle_segment_direct,
                    args=(conn, addr, idx, off, ln, data)
                )
                t.start()
                threads.append(t)
        for t in threads: t.join()

    # 3) Handshake READY/GO
    print("[S] Broadcast READY")
    for conn, addr in clients:
        try:
            conn.sendall(b"READY\n")
        except:
            pass

    # Espera GO de cada cliente
    go_set = set()
    end_wait = time.time() + 15
    while time.time() < end_wait and len(go_set) < NUM_CLIENTS:
        for conn, addr in clients:
            conn.settimeout(1.0)
            try:
                line = conn.recv(64).decode().strip()
                if line == "GO":
                    last = int(addr[0].split('.')[-1])
                    if last in SEGMENT_ORDER:
                        go_set.add(SEGMENT_ORDER[last])
                        print(f"[S] GO from {addr}")
            except:
                pass
        time.sleep(0.1)

    if len(go_set) == NUM_CLIENTS:
        print("[S] Todos GO recibidos.")
    else:
        print(f"[S] Faltaron GOs: {set(range(NUM_CLIENTS))-go_set}")

    # 4) Mostrar y limpiar
    print("[S] Broadcast SHOW_TEMP")
    for conn, addr in clients:
        try:
            conn.sendall(b"SHOW_TEMP\n")
        except:
            pass

    print("[S] Broadcast CLEAR_BUFFER")
    for conn, addr in clients:
        try:
            conn.sendall(b"CLEAR_BUFFER\n")
        except:
            pass

def handle_full_load_segment(conn, addr, idx, name, offset, length, data_bytes):
    """
    Igual que send_segmented, pero con LOAD_IMAGE:<name>
    """
    try:
        segment = data_bytes[offset:offset+length]
        header  = f"LOAD_IMAGE:{name}:{length}\n".encode()
        conn.sendall(header)
        t0 = time.time()
        conn.sendall(segment)
        t1 = time.time()
        bps = (length*8)/(t1-t0)
        print(f"[S]→{addr} LOAD idx={idx} {length}B in {t1-t0:.2f}s → {bps/1e6:.2f}Mbps")
        conn.settimeout(5.0)
        try:
            ack = conn.recv(1024).decode().strip()
            print(f"[S] ACK from {addr} idx={idx}: {ack}")
        except socket.timeout:
            print(f"[S] No ACK (timeout) from {addr} idx={idx}")
        finally:
            conn.settimeout(None)
    except Exception as e:
        print(f"[S] Error during LOAD for {addr} idx={idx}: {e}")

def send_full(server_sock, clients, name, data):
    segments        = calculate_segments(len(data), NUM_CLIENTS)
    ordered_clients = [None]*NUM_CLIENTS

    for conn, addr in clients:
        last = int(addr[0].split('.')[-1])
        if last in SEGMENT_ORDER:
            ordered_clients[SEGMENT_ORDER[last]] = (conn, addr)

    threads = []
    for idx, cli in enumerate(ordered_clients):
        if cli:
            conn, addr = cli
            off, ln = segments[idx]
            t = threading.Thread(
                target=handle_full_load_segment,
                args=(conn, addr, idx, name, off, ln, data)
            )
            t.start()
            threads.append(t)
        else:
            print(f"[S] No client para LOAD idx={idx}")
    for t in threads: t.join()

def broadcast(clients, cmd):
    for conn, addr in clients:
        try:
            conn.sendall((cmd+"\n").encode())
            print(f"[S]→{addr}: {cmd}")
        except Exception as e:
            print(f"[S] Error sending '{cmd}' to {addr}: {e}")

def receive_list_from_client(conn, timeout=5.0):
    names = set()
    conn.settimeout(timeout)
    try:
        fp = conn.makefile("r")
        line = fp.readline().strip()
        if line != "IMAGES:":
            return names
        while True:
            line = fp.readline().strip()
            if line == "END_IMAGES": break
            if line: names.add(line)
    except:
        pass
    finally:
        conn.settimeout(None)
    return names

def list_images_from_all_clients(clients):
    broadcast(clients, "LIST_IMAGES")
    common = None
    for conn, addr in clients:
        s = receive_list_from_client(conn)
        print(f"[S] {addr} has {s}")
        common = s if common is None else (common & s)
    return common or set()

def blob_to_matrix(blob_data):
    return np.load(io.BytesIO(blob_data))

def main(inputString):
    server_sock = socket.socket()
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("", PORT))
    server_sock.listen(NUM_CLIENTS)
    print(f"[S] Listening on {PORT} for {NUM_CLIENTS} client(s)…")

    clients = []
    try:
        while len(clients) < NUM_CLIENTS:
            conn, addr = server_sock.accept()
            print(f"[S] Client connected: {addr}")
            clients.append((conn, addr))

        print("[S] Ready. Commands: LIST | LOAD <name> | SEND <name> | SHOW <name> | INCREASE | DECREASE | TEXT <message>")

        while True:
            parts = inputString.strip().split()
            if not parts: continue
            cmd = parts[0].upper()

            if cmd == "LIST":
                common = list_images_from_all_clients(clients)
                print("[S] Common:", common or "(none)")

            elif cmd == "LOAD" and len(parts)==2:
                name = parts[1]
                try:
                    mat = load_matrix_from_db(name)
                except Exception as e:
                    print(f"[S] Load error: {e}")
                    continue
                data = mat.tobytes()
                print(f"[S] Load & distribute '{name}' → {len(data)}B")
                send_full(server_sock, clients, name, data)

            elif cmd == "SEND" and len(parts)==2:
                name = parts[1]
                try:
                    mat = blob_to_matrix(load_matrix_from_db(name))
                except Exception as e:
                    print(f"[S] Load error: {e}")
                    continue
                data = mat.tobytes()
                print(f"[S] Segment send '{name}' → {len(data)}B")
                send_segmented(server_sock, clients, data)

            elif cmd == "SHOW" and len(parts)==2:
                broadcast(clients, f"SHOW_IMAGE:{parts[1]}")

            elif cmd == "INCREASE":
                broadcast(clients, "increase")

            elif cmd == "DECREASE":
                broadcast(clients, "decrease")

            elif cmd == "TEXT" and len(parts)>=2:
                message = " ".join(parts[1:])
                print(f"[S] Generating image for text: '{message}'")
                try:
                    run(["python3","text_to_image.py",message],check=True)
                    mat = load_matrix_from_db("text")
                    data = mat.tobytes()
                    print(f"[S] Segment send 'text' → {len(data)}B")
                    send_segmented(server_sock, clients, data)
                except CalledProcessError as e:
                    print(f"[S] text_to_image.py error: {e}")
                except Exception as e:
                    print(f"[S] Error sending text image: {e}")

            else:
                print("Usage: LIST | LOAD <name> | SEND <name> | SHOW <name> | INCREASE | DECREASE | TEXT <message>")

    except KeyboardInterrupt:
        print("\n[S] Interrupt received. Shutting down…")
    finally:
        for conn, addr in clients:
            try:
                conn.close()
            except:
                pass
        server_sock.close()
        print("[S] Server closed.")


if __name__ == "__main__":
    main()