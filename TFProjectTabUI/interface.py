import tkinter as tk
from operation_manager import Operation
from judge_on_off import JudgeClass
import threading
import common_delays as c

class Interface:
    def __init__(self, master):
        self.operation = Operation(config_file="./config.yaml")
        self.master = master
        self.rows = len(c.delays)       # 4
        self.columns = 2
        self.delay_label = [[None for _ in range(self.columns)] for _ in range(self.rows)]
        self.delay_entry = [[None for _ in range(self.columns)] for _ in range(self.rows)]
        self.update_button = [[None for _ in range(self.columns)] for _ in range(self.rows)]
        self.status_label = [[None for _ in range(self.columns)] for _ in range(self.rows)]

        for i in range(self.rows):
            for j in range(self.columns):
                self.delay_label[i][j] = tk.Label(master, text=f"Valve {i} {JudgeClass.OpenClose(j)} delay (from pump {i} {JudgeClass.InfuseStop(j)})")
                self.delay_label[i][j].grid(row=2*i+j, column=0, padx=10, pady=5, sticky="nw")
                self.delay_entry[i][j] = tk.Entry(master)
                self.delay_entry[i][j].insert(0, 0)
                self.delay_entry[i][j].grid(row=2*i+j, column=1, padx=10, pady=5, sticky="nw")
                self.update_button[i][j] = tk.Button(master, text="Update", command=lambda i=i, j=j : self.update_delay(self.master, i, j, self.operation)) # lambda式を使ってiとjを保持している
                self.update_button[i][j].grid(row=2*i+j, column=2, padx=10, pady=5, sticky="nw")
                self.status_label[i][j] = tk.Label(master, text=f"Current value: {c.delays[i][j]} seconds")
                self.status_label[i][j].grid(row=2*i+j, column=3, padx=10, pady=5, sticky="nw")

        self.startbutton = tk.Button(master, text="Start", command=lambda : self.start_operation(self.operation))
        self.startbutton.grid(row=2*self.rows, column=0, columnspan=2, pady=10)
        self.stopbutton = tk.Button(master, text="Stop", command=lambda : self.stop_operation(self.operation))
        self.stopbutton.grid(row=2*self.rows, column=2, columnspan=2, pady=10)

    def update_delay(self, master, i, j, Operation):
        '''バルブ1の開放開始時間の更新'''
        c.delays[i][j] = float(self.delay_entry[i][j].get())
        self.status_label[i][j].config(text=f"Current value: {c.delays[i][j]} seconds")
        # print(f"g.delaysの{i}, {j}は{g.delays[i][j]}")
    
    def start_operation(self, Operation):                
        self.operation_thread = threading.Thread(target=Operation.run)
        if Operation.status == False:
            # シリンジポンプ操作スレッドの開始
            Operation.status = True
            print("operation starting")
            self.operation_thread.start()


    def stop_operation(self, Operation):
        if Operation.status == True:
            # シリンジポンプ操作スレッドの停止
            Operation.status = False
            self.operation_thread.join()  # スレッドの終了を待つ
            print("operation_thread over")


        

