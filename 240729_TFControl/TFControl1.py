import threading
from tkinter import Tk, Label, Entry, Button
import serial
import csv
import math
import time
import RPi.GPIO as GPIO
from datetime import datetime

# グローバル変数
valve_delay_1A = 0.0    # バルブ1の開放の遅れ時間
valve_delay_1C = 0.0    # バルブ1の閉鎖の遅れ時間
valve_delay_2A = 0.0    # バルブ2の開放の遅れ時間
valve_delay_2C = 0.0    # バルブ2の閉鎖の遅れ時間
valve_delay_3A = 0.1    # バルブ3の開放の遅れ時間
valve_delay_3C = 0.1    # バルブ3の閉鎖の遅れ時間
valve_delay_4A = 0.1    # バルブ4の開放の遅れ時間
valve_delay_4C = 0.1    # バルブ4の閉鎖の遅れ時間

# Settings
TubeDiameterInch = 1/8   # inch チューブの内径
SyringeDiameter = 29.2   # mm シリンジポンプの内径
TotalRate = 3            # mL/min 合計流量
TotalTime = 1            # min 合計時間
AlarmTime = 0.5          # min アラームが鳴る時間
SlugLength1 = 30          # mm スラグ1の長さ(実際は少しずれる)
SlugLength2 = 50         # mm スラグ2の長さ(実際は少しずれる)
ResponseTime = 0.1       # s 応答を待つ時間

# GPIOの設定
GPIO.setmode(GPIO.BCM)  # BCM番号でGPIOピンを指定
# GPIO.setwarnings(False)

# 使用するGPIOピンの設定
pin1 = 6  # 使用するGPIOピン番号を指定
pin2 = 13  # 使用するGPIOピン番号を指定
pin3 = 19  # 使用するGPIOピン番号を指定
pin4 = 26  # 使用するGPIOピン番号を指定
GPIO.setup(pin1, GPIO.OUT)  # GPIOピンを出力モードに設定
GPIO.setup(pin2, GPIO.OUT)  # GPIOピンを出力モードに設定
GPIO.setup(pin3, GPIO.OUT)  # GPIOピンを出力モードに設定
GPIO.setup(pin4, GPIO.OUT)  # GPIOピンを出力モードに設定

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
ser1 = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=1)
ser2 = serial.Serial(port='/dev/ttyACM1', baudrate=115200, timeout=1)

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

def update_delay_1A():
    """バルブ1の開放開始時間の更新"""
    global valve_delay_1A
    valve_delay_1A = float(delay_entry_1A.get())
    status_label_1A.config(text=f"Switch delay of valve open updated to {valve_delay_1A} seconds")

def update_delay_1C():
    """バルブ1の閉鎖開始時間の更新"""
    global valve_delay_1C
    valve_delay_1C = float(delay_entry_1C.get())
    status_label_1C.config(text=f"Switch delay of valve close updated to {valve_delay_1C} seconds")

def update_delay_2A():
    """バルブ2の開放開始時間の更新"""
    global valve_delay_2A
    valve_delay_2A = float(delay_entry_2A.get())
    status_label_2A.config(text=f"Switch delay of valve open updated to {valve_delay_2A} seconds")

def update_delay_2C():
    """バルブ2の閉鎖開始時間の更新"""
    global valve_delay_2C
    valve_delay_2C = float(delay_entry_2C.get())
    status_label_2C.config(text=f"Switch delay of valve close updated to {valve_delay_2C} seconds")

def update_delay_3A():
    """バルブ3の開放開始時間の更新"""
    global valve_delay_3A
    valve_delay_3A = float(delay_entry_3A.get())
    status_label_3A.config(text=f"Switch delay of valve open updated to {valve_delay_3A} seconds")

def update_delay_3C():
    """バルブ1の閉鎖開始時間の更新"""
    global valve_delay_3C
    valve_delay_3C = float(delay_entry_3C.get())
    status_label_3C.config(text=f"Switch delay of valve close updated to {valve_delay_3C} seconds")

def update_delay_4A():
    """バルブ4の開放開始時間の更新"""
    global valve_delay_4A
    valve_delay_4A = float(delay_entry_4A.get())
    status_label_4A.config(text=f"Switch delay of valve open updated to {valve_delay_4A} seconds")

def update_delay_4C():
    """バルブ4の閉鎖開始時間の更新"""
    global valve_delay_4C
    valve_delay_4C = float(delay_entry_4C.get())
    status_label_4C.config(text=f"Switch delay of valve close updated to {valve_delay_4C} seconds")

def operation():
    """メインの操作プログラム"""
    # プログラムの開始のマークと、ポンプ押出時間の出力
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

    """
    プロセス命名規則: 機器種類名 + 機器番号 + 操作種類
    機器種類 p: ポンプ v: バルブ
    操作種類 A: open B: open記録 C: close D: close記録
    例 v2C: バルブ2をclose(電源ON)
    """

    # 初期条件タイミング
    next_p1A_time = 0  # 0秒後に実行開始
    next_p1B_time = next_p1A_time + ResponseTime   # Aの押出開始後、応答時間が過ぎたら実行開始
    next_p1C_time = next_p1A_time + InfuseTime1    # ポンプ1の押出時間後に実行開始
    next_p1D_time = next_p1C_time + ResponseTime   # ポンプ1の停止後、応答時間が過ぎたら実行開始
    next_p2A_time = next_p1A_time + InfuseTime1    # ポンプ1の停止と同時に実行
    next_p2B_time = next_p2A_time + ResponseTime   # Bの押出開始後、応答時間が過ぎたら実行開始
    next_p2C_time = next_p2A_time + InfuseTime2    # ポンプ2の押出時間後に実行開始
    next_p2D_time = next_p2C_time + ResponseTime   # ポンプ2の停止後、応答時間が過ぎたら実行開始
    next_v1A_time = next_p1A_time + valve_delay_1A # ポンプ1の押出後、遅れ時間経過した後、バルブ1を停止（開放）
    next_v1C_time = next_p1C_time + valve_delay_1C # ポンプ1の停止と同時にバルブ1を稼働（閉鎖）
    next_v2A_time = next_p2A_time + valve_delay_2A # ポンプ2の停止と同時にバルブ2を稼働（閉鎖）
    next_v2C_time = next_p2C_time + valve_delay_2C # ポンプ2の押出と同時にバルブ2を停止（開放）
    next_v3A_time = next_p1A_time + valve_delay_3A # ポンプ1の停止後、遅れ時間経過した後、バルブ3を稼働（閉鎖）
    next_v3C_time = next_p1C_time + valve_delay_3C # ポンプ1の押出後、遅れ時間経過した後、バルブ3を停止（開放）
    next_v4A_time = next_p2A_time + valve_delay_4A # ポンプ2の停止後、遅れ時間経過した後、バルブ4を稼働（閉鎖）
    next_v4C_time = next_p2C_time + valve_delay_4C # ポンプ2の押出後、遅れ時間経過した後、バルブ4を停止（開放）

    # 各プロセスの実行回数の設定
    iteration_p1A = 0
    iteration_p1B = 0
    iteration_p1C = 0
    iteration_p1D = 0
    iteration_p2A = 0
    iteration_p2B = 0
    iteration_p2C = 0
    iteration_p2D = 0
    iteration_v1A = 0
    iteration_v1C = 0
    iteration_v2A = 0
    iteration_v2C = 0
    iteration_v3A = 0
    iteration_v3C = 0
    iteration_v4A = 0
    iteration_v4C = 0

    while time.time() < EndTime:
        PassedTime = time.time() - StartTime 

        if PassedTime >= next_p1C_time and iteration_p1C < iteration_p1A:   
            send_command(ser1, 'STOP')
            log_to_csv('Pump 1', 'Stop')
            print('PUMP1 STOP\n')
            iteration_p1C += 1

        if PassedTime >= next_p1D_time and iteration_p1D < iteration_p1A:   
            response = receive_command(ser1)
            log_to_csv('Pump 1', f'Pump 1 Stop Response: {response}')
            iteration_p1D += 1

        if PassedTime >= next_p2C_time and iteration_p2C < iteration_p2A:   
            send_command(ser2, 'STOP')
            log_to_csv('Pump 2', 'Stop')
            print('PUMP2 STOP\n')
            iteration_p2C += 1

        if PassedTime >= next_p2D_time and iteration_p2D < iteration_p2A:   
            response = receive_command(ser2)
            log_to_csv('Pump 2', f'Pump 2 Stop Response: {response}')
            iteration_p2D += 1

        if PassedTime >= next_p1A_time and iteration_p1A == iteration_p1C:
            next_p1B_time = next_p1A_time + ResponseTime   # Aの押出開始後、応答時間が過ぎたら実行開始
            next_p1C_time = next_p1A_time + InfuseTime1    # ポンプ1の押出時間後に実行開始
            next_p1D_time = next_p1C_time + ResponseTime   # ポンプ1の停止後、応答時間が過ぎたら実行開始
            next_v1A_time = next_p1A_time + valve_delay_1A # ポンプ1の押出開始後、遅れ時間経過したらバルブ1を停止（開放）
            next_v3A_time = next_p1A_time + valve_delay_3A # ポンプ1の押出開始後、遅れ時間経過したらバルブ3を停止（開放）
            send_command(ser1, 'IRUN')
            log_to_csv('Pump 1', 'Run')
            print('PUMP1 RUN')
            iteration_p1A += 1
            print(f'Iteration of 1A: {iteration_p1A}')
            next_p1A_time = InfuseTime1 * iteration_p1A + InfuseTime2 * iteration_p1A  # プロセス1Aの次の実行時間を設定
            print(f'next_p1A_time: {next_p1A_time}')

        if PassedTime >= next_p1B_time and iteration_p1B < iteration_p1A:   
            response = receive_command(ser1)
            log_to_csv('Pump 1', f'Pump 1 Run Response: {response}')
            iteration_p1B += 1

        if PassedTime >= next_p2A_time and iteration_p2A == iteration_p2C:
            next_p2B_time = next_p2A_time + ResponseTime  # Bの押出開始後、応答時間が過ぎたら実行開始
            next_p2C_time = next_p2A_time + InfuseTime2   # ポンプ2の押出時間後に実行開始
            next_p2D_time = next_p2C_time + ResponseTime  # ポンプ2の停止後、応答時間が過ぎたら実行開始
            next_v2A_time = next_p2A_time + valve_delay_2A # ポンプ2の押出開始後、遅れ時間経過したらバルブ2を停止（開放）
            next_v4A_time = next_p2A_time + valve_delay_4A # ポンプ2の押出開始後、遅れ時間経過したらバルブ4を停止（開放）
            send_command(ser1, 'IRUN')
            send_command(ser2, 'IRUN')
            log_to_csv('Pump 2', 'Run')
            print('PUMP2 RUN')
            iteration_p2A += 1
            print(f'Iteration of 2A: {iteration_p2A}')
            next_p2A_time = InfuseTime1 * (iteration_p1A + 1) + InfuseTime2 * iteration_p2A  # プロセス2Aの次の実行時間を設定
            print(f'next_p2A_time: {next_p2A_time}')

        if PassedTime >= next_p2B_time and iteration_p2B < iteration_p2A:   
            response = receive_command(ser2)
            log_to_csv('Pump 2', f'Pump 2 Run Response: {response}')
            iteration_p2B += 1
        
        if PassedTime >= next_v1A_time and iteration_v1A == iteration_v1C:
            next_v1A_time = next_p1A_time + valve_delay_1A
            GPIO.output(pin1, GPIO.LOW)
            log_to_csv('Valve 1', 'Open')
            iteration_v1A += 1

        if PassedTime >= next_v1C_time and iteration_v1C < iteration_v1A:
            next_v1C_time = next_p1C_time + valve_delay_1C
            GPIO.output(pin1, GPIO.HIGH)
            log_to_csv('Valve1', 'Close')
            iteration_v1C += 1

        if PassedTime >= next_v2A_time and iteration_v2A == iteration_v2C:
            next_v2A_time = next_p2A_time + valve_delay_2A
            GPIO.output(pin2, GPIO.LOW)
            log_to_csv('Valve 2', 'Open')
            iteration_v2A += 1

        if PassedTime >= next_v2C_time and iteration_v2C < iteration_v2A:
            next_v2C_time = next_p2C_time + valve_delay_2C
            GPIO.output(pin2, GPIO.HIGH)
            log_to_csv('Valve2', 'Close')
            iteration_v2C += 1
        
        if PassedTime >= next_v3A_time and iteration_v3A == iteration_v3C:
            next_v3A_time = next_p1A_time + valve_delay_3A
            GPIO.output(pin3, GPIO.LOW)
            log_to_csv('Valve 3', 'Open')
            iteration_v3A += 1

        if PassedTime >= next_v3C_time and iteration_v3C < iteration_v3A:
            next_v3C_time = next_p1C_time + valve_delay_3C
            GPIO.output(pin3, GPIO.HIGH)
            log_to_csv('Valve3', 'Close')
            iteration_v3C += 1
                
        if PassedTime >= next_v4A_time and iteration_v4A == iteration_v4C:
            next_v4A_time = next_p2A_time + valve_delay_4A
            GPIO.output(pin4, GPIO.LOW)
            log_to_csv('Valve 4', 'Open')
            iteration_v4A += 1

        if PassedTime >= next_v4C_time and iteration_v4C < iteration_v4A:
            next_v4C_time = next_p2C_time + valve_delay_4C
            GPIO.output(pin4, GPIO.HIGH)
            log_to_csv('Valve4', 'Close')
            iteration_v4C += 1
        

        time.sleep(0.01)  # 0.01秒おきに実行

    send_command(ser1, 'STOP')
    log_to_csv('Pump 1', 'Stop')
    send_command(ser2, 'STOP')
    log_to_csv('Pump 2', 'Stop')   
    close_serial(ser1)
    close_serial(ser2)
    print("Serial connections closed.")

# GUIセットアップ
root = Tk()
root.title("Valve Delay Controller")

# GUIの中身
Label(root, text="Valve 1 open delay (from pump 1 infuse):").pack()
delay_entry_1A = Entry(root)
delay_entry_1A.pack()

update_button_1A = Button(root, text="Update valve 1 open delay", command=update_delay_1A)
update_button_1A.pack()

status_label_1A = Label(root, text=f"Current valve 1 open delay: {valve_delay_1A} seconds")
status_label_1A.pack()

Label(root, text="Valve 1 close delay (from pump 1 stop):").pack()
delay_entry_1C = Entry(root)
delay_entry_1C.pack()

update_button_1C = Button(root, text="Update valve 1 close delay", command=update_delay_1C)
update_button_1C.pack()

status_label_1C = Label(root, text=f"Current valve 1 close delay: {valve_delay_1C} seconds")
status_label_1C.pack()


Label(root, text="Valve 2 open delay (from pump 2 infuse):").pack()
delay_entry_2A = Entry(root)
delay_entry_2A.pack()

update_button_2A = Button(root, text="Update valve 2 open delay", command=update_delay_2A)
update_button_2A.pack()

status_label_2A = Label(root, text=f"Current valve 2 open delay: {valve_delay_2A} seconds")
status_label_2A.pack()

Label(root, text="Valve 2 close delay (from pump 2 stop):").pack()
delay_entry_2C = Entry(root)
delay_entry_2C.pack()

update_button_2C = Button(root, text="Update valve 2 close delay", command=update_delay_2C)
update_button_2C.pack()

status_label_2C = Label(root, text=f"Current valve 2 close delay: {valve_delay_2C} seconds")
status_label_2C.pack()


Label(root, text="Valve 3 open delay (from pump 1 infuse):").pack()
delay_entry_3A = Entry(root)
delay_entry_3A.pack()

update_button_3A = Button(root, text="Update valve 3 open delay", command=update_delay_3A)
update_button_3A.pack()

status_label_3A = Label(root, text=f"Current valve 3 open delay: {valve_delay_3A} seconds")
status_label_3A.pack()

Label(root, text="Valve 3 close delay (from pump 1 stop):").pack()
delay_entry_3C = Entry(root)
delay_entry_3C.pack()

update_button_3C = Button(root, text="Update valve 3 close delay", command=update_delay_3C)
update_button_3C.pack()

status_label_3C = Label(root, text=f"Current valve 3 close delay: {valve_delay_3C} seconds")
status_label_3C.pack()


Label(root, text="Valve 4 open delay (from pump 2 infuse):").pack()
delay_entry_4A = Entry(root)
delay_entry_4A.pack()

update_button_4A = Button(root, text="Update valve 4 open delay", command=update_delay_4A)
update_button_4A.pack()

status_label_4A = Label(root, text=f"Current valve 4 open delay: {valve_delay_4A} seconds")
status_label_4A.pack()

Label(root, text="Valve 4 close delay (from pump 2 stop):").pack()
delay_entry_4C = Entry(root)
delay_entry_4C.pack()

update_button_4C = Button(root, text="Update valve 4 close delay", command=update_delay_4C)
update_button_4C.pack()

status_label_4C = Label(root, text=f"Current valve 4 close delay: {valve_delay_4C} seconds")
status_label_4C.pack()


# シリンジポンプ操作スレッドの開始
operation_thread = threading.Thread(target=operation)
operation_thread.start()


# GUIループの開始
root.mainloop()

# 終了
operation_thread.join()
GPIO.cleanup()

print("All threads have exited.")
