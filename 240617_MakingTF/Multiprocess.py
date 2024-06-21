import serial
import time
import csv
from datetime import datetime
from multiprocessing import Process, Queue, current_process

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

def log_to_csv(log_queue):
    """CSVファイルにログを記録する"""
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)
        while True:
            log_entry = log_queue.get()
            if log_entry == 'STOP':
                break
            writer.writerow(log_entry)

def pump_operation(pump_number, port, log_queue):
    """シリンジポンプの操作を行う"""
    ser = serial.Serial(
        port=port,
        baudrate=115200,
        timeout=1
    )

    response = send_command(ser, f'DIAMETER {SyringeDiameter}')
    log_queue.put([datetime.now().isoformat(), pump_number, f'Set Diameter {SyringeDiameter}'])
    print(f'{pump_number} Response diameter:', response)
    response = send_command(ser, f'IRATE {TotalRate} m/m')
    log_queue.put([datetime.now().isoformat(), pump_number, f'Set Infuse Rate {TotalRate} mL/min'])
    print(f'{pump_number} Response infuse rate:', response)

    for i in range(10):
        # ポンプを開始
        response = send_command(ser, 'IRUN')
        log_queue.put([datetime.now().isoformat(), pump_number, 'RUN'])
        print(f'{pump_number} Run Response (Iteration {i+1}):', response)
        time.sleep(1)  # 1 mL流すのにかかる時間 (20秒)

        # ポンプを停止
        response = send_command(ser, 'STOP')
        log_queue.put([datetime.now().isoformat(), pump_number, 'STOP'])
        print(f'{pump_number} Stop Response (Iteration {i+1}):', response)
        # time.sleep(1)  # 次のポンプの操作までの待機時間

    ser.close()

if __name__ == '__main__':
    log_queue = Queue()

    # ログプロセスの開始
    log_process = Process(target=log_to_csv, args=(log_queue,))
    log_process.start()

    # シリンジポンプの操作プロセスの開始
    pump1_process = Process(target=pump_operation, args=('Pump 1', 'COM6', log_queue))
    pump2_process = Process(target=pump_operation, args=('Pump 2', 'COM7', log_queue))

    pump1_process.start()
    pump2_process.start()

    pump1_process.join()
    pump2_process.join()

    # ログプロセスの終了
    log_queue.put('STOP')
    log_process.join()

    print("All processes finished.")
