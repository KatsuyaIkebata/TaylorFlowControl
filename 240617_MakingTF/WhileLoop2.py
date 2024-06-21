import serial
import csv
import math
import time
from datetime import datetime

# Settings
TubeDiameterInch = 1/8   # inch チューブの内径
SyringeDiameter = 29.2   # mm シリンジポンプの内径
TotalRate = 3            # mL/min 合計流量
TotalTime = 0.2          # min 合計時間
AlarmTime = 0.5          # min アラームが鳴る時間
SlugLength1 = 2          # mm スラグ1の長さ
SlugLength2 = 10         # mm スラグ2の長さ
ResponseTime = 0.1       # s 応答を待つ時間

# Calculations
TubeDiameter = 25.4 * TubeDiameterInch                               # inchからmmへ
Volume1 = SlugLength1 * TubeDiameter * TubeDiameter * math.pi * 0.25 # mm3 スラグ1の体積
InfuseTime1 = Volume1 / TotalRate * 60 * 0.001                       # s ポンプ1を押し出す秒数
Volume2 = SlugLength2 * TubeDiameter * TubeDiameter * math.pi * 0.25 # mm3 スラグ2の体積
InfuseTime2 = Volume2 / TotalRate * 60 * 0.001                       # s ポンプ2を押し出す秒数

# CSVファイルの設定
current_time = datetime.now().strftime("%Y%m%d-%H%M")
csv_filename = f'OperationLog-{current_time}.csv'
csv_header = ['Hour', 'Minute', 'Second','millisecond', 'Pump', 'Action']

# シリアルポートの設定
ser1 = serial.Serial(port='COM6', baudrate=115200, timeout=1)
ser2 = serial.Serial(port='COM7', baudrate=115200, timeout=1)

def pump_setting(ser, name):
    """シリンジポンプの設定を行う"""
    send_command(ser, f'DIAMETER {SyringeDiameter}')
    time.sleep(0.1)
    response = receive_command(ser)
    log_to_csv(name, f'Set Diameter {SyringeDiameter}, response: {response}') 

    send_command(ser, f'IRATE {TotalRate} m/m')
    time.sleep(0.1)
    response = receive_command(ser)
    log_to_csv(name, f'Set Infuse Rate {TotalRate} mL/min, response: {response}')   

def send_command(ser, command):
    """シリンジポンプにコマンドを送信する"""
    command += '\r\n'
    ser.write(command.encode())

def receive_command(ser):
    """シリンジポンプから応答を受け取る"""
    response = ser.read(ser.in_waiting or 1).decode().strip()
    return response

def close_serial(ser):
    """シリアルポートを閉じる"""
    ser.close()
    
def log_to_csv(device, action):
    """CSVファイルにログを記録する"""
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        now = datetime.now()
        writer.writerow([now.hour, now.minute, now.second, now.microsecond // 1000, device, action])

if __name__ == '__main__':
    print(f'infuse time 1 = {InfuseTime1} s')
    print(f'infuse time 2 = {InfuseTime2} s')

    # CSVファイルにヘッダーを書き込む
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)
   
    # ポンプの設定(time.sleepが含まれているので注意)
    pump_setting(ser1, 'Pump 1')
    pump_setting(ser2, 'Pump 2')

    # 現在時刻をStartTimeにする
    StartTime = time.time()
    EndTime = StartTime + TotalTime * 60
    PassedTime = 0 

    next_1A_time = 0  # 0秒後に実行開始
    next_1B_time = next_1A_time + ResponseTime  # Aの押出開始後、応答時間が過ぎたら実行開始
    next_1C_time = next_1A_time + InfuseTime1   # ポンプ1の押出時間後に実行開始
    next_1D_time = next_1C_time + ResponseTime  # ポンプ1の停止後、応答時間が過ぎたら実行開始
    next_2A_time = next_1A_time + InfuseTime1   # ポンプ1の停止と同時に実行
    next_2B_time = next_2A_time + ResponseTime  # Bの押出開始後、応答時間が過ぎたら実行開始
    next_2C_time = next_2A_time + InfuseTime2   # ポンプ2の押出時間後に実行開始
    next_2D_time = next_2C_time + ResponseTime  # ポンプ2の停止後、応答時間が過ぎたら実行開始


    # 各プロセスの実行回数の設定
    Iteration1A = 0
    Iteration1B = 0
    Iteration1C = 0
    Iteration1D = 0
    Iteration2A = 0
    Iteration2B = 0
    Iteration2C = 0
    Iteration2D = 0  

    while time.time() < EndTime:
        PassedTime = time.time() - StartTime 

        if PassedTime >= next_1C_time and Iteration1C < Iteration1A:   
            send_command(ser1, 'STOP')
            log_to_csv('Pump 1', 'Stop')
            print('PUMP1 STOP\n')
            Iteration1C += 1

        if PassedTime >= next_1D_time and Iteration1D < Iteration1A:   
            response = receive_command(ser1)
            log_to_csv('Pump 1', f'Pump 1 Stop Response: {response}')
            Iteration1D += 1

        if PassedTime >= next_2C_time and Iteration2C < Iteration2A:   
            send_command(ser2, 'STOP')
            log_to_csv('Pump 2', 'Stop')
            print('PUMP2 STOP\n')
            Iteration2C += 1

        if PassedTime >= next_2D_time and Iteration2D < Iteration2A:   
            response = receive_command(ser2)
            log_to_csv('Pump 2', f'Pump 2 Stop Response: {response}')
            Iteration2D += 1

        if PassedTime >= next_1A_time and Iteration1A == Iteration1C:
            next_1B_time = next_1A_time + ResponseTime  # Aの押出開始後、応答時間が過ぎたら実行開始
            next_1C_time = next_1A_time + InfuseTime1   # ポンプ1の押出時間後に実行開始
            next_1D_time = next_1C_time + ResponseTime  # ポンプ1の停止後、応答時間が過ぎたら実行開始
            send_command(ser1, 'IRUN')
            log_to_csv('Pump 1', 'Run')
            print('PUMP1 RUN')
            Iteration1A += 1
            print(f'Iteration of 1A: {Iteration1A}')
            next_1A_time = InfuseTime1 * Iteration1A + InfuseTime2 * Iteration1A  # プロセス1Aの次の実行時間を設定
            print(f'next_1A_time: {next_1A_time}')

        if PassedTime >= next_1B_time and Iteration1B < Iteration1A:   
            response = receive_command(ser1)
            log_to_csv('Pump 1', f'Pump 1 Run Response: {response}')
            Iteration1B += 1

        if PassedTime >= next_1C_time and Iteration1C < Iteration1A:   
            send_command(ser1, 'STOP')
            log_to_csv('Pump 1', 'Stop')
            print('PUMP1 STOP\n')
            Iteration1C += 1

        if PassedTime >= next_1D_time and Iteration1D < Iteration1A:   
            response = receive_command(ser1)
            log_to_csv('Pump 1', f'Pump 1 Stop Response: {response}')
            Iteration1D += 1

        if PassedTime >= next_2A_time and Iteration2A == Iteration2C:
            next_2B_time = next_2A_time + ResponseTime  # Bの押出開始後、応答時間が過ぎたら実行開始
            next_2C_time = next_2A_time + InfuseTime2   # ポンプ2の押出時間後に実行開始
            next_2D_time = next_2C_time + ResponseTime  # ポンプ2の停止後、応答時間が過ぎたら実行開始 send_command(ser2, 'IRUN')
            send_command(ser2, 'IRUN')
            log_to_csv('Pump 2', 'Run')
            print('PUMP2 RUN')
            Iteration2A += 1
            print(f'Iteration of 2A: {Iteration2A}')
            next_2A_time = InfuseTime1 * (Iteration1A + 1) + InfuseTime2 * Iteration2A  # プロセス2Aの次の実行時間を設定
            print(f'next_2A_time: {next_2A_time}')

        if PassedTime >= next_2B_time and Iteration2B < Iteration2A:   
            response = receive_command(ser2)
            log_to_csv('Pump 2', f'Pump 2 Run Response: {response}')
            Iteration2B += 1
        
        time.sleep(0.01)  # 0.01秒おきに実行

    send_command(ser1, 'STOP')
    log_to_csv('Pump 1', 'Stop')
    send_command(ser2, 'STOP')
    log_to_csv('Pump 2', 'Stop')   
    close_serial(ser1)
    close_serial(ser2)
    print("Serial connections closed.")
