import tkinter as tk
import threading as th
from tkinter import ttk
import serial
import csv
import math
import time
# import RPI.GPIO as GPIO
from datetime import datetime
from interface import Interface
from operation_manager import OperationManager
from syringe_pump import SyringePump
from valve import Valve

def main():
    global status, delays
    root = tk.Tk()
    display = Interface(root)
    delays = float(display.delay_entry[i][j])
    if display.startbutton == True and status == False:
        # シリンジポンプ操作スレッドの開始
        new_thread = th.Thread(target=OperationThread)
        new_thread.start()
    elif display.startbutton == False and status == True:
        # シリンジポンプ操作スレッドの停止
        new_thread.join()
    root.mainloop()

def OperationThread():
    global status, delays
    NewOperation = OperationManager(delays)
    status = True

def Settings(NewOpe):
    # Settings
    NewOpe.TubeDiameterInch = 1/8   # inch チューブの内径
    NewOpe.SyringeDiameter = 29.2   # mm シリンジポンプの内径
    NewOpe.TotalRate = 3            # mL/min 合計流量
    NewOpe.TotalTime = 1            # min 合計時間
    NewOpe.AlarmTime = 0.5          # min アラームが鳴る時間
    NewOpe.SlugLength1 = 30          # mm スラグ1の長さ(実際は少しずれる)
    NewOpe.SlugLength2 = 50         # mm スラグ2の長さ(実際は少しずれる)
    NewOpe.ResponseTime = 0.1       # s 応答を待つ時間  
    '''
    ファイル間共通変数 delaysの初期設定
    バルブ命令の遅れ時間を設定
    [0][0]:バルブ0の開放(電源OFF)
    [3][1]: バルブ3の閉鎖(電源ON)
    '''
    NewOpe.delays = [[0.0 for _ in range(2)] for _ in range(4)]


if __name__ == "__main__":
    NewOpe = OperationManager()
    Settings(NewOpe)    

    status = False # 操作停止: False, 操作中: True
    main()
    # GPIO.cleanup()
    print("main program is over.")
