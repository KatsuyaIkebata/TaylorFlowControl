from pump import Pump
from valve import Valve
import serial
import csv
import math
import time
import RPi.GPIO as GPIO
from datetime import datetime
import copy

class Operation:
    def __init__(self, config):
        self.config = config
        self.valve_num  = valve_num
        self.gpio_pin = copy.deepcopy(gpio_pin)
        self.serial_port = copy.deepcopy(serial_port)
        self.baudrate = baudrate

        self.pumps = [Pump(i) for i in range(self.pump_num)]
        self.valves = [Valve(i) for i in range(self.valve_num)]
        self.tube_diameter_inch = 1/8   # inch チューブの内径
        self.syringe_diameter = 29.2   # mm シリンジポンプの内径
        self.total_rate = 3            # mL/min 合計流量
        self.total_time = 1            # min 合計時間
        self.alarm_time = 0.5          # min アラームが鳴る時間
        self.slug_length0 = 30         # スラグ0の長さ(実際は少しずれる)
        self.slug_length1 = 50         # mm スラグ1の長さ(実際は少しずれる)
        self.response_time = 0.1       # s 応答を待つ時間
        '''
        バルブ命令の遅れ時間 delaysを設定
        [0][0]:バルブ0の開放(電源OFF)
        [3][1]:バルブ3の閉鎖(電源ON)
        '''
        self.delays = [[0.0 for _ in range(2)] for _ in range(self.valve_num)]
        self.status = False            # 運転を継続するか判断するための変数。Trueであれば運転、Falseであれば停止

        self.calculations(self.tube_diameter_inch, self.slug_length0, self.slug_length1, self.total_rate)
        self.initialTiming(self.response_time, self.infuse_time0, self.infuse_time1, self.delays)
        

        GPIO.setmode(GPIO.BCM)  # BCM番号でGPIOピンを指定
        GPIO.setup(self.gpio_pin, GPIO.OUT)  # GPIOピンを出力モードに設定
        self.ser = [None for _ in self.serial_port]
        for i in range(len(self.serial_port)):
            self.ser[i] = serial.Serial(port=self.serial_port[i], baudrate=self.baudrate, timeout=1)

    def calculations(self, tube_diameter_inch, slug_length0, slug_length1, total_rate):
        self.TubeDiameter = 25.4 * self.tube_diameter_inch                               # inchからmmへ
        self.Volume0 = slug_length0 * self.TubeDiameter * self.TubeDiameter * math.pi * 0.25 # mm3 スラグ0の体積
        self.infuse_time0 = self.Volume0 / self.total_rate * 60 * 0.001                       # s ポンプ0を押し出す秒数
        self.Volume1 = slug_length1 * self.TubeDiameter * self.TubeDiameter * math.pi * 0.25 # mm3 スラグ1の体積
        self.infuse_time1 = self.Volume1 / self.total_rate * 60 * 0.001                       # s ポンプ1を押し出す秒数

    def initialTiming(self, response_time, infuse_time0, infuse_time1, delays):
        # 初期条件タイミング
        self.next_p0A_time = 0  # 0秒後に実行開始
        self.next_p0B_time = self.next_p0A_time + self.response_time   # Aの押出開始後、応答時間が過ぎたら実行開始
        self.next_p0C_time = self.next_p0A_time + self.infuse_time0   # ポンプ0の押出時間後に実行開始
        self.next_p0D_time = self.next_p0C_time + self.response_time   # ポンプ0の停止後、応答時間が過ぎたら実行開始
        self.next_p1A_time = self.next_p0A_time + self.infuse_time0    # ポンプ0の停止と同時に実行
        self.next_p1B_time = self.next_p1A_time + self.response_time   # Bの押出開始後、応答時間が過ぎたら実行開始
        self.next_p1C_time = self.next_p1A_time + self.infuse_time1    # ポンプ1の押出時間後に実行開始
        self.next_p1D_time = self.next_p1C_time + self.response_time   # ポンプ1の停止後、応答時間が過ぎたら実行開始
        self.next_v0A_time = self.next_p0A_time + self.delays[0][0] # ポンプ0の押出後、遅れ時間経過した後、バルブ0を開放（電源OFF）
        self.next_v0C_time = self.next_p0C_time + self.delays[0][1] # ポンプ0の停止後、遅れ時間経過した後、バルブ0を開放（電源OFF）
        self.next_v1A_time = self.next_p1A_time + self.delays[1][0] # ポンプ1の停止と同時にバルブ1を稼働（閉鎖）
        self.next_v1C_time = self.next_p1C_time + self.delays[1][1] # ポンプ1の押出と同時にバルブ1を停止（開放）
        self.next_v2A_time = self.next_p0A_time + self.delays[2][0] # ポンプ0の停止後、遅れ時間経過した後、バルブ2を稼働（閉鎖）
        self.next_v2C_time = self.next_p0C_time + self.delays[2][1] # ポンプ0の押出後、遅れ時間経過した後、バルブ2を停止（開放）
        self.next_v3A_time = self.next_p1A_time + self.delays[3][0] # ポンプ1の停止後、遅れ時間経過した後、バルブ3を稼働（閉鎖）
        self.next_v3C_time = self.next_p1C_time + self.delays[3][1] # ポンプ1の押出後、遅れ時間経過した後、バルブ3を停止（開放）
        # 各プロセスの実行回数の設定
        self.iteration_p0A = 0
        self.iteration_p0B = 0
        self.iteration_p0C = 0
        self.iteration_p0D = 0
        self.iteration_p1A = 0
        self.iteration_p1B = 0
        self.iteration_p1C = 0
        self.iteration_p1D = 0
        self.iteration_v0A = 0
        self.iteration_v0C = 0
        self.iteration_v1A = 0
        self.iteration_v1C = 0
        self.iteration_v2A = 0
        self.iteration_v2C = 0
        self.iteration_v3A = 0
        self.iteration_v3C = 0

    def run(self):
        # 実行
        while time.time() < EndTime:
            PassedTime = time.time() - StartTime 

            if PassedTime >= next_p0C_time and iteration_p0C < iteration_p0A:   
                self.send_command(ser0, 'STOP')
                log_to_csv('Pump 0', 'Stop')
                print('Pump0 STOP\n')
                iteration_p0C += 1

            if PassedTime >= next_p0D_time and iteration_p0D < iteration_p0A:   
                response = receive_command(ser0)
                log_to_csv('Pump 0', f'Pump 0 Stop Response: {response}')
                iteration_p0D += 1

            if PassedTime >= next_p1C_time and iteration_p1C < iteration_p1A:   
                self.send_command(ser1, 'STOP')
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
                self.send_command(ser0, 'IRUN')
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
                self.send_command(ser1, 'IRUN')
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

    def stop(self):
        # 停止時の挙動
        
        send_command(ser0, 'STOP')
        log_to_csv('Pump 0', 'Stop')
        send_command(ser1, 'STOP')
        log_to_csv('Pump 1', 'Stop')   

    def end(self):
        # 終了時の挙動
        self.pin(stop)
        send_command(ser0, 'STOP')
        log_to_csv('Pump 0', 'Stop')
        send_command(ser1, 'STOP')
        log_to_csv('Pump 1', 'Stop') 
        close_serial(ser0)
        close_serial(ser1)
        GPIO.cleanup()
