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
from write_txt import TxtClass
from operation_4_2 import TimingClass_4_2, IterationClass_4_2, RunOpeClass_4_2

class OperationClass:
    @dataclass
    class Config:
        tube_diameter: float = 1.58      # mm チューブの内径
        syringe_diameter: float = 34.5   # mm シリンジポンプの内径
        total_rate: float = 1            # mL/min 合計流量
        total_time: float = 1            # min 合計時間
        alarm_time: float = 0.5          # min アラームが鳴る時間
        slug_volume0: float = 10         # μL スラグ0の体積
        slug_volume1: float = 10         # μL スラグ1の体積
        response_time: float = 0.1       # s 応答を待つ時間
        pump_num: int = 2,               # ポンプの数
        valve_num: int = 4,              # バルブの数
        gpio_pin: list = [6, 13, 19, 26], # BCM番号でGPIOピンを指定       
        serial_port: list = field(default_factory=list), # シリンジポンプをつないだシリアルポート
        baudrate: int = 115200  

    def __init__(self, config: Config):
        self.config = config
        self.status = False            # 運転を継続するか判断するための変数。Trueであれば運転、Falseであれば停止

        self.Pump = [PumpClass(i) for i in range(self.config.pump_num)]
        for i in range(len(self.config.serial_port)):
            self.Pump[i].ser = serial.Serial(port=self.config.serial_port[i], baudrate=self.config.baudrate, timeout=1)
            print(f'pump{self.Pump[i].id}: {self.config.serial_port[i]}, status: {self.Pump[i].ser.is_open}')

        GPIO.setmode(GPIO.BCM)  # BCM番号でGPIOピンを指定
        GPIO.setup(self.config.gpio_pin, GPIO.OUT)  # GPIOピンを出力モードに設定
        self.Valve = [ValveClass(i, self.config.gpio_pin[i]) for i in range(self.config.valve_num)]

        '''
        バルブ命令の遅れ時間 delaysを設定
        [0][0]:バルブ0の開放(電源OFF)
        [3][1]:バルブ3の閉鎖(電源ON)
        '''
        self.delays = [[0.0 for _ in range(2)] for _ in range(self.config.valve_num)]

        self.calculations()
        if self.config.valve_num == 4 and self.config.pump_num == 2 :
            self.Timing = TimingClass_4_2(self.config, self.delays)
            self.Iteration = IterationClass_4_2()
        else:
            print("他のバルブとポンプ数でのoperationクラスを作成してください")
        # self.Timing = TimingClass_4_2(self.config, self.delays)
        # self.Iteration = IterationClass_4_2()

    def calculations(self):
        self.config.Volume0 = self.config.slug_volume0 * 1000 # mL スラグ0の体積
        self.config.infuse_time0 = self.config.Volume0 / self.config.total_rate * 60 # s ポンプ0を押し出す秒数
        self.config.Volume1 = self.config.slug_volume1 * 1000 # mL スラグ1の体積
        self.config.infuse_time1 = self.config.Volume1 / self.config.total_rate * 60 # s ポンプ1を押し出す秒数

    def logCSV(self, device, action):
        try:
            self.NewCSV.log(device, action)
        except AttributeError:
            print("NewCSV is not defined on Operation.")

    def run(self):   
        # csvファイルを作る
        current_time = datetime.now().strftime("%Y%m%d-%H%M")
        csv_name = f'../data/OperationLog-{current_time}.csv'
        self.NewCSV = CSVClass(csv_name)
        txt_name = f'../data/FinalSetting-{current_time}.txt'
        self.NewTxt = TxtClass(txt_name)

        # シリンジポンプの設定
        for i in range(self.config.pump_num):
            self.Pump[i].setting(self)

        # 現在時刻をstart_timeにする
        self.start_time = time.time()
        self.end_time = self.start_time + self.config.total_time * 60
        self.passed_time = 0 

        if self.config.valve_num == 4 and self.config.pump_num == 2 :
            self.RunOpe = RunOpeClass_4_2.operation_4_2
        else:
            print("他のバルブとポンプ数でのoperationクラスを作成してください")

        while time.time() < self.end_time and self.status == True:
            self.passed_time = time.time() - self.start_time 
            self.RunOpe(self)
            time.sleep(0.01)  # 0.01秒おきに実行
            
        self.stop()
        print("Operation stopped.")

    def stop(self):
        # 停止時の挙動  
        for i in range(self.config.pump_num):
            self.Pump[i].stop(self)
        for i in range(self.config.valve_num):
            self.Valve[i].open(self) 
        self.status = False        
        self.NewTxt.close(self)

    def end(self):
        # 終了時の挙動
        for i in range(self.config.pump_num):
            self.Pump[i].end(self)
        for i in range(self.config.valve_num):
            self.Valve[i].end(self)
        self.status = False
        GPIO.cleanup()
        