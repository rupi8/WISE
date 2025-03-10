#!/bin/env python3
import zmq
from tokenizers import Tokenizer
import http.server
import socketserver
import threading
import socket
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
tokenizers_obj = {}
tokenizers_content = {}
server_obj = {}
url_path_map = {}

context = zmq.Context()
zmq_socket = context.socket(zmq.REP)
zmq_socket.bind("ipc:///tmp/rpc.tokenizer")


class Request(BaseHTTPRequestHandler):
    timeout = 5
    server_version = "Apache"
    def do_GET(self):
        server_ip, server_port = self.server.server_address
        val = 'http://localhost:{}'.format(server_port)
        token_obj = tokenizers_obj[url_path_map[val]]

        print(self.path)
        self.send_response(200)
        self.send_header("type", "get")
        self.end_headers()
        if self.path == "/bos_id":
            bos_id = token_obj.bos_id
            if bos_id is None:
                msg = json.dumps({"bos_id": -1})
            else:
                msg = json.dumps({"bos_id": bos_id})
        elif self.path == "/eos_id":
            eos_id = token_obj.eos_id
            if eos_id is None:
                msg = json.dumps({"eos_id": -1})
            else:
                msg = json.dumps({"eos_id": eos_id})
        else:
            msg = "error"
        print(msg)
        msg = str(msg).encode()
        self.wfile.write(msg)

    def do_POST(self):
        server_ip, server_port = self.server.server_address
        val = 'http://localhost:{}'.format(server_port)
        token_obj = tokenizers_obj[url_path_map[val]]
        data = self.rfile.read(
            int(self.headers["content-length"])
        )
        data = data.decode()
        self.send_response(200)
        self.send_header("type", "post")
        self.end_headers()
        if self.path == "/encode":
            req = json.loads(data)
            prompt = req['text']
            token_ids = token_obj.encode(prompt, tokenizers_content[url_path_map[val]])
            if token_ids is None:
                msg = json.dumps({"token_ids": -1})
            else:
                msg = json.dumps({"token_ids": token_ids})
        elif self.path == "/decode":
            req = json.loads(data)
            token_ids = req["token_ids"]
            text = token_obj.decode(token_ids)
            if text is None:
                msg = json.dumps({"text": ""})
            else:
                msg = json.dumps({"text": text})
        else:
            msg = "error"
        print(msg)
        msg = str(msg).encode()
        self.wfile.write(msg)


def start_server(httpd):
    httpd.serve_forever()

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

def rpc_forever():
    while True:
        try:
            message_parts = socket.recv_multipart()
            action = message_parts[0].decode('utf-8')
            rawmsg = message_parts[1].decode('utf-8')
            
            val = 'None'
            if action == 'creat_tokenizer':
                json_args = json.loads(rawmsg)
                tokenizer_path = json_args['path']
                tokenizer_content = json_args['content']
                tokenizers_content[tokenizer_path] = tokenizer_content
                tokenizers_obj[tokenizer_path] = Tokenizer.from_file(tokenizer_path)
                server_obj[tokenizer_path] = socketserver.TCPServer(("", 0), Request)
                server_ip, server_port = server_obj[tokenizer_path].server_address
                val = 'http://localhost:{}'.format(server_port)
                url_path_map[val] = tokenizer_path
                thread = threading.Thread(target=start_server, args=(server_obj[tokenizer_path]))
                thread.daemon = True
                thread.start()
                
            if action == 'close_tokenizer':
                tokenizer_path = rawmsg.decode('utf-8')
                server_obj[tokenizer_path].shutdown()
                server_obj[tokenizer_path].server_close()
                del server_obj[tokenizer_path]
                del tokenizers_obj[tokenizer_path]
                del tokenizers_content[tokenizer_path]
                for key, value in list(url_path_map.items()):
                    if value == tokenizer_path:
                        del url_path_map[key]
            zmq_socket.send(val.encode('utf-8'))
        except:
            zmq_socket.send('error'.encode('utf-8'))

if __name__ == "__main__":
    rpc_forever()
