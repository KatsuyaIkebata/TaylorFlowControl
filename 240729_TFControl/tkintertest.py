import threading
from tkinter import Tk, Label, Entry, Button

# グローバル変数
switch_delay_1 = 2.0
switch_delay_2 = 2.0

def update_delay_1():
    global switch_delay_1
    switch_delay_1 = float(delay_entry_1.get())
    status_label_1.config(text=f"Switch delay 1 updated to {switch_delay_1} seconds")

def update_delay_2():
    global switch_delay_2 
    switch_delay_2 = float(delay_entry_2.get())
    status_label_2.config(text=f"Switch delay 2 updated to {switch_delay_2} seconds")

def operation():
    print(f'switch_delay 1 = {switch_delay_1} s')
    print(f'switch_delay 2 = {switch_delay_2} s')

# GUIセットアップ
root = Tk()
root.title("Switch Delay Controller")

Label(root, text="Enter new switch delay 1:").pack()
delay_entry_1 = Entry(root)
delay_entry_1.pack()

Label(root, text="Enter new switch delay 2:").pack()
delay_entry_2 = Entry(root)
delay_entry_2.pack()

update_button_1 = Button(root, text="Update Delay 1", command=update_delay_1)
update_button_1.pack()

update_button_2 = Button(root, text="Update Delay 2", command=update_delay_2)
update_button_2.pack()

status_label_1 = Label(root, text=f"Current switch delay 1: {switch_delay_1} seconds")
status_label_1.pack()

status_label_2 = Label(root, text=f"Current switch delay 2: {switch_delay_2} seconds")
status_label_2.pack()

# GUIループの開始
root.mainloop()

# シリンジポンプ操作スレッド
operation_thread = threading.Thread(target=operation)
operation_thread.start()

# スレッドの終了を待つ
operation_thread.join()