class FakeConnection:
    def sendall(self, data):
        print(f"[FakeConnection] Data sent: {data.decode().strip()}")

    def close(self):
        print("[FakeConnection] Connection closed.")

# Crear una lista falsa de 10 clientes
fake_clients = [
    (FakeConnection(), (f"192.168.1.{i+1}", 5000 + i)) for i in range(10)
]
