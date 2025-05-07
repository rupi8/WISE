#!/usr/bin/env python3
import socket
import threading
import os
import time
import numpy as np
from subprocess import run, CalledProcessError

MATRIX_FOLDER = "/home/iot/Desktop/PAE/intento1/matrixes"
NUM_CLIENTS   = 10
PORT          = 5000

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

def load_matrix_from_file(name):
    filename = f"image_matrix_{name}.py"
    path = os.path.join(MATRIX_FOLDER, filename)
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    env = {}
    with open(path) as f:
        exec(f.read(), env)
    if "image_matrix" not in env:
        raise ValueError(f"no image_matrix in {filename}")
    return np.array(env["image_matrix"], dtype=np.uint16)

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

def handle_full_load_segment(conn, addr, name, offset, length, data_bytes):
    try:
        segment = data_bytes[offset:offset+length]
        header = f"LOAD_IMAGE:{name}:{length}\n".encode()
        conn.sendall(header)
        t0 = time.time()
        conn.sendall(segment)
        t1 = time.time()
        bps = (length * 8) / (t1 - t0)
        print(f"[S]→{addr} LOAD {length}B in {t1 - t0:.2f}s → {bps / 1e6:.2f}Mbps")
        conn.settimeout(5.0)
        try:
            ack = conn.recv(1024).decode().strip()
            print(f"[S] ACK from {addr}: {ack}")
        except socket.timeout:
            print(f"[S] No ACK (timeout) from {addr}")
        finally:
            conn.settimeout(None)
    except Exception as e:
        print(f"[S] Error during LOAD for {addr}: {e}")

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
            t = threading.Thread(target=handle_full_load_segment,
                                 args=(conn, addr, name, off, ln, data))
            t.start()
            threads.append(t)
        else:
            print(f"[S] No client for LOAD segment #{idx + 1}")
    for t in threads:
        t.join()

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
            print(f"[S] Expected IMAGES:, got '{line}'")
            return names
        while True:
            line = fp.readline().strip()
            if line == "END_IMAGES":
                break
            if line:
                names.add(line)
    except Exception as e:
        print(f"[S] Error reading list: {e}")
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

def main():
    server_sock = socket.socket()
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
            line = input(">> ").strip().split()
            if not line:
                continue
            cmd = line[0].upper()

            if cmd == "LIST":
                common = list_images_from_all_clients(clients)
                print("[S] Common:", common or "(none)")

            elif cmd == "LOAD" and len(line) == 2:
                name = line[1]
                try:
                    mat = load_matrix_from_file(name)
                except Exception as e:
                    print(f"[S] Load error: {e}")
                    continue
                data = mat.tobytes()
                print(f"[S] Load & distribute '{name}' → {len(data)}B")
                send_full(server_sock, clients, name, data)

            elif cmd == "SEND" and len(line) == 2:
                name = line[1]
                try:
                    mat = load_matrix_from_file(name)
                except Exception as e:
                    print(f"[S] Load error: {e}")
                    continue
                data = mat.tobytes()
                print(f"[S] Segment send '{name}' → {len(data)}B")
                send_segmented(server_sock, clients, data)
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
                    mat = load_matrix_from_file("text")
                    data = mat.tobytes()
                    print(f"[S] Segment send 'text' → {len(data)}B")
                    send_segmented(server_sock, clients, data)
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
        server_sock.close()
        print("[S] Server socket closed.")

if __name__ == "__main__":
    main()