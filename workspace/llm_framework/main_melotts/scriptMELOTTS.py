import socket
import json
import base64
import time
import os
import argparse

# Configuración para el LLM630
REMOTE_USER = "root"
REMOTE_HOST = "10.4.37.198"
REMOTE_PATH = "/dev/shm/temp_audio.wav"

def create_tcp_connection(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # Timeout de 5 segundos para la conexión inicial
        sock.connect((host, port))
        print(f"Conexión establecida con {host}:{port}")
        return sock
    except Exception as e:
        print(f"Error al conectar con el servidor: {e}")
        return None

def send_json(sock, data):
    try:
        json_data = json.dumps(data, ensure_ascii=False) + '\n'
        print(f"Enviando datos: {json_data.strip()}")
        sock.sendall(json_data.encode('utf-8'))
    except Exception as e:
        print(f"Error al enviar datos al servidor: {e}")

def receive_response(sock, timeout=5):
    try:
        sock.settimeout(timeout)
        response = ''
        start_time = time.time()
        while True:
            part = sock.recv(4096).decode('utf-8')
            response += part
            if '\n' in response:
                break
            if time.time() - start_time > timeout:
                print("Timeout parcial: No se recibió fin de línea a tiempo.")
                break
        responses = response.strip().split('\n')
        return [json.loads(resp) for resp in responses]
    except socket.timeout:
        print("Timeout: No se recibió respuesta del servidor a tiempo.")
        return []
    except Exception as e:
        print(f"Error al recibir respuesta del servidor: {e}")
        return []

def play_audio(audio_data):
    try:
        # Guardar el audio temporalmente en la PC
        local_audio_file = "temp_audio.wav"
        print(f"Guardando audio localmente en {local_audio_file}")
        with open(local_audio_file, "wb") as f:
            f.write(audio_data)

        # Transferir al LLM630 usando scp
        scp_command = f"scp {local_audio_file} {REMOTE_USER}@{REMOTE_HOST}:{REMOTE_PATH}"
        print(f"Transfiriendo audio: {scp_command}")
        os.system(scp_command)

        # Reproducir en el LLM630 usando ssh
        ssh_command = f"ssh {REMOTE_USER}@{REMOTE_HOST} 'aplay -D plughw:0,1 {REMOTE_PATH}'"
        print(f"Reproduciendo audio en LLM630: {ssh_command}")
        os.system(ssh_command)

        # Limpiar archivo local
        os.remove(local_audio_file)
    except Exception as e:
        print(f"Error al reproducir audio: {e}")

def close_connection(sock):
    if sock:
        try:
            sock.close()
            print("Conexión cerrada.")
        except Exception as e:
            print(f"Error al cerrar la conexión: {e}")

def clear_existing_tasks(sock):
    print("Intentando liberar tareas activas en el servidor...")
    possible_work_ids = ["melotts"] + [f"melotts_{i}" for i in range(3)]
    for work_id in possible_work_ids:
        send_json(sock, {
            "request_id": f"melotts_clear_{work_id}",
            "work_id": work_id,
            "action": "exit",
            "object": "melotts.exit"
        })
        responses = receive_response(sock, timeout=2)
        if not responses:
            print(f"No se recibió respuesta para work_id: {work_id}. Continuando...")
            continue
        for response_data in responses:
            error = response_data.get('error')
            if error and error.get('code') == -6:
                print(f"No hay tareas activas para liberar con work_id: {work_id}.")
            elif error and error.get('code') == -9:
                print(f"No se pudo liberar la tarea con work_id: {work_id} (unit call false).")
            else:
                print(f"Tarea con work_id {work_id} liberada con éxito:", response_data)
        time.sleep(0.1)

def create_init_data():
    return {
        "request_id": "melotts_001",
        "work_id": "melotts",
        "action": "setup",
        "object": "melotts.setup",
        "data": {
            "model": "melotts_zh-cn",
            "response_format": "tts.utf-8.stream",
            "enoutput": True,
            "input": ["tts.utf-8"],
            "mode_param": {
                "encoder": "/opt/m5stack/data/melotts_zh-cn/encoder.ort",
                "decoder": "/opt/m5stack/data/melotts_zh-cn/decoder.axmodel",
                "gbin": "/opt/m5stack/data/melotts_zh-cn/g.bin",
                "tokens": "/opt/m5stack/data/melotts_zh-cn/tokens.txt",
                "lexicon": "/opt/m5stack/data/melotts_zh-cn/lexicon.txt",
                "spacker_speed": 1.0,
                "mode_rate": 44100,
                "audio_rate": 16000,
                "awake_delay": 1000
            }
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
    clear_existing_tasks(sock)
    print("Configurando MELOTTS...")
    sent_request_id = init_data['request_id']
    send_json(sock, init_data)
    responses = receive_response(sock, timeout=5)
    if not responses:
        print("Advertencia: No se recibió respuesta del servidor durante la configuración. Usando work_id por defecto.")
        return "melotts"
    response_data = responses[0]
    error = response_data.get('error')
    if error and error.get('code') == -21:
        print("Error: El servidor no puede aceptar más tareas (task full).")
        return None
    work_id = parse_setup_response(response_data, sent_request_id)
    if not work_id:
        print("No se obtuvo work_id válido, usando valor por defecto 'melotts'.")
        return "melotts"
    return work_id

def exit_session(sock, deinit_data):
    send_json(sock, deinit_data)
    responses = receive_response(sock, timeout=2)
    response_data = responses[0] if responses else {}
    print("Exit Response:", response_data)

def parse_inference_response(response_data):
    error = response_data.get('error')
    if error and error.get('code') != 0:
        print(f"Error Code: {error['code']}, Message: {error['message']}")
        return None
    data = response_data.get('data')
    if isinstance(data, str):
        try:
            decoded_data = base64.b64decode(data)
            if decoded_data:
                return {"delta": decoded_data, "finish": response_data.get("finish", False)}
        except base64.binascii.Error:
            print("Error: No se pudo decodificar 'data' como base64.")
            return None
    print("Error: 'data' no es una cadena base64 válida.")
    return None

def main(host, port):
    sock = create_tcp_connection(host, port)
    if not sock:
        print("No se pudo establecer la conexión con el servidor.")
        return

    try:
        print("Setup MELOTTS...")
        init_data = create_init_data()
        melotts_work_id = setup(sock, init_data)
        if not melotts_work_id:
            print("Error crítico durante la configuración. Cerrando conexión.")
            return
        print("Setup MELOTTS finished. Work ID:", melotts_work_id)

        while True:
            user_input = input("Ingrese su texto para convertir a voz (o 'exit' para salir): ")
            if user_input.lower() == 'exit':
                break

            send_json(sock, {
                "request_id": "melotts_001",
                "work_id": melotts_work_id,
                "action": "inference",
                "object": "tts.utf-8",
                "data": {
                    "delta": user_input,
                    "index": 0,
                    "finish": True
                }
            })

            start_time = time.time()
            while True:
                responses = receive_response(sock, timeout=10)
                if not responses:
                    if time.time() - start_time > 15:
                        print("Error: No se recibió respuesta del servidor durante la inferencia.")
                        break
                for response_data in responses:
                    print("Respuesta cruda del servidor:", response_data)
                    data = parse_inference_response(response_data)
                    if data is None:
                        print("Error: Respuesta de inferencia no válida.")
                        continue
                    audio_data = data.get('delta')
                    finish = data.get('finish')
                    if audio_data:
                        play_audio(audio_data)
                    if finish:
                        print("Inferencia completada.")
                        break
                else:
                    continue
                break

        exit_session(sock, {
            "request_id": "melotts_exit",
            "work_id": melotts_work_id,
            "action": "exit"
        })
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        exit_session(sock, {
            "request_id": "melotts_exit",
            "work_id": "melotts",
            "action": "exit"
        })
        close_connection(sock)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TCP Client to interact with MELOTTS on LLM630.')
    parser.add_argument('--host', type=str, default='10.4.37.198', help='Server hostname (default: 10.4.37.198)')
    parser.add_argument('--port', type=int, default=10001, help='Server port (default: 10001)')
    args = parser.parse_args()
    main(args.host, args.port)