import serial
import time

# シリアルポートの設定
ser = serial.Serial(
    port='COM6',    # 使用するシリアルポートの名前
    baudrate=115200,  # ボーレートをシリンジポンプの設定に合わせる
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

def send_command(command):
    """ シリンジポンプにコマンドを送信 """
    ser.write((command + '\r').encode())
    time.sleep(0.01)  # 応答を待つための短い遅延
    response = ser.read(ser.in_waiting).decode()
    return response

# シリンジポンプにコマンドを送信して応答を表示
response = send_command('VER')  # 'VER'はバージョン情報を取得するコマンドの例
print('Response:', response)

# シリアルポートを閉じる
ser.close()
