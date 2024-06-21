import serial
import time

ser1 = serial.Serial(
    port='COM6',         # シリンジポンプ1のCOMポート
    baudrate=115200,     # ボーレート
    timeout=1            # タイムアウト
)


ser2 = serial.Serial(
    port='COM7',         # シリンジポンプ2のCOMポート
    baudrate=115200,     # ボーレート
    timeout=1            # タイムアウト
)


def send_command(ser, command):
    """シリンジポンプにコマンドを送信し、応答を受け取る"""
    command += '\r\n'
    ser.write(command.encode())
    time.sleep(0.2)
    response = ser.read(ser.in_waiting or 1).decode().strip()
    return response

response = send_command(ser1, "address")
print(f'Pump 1 Response:', (response))

response = send_command(ser2, "address")
print(f'Pump 2 Response:', (response))


ser1.close()
ser2.close()
print("Serial connections closed.")