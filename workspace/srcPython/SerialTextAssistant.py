import serial
import time
from m5stack import lcd

class M5ModuleLLM:
    def __init__(self, port, baudrate):
        self.ser = serial.Serial(port, baudrate, timeout=1)

    def begin(self):
        # Inicializa el módulo LLM (envía un comando de inicialización al módulo LLM)
        self.ser.write(b'INIT_LLM\n')

    def check_connection(self):
        # Verifica la conexión del módulo LLM
        self.ser.write(b'CHECK_CONNECTION\n')
        response = self.ser.readline().decode('utf-8').strip()
        return response == 'OK'

    def reset(self):
        # Resetea el módulo LLM
        self.ser.write(b'RESET_LLM\n')

    def setup(self, max_token_len):
        # Configura el módulo LLM y devuelve el ID de trabajo
        self.ser.write(f'SETUP_LLM {max_token_len}\n'.encode('utf-8'))
        response = self.ser.readline().decode('utf-8').strip()
        return response

    def inference_and_wait_result(self, work_id, question, callback):
        # Envía la pregunta al módulo LLM y espera el resultado de la inferencia
        self.ser.write(f'INFERENCE {work_id} {question}\n'.encode('utf-8'))
        result = self.ser.readline().decode('utf-8').strip()
        callback(result)

def main():
    # Inicializa la pantalla
    lcd.clear()
    lcd.setTextSize(2)
    lcd.setTextScroll(True)

    # Inicializa la comunicación serial USB
    comm_serial_port = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

    # Inicializa el puerto serie para el módulo LLM
    module_llm = M5ModuleLLM('/dev/ttyUSB1', 115200)
    module_llm.begin()

    # Asegura que el módulo LLM esté conectado
    lcd.print(">> Check ModuleLLM connection..\n")
    while not module_llm.check_connection():
        time.sleep(1)

    # Reinicia el módulo LLM
    lcd.print(">> Reset ModuleLLM..\n")
    module_llm.reset()

    # Configura el módulo LLM y guarda el ID de trabajo devuelto
    lcd.print(">> Setup llm..\n")
    llm_work_id = module_llm.setup(1023)

    lcd.print(">> Setup finish\n")
    lcd.print(">> Try send your question via usb serial port\n")
    lcd.setTextColor(lcd.GREEN)
    lcd.print("e.g. \nHi, What's your name?\n")
    lcd.print("(end with CRLF \\r\\n)\n\n")

    received_question = ""
    question_ok = False

    while True:
        # Verifica si hay datos disponibles en el puerto serie USB
        if comm_serial_port.in_waiting > 0:
            while comm_serial_port.in_waiting > 0:
                in_char = comm_serial_port.read().decode('utf-8')
                received_question += in_char

                # Verifica si la pregunta ha terminado
                if received_question.endswith("\r\n"):
                    received_question = received_question[:-2]
                    question_ok = True
                    break

        # Si la pregunta es válida
        if question_ok:
            lcd.setTextColor(lcd.GREEN)
            lcd.print(f"<< {received_question}\n")
            lcd.setTextColor(lcd.YELLOW)
            lcd.print(">> ")
            comm_serial_port.write(f"<< \"{received_question}\"\n".encode('utf-8'))
            comm_serial_port.write(">> ".encode('utf-8'))

            # Envía la pregunta al módulo LLM y espera el resultado de la inferencia
            module_llm.inference_and_wait_result(llm_work_id, received_question, lambda result: (
                lcd.print(result),
                comm_serial_port.write(result.encode('utf-8'))
            ))

            # Limpia la pregunta para la siguiente
            received_question = ""
            question_ok = False

            lcd.println()
            comm_serial_port.write("\n".encode('utf-8'))

        time.sleep(0.02)  # Pausa breve para evitar sobrecargar el ciclo del loop

if __name__ == "__main__":
    main()