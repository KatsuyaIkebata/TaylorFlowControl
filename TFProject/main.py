import tkinter as tk
from tkinter import ttk
from interface import Interface
from operation_manager import OperationClass
from pump import PumpClass
from valve import ValveClass
import RPi.GPIO as GPIO

def main():
    def create_app():
        root = tk.Tk()
        root.title("Taylor Flow Controller")
        root.geometry("800x400")

        # Frame to hold canvas and scrollbars
        frame = ttk.Frame(root)

        # Canvas and scrollbar
        canvas = tk.Canvas(root)
        v_scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(root, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack canvas and scrollbar
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        frame.pack(fill="both", expand=True)

        return root, scrollable_frame
    
    # 設定
    
    GPIO.setmode(GPIO.BCM)  # BCM番号でGPIOピンを指定
    config = OperationClass.Config(
        tube_diameter_inch = 1/8,    # inch チューブの内径
        syringe_diameter = 29.2,    # mm シリンジポンプの内径
        total_rate = 3,             # mL/min 合計流量
        total_time = 1,             # min 合計時間
        alarm_time = 0.5,           # min アラームが鳴る時間
        slug_length0 = 30,          # mm スラグ1の長さ(実際は少しずれる)
        slug_length1 = 50,          # mm スラグ2の長さ(実際は少しずれる)
        response_time = 0.1,        # s 応答を待つ時間
        pump_num = 2,               # ポンプの数
        valve_num = 4,              # バルブの数
        gpio_pin = [6, 13, 19, 26], # BCM番号でGPIOピンを指定       
        serial_port = ['/dev/ttyACM0', '/dev/ttyACM1'] # シリンジポンプをつないだシリアルポート
    )
    
    NewOpe = OperationClass(config)
    root, scrollable_frame = create_app()
    Monitor = Interface(master=scrollable_frame, Operation=NewOpe)
    root.mainloop()
    NewOpe.end()

if __name__ == "__main__":
    main()
    print("main program is over.")
