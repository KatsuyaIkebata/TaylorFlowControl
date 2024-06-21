import serial
import time
import csv
import math
from datetime import datetime
from multiprocessing import Process, Queue, Event

# Settings
TubeDiameterInch = 1/8   # inch チューブの内径
SyringeDiameter = 29.2   # mm シリンジポンプの内径
TotalRate = 3            # mL/min 合計流量
TotalTime = 30           # min 合計時間
AlarmTime = 5            # min アラームが鳴る時間
SlugLength1 = 2        # mm スラグ1の長さ
SlugLength2 = 10        # mm スラグ2の長さ

# Calculations
TubeDiameter = 25.4 * TubeDiameterInch                              # inchからmmへ
Volume1 = SlugLength1 * TubeDiameter * TubeDiameter * math.pi * 0.25 # mm3 スラグ1の体積
InfuseTime1 = Volume1 / TotalRate * 60 * 0.001                        # s ポンプ1を押し出す秒数
Volume2 = SlugLength2 * TubeDiameter * TubeDiameter * math.pi * 0.25 # mm3 スラグ2の体積
InfuseTime2 = Volume2 / TotalRate * 60 * 0.001                        # s ポンプ1を押し出す秒数

print(f'infuse time 1 = {InfuseTime1} s')
print(f'infuse time 2 = {InfuseTime2} s')

# CSVファイルの設定
current_time = datetime.now().strftime("%Y%m%d-%H%M")
csv_filename = f'OperationLog-{current_time}.csv'
csv_header = ['Hour', 'Minute', 'Second', 'Pump', 'Action']

def send_command(ser, command):
    """シリンジポンプにコマンドを送信する"""
    command += '\r\n'
    ser.write(command.encode())

def receive_command(ser):
    """シリンジポンプから応答を受け取る"""
    response = ser.read(ser.in_waiting or 1).decode().strip()
    return response

def log_to_csv(log_queue, stop_event):
    """CSVファイルにログを記録する"""
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)
        while not stop_event.is_set() or not log_queue.empty():
            if not log_queue.empty():
                log_entry = log_queue.get()
                writer.writerow(log_entry)

def pump_setting(pump_number, port):
    ser = serial.Serial(
        port=port,
        baudrate=115200,
        timeout=1
    )

    send_command(ser, f'DIAMETER {SyringeDiameter}')
    log_queue.put([*datetime.now().strftime("%H %M %S.%f").split(), pump_number, f'Set Diameter {SyringeDiameter}'])
    send_command(ser, f'IRATE {TotalRate} m/m')
    log_queue.put([*datetime.now().strftime("%H %M %S.%f").split(), pump_number, f'Set Infuse Rate {TotalRate} mL/min'])    


def pump_operation(pump_number, port, InfuseTime, log_queue, start_event, stop_event, other_pump_event):
    """シリンジポンプの操作を行う"""
    ser = serial.Serial(
        port=port,
        baudrate=115200,
        timeout=1
    )

    for _ in range(10):
        start_event.wait()  # ポンプの開始イベントを待つ
        # ポンプを開始
        send_command(ser, 'IRUN')
        log_queue.put([*datetime.now().strftime("%H %M %S.%f").split(), pump_number, 'RUN'])

        time.sleep(InfuseTime)  # 1 mL流すのにかかる時間 (1秒)

        # ポンプを停止
        send_command(ser, 'STOP')
        log_queue.put([*datetime.now().strftime("%H %M %S.%f").split(), pump_number, 'STOP'])

        start_event.clear()  # 自分のポンプの開始イベントをクリア
        other_pump_event.set()  # 他のポンプの開始イベントをセット

    ser.close()
    stop_event.set()

if __name__ == '__main__':
    log_queue = Queue()      # ログメッセージのキューの作成
    start_event1 = Event()
    stop_event1 = Event()
    start_event2 = Event()
    stop_event2 = Event()

    # ログプロセスの開始
    log_process = Process(target=log_to_csv, args=(log_queue, stop_event1))
    log_process.start()

    # シリンジポンプの設定
    pump_setting('Pump 1', 'COM6')
    pump_setting('Pump 2', 'COM7')

    # シリンジポンプの操作プロセスの開始
    pump1_process = Process(target=pump_operation, args=('Pump 1', 'COM6', InfuseTime1,  log_queue, start_event1, stop_event1, start_event2))
    pump2_process = Process(target=pump_operation, args=('Pump 2', 'COM7', InfuseTime2, log_queue, start_event2, stop_event2, start_event1))

    pump1_process.start()
    pump2_process.start()

    start_event1.set()  # ポンプ1の開始イベントを設定

    pump1_process.join()
    pump2_process.join()

    # ログプロセスの終了
    stop_event1.set()
    log_queue.put('STOP')
    log_process.join()

    print("All processes finished.")
