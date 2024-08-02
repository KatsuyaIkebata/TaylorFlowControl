import tkinter as tk
from config import operation
import global_value as g

def create_widgets(parent):
    def update_delay(i, j):
        '''バルブ1の開放開始時間の更新'''
        g.delays[i][j] = float(delay_entry[i][j].get())
        status_label[i][j].config(text=f"Current value: {g.delays[i][j]} seconds")
        # print(f"g.delaysの{i}, {j}は{g.delays[i][j]}")

    def OpenClose(Bool):
        '''開放か閉鎖か判断'''
        if(Bool == 0):
            return "Open"
        elif(Bool == 1):
            return "Close"
        else:
            return "Error"
        
    def PumpNum(rows):
        '''バルブ番号からポンプ番号の判断'''
        if(rows % 2 == 0):
            return 0
        elif(rows % 2 == 1):
            return 1
        else:
            return "Error"
        
    def InfuseStop(columns):
        '''バルブのON/OFFからポンプのInfuse/Stopの判断'''
        if(columns == 0):
            return "stop"
        elif(columns == 1):
            return "infuse"
        else:
            return "Error"


    rows = len(g.delays)       # 4
    columns = len(g.delays[0]) # 2
    delay_label = [[None for _ in range(columns)] for _ in range(rows)]
    delay_entry = [[None for _ in range(columns)] for _ in range(rows)]
    update_button = [[None for _ in range(columns)] for _ in range(rows)]
    status_label = [[None for _ in range(columns)] for _ in range(rows)]


    for i in range(rows):
        for j in range(columns):
            delay_label[i][j] = tk.Label(parent, text=f"Valve {i} {OpenClose(j)} delay (from pump {PumpNum(i)} {InfuseStop(j)})")
            delay_label[i][j].grid(row=2*i+j, column=0, padx=10, pady=5, sticky="nw")
            delay_entry[i][j] = tk.Entry(parent)
            delay_entry[i][j].insert(0, 0)
            delay_entry[i][j].grid(row=2*i+j, column=1, padx=10, pady=5, sticky="nw")
            update_button[i][j] = tk.Button(parent, text="Update", command=lambda i=i, j=j : update_delay(i,j)) # lambda式を使ってiとjを保持している
            update_button[i][j].grid(row=2*i+j, column=2, padx=10, pady=5, sticky="nw")
            status_label[i][j] = tk.Label(parent, text=f"Current value: {g.delays[i][j]} seconds")
            status_label[i][j].grid(row=2*i+j, column=3, padx=10, pady=5, sticky="nw")

    # Example button to start the operation
    start_button = tk.Button(parent, text="Start Operation", command=operation)
    start_button.grid(row=2*rows, column=0, columnspan=4, pady=10)

