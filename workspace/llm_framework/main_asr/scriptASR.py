import pyaudio
import json
import zmq
import threading
import time
import argparse
import socket

# Configuración del LLM630
LLM_IP = "10.4.37.198"
LLM_PORT = 10001  # Ajusta según la configuración real
CHANNEL_URL = f"tcp://{LLM_IP}:{LLM_PORT}"

# Configuración de audio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Contexto ZeroMQ
context = zmq.Context()

def create_tcp_connection(host, port):
    """Crea una conexión TCP al servidor."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    return sock

def send_json(sock, data):
    """Envía datos JSON al servidor usando TCP."""
    json_data = json.dumps(data, ensure_ascii=False, indent=4)
    sock.sendall(json_data.encode('utf-8'))

def receive_response(sock):
    """Recibe una respuesta JSON del servidor usando TCP."""
    response = ''
    while True:
        part = sock.recv(4096).decode('utf-8')
        response += part
        if '\n' in response:
            break
    return json.loads(response.strip())

def create_init_data():
    """Crea un JSON actualizado para configurar el ASR."""
    return {
        "request_id": "asr_001",
        "work_id": "task1",
        "action": "setup",
        "object": "llm.setup",
        "data": {
            "mode":"sherpa-ncnn-streaming-zipformer-20M-2023-02-17",
            "type":"asr",
            "capabilities":[
                "Automatic_Speech_Recognition",
                "English"
            ],
            "input_type":[
                "sys.pcm",
                "sys.cap.0_0"
            ],
            "output_type":[
                "asr.utf-8",
                "asr.bool"
            ],
            "mode_param":{
                "model_config.encoder_param":"encoder_jit_trace-pnnx.ncnn.param",
                "model_config.encoder_bin":"encoder_jit_trace-pnnx.ncnn.bin",
                "model_config.decoder_param":"decoder_jit_trace-pnnx.ncnn.param",
                "model_config.decoder_bin":"decoder_jit_trace-pnnx.ncnn.bin",
                "model_config.joiner_param":"joiner_jit_trace-pnnx.ncnn.param",
                "model_config.joiner_bin":"joiner_jit_trace-pnnx.ncnn.bin",
                "model_config.tokens":"tokens.txt",
                "feat_config.feature_dim":80,
                "feat_config.sampling_rate":16000,
                "endpoint_config.rule1.min_trailing_silence":2.4,
                "endpoint_config.rule2.min_trailing_silence":1.2,
                "endpoint_config.rule3.min_utterance_length":30,
                "enable_endpoint":True,
                "awake_delay":50
            },
            "mode_param_bak":{
                "model_config.encoder_opt.num_threads":2,
                "model_config.decoder_opt.num_threads":2,
                "model_config.joiner_opt.num_threads":2,
                "decoder_config.method":"greedy_search",
                "decoder_config.num_active_paths":4,
                "endpoint_config.rule1.must_contain_nonsilence":False,
                "endpoint_config.rule1.min_utterance_length":0,
                "endpoint_config.rule2.must_contain_nonsilence":True,
                "endpoint_config.rule2.min_utterance_length":0,
                "endpoint_config.rule3.must_contain_nonsilence":False,
                "endpoint_config.rule3.min_trailing_silence":0,
                "hotwords_file":"",
                "hotwords_score":1.5
            }
        }
    }

def setup_asr(host, port):
    """Envía la configuración inicial al LLM630 usando TCP."""
    sock = create_tcp_connection(host, port)
    print("Enviando configuración al LLM630...")
    try:
        send_json(sock, create_init_data())
        print("Esperando respuesta...")
        response = receive_response(sock)
        print("Respuesta de configuración:", response)
        if response.get("error"):
            print(f"Error del servidor: {response['error']['message']} (Código: {response['error']['code']})")
            return False
        return response.get("code", -1) == 0
    except Exception as e:
        print(f"Error al configurar el ASR: {e}")
        return False
    finally:
        sock.close()

def send_audio():
    """Captura audio y lo envía usando ZeroMQ PUB con timeout."""
    socket = context.socket(zmq.PUB)
    socket.setsockopt(zmq.SNDTIMEO, 5000)  # Timeout para envío
    socket.connect(CHANNEL_URL)
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("Enviando audio desde el micrófono... (habla ahora)")
    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            try:
                socket.send_multipart([b"sys.pcm", data])  # Enviar como mensaje multipart
            except zmq.error.Again:
                print("Error: Timeout al enviar audio.")
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Deteniendo captura de audio...")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        socket.close()

def receive_text():
    """Recibe texto reconocido usando ZeroMQ SUB con timeout."""
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.RCVTIMEO, 5000)  # Timeout para recepción
    socket.connect(CHANNEL_URL)
    socket.setsockopt_string(zmq.SUBSCRIBE, "asr.utf-8.stream")
    print("Esperando texto reconocido...")
    try:
        while True:
            try:
                topic, message = socket.recv_multipart()
                data = json.loads(message.decode('utf-8'))
                print(f"Texto reconocido: {data.get('delta', '')}")
                if data.get("finish", False):
                    print("Reconocimiento finalizado.")
                    break
            except zmq.error.Again:
                print("Error: Timeout al recibir texto.")
    except KeyboardInterrupt:
        print("Deteniendo recepción...")
    finally:
        socket.close()

def main(host, port):
    if not setup_asr(host, port):
        print("Error al configurar el ASR. Abortando.")
        return
    audio_thread = threading.Thread(target=send_audio)
    text_thread = threading.Thread(target=receive_text)
    audio_thread.start()
    text_thread.start()
    try:
        audio_thread.join()
        text_thread.join()
    except KeyboardInterrupt:
        print("Programa terminado por el usuario.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ZeroMQ Client for ASR.')
    parser.add_argument('--host', type=str, default='localhost', help='Server hostname (default: localhost)')
    parser.add_argument('--port', type=int, default=10001, help='Server port (default: 10001)')
    args = parser.parse_args()
    main(args.host, args.port)