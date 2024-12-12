from pump import PumpClass
from valve import ValveClass
import serial
import csv
import math
import time
import RPi.GPIO as GPIO
from datetime import datetime
from write_csv import CSVClass
from write_txt import TxtClass
from controller import TimingClass, IterationClass, RunOpeClass
import yaml
from config import Config
import common_delays as c

class Operation:
    def __init__(self, config_file):
        config_data = self.load_config(config_file)
        self.config = Config(config_data)
        c.delays = self.config.delay
        self.status = False            # 運転を継続するか判断するための変数。Trueであれば運転、Falseであれば停止

        self.Pump = [PumpClass(i) for i in self.config.serial_port]
        for i in self.config.serial_port:
            try:
                self.Pump[i].ser = serial.Serial(port=self.config.serial_port[i], baudrate=self.config.baudrate, timeout=1)
                print(f'pump{self.Pump[i].id}: {self.config.serial_port[i]}, status: {self.Pump[i].ser.is_open}')
            except: 
                try: 
                    print(f'pump{self.Pump[i].id}: {i}, status: false')
                except:
                    print (f'{i} is not detected')
                pass

        GPIO.setmode(GPIO.BCM)  # BCM番号でGPIOピンを指定
        GPIO.setup(self.config.gpio_pin, GPIO.OUT)  # GPIOピンを出力モードに設定
        self.Valve = [ValveClass(i, self.config.gpio_pin[i]) for i in range(self.config.valve_num)]

        self.calculations()
        self.Timing = TimingClass(self.config)
        self.Iteration = IterationClass(self.config)

    def load_config(self, config_file):
        """設定ファイルを読み込む"""
        try:
            with open(config_file, "r") as file:
                config = yaml.safe_load(file)
                return config
        except Exception as e:
            print("Error", f"Failed to load config file: {e}")
            return {}

    def calculations(self):
        self.config.Volume = [vol / 1000 for vol in self.config.slug_volume]
        self.config.infuse_time = [volume / self.config.total_rate * 60 for volume in self.config.Volume]

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
            self.RunOpe = RunOpeClass.operation
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
        
