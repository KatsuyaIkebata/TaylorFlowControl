import serial
import csv
import math
import time
from datetime import datetime, timedelta

# Settings
TubeDiameterInch = 1/8   # inch チューブの内径
SyringeDiameter = 29.2   # mm シリンジポンプの内径
TotalRate = 3            # mL/min 合計流量
TotalTime = 1           # min 合計時間
AlarmTime = 0.5            # min アラームが鳴る時間
SlugLength1 = 2        # mm スラグ1の長さ
SlugLength2 = 10        # mm スラグ2の長さ
ResponseTime = 0.1      # s 応答を待つ時間

# Calculations
TubeDiameter = 25.4 * TubeDiameterInch                               # inchからmmへ
Volume1 = SlugLength1 * TubeDiameter * TubeDiameter * math.pi * 0.25 # mm3 スラグ1の体積
InfuseTime1 = Volume1 / TotalRate * 60 * 0.001                       # s ポンプ1を押し出す秒数
Volume2 = SlugLength2 * TubeDiameter * TubeDiameter * math.pi * 0.25 # mm3 スラグ2の体積
InfuseTime2 = Volume2 / TotalRate * 60 * 0.001                       # s ポンプ1を押し出す秒数

print(f'infuse time 1 = {InfuseTime1} s')
print(f'infuse time 2 = {InfuseTime2} s')

# CSVファイルの設定
current_time = datetime.now().strftime("%Y%m%d-%H%M")
csv_filename = f'OperationLog-{current_time}.csv'
csv_header = ['Hour', 'Minute', 'Second', 'Pump', 'Action']


# シリアルポートの設定
ser1 = serial.Serial(
    port='COM6',
    baudrate=115200,
    timeout=1
    )

ser2 = serial.Serial(
    port='COM7',
    baudrate = 115200,
    timeout = 1
)


def pump_setting(ser):
    """シリンジポンプの設定を行う"""
    send_command(ser, f'DIAMETER {SyringeDiameter}')
    send_command(ser, f'IRATE {TotalRate} m/m')

def send_command(ser, command):
    """シリンジポンプにコマンドを送信する"""
    command += '\r\n'
    ser.write(command.encode())

def receive_command(ser):
    """シリンジポンプから応答を受け取る"""
    response = ser.read(ser.in_waiting or 1).decode().strip()
    return response

def close_serial(port):
    ser = serial.Serial(
        port=port,
        baudrate=115200,
        timeout=1
    )
    ser.close()
    
def log_to_csv(device, action):
    """CSVファイルにログを記録する"""
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        timestamp = datetime.now().isoformat()
        writer.writerow([timestamp, device, action])

if __name__ == '__main__':

    # 現在時刻をStartTimeにする
    StartTime = time.time()
    EndTime = StartTime + TotalTime * 60
    pump_setting(ser1)
    log_to_csv('Pump 1 ', f'Set Diameter {SyringeDiameter}') 
    log_to_csv('Pump 1', f'Set Infuse Rate {TotalRate} mL/min')   
    pump_setting(ser2)
    log_to_csv('Pump 2 ', f'Set Diameter {SyringeDiameter}') 
    log_to_csv('Pump 2', f'Set Infuse Rate {TotalRate} mL/min')   

    next_1A_time = 1 # 1秒後に実行開始
    PassedTime = 0 

# 各プロセスの実行回数の設定
Iteration1A = 0
Iteration1B = 0
Iteration1C = 0
Iteration1D = 0
Iteration2A = 0
Iteration2B = 0
Iteration2C = 0
Iteration2D = 0  

# イベント発火するための閾値
i1A = 1
i1B = 1
i1C = 1
i1D = 1
i2A = 1
i2B = 1
i2C = 1
i2D = 1                                 

while (PassedTime < EndTime):
    PassedTime = time.time() - StartTime

    next_1B_time = next_1A_time + ResponseTime # Aの押出開始後、応答時間が過ぎたら実行開始
    next_1C_time = next_1A_time + InfuseTime1  # ポンプ1の押出時間後に実行開始
    next_1D_time = next_1C_time + ResponseTime # ポンプ1の停止後、応答時間が過ぎたら実行開始
    next_2A_time = next_1C_time                # ポンプ1の停止と同時に実行
    next_2B_time = next_2A_time + InfuseTime2  # Bの押出開始後、応答時間が過ぎたら実行開始
    next_2C_time = next_2A_time + InfuseTime2  # 1 + ポンプ1の押出時間後に実行開始
    next_2D_time = next_2C_time + ResponseTime # ポンプ2の停止後、応答時間が過ぎたら実行開始 

    if PassedTime >= next_1A_time and Iteration1A < i1A:
        '''プロセス1Aの実行_ポンプ1をIRUNする'''
        Iteration1A += 1
        send_command(ser1, 'IRUN')
        log_to_csv('Pump 1 ', 'Run')
        print('PUMP1 RUN')
        next_A_time = StartTime + InfuseTime1 * Iteration1A + InfuseTime2 * Iteration1A  # プロセス1Aの次の実行時間を設定

    if PassedTime >= next_1B_time and Iteration1B < i1A:   
        '''プロセス1Bの実行_ポンプ1から応答を受け取る'''
        Iteration1B += 1
        response = receive_command(ser1)
        log_to_csv('Pump 1 ', f'pump 1 Run Response (iteration {Iteration1A}): response')

    if PassedTime >= next_1C_time and Iteration1C < i1A:   
        '''プロセス1Cの実行_ポンプ1をSTOPする'''
        Iteration1C += 1
        i1A += 1
        send_command(ser1, 'STOP')
        log_to_csv('Pump 1 ', 'Stop')

    if PassedTime >= next_1D_time and Iteration1D < i1A:   
        '''プロセス1Dの実行_ポンプ1から応答を受け取る'''
        Iteration1D += 1
        response = receive_command(ser1)
        log_to_csv('Pump 1 ', f'pump 1 Stop Response (iteration {Iteration1A}): response')

    if PassedTime >= next_2A_time and Iteration2A > i2A:
        '''プロセス1Aの実行_ポンプ2をIRUNする'''
        Iteration2A += 1
        send_command(ser2, 'IRUN')
        log_to_csv('Pump 2 ', 'Run')

    if PassedTime >= next_2B_time:   
        '''プロセス1Bの実行_ポンプ2から応答を受け取る'''
        Iteration2B += 1
        response = receive_command(ser2)
        log_to_csv('Pump 2 ', f'pump 2 Run Response (iteration {Iteration1A}): response')

    if PassedTime >= next_2C_time:   
        '''プロセス1Cの実行_ポンプ2をSTOPする'''
        Iteration2C += 1
        i2A +=1
        send_command(ser2, 'STOP')
        log_to_csv('Pump 2 ', 'Stop')

    if PassedTime >= next_1D_time:   
        '''プロセス2Dの実行_ポンプ2から応答を受け取る'''
        Iteration2D += 1
        response = receive_command(ser2)
        log_to_csv('Pump 2 ', f'pump 2 Stop Response (iteration {Iteration1A}): response')
    
    time.sleep(0.001) # 0.001秒おきに実行

close_serial(ser1)
close_serial(ser2)
print("Serial connections closed.")