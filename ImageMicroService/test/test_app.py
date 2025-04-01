import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controller.app import app

def test_home():
    client = app.test_client()
    response = client.get('/api/image/test')
    print("Status Code:", response.status_code)  # Inspecciona el código de estado
    print("Response JSON:", response.get_json())  # Inspecciona la respuesta
    assert response.status_code == 200
    assert response.get_json() == {"message": "Microservicio funcionando!"}

def test_command_valid():
    client = app.test_client()
    response = client.post('/api/image/command', json={"command": "subir brillo"})
    print("Status Code:", response.status_code)
    print("Response JSON:", response.get_json())
    assert response.status_code == 200
    assert "result" in response.get_json()