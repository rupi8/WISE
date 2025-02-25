import serial

def connect_to_serial(port, baudrate):
    ser = None
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"Connected to {port} at {baudrate} baud.")
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                print(line)
            user_input = input("Enter message to send (or 'exit' to quit): ")
            if user_input.lower() == 'exit':
                break
            ser.write(user_input.encode('utf-8'))
    except serial.SerialException as e:
        print(f"Error: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("Connection closed.")

if __name__ == "__main__":
    connect_to_serial('COM4', 115200)