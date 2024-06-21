import serial
import time
import csv
from datetime import datetime


# Settings
TubeDiameterInch = 1/8   # inch チューブの内径
SyringeDiameter = 29.2   # mm シリンジポンプの内径
TotalRate = 3            # mL/min 合計流量
TotalTime = 30           # min 合計時間
AlarmTime = 5            # min アラームが鳴る時間
SlugLength1 = 3          # mm スラグ1の長さ
SlugLength2 = 5          # mm スラグ2の長さ


# Calculations
TubeDiameter = 25.4 * TubeDiameterInch # inchからmmへ


# シリアルポートの設定
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
    time.sleep(0.1)
    response = ser.read(ser.in_waiting or 1).decode().strip()
    return response

print('infuse rate: ' + str(TotalRate))

"""シリンジポンプに設定を送信"""
response = send_command(ser1, f'DIAMETER {SyringeDiameter}') 
print(f'Pump 1 Response diameter:', response)
response = send_command(ser1, f'IRATE: {TotalRate} m/m') 
print(f'Pump 1 Response infuse rate:', response)

response = send_command(ser2, f'DIAMETER {SyringeDiameter}') 
print(f'Pump 2 Response diameter:', response)
response = send_command(ser2, f'IRATE: {TotalRate} m/m') 
print(f'Pump 2 Response infuse rate:', response)


# 各ポンプが合計で50 mL流すまで交互に1 mLずつ流す
for i in range(10):
    # シリンジポンプ1で1 mL流す
    response = send_command(ser1, 'IRUN')  # ポンプを開始
    print(f'Pump 1 Run Response (Iteration {i+1}):', response)
    time.sleep(1)  # 1 mL流すのにかかる時間を適宜調整

    response = send_command(ser1, 'STOP')  # ポンプを停止
    print(f'Pump 1 Stop Response (Iteration {i+1}):', response)

    # シリンジポンプ2で1 mL流す
    response = send_command(ser2, 'IRUN')  # ポンプを開始
    print(f'Pump 2 Run Response (Iteration {i+1}):', response)
    time.sleep(1)  # 1 mL流すのにかかる時間を適宜調整

    response = send_command(ser2, 'STOP')  # ポンプを停止
    print(f'Pump 2 Stop Response (Iteration {i+1}):', response)


# シリアル接続を閉じる
ser1.close()
ser2.close()
print("Serial connections closed.")
