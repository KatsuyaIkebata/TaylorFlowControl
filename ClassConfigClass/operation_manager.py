from pump import PumpClass
from valve import ValveClass
import serial
import csv
import math
import time
import RPi.GPIO as GPIO
from datetime import datetime
import copy
from dataclasses import dataclass, field
from write_csv import CSVClass

class OperationClass:
    @dataclass
    class Config:
        tube_diameter_inch: float = 1/8   # inch チューブの内径
        syringe_diameter: float = 29.2   # mm シリンジポンプの内径
        total_rate: float = 3            # mL/min 合計流量
        total_time: float = 1            # min 合計時間
        alarm_time: float = 0.5          # min アラームが鳴る時間
        slug_length0: float = 30         # スラグ0の長さ(実際は少しずれる)
        slug_length1: float = 50         # mm スラグ1の長さ(実際は少しずれる)
        response_time: float = 0.1       # s 応答を待つ時間
        pump_num: int = 2,               # ポンプの数
        valve_num: int = 4,              # バルブの数
        gpio_pin: list = [6, 13, 19, 26], # BCM番号でGPIOピンを指定       
        serial_port: list = field(default_factory=list), # シリンジポンプをつないだシリアルポート
        baudrate: int = 115200
    
    class TimingClass:
        def __init__(self, config, delays):
            self.p0A = 0  # 0秒後に実行開始
            self.p0B = self.p0A + config.response_time   # Aの押出開始後、応答時間が過ぎたら実行開始
            self.p0C = self.p0A + config.infuse_time0    # ポンプ0の押出時間後に実行開始
            self.p0D = self.p0C + config.response_time   # ポンプ0の停止後、応答時間が過ぎたら実行開始
            self.p1A = self.p0A + config.infuse_time0    # ポンプ0の停止と同時に実行
            self.p1B = self.p1A + config.response_time   # Bの押出開始後、応答時間が過ぎたら実行開始
            self.p1C = self.p1A + config.infuse_time1    # ポンプ1の押出時間後に実行開始
            self.p1D = self.p1C + config.response_time   # ポンプ1の停止後、応答時間が過ぎたら実行開始
            self.v0A = self.p0A + delays[0][0]    # ポンプ0の押出後、遅れ時間経過した後、バルブ0を開放（電源OFF）
            self.v0C = self.p0C + delays[0][1]    # ポンプ0の停止後、遅れ時間経過した後、バルブ0を開放（電源OFF）
            self.v1A = self.p1A + delays[1][0]    # ポンプ1の停止と同時にバルブ1を稼働（閉鎖）
            self.v1C = self.p1C + delays[1][1]    # ポンプ1の押出と同時にバルブ1を停止（開放）
            self.v2A = self.p0A + delays[2][0]    # ポンプ0の停止後、遅れ時間経過した後、バルブ2を稼働（閉鎖）
            self.v2C = self.p0C + delays[2][1]    # ポンプ0の押出後、遅れ時間経過した後、バルブ2を停止（開放）
            self.v3A = self.p1A + delays[3][0]    # ポンプ1の停止後、遅れ時間経過した後、バルブ3を稼働（閉鎖）
            self.v3C = self.p1C + delays[3][1]    # ポンプ1の押出後、遅れ時間経過した後、バルブ3を停止

    class IterationClass:
        def __init(self):
            # 各プロセスの実行回数の設定
            self.p0A = 0
            self.p0B = 0
            self.p0C = 0
            self.p0D = 0
            self.p1A = 0
            self.p1B = 0
            self.p1C = 0
            self.p1D = 0
            self.v0A = 0
            self.v0C = 0
            self.v1A = 0
            self.v1C = 0
            self.v2A = 0
            self.v2C = 0
            self.v3A = 0
            self.v3C = 0
    

    def __init__(self, config: Config):
        self.config = config
        self.Pump = [PumpClass(i) for i in range(self.config.pump_num)]
        self.Valve = [ValveClass(i, self.config.gpio_pin[i]) for i in range(self.config.valve_num)]
        '''
        バルブ命令の遅れ時間 delaysを設定
        [0][0]:バルブ0の開放(電源OFF)
        [3][1]:バルブ3の閉鎖(電源ON)
        '''
        self.delays = [[0.0 for _ in range(2)] for _ in range(self.config.valve_num)]
        self.status = False            # 運転を継続するか判断するための変数。Trueであれば運転、Falseであれば停止

        self.calculations()
        self.Timing = self.TimingClass(self.config, self.delays)
        self.Iteration = self.IterationClass()
        
        GPIO.setmode(GPIO.BCM)  # BCM番号でGPIOピンを指定
        GPIO.setup(self.config.gpio_pin, GPIO.OUT)  # GPIOピンを出力モードに設定

        for i in range(len(self.config.serial_port)):
            self.Pump[i].ser = serial.Serial(port=self.config.serial_port[i], baudrate=self.config.baudrate, timeout=1)
    
    def calculations(self):
        self.config.TubeDiameter = 25.4 * self.config.tube_diameter_inch                               # inchからmmへ
        self.config.Volume0 = self.config.slug_length0 * self.config.TubeDiameter* self.config.TubeDiameter * math.pi * 0.25 # mm3 スラグ0の体積
        self.config.infuse_time0 = self.config.Volume0 / self.config.total_rate * 60 * 0.001                       # s ポンプ0を押し出す秒数
        self.config.Volume1 = self.config.slug_length1 * self.config.TubeDiameter * self.config.TubeDiameter * math.pi * 0.25 # mm3 スラグ1の体積
        self.config.infuse_time1 = self.config.Volume1 / self.config.total_rate * 60 * 0.001                       # s ポンプ1を押し出す秒数


    def run(self):   
        # 現在時刻をstart_timeにする
        self.start_time = time.time()
        self.end_time = self.start_time + self.config.total_time * 60
        self.passed_time = 0 

        current_time = datetime.now().strftime("%Y%m%d-%H%M")
        file_name = f'OperationLog-{current_time}.csv'
        self.NewCSV = CSVClass(file_name)

        while time.time() <self.end_time:
            self.passed_time = time.time() - self.start_time 

            if self.passed_time >= self.Timing.p0C and self.Iteration.p0C < self.Iteration.p0A:
                self.Pump[0].stop()   
                self.send_command(ser0, 'STOP')
                log_to_csv('Pump 0', 'Stop')
                print('Pump0 STOP\n')
                self.Iteration.p0C += 1

            if self.passed_time >= self.Timing.p0D and self.Iteration.p0D < self.Iteration.p0A:   
                response = receive_command(ser0)
                log_to_csv('Pump 0', f'Pump 0 Stop Response: {response}')
                self.Iteration.p0D += 1

            if self.passed_time >= self.Timing.p1C and self.Iteration.p1C < self.Iteration.p1A:   
                self.send_command(ser1, 'STOP')
                log_to_csv('Pump 1', 'Stop')
                print('Pump1 STOP\n')
                self.Iteration.p1C += 1

            if self.passed_time >= self.Timing.p1D and self.Iteration.p1D < self.Iteration.p1A:   
                response = receive_command(ser1)
                log_to_csv('Pump 1', f'Pump 1 Stop Response: {response}')
                self.Iteration.p1D += 1

            if self.passed_time >= self.Timing.p0A and self.Iteration.p0A == self.Iteration.p0C:
                self.Timing.p0B = self.Timing.p0A + ResponseTime   # Aの押出開始後、応答時間が過ぎたら実行開始
                self.Timing.p0C = self.Timing.p0A + InfuseTime0    # ポンプ0の押出時間後に実行開始
                self.Timing.p0D = self.Timing.p0C + ResponseTime   # ポンプ0の停止後、応答時間が過ぎたら実行開始
                self.Timing.v0A = self.Timing.p0A + g.delays[0][0] # ポンプ0の押出開始後、遅れ時間経過したらバルブ0を開放（電源OFF）
                self.Timing.v0C = self.Timing.p0C + g.delays[0][1] # ポンプ0の停止後、遅れ時間経過したらバルブ0を閉鎖（電源ON）
                self.Timing.v2A = self.Timing.p0A + g.delays[2][0] # ポンプ0の押出開始後、遅れ時間経過したらバルブ2を開放（電源OFF）
                self.Timing.v2C = self.Timing.p0C + g.delays[2][1] # ポンプ0の停止後、遅れ時間経過したらバルブ2を閉鎖（電源ON）
                self.send_command(ser0, 'IRUN')
                log_to_csv('Pump 0', 'Run')
                print('PUMp0 RUN')
                self.Iteration.p0A += 1
                print(f'Iteration of 1A: {self.Iteration.p0A}')
                self.Timing.p0A = InfuseTime0 * self.Iteration.p0A + InfuseTime1 * self.Iteration.p0A  # プロセス1Aの次の実行時間を設定
                print(f'self.Timing.p0A: {self.Timing.p0A}')

            if self.passed_time >= self.Timing.p0B and self.Iteration.p0B < self.Iteration.p0A:   
                response = receive_command(ser0)
                log_to_csv('Pump 0', f'Pump 0 Run Response: {response}')
                self.Iteration.p0B += 1

            if self.passed_time >= self.Timing.p1A and self.Iteration.p1A == self.Iteration.p1C:
                self.Timing.p1B = self.Timing.p1A + ResponseTime  # Bの押出開始後、応答時間が過ぎたら実行開始
                self.Timing.p1C = self.Timing.p1A + InfuseTime1   # ポンプ1の押出時間後に実行開始
                self.Timing.p1D = self.Timing.p1C + ResponseTime  # ポンプ1の停止後、応答時間が過ぎたら実行開始
                self.Timing.v1A = self.Timing.p1A + g.delays[1][0] # ポンプ1の押出開始後、遅れ時間経過したらバルブ1を開放（電源OFF）
                self.Timing.v1C = self.Timing.p1C + g.delays[1][1] # ポンプ1の停止後、遅れ時間経過したらバルブ1を閉鎖（電源ON）
                self.Timing.v3A = self.Timing.p1A + g.delays[3][0] # ポンプ1の押出開始後、遅れ時間経過したらバルブ3を開放（電源OFF）
                self.Timing.v3C = self.Timing.p1C + g.delays[3][1] # ポンプ1の停止後、遅れ時間経過したらバルブ3を閉鎖（電源ON)
                self.send_command(ser1, 'IRUN')
                log_to_csv('Pump 1', 'Run')
                print('PUMp1 RUN')
                self.Iteration.p1A += 1
                print(f'Iteration of 2A: {self.Iteration.p1A}')
                self.Timing.p1A = InfuseTime0 * (self.Iteration.p0A + 1) + InfuseTime1 * self.Iteration.p1A  # プロセス1Aの次の実行時間を設定
                print(f'self.Timing.p1A: {self.Timing.p1A}')

            if self.passed_time >= self.Timing.p1B and self.Iteration.p1B < self.Iteration.p1A:   
                response = receive_command(ser1)
                log_to_csv('Pump 1', f'Pump 1 Run Response: {response}')
                self.Iteration.p1B += 1
            
            if self.passed_time >= self.Timing.v0A and self.Iteration.v0A == self.Iteration.v0C:
                self.Timing.v0A = self.Timing.p0A + g.delays[0][0]
                GPIO.output(pin0, GPIO.LOW)
                log_to_csv('Valve 0', 'Open')
                self.Iteration.v0A += 1

            if self.passed_time >= self.Timing.v0C and self.Iteration.v0C < self.Iteration.v0A:
                self.Timing.v0C = self.Timing.p0C + g.delays[0][1]
                GPIO.output(pin0, GPIO.HIGH)
                log_to_csv('Valve 0', 'Close')
                self.Iteration.v0C += 1

            if self.passed_time >= self.Timing.v1A and self.Iteration.v1A == self.Iteration.v1C:
                self.Timing.v1A = self.Timing.p1A + g.delays[1][0]
                GPIO.output(pin1, GPIO.LOW)
                log_to_csv('Valve 1', 'Open')
                self.Iteration.v1A += 1

            if self.passed_time >= self.Timing.v1C and self.Iteration.v1C < self.Iteration.v1A:
                self.Timing.v1C = self.Timing.p1C + g.delays[1][1]
                GPIO.output(pin1, GPIO.HIGH)
                log_to_csv('Valve 1', 'Close')
                self.Iteration.v1C += 1
            
            if self.passed_time >= self.Timing.v2A and self.Iteration.v2A == self.Iteration.v2C:
                self.Timing.v2A = self.Timing.p0A + g.delays[2][0]
                GPIO.output(pin2, GPIO.LOW)
                log_to_csv('Valve 2', 'Open')
                self.Iteration.v2A += 1

            if self.passed_time >= self.Timing.v2C and self.Iteration.v2C < self.Iteration.v2A:
                self.Timing.v2C = self.Timing.p0C + g.delays[2][1]
                GPIO.output(pin2, GPIO.HIGH)
                log_to_csv('Valve 2', 'Close')
                self.Iteration.v2C += 1
                    
            if self.passed_time >= self.Timing.v3A and self.Iteration.v3A == self.Iteration.v3C:
                self.Timing.v3A = self.Timing.p1A + g.delays[3][0]
                GPIO.output(pin3, GPIO.LOW)
                log_to_csv('Valve 3', 'Open')
                self.Iteration.v3A += 1

            if self.passed_time >= self.Timing.v3C and self.Iteration.v3C < self.Iteration.v3A:
                self.Timing.v3C = self.Timing.p1C + g.delays[3][1]
                GPIO.output(pin3, GPIO.HIGH)
                log_to_csv('Valve 3', 'Close')
                self.Iteration.v3C += 1
        
        time.sleep(0.01)  # 0.01秒おきに実行

    def stop(self):
        # 停止時の挙動  
        self.Pump.stop(self)
        self.Valve.open(self)  

    def end(self):
        # 終了時の挙動
        for i in range(self.config.pump_num):
            self.Pump[i].end(self)
        for i in range(self.config.valve_num):
            self.Valve[i].end(self)
