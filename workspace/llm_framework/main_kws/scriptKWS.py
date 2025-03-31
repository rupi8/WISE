import socket
import json
import argparse
import sys
import time

# Configuración del host y puerto
HOST = "10.4.37.198"  # IP proporcionada
PORT = 10001
REMOTE_USER = "root"
REMOTE_HOST = "10.4.37.198"

# Tiempo máximo de ejecución del script (en segundos)
GLOBAL_TIMEOUT = 60  # 60 segundos

def create_tcp_connection(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)  # Timeout de 30 segundos por solicitud
        sock.connect((host, port))
        print(f"Conexión establecida con {host}:{port}")
        return sock
    except Exception as e:
        print(f"Error al conectar: {e}")
        return None

def send_json(sock, data):
    try:
        json_data = json.dumps(data, ensure_ascii=False) + '\n'
        print(f"Enviando: {json_data.strip()}")
        sock.sendall(json_data.encode('utf-8'))
    except Exception as e:
        print(f"Error al enviar: {e}")

def receive_response(sock, timeout=30):
    try:
        sock.settimeout(timeout)
        response = ''
        start_time = time.time()
        while time.time() - start_time < timeout:
            part = sock.recv(4096).decode('utf-8')
            response += part
            if '\n' in response:
                break
        print("Respuesta recibida:", response.strip())
        return json.loads(response.strip()) if response.strip() else {}
    except socket.timeout:
        print("Timeout: No se recibió respuesta a tiempo.")
        return {}
    except Exception as e:
        print(f"Error al recibir: {e}")
        return {}

def close_connection(sock):
    if sock:
        sock.close()

def create_init_data():
    return {
        "request_id": "kws_setup_001",
        "work_id": "kws",
        "action": "setup",
        "object": "kws.setup",
        "data": {
            "kws": "HELLO",
            "model": "sherpa-onnx-kws-zipformer-gigaspeech-3.3M-2024-01-01",
            "response_format": "kws.exec",
            "input": "sys.pcm",  # Usar el micrófono en tiempo real
            "enoutput": True
        }
    }

def parse_setup_response(response_data, sent_request_id):
    error = response_data.get('error')
    request_id = response_data.get('request_id')

    if request_id != sent_request_id:
        print(f"Request ID mismatch: sent {sent_request_id}, received {request_id}")
        return None

    if error and error.get('code') != 0:
        print(f"Error Code: {error['code']}, Message: {error['message']}")
        return None

    return response_data.get('work_id')

def setup(sock, init_data):
    sent_request_id = init_data['request_id']
    send_json(sock, init_data)
    response = receive_response(sock)
    response_data = json.loads(response)
    return parse_setup_response(response_data, sent_request_id)

def exit_session(sock, deinit_data):
    send_json(sock, deinit_data)
    response = receive_response(sock)
    response_data = json.loads(response)
    print("Exit Response:", response_data)

def parse_inference_response(response_data):
    error = response_data.get('error')
    if error and error.get('code') != 0:
        print(f"Error Code: {error['code']}, Message: {error['message']}")
        return None
    return response_data.get('data')

def main(host, port):
    # Registrar el tiempo de inicio para el temporizador global
    global_start_time = time.time()

    sock = create_tcp_connection(host, port)
    if not sock:
        return

    try:
        print("Setup KWS...")
        init_data = create_init_data()
        kws_work_id = setup(sock, init_data)
        if not kws_work_id:
            print("Setup KWS failed.")
            return
        print("Setup KWS finished. Work ID:", kws_work_id)

        # Bucle para escuchar la palabra clave con un tiempo máximo
        print("Di 'HELLO' cerca del micrófono del LLM630 para probar...")
        attempt = 0
        max_attempts = 10  # Máximo número de intentos
        inference_timeout = 30  # Tiempo máximo para el bucle de inferencia (en segundos)
        start_time = time.time()

        while attempt < max_attempts and (time.time() - start_time) < inference_timeout:
            # Verificar el tiempo global
            if (time.time() - global_start_time) >= GLOBAL_TIMEOUT:
                print(f"\nTiempo máximo de ejecución ({GLOBAL_TIMEOUT} segundos) alcanzado. Cerrando el programa.")
                break

            inference_data = {
                "request_id": f"kws_inference_{attempt}",
                "work_id": kws_work_id,
                "action": "inference",
                "object": "kws.exec",
                "data": {"index": 0, "finish": False}
            }
            send_json(sock, inference_data)
            response = receive_response(sock)
            data = parse_inference_response(response)
            if data is True:
                print("¡Palabra clave 'HELLO' detectada!")
                break
            elif data is False:
                print("No se detectó 'HELLO' aún...")
            elif data is None:
                print("Error en la inferencia.")
                break
            attempt += 1
            time.sleep(1)

        if (time.time() - start_time) >= inference_timeout:
            print(f"Tiempo máximo de inferencia ({inference_timeout} segundos) alcanzado. No se detectó 'HELLO'.")

        # Finalizar la sesión
        exit_data = {
            "request_id": "kws_exit_001",
            "work_id": kws_work_id,
            "action": "exit",
            "object": "kws.exit"
        }
        exit_session(sock, exit_data)

    finally:
        close_connection(sock)
        print("Conexión cerrada.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TCP Client to send JSON data.')
    parser.add_argument('--host', type=str, default='localhost', help='Server hostname (default: localhost)')
    parser.add_argument('--port', type=int, default=10001, help='Server port (default: 10001)')

    args = parser.parse_args()
    main(args.host, args.port)