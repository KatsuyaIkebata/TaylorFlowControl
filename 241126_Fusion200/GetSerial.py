import serial
import serial. tools.list_ports

for port in serial.tools.list_ports.comports():
    print(f'# {port = } / {port.device =}')