import tkinter as tk
from tkinter import ttk

# グローバル変数
valve_delay_1A = 0.0    # バルブ1の開放の遅れ時間
valve_delay_1C = 0.0    # バルブ1の閉鎖の遅れ時間
valve_delay_2A = 0.0    # バルブ2の開放の遅れ時間
valve_delay_2C = 0.0    # バルブ2の閉鎖の遅れ時間
valve_delay_3A = 0.1    # バルブ3の開放の遅れ時間
valve_delay_3C = 0.1    # バルブ3の閉鎖の遅れ時間
valve_delay_4A = 0.1    # バルブ4の開放の遅れ時間
valve_delay_4C = 0.1    # バルブ4の閉鎖の遅れ時間

def update_delay_1A():
    """バルブ1の開放開始時間の更新"""
    global valve_delay_1A
    valve_delay_1A = float(delay_entry_1A.get())
    status_Label_1A.config(text=f"Current valve 1 open delay: {valve_delay_1A} seconds")

def update_delay_1C():
    """バルブ1の閉鎖開始時間の更新"""
    global valve_delay_1C
    valve_delay_1C = float(delay_entry_1C.get())
    status_Label_1C.config(text=f"Current valve 1 close delay: {valve_delay_1C} seconds\n")

def update_delay_2A():
    """バルブ2の開放開始時間の更新"""
    global valve_delay_2A
    valve_delay_2A = float(delay_entry_2A.get())
    status_Label_2A.config(text=f"Current valve 1 open delay: {valve_delay_2A} seconds")

def update_delay_2C():
    """バルブ2の閉鎖開始時間の更新"""
    global valve_delay_2C
    valve_delay_2C = float(delay_entry_2C.get())
    status_Label_2C.config(text=f"Current valve 1 close delay: {valve_delay_2C} seconds\n")

def update_delay_3A():
    """バルブ3の開放開始時間の更新"""
    global valve_delay_3A
    valve_delay_3A = float(delay_entry_3A.get())
    status_Label_3A.config(text=f"Current valve 3 open delay: {valve_delay_3A} seconds")

def update_delay_3C():
    """バルブ1の閉鎖開始時間の更新"""
    global valve_delay_3C
    valve_delay_3C = float(delay_entry_3C.get())
    status_Label_3C.config(text=f"Current valve 3 close delay: {valve_delay_3C} seconds\n")

def update_delay_4A():
    """バルブ4の開放開始時間の更新"""
    global valve_delay_4A
    valve_delay_4A = float(delay_entry_4A.get())
    status_Label_4A.config(text=f"Current valve 4 open delay: {valve_delay_4A} seconds")

def update_delay_4C():
    """バルブ4の閉鎖開始時間の更新"""
    global valve_delay_4C
    valve_delay_4C = float(delay_entry_4C.get())
    status_Label_4C.config(text=f"Current valve 4 close delay: {valve_delay_4C} seconds\n")

root = tk.Tk()
root.title("Valve Delay Settings")

# Canvas and scrollbar
canvas = tk.Canvas(root)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Pack canvas and scrollbar
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


tk.Label(scrollable_frame, text="Valve 1 open delay (from pump 1 infuse):").pack()
delay_entry_1A = tk.Entry(scrollable_frame)
delay_entry_1A.pack()

update_button_1A = tk.Button(scrollable_frame, text="Update valve 1 open delay", command=update_delay_1A)
update_button_1A.pack()

status_Label_1A = tk.Label(scrollable_frame, text=f"Current valve 1 open delay: {valve_delay_1A} seconds")
status_Label_1A.pack()

tk.Label(scrollable_frame, text="Valve 1 close delay (from pump 1 stop):").pack()
delay_entry_1C = tk.Entry(scrollable_frame)
delay_entry_1C.pack()

update_button_1C = tk.Button(scrollable_frame, text="Update valve 1 close delay", command=update_delay_1C)
update_button_1C.pack()

status_Label_1C = tk.Label(scrollable_frame, text=f"Current valve 1 close delay: {valve_delay_1C} seconds\n")
status_Label_1C.pack()


tk.Label(scrollable_frame, text="Valve 2 open delay (from pump 2 infuse):").pack()
delay_entry_2A = tk.Entry(scrollable_frame)
delay_entry_2A.pack()

update_button_2A = tk.Button(scrollable_frame, text="Update valve 2 open delay", command=update_delay_2A)
update_button_2A.pack()

status_Label_2A = tk.Label(scrollable_frame, text=f"Current valve 2 open delay: {valve_delay_2A} seconds")
status_Label_2A.pack()

tk.Label(scrollable_frame, text="Valve 2 close delay (from pump 2 stop):").pack()
delay_entry_2C = tk.Entry(scrollable_frame)
delay_entry_2C.pack()

update_button_2C = tk.Button(scrollable_frame, text="Update valve 2 close delay", command=update_delay_2C)
update_button_2C.pack()

status_Label_2C = tk.Label(scrollable_frame, text=f"Current valve 2 close delay: {valve_delay_2C} seconds\n")
status_Label_2C.pack()


tk.Label(scrollable_frame, text="Valve 3 open delay (from pump 1 infuse):").pack()
delay_entry_3A = tk.Entry(scrollable_frame)
delay_entry_3A.pack()

update_button_3A = tk.Button(scrollable_frame, text="Update valve 3 open delay", command=update_delay_3A)
update_button_3A.pack()

status_Label_3A = tk.Label(scrollable_frame, text=f"Current valve 3 open delay: {valve_delay_3A} seconds")
status_Label_3A.pack()

tk.Label(scrollable_frame, text="Valve 3 close delay (from pump 1 stop):").pack()
delay_entry_3C = tk.Entry(scrollable_frame)
delay_entry_3C.pack()

update_button_3C = tk.Button(scrollable_frame, text="Update valve 3 close delay", command=update_delay_3C)
update_button_3C.pack()

status_Label_3C = tk.Label(scrollable_frame, text=f"Current valve 3 close delay: {valve_delay_3C} seconds\n")
status_Label_3C.pack()


tk.Label(scrollable_frame, text="Valve 4 open delay (from pump 2 infuse):").pack()
delay_entry_4A = tk.Entry(scrollable_frame)
delay_entry_4A.pack()

update_button_4A = tk.Button(scrollable_frame, text="Update valve 4 open delay", command=update_delay_4A)
update_button_4A.pack()

status_Label_4A = tk.Label(scrollable_frame, text=f"Current valve 4 open delay: {valve_delay_4A} seconds")
status_Label_4A.pack()

tk.Label(scrollable_frame, text="Valve 4 close delay (from pump 2 stop):").pack()
delay_entry_4C = tk.Entry(scrollable_frame)
delay_entry_4C.pack()

update_button_4C = tk.Button(scrollable_frame, text="Update valve 4 close delay", command=update_delay_4C)
update_button_4C.pack()

status_Label_4C = tk.Label(scrollable_frame, text=f"Current valve 4 close delay: {valve_delay_4C} seconds\n")
status_Label_4C.pack()


root.mainloop()
