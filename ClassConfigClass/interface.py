import tkinter as tk
from operation_manager import OperationClass

class Interface:
    def __init__(self, master, Operation):
        self.master = master
        self.Operation = Operation
        self.rows = len(self.Operation.delays)       # 4
        self.columns = len(self.Operation.delays[0]) # 2
        self.delay_label = [[None for _ in range(self.columns)] for _ in range(self.rows)]
        self.delay_entry = [[None for _ in range(self.columns)] for _ in range(self.rows)]
        self.update_button = [[None for _ in range(self.columns)] for _ in range(self.rows)]
        self.status_label = [[None for _ in range(self.columns)] for _ in range(self.rows)]

        for i in range(self.rows):
            for j in range(self.columns):
                self.delay_label[i][j] = tk.Label(master, text=f"Valve {i} {self.OpenClose(j)} delay (from pump {i} {self.InfuseStop(j)})")
                self.delay_label[i][j].grid(row=2*i+j, column=0, padx=10, pady=5, sticky="nw")
                self.delay_entry[i][j] = tk.Entry(master)
                self.delay_entry[i][j].insert(0, 0)
                self.delay_entry[i][j].grid(row=2*i+j, column=1, padx=10, pady=5, sticky="nw")
                self.update_button[i][j] = tk.Button(master, text="Update", command=lambda i=i, j=j : self.update_delay(self.master, i, j, self.Operation)) # lambda式を使ってiとjを保持している
                self.update_button[i][j].grid(row=2*i+j, column=2, padx=10, pady=5, sticky="nw")
                self.status_label[i][j] = tk.Label(master, text=f"Current value: {self.Operation.delays[i][j]} seconds")
                self.status_label[i][j].grid(row=2*i+j, column=3, padx=10, pady=5, sticky="nw")

        self.startbutton = tk.Button(master, text="Start", command=lambda : self.start_operation(self.Operation))
        self.startbutton.grid(row=2*self.rows, column=0, columnspan=2, pady=10)
        self.stopbutton = tk.Button(master, text="Stop", command=lambda : self.stop_operation(self.Operation))
        self.stopbutton.grid(row=2*self.rows, column=2, columnspan=2, pady=10)

    def update_delay(self, master, i, j, Operation):
        '''バルブ1の開放開始時間の更新'''
        self.Operation.delays[i][j] = float(self.delay_entry[i][j].get())
        self.status_label[i][j].config(text=f"Current value: {self.Operation.delays[i][j]} seconds")
        # print(f"g.delaysの{i}, {j}は{g.delays[i][j]}")

    def OpenClose(self, columns):
        '''開放か閉鎖か判断'''
        if(columns == 0):
            return "Open"
        elif(columns == 1):
            return "Close"
        else:
            return "Error"
        
    def PumpNum(self, rows):
        '''バルブ番号からポンプ番号の判断'''
        if(rows % 2 == 0):
            return 0
        elif(rows % 2 == 1):
            return 1
        else:
            return "Error"
        
    def InfuseStop(self, columns):
        '''バルブのON/OFFからポンプのInfuse/Stopの判断'''
        if(columns == 0):
            return "stop"
        elif(columns == 1):
            return "infuse"
        else:
            return "Error"

    def start_operation(self, Operation):
        if self.Operation.status == False:
            # シリンジポンプ操作スレッドの開始
            self.Operation.status = True
            Operation.run()
            print("operation started")

    def stop_operation(self, operation):
        if self.Operation.status == True:
            # シリンジポンプ操作スレッドの停止
            self.Operation.status = False
            Operation.stop()
            print("operation stopped")

