#!/usr/bin/env python3
import socket
import threading
import os
import time
import numpy as np
import sqlite3
import sys
from subprocess import run, CalledProcessError
from scripts_tcp.fake_clients import FakeConnection  # Si lo usas para tests


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




def load_matrix_from_db(image_name):
   """
   1) Lee el BLOB (texto de un .py) que define `image_matrix = [[...], ...]`
   2) Ejecuta ese texto para extraer la lista anidada
   3) Devuelve un ndarray(uint16) con la forma original
   """
   if not os.path.exists(DB_PATH):
       raise FileNotFoundError(f"No se encontró la base de datos en {DB_PATH}")


   conn   = sqlite3.connect(DB_PATH)
   cursor = conn.cursor()
   cursor.execute("SELECT image_data FROM images WHERE image_name = ?", (image_name,))
   row = cursor.fetchone()
   conn.close()


   if not row:
       raise ValueError(f"No se encontró una imagen con nombre '{image_name}'")


   blob = row[0]
   # Si vino como bytes, lo decodificamos; si ya es str, lo usamos tal cual
   text = blob.decode('utf-8') if isinstance(blob, (bytes, bytearray)) else blob


   # Ejecutamos el código en un namespace aislado
   namespace = {}
   exec(text, {}, namespace)


   if 'image_matrix' not in namespace:
       raise ValueError("El BLOB no define la variable 'image_matrix'")


   mat = np.array(namespace['image_matrix'], dtype=np.uint16)
   alto, ancho = mat.shape
   print(f"[DEBUG] Matriz '{image_name}' cargada: shape = ({alto}, {ancho})")
   return mat




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
           if ack == "ACK":
               with ACK_LOCK:
                   ACKED_INDICES.add(idx)
           print(f"[S] ACK from {addr} idx={idx}: {ack}")
       except socket.timeout:
           print(f"[S] No ACK (timeout) from {addr} idx={idx}")
       finally:
           conn.settimeout(None)


   except Exception as e:
       print(f"[S] Error enviando segmento a {addr} idx={idx}: {e}")




def send_segmented(clients, data):
   global ACKED_INDICES
   ACKED_INDICES.clear()


   segments        = calculate_segments(len(data), NUM_CLIENTS)
   ordered_clients = [None]*NUM_CLIENTS
   for conn, addr in clients:
       last = int(addr[0].split('.')[-1])
       if last in SEGMENT_ORDER:
           ordered_clients[SEGMENT_ORDER[last]] = (conn, addr)


   # 1) Envío inicial
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
           print(f"[S] No hay cliente para idx={idx}")
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
   for conn, _ in clients:
       try: conn.sendall(b"READY\n")
       except: pass


   go_set   = set()
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
           except: pass
       time.sleep(0.1)


   if len(go_set) == NUM_CLIENTS:
       print("[S] Todos GO recibidos.")
   else:
       faltan = set(range(NUM_CLIENTS)) - go_set
       print(f"[S] Faltaron GOs de índices: {faltan}")


   # 4) SHOW_TEMP y CLEAR_BUFFER
   for cmd in ("SHOW_TEMP", "CLEAR_BUFFER"):
       print(f"[S] Broadcast {cmd}")
       for conn, _ in clients:
           try: conn.sendall(f"{cmd}\n".encode())
           except: pass


def handle_full_load_segment(conn, addr, idx, name, offset, length, data):
   try:
       header = f"LOAD_IMAGE:{name}:{length}\n".encode()
       segment = data[offset:offset+length]
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




def send_full(clients, name, data):
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
           print(f"[S] No hay cliente para LOAD idx={idx}")
   for t in threads: t.join()




def broadcast(clients, cmd):
   for conn, _ in clients:
       try:
           conn.sendall((cmd + "\n").encode())
       except Exception as e:
           print(f"[S] Error enviando '{cmd}': {e}")




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
           if line == "END_IMAGES":
               break
           if line:
               names.add(line)
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




def main(clients, inputString):

    while True:
        parts = inputString.strip().split()
        if not parts:
            continue
        cmd = parts[0].upper()


        if cmd == "LIST":
            common = list_images_from_all_clients(clients)
            print("[S] Common:", common or "(none)")
            break


        elif cmd == "LOAD" and len(parts) == 2:
            name = parts[1]
            try:
                mat = load_matrix_from_db(name)
            except Exception as e:
                print(f"[S] Load error: {e}")
                continue
            data = mat.tobytes()
            print(f"[S] Load & distribute '{name}' → {len(data)}B")
            send_full(clients, name, data)
            break


        elif cmd == "SEND" and len(parts) == 2:
            name = parts[1]
            try:
                mat = load_matrix_from_db(name)
            except Exception as e:
                print(f"[S] Load error: {e}")
                continue
            data = mat.tobytes()
            print(f"[S] Segment send '{name}' → {len(data)}B")
            send_segmented(clients, data)
            break


        elif cmd == "SHOW" and len(parts) == 2:
            broadcast(clients, f"SHOW_IMAGE:{parts[1]}")
            break


        elif cmd == "INCREASE":
            broadcast(clients, "increase")
            break


        elif cmd == "DECREASE":
            broadcast(clients, "decrease")
            break


        elif cmd == "TEXT" and len(parts) >= 2:
            if len(parts) > 2 and parts[2] == "off":
                print("[S] TEXT OFF: Cerrando conexiones con los clientes...")
                for conn, _ in clients:
                    try:
                        conn.close()
                    except Exception as e:
                        print(f"[S] Error cerrando conexión: {e}")
                clients.clear()
                print("[S] Todas las conexiones han sido cerradas.")
                break
            elif (len(parts) > 2 and parts[2] == "on" and len(clients) < 10 ):
                server_sock = socket.socket()
                server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_sock.bind(("", PORT))
                server_sock.listen(NUM_CLIENTS)
                print(f"[S] Listening on port {PORT} for {NUM_CLIENTS} clients…")
                try:
                    while len(clients) < NUM_CLIENTS:
                        conn, addr = server_sock.accept()
                        print(f"[S] Client connected: {addr}")
                        clients.append((conn, addr))
                finally:
                    break
            else:
                message = " ".join(parts[1:])
                print(f"[S] Generating image for text: '{message}'")
                try:
                    run(["python3", "text_to_image.py", message], check=True)
                    mat = load_matrix_from_db('text')
                    data = mat.tobytes()
                    print(f"[S] Segment send 'text' → {len(data)}B")
                    send_segmented(clients, data)
                except CalledProcessError as e:
                    print(f"[S] text_to_image.py error: {e}")
                except Exception as e:
                    print(f"[S] Error sending text image: {e}")
                break

        else:
            print("Usage: LIST | LOAD <name> | SEND <name> | SHOW <name> | INCREASE | DECREASE | TEXT <message>")







if __name__ == "__main__":
   main("")



