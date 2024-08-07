import serial
import csv
import math
import time
import RPi.GPIO as GPIO
from datetime import datetime
import tkinter as tk
import global_value as g

def operation(parent):
    # Settings
    TubeDiameterInch = 1/8   # inch チューブの内径
    SyringeDiameter = 29.2   # mm シリンジポンプの内径
    TotalRate = 3            # mL/min 合計流量
    TotalTime = 0.5            # min 合計時間
    AlarmTime = 0.5          # min アラームが鳴る時間
    SlugLength0 = 30          # mm スラグ0の長さ(実際は少しずれる)
    SlugLength1 = 50         # mm スラグ1の長さ(実際は少しずれる)
    ResponseTime = 0.1       # s 応答を待つ時間

    # GPIOの設定
    GPIO.setmode(GPIO.BCM)  # BCM番号でGPIOピンを指定
    # GPIO.setwarnings(False)

    # 使用するGPIOピンの設定
    pin0, pin1, pin2, pin3 = 6, 13, 19, 26 # 使用するGPIOピン番号を指定
    GPIO.setup(pin0, GPIO.OUT)  # GPIOピンを出力モードに設定
    GPIO.setup(pin1, GPIO.OUT)  # GPIOピンを出力モードに設定
    GPIO.setup(pin2, GPIO.OUT)  # GPIOピンを出力モードに設定
    GPIO.setup(pin3, GPIO.OUT)  # GPIOピンを出力モードに設定

    # Calculations
    TubeDiameter = 25.4 * TubeDiameterInch                               # inchからmmへ
    Volume0 = SlugLength0 * TubeDiameter * TubeDiameter * math.pi * 0.25 # mm3 スラグ0の体積
    InfuseTime0 = Volume0 / TotalRate * 60 * 0.001                       # s ポンプ0を押し出す秒数
    Volume1 = SlugLength1 * TubeDiameter * TubeDiameter * math.pi * 0.25 # mm3 スラグ1の体積
    InfuseTime1 = Volume1 / TotalRate * 60 * 0.001                       # s ポンプ1を押し出す秒数

    # CSVファイルの設定
    current_time = datetime.now().strftime("%Y%m%d-%H%M")
    csv_filename = f'OperationLog-{current_time}.csv'
    csv_header = ['Hour', 'Minute', 'Second','millisecond', 'Pump', 'Action']

    # シリアルポートの設定
    ser0 = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=1)
    ser1 = serial.Serial(port='/dev/ttyACM1', baudrate=115200, timeout=1)

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


    """メインの操作プログラム"""
    # プログラムの開始のマークと、ポンプ押出時間の出力
    print(f'infuse time 0 = {InfuseTime0} s')
    print(f'infuse time 1 = {InfuseTime1} s')

    # CSVファイルにヘッダーを書き込む
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)

    # ポンプの設定(time.sleepが含まれているので注意)
    pump_setting(ser0, 'Pump 0')
    pump_setting(ser1, 'Pump 0')

    # 現在時刻をStartTimeにする
    StartTime = time.time()
    EndTime = StartTime + TotalTime * 60
    PassedTime = 0 

    # 初期条件タイミング
    next_p0A_time = 0  # 0秒後に実行開始
    next_p0B_time = next_p0A_time + ResponseTime   # Aの押出開始後、応答時間が過ぎたら実行開始
    next_p0C_time = next_p0A_time + InfuseTime0    # ポンプ0の押出時間後に実行開始
    next_p0D_time = next_p0C_time + ResponseTime   # ポンプ0の停止後、応答時間が過ぎたら実行開始
    next_p1A_time = next_p0A_time + InfuseTime0    # ポンプ0の停止と同時に実行
    next_p1B_time = next_p1A_time + ResponseTime   # Bの押出開始後、応答時間が過ぎたら実行開始
    next_p1C_time = next_p1A_time + InfuseTime1    # ポンプ1の押出時間後に実行開始
    next_p1D_time = next_p1C_time + ResponseTime   # ポンプ1の停止後、応答時間が過ぎたら実行開始
    next_v0A_time = next_p0A_time + g.delays[0][0] # ポンプ0の押出後、遅れ時間経過した後、バルブ0を開放（電源OFF）
    next_v0C_time = next_p0C_time + g.delays[0][1] # ポンプ0の停止後、遅れ時間経過した後、バルブ0を開放（電源OFF）
    next_v1A_time = next_p1A_time + g.delays[1][0] # ポンプ1の停止と同時にバルブ1を稼働（閉鎖）
    next_v1C_time = next_p1C_time + g.delays[1][1] # ポンプ1の押出と同時にバルブ1を停止（開放）
    next_v2A_time = next_p0A_time + g.delays[2][0] # ポンプ0の停止後、遅れ時間経過した後、バルブ2を稼働（閉鎖）
    next_v2C_time = next_p0C_time + g.delays[2][1] # ポンプ0の押出後、遅れ時間経過した後、バルブ2を停止（開放）
    next_v3A_time = next_p1A_time + g.delays[3][0] # ポンプ1の停止後、遅れ時間経過した後、バルブ3を稼働（閉鎖）
    next_v3C_time = next_p1C_time + g.delays[3][1] # ポンプ1の押出後、遅れ時間経過した後、バルブ3を停止（開放）

    # 各プロセスの実行回数の設定
    iteration_p0A = 0
    iteration_p0B = 0
    iteration_p0C = 0
    iteration_p0D = 0
    iteration_p1A = 0
    iteration_p1B = 0
    iteration_p1C = 0
    iteration_p1D = 0
    iteration_v0A = 0
    iteration_v0C = 0
    iteration_v1A = 0
    iteration_v1C = 0
    iteration_v2A = 0
    iteration_v2C = 0
    iteration_v3A = 0
    iteration_v3C = 0

    while time.time() < EndTime:
        PassedTime = time.time() - StartTime 

        if PassedTime >= next_p0C_time and iteration_p0C < iteration_p0A:   
            send_command(ser0, 'STOP')
            log_to_csv('Pump 0', 'Stop')
            print('Pump0 STOP\n')
            iteration_p0C += 1

        if PassedTime >= next_p0D_time and iteration_p0D < iteration_p0A:   
            response = receive_command(ser0)
            log_to_csv('Pump 0', f'Pump 0 Stop Response: {response}')
            iteration_p0D += 1

        if PassedTime >= next_p1C_time and iteration_p1C < iteration_p1A:   
            send_command(ser1, 'STOP')
            log_to_csv('Pump 1', 'Stop')
            print('Pump1 STOP\n')
            iteration_p1C += 1

        if PassedTime >= next_p1D_time and iteration_p1D < iteration_p1A:   
            response = receive_command(ser1)
            log_to_csv('Pump 1', f'Pump 1 Stop Response: {response}')
            iteration_p1D += 1

        if PassedTime >= next_p0A_time and iteration_p0A == iteration_p0C:
            next_p0B_time = next_p0A_time + ResponseTime   # Aの押出開始後、応答時間が過ぎたら実行開始
            next_p0C_time = next_p0A_time + InfuseTime0    # ポンプ0の押出時間後に実行開始
            next_p0D_time = next_p0C_time + ResponseTime   # ポンプ0の停止後、応答時間が過ぎたら実行開始
            next_v0A_time = next_p0A_time + g.delays[0][0] # ポンプ0の押出開始後、遅れ時間経過したらバルブ0を開放（電源OFF）
            next_v0C_time = next_p0C_time + g.delays[0][1] # ポンプ0の停止後、遅れ時間経過したらバルブ0を閉鎖（電源ON）
            next_v2A_time = next_p0A_time + g.delays[2][0] # ポンプ0の押出開始後、遅れ時間経過したらバルブ2を開放（電源OFF）
            next_v2C_time = next_p0C_time + g.delays[2][1] # ポンプ0の停止後、遅れ時間経過したらバルブ2を閉鎖（電源ON）
            send_command(ser0, 'IRUN')
            log_to_csv('Pump 0', 'Run')
            print('PUMp0 RUN')
            iteration_p0A += 1
            print(f'Iteration of 1A: {iteration_p0A}')
            next_p0A_time = InfuseTime0 * iteration_p0A + InfuseTime1 * iteration_p0A  # プロセス1Aの次の実行時間を設定
            print(f'next_p0A_time: {next_p0A_time}')

        if PassedTime >= next_p0B_time and iteration_p0B < iteration_p0A:   
            response = receive_command(ser0)
            log_to_csv('Pump 0', f'Pump 0 Run Response: {response}')
            iteration_p0B += 1

        if PassedTime >= next_p1A_time and iteration_p1A == iteration_p1C:
            next_p1B_time = next_p1A_time + ResponseTime  # Bの押出開始後、応答時間が過ぎたら実行開始
            next_p1C_time = next_p1A_time + InfuseTime1   # ポンプ1の押出時間後に実行開始
            next_p1D_time = next_p1C_time + ResponseTime  # ポンプ1の停止後、応答時間が過ぎたら実行開始
            next_v1A_time = next_p1A_time + g.delays[1][0] # ポンプ1の押出開始後、遅れ時間経過したらバルブ1を開放（電源OFF）
            next_v1C_time = next_p1C_time + g.delays[1][1] # ポンプ1の停止後、遅れ時間経過したらバルブ1を閉鎖（電源ON）
            next_v3A_time = next_p1A_time + g.delays[3][0] # ポンプ1の押出開始後、遅れ時間経過したらバルブ3を開放（電源OFF）
            next_v3C_time = next_p1C_time + g.delays[3][1] # ポンプ1の停止後、遅れ時間経過したらバルブ3を閉鎖（電源ON)
            send_command(ser1, 'IRUN')
            log_to_csv('Pump 1', 'Run')
            print('PUMp1 RUN')
            iteration_p1A += 1
            print(f'Iteration of 2A: {iteration_p1A}')
            next_p1A_time = InfuseTime0 * (iteration_p0A + 1) + InfuseTime1 * iteration_p1A  # プロセス1Aの次の実行時間を設定
            print(f'next_p1A_time: {next_p1A_time}')

        if PassedTime >= next_p1B_time and iteration_p1B < iteration_p1A:   
            response = receive_command(ser1)
            log_to_csv('Pump 1', f'Pump 1 Run Response: {response}')
            iteration_p1B += 1
        
        if PassedTime >= next_v0A_time and iteration_v0A == iteration_v0C:
            next_v0A_time = next_p0A_time + g.delays[0][0]
            GPIO.output(pin0, GPIO.LOW)
            log_to_csv('Valve 0', 'Open')
            iteration_v0A += 1

        if PassedTime >= next_v0C_time and iteration_v0C < iteration_v0A:
            next_v0C_time = next_p0C_time + g.delays[0][1]
            GPIO.output(pin0, GPIO.HIGH)
            log_to_csv('Valve 0', 'Close')
            iteration_v0C += 1

        if PassedTime >= next_v1A_time and iteration_v1A == iteration_v1C:
            next_v1A_time = next_p1A_time + g.delays[1][0]
            GPIO.output(pin1, GPIO.LOW)
            log_to_csv('Valve 1', 'Open')
            iteration_v1A += 1

        if PassedTime >= next_v1C_time and iteration_v1C < iteration_v1A:
            next_v1C_time = next_p1C_time + g.delays[1][1]
            GPIO.output(pin1, GPIO.HIGH)
            log_to_csv('Valve 1', 'Close')
            iteration_v1C += 1
        
        if PassedTime >= next_v2A_time and iteration_v2A == iteration_v2C:
            next_v2A_time = next_p0A_time + g.delays[2][0]
            GPIO.output(pin2, GPIO.LOW)
            log_to_csv('Valve 2', 'Open')
            iteration_v2A += 1

        if PassedTime >= next_v2C_time and iteration_v2C < iteration_v2A:
            next_v2C_time = next_p0C_time + g.delays[2][1]
            GPIO.output(pin2, GPIO.HIGH)
            log_to_csv('Valve 2', 'Close')
            iteration_v2C += 1
                
        if PassedTime >= next_v3A_time and iteration_v3A == iteration_v3C:
            next_v3A_time = next_p1A_time + g.delays[3][0]
            GPIO.output(pin3, GPIO.LOW)
            log_to_csv('Valve 3', 'Open')
            iteration_v3A += 1

        if PassedTime >= next_v3C_time and iteration_v3C < iteration_v3A:
            next_v3C_time = next_p1C_time + g.delays[3][1]
            GPIO.output(pin3, GPIO.HIGH)
            log_to_csv('Valve 3', 'Close')
            iteration_v3C += 1
        

        time.sleep(0.01)  # 0.01秒おきに実行

    send_command(ser0, 'STOP')
    log_to_csv('Pump 0', 'Stop')
    send_command(ser1, 'STOP')
    log_to_csv('Pump 1', 'Stop')   
    close_serial(ser0)
    close_serial(ser1)
    GPIO.cleanup()
    
    # 終了メッセージ表示
    end_label = tk.Label(parent, text="Operation Finished", font=("Helvetica", 16), fg="red")
    end_label.grid(row=len(g.delays)*2+1, column=0, columnspan=4, pady=10)
    print("Serial connections closed.")
