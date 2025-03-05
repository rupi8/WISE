from m5stack import *
from m5ui import *
from uiflow import *
import time

# Inicialización del acelerómetro y giroscopio
imu = M5IMU()

# Leer datos del acelerómetro y giroscopio
def read_imu():
    accel = imu.get_accel_data()  # Lee el acelerómetro
    gyro = imu.get_gyro_data()    # Lee el giroscopio
    return accel, gyro

# Mostrar los resultados
accel, gyro = read_imu()
print(f"Acelerómetro: {accel}")
print(f"Giroscopio: {gyro}")
