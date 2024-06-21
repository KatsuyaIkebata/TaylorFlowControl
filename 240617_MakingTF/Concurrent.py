import serial
import time
import csv
from datetime import datetime
import threading

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

# CSVファイルの設定
csv_filename = 'pump_operation_log.csv'
csv_header = ['Timestamp', 'Pump', 'Action']

def send_command(ser, command):
    """シリンジポンプにコマンドを送信し、応答を受け取る"""
    command += '\r\n'
    ser.write(command.encode())
    time.sleep(0.05)  # コマンド送信後の待機時間を短縮
    response = ser.read(ser.in_waiting or 1).decode().strip()
    return response

def log_to_csv(pump, action):
    """CSVファイルにログを記録する"""
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        timestamp = datetime.now().isoformat()
        writer.writerow([timestamp, pump, action])

def pump_operation(pump_number, ser):
    """シリンジポンプの操作を行う"""
    for i in range(50):
        # ポンプを開始
        response = send_command(ser, 'IRUN')
        log_to_csv(pump_number, 'RUN')
        print(f'Pump {pump_number} Run Response (Iteration {i+1}):', response)
        time.sleep(20 / 3)  # 1 mL流すのにかかる時間 (20秒)

        # ポンプを停止
        response = send_command(ser, 'STOP')
        log_to_csv(pump_number, 'STOP')
        print(f'Pump {pump_number} Stop Response (Iteration {i+1}):', response)
        # time.sleep(1)  # 次のポンプの操作までの待機時間

# CSVファイルにヘッダー行を書き込む
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(csv_header)

# シリンジポンプの設定を送信
response = send_command(ser1, f'DIAMETER {SyringeDiameter}') 
log_to_csv('Pump 1', f'Set Diameter {SyringeDiameter}')
print(f'Pump 1 Response diameter:', response)
response = send_command(ser1, f'IRATE {TotalRate} m/m') 
log_to_csv('Pump 1', f'Set Infuse Rate {TotalRate} mL/min')
print(f'Pump 1 Response infuse rate:', response)

response = send_command(ser2, f'DIAMETER {SyringeDiameter}') 
log_to_csv('Pump 2', f'Set Diameter {SyringeDiameter}')
print(f'Pump 2 Response diameter:', response)
response = send_command(ser2, f'IRATE {TotalRate} m/m') 
log_to_csv('Pump 2', f'Set Infuse Rate {TotalRate} mL/min')
print(f'Pump 2 Response infuse rate:', response)

# 並行処理のためのスレッドを作成
thread1 = threading.Thread(target=pump_operation, args=('Pump 1', ser1))
thread2 = threading.Thread(target=pump_operation, args=('Pump 2', ser2))

# スレッドを開始
thread1.start()
thread2.start()

# スレッドの完了を待機
thread1.join()
thread2.join()

# シリアル接続を閉じる
ser1.close()
ser2.close()
print("Serial connections closed.")
