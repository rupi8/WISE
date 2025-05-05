#!/usr/bin/env python3 
import socket
import threading
import os
import time
import numpy as np

MATRIX_FOLDER = os.path.join(os.path.dirname(__file__), "matrixes")
NUM_CLIENTS   = 1
PORT          = 5000

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

def accept_new_client(server_sock, idx, clients):
    """Block on accept(), replace clients[idx] with the new conn/addr."""
    print(f"[S] Waiting for client #{idx} to reconnect…")
    conn, addr = server_sock.accept()
    print(f"[S] Reconnected: {addr}")
    clients[idx] = (conn, addr)

def handle_segment(server_sock, clients, i, offset, length, data):
    conn, addr = clients[i]
    try:
        header = f"SEGMENT:{offset}:{length}\n".encode()
        conn.sendall(header)
        t0 = time.time()
        conn.sendall(data[offset:offset+length])
        t1 = time.time()
        bps = (length*8)/(t1-t0)
        print(f"[S]→{addr} {length}B in {t1-t0:.2f}s → {bps/1e6:.2f}Mbps")
        conn.settimeout(5.0)
        try:
            ack = conn.recv(1024).decode().strip()
            print(f"[S] ACK from {addr}: {ack}")
        except socket.timeout:
            print(f"[S] No ACK (timeout) from {addr}")
        finally:
            conn.settimeout(None)
    except BrokenPipeError:
        print(f"[S] Broken pipe to {addr}; re-accepting")
        conn.close()
        accept_new_client(server_sock, i, clients)
    except Exception as e:
        print(f"[S] Error on segment → {addr}: {e}")

def handle_full_load(server_sock, clients, i, name, data_bytes):
    conn, addr = clients[i]
    try:
        length = len(data_bytes)
        header = f"LOAD_IMAGE:{name}:{length}\n".encode()
        conn.sendall(header)
        t0 = time.time()
        conn.sendall(data_bytes)
        t1 = time.time()
        bps = (length*8)/(t1-t0)
        print(f"[S]→{addr} full {length}B in {t1-t0:.2f}s → {bps/1e6:.2f}Mbps")
        conn.settimeout(5.0)
        try:
            ack = conn.recv(1024).decode().strip()
            print(f"[S] ACK from {addr}: {ack}")
        except socket.timeout:
            print(f"[S] No ACK (timeout) from {addr}")
        finally:
            conn.settimeout(None)
    except BrokenPipeError:
        print(f"[S] Broken pipe to {addr}; re-accepting")
        conn.close()
        accept_new_client(server_sock, i, clients)
    except Exception as e:
        print(f"[S] Error on full load → {addr}: {e}")

def send_segmented(server_sock, clients, data):
    total = len(data)
    per    = total // len(clients)
    threads = []
    for i in range(len(clients)):
        off = i*per
        ln  = total-off if i==len(clients)-1 else per
        t = threading.Thread(target=handle_segment,
                             args=(server_sock, clients, i, off, ln, data))
        t.start(); threads.append(t)
    for t in threads: t.join()

def send_full(server_sock, clients, name, data):
    threads = []
    for i in range(len(clients)):
        t = threading.Thread(target=handle_full_load,
                             args=(server_sock, clients, i, name, data))
        t.start(); threads.append(t)
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
            print(f"[S] Expected IMAGES:, got '{line}'")
            return names
        while True:
            line = fp.readline().strip()
            if line=="END_IMAGES": break
            if line: names.add(line)
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

def main(inputString):
    server_sock = socket.socket()
    server_sock.bind(("", PORT))
    server_sock.listen(NUM_CLIENTS)
    print(f"[S] Listening on {PORT} for {NUM_CLIENTS} client(s)…")

    clients = []
    while len(clients) < NUM_CLIENTS:
        conn, addr = server_sock.accept()
        print(f"[S] Client connected: {addr}")
        clients.append((conn, addr))

    print("[S] Ready. Commands: LIST | LOAD <name> | SEND <name> | SHOW <name> | INCREASE | DECREASE")
    while True:
        line = inputString
        if not line: continue
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
            print(f"[S] Full load '{name}' → {len(data)}B")
            send_full(server_sock, clients, name, data)

        elif cmd == "SEND" and len(line) == 2:
            name = line[1]
            try:
                mat = load_matrix_from_file(name)
            except Exception as e:
                print(f"[S] Load error: {e}")
                continue
            data = mat.tobytes()
            print(f"[S] Segmented send '{name}' → {len(data)}B")
            send_segmented(server_sock, clients, data)

        elif cmd == "SHOW" and len(line) == 2:
            broadcast(clients, f"SHOW_IMAGE:{line[1]}")

        elif cmd == "INCREASE":
            broadcast(clients, "increase")  # Send increase brightness command to all clients

        elif cmd == "DECREASE":
            broadcast(clients, "decrease")  # Send decrease brightness command to all clients

        else:
            print("Usage: LIST | LOAD <name> | SEND <name> | SHOW <name> | INCREASE | DECREASE")

if __name__ == "__main__":
    main()
