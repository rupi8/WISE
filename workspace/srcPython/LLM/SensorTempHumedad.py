from m5stack import *
from m5ui import *
from uiflow import *
import time
import dht

# Inicialización del sensor DHT
sensor = dht.DHT11(Pin(21))  # Pin 21 en el M5Stack

# Leer la temperatura y humedad
def read_dht():
    sensor.measure()  # Realiza la medición
    temp = sensor.temperature()  # Lee la temperatura
    humidity = sensor.humidity()  # Lee la humedad
    return temp, humidity

# Mostrar los resultados
temp, humidity = read_dht()
print(f"Temperatura: {temp} °C")
print(f"Humedad: {humidity} %")
