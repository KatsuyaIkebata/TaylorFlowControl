import tkinter as tk
from interface import interface
from operation_manager import OperationManager
from syringe_pump import SyringePump
from valve import Valve
from Threading import Thread

def main():
    global status, delays
    root = tk.Tk()
    display = Interface(root)
    delays = float(display.delay_entry[i][j])
    if display.startbutton == True and status == False:
        # シリンジポンプ操作スレッドの開始
        new_thread = threading.Thread(target=OperationThread)
        new_thread.start()
    elif display.startbutton == False and status == True:
        new_thread.join()
    root.mainloop()

def OperationThread():
    global status, delays
    NewOperation = OperationManager(delays)
    status = True


if __name__ == "__main__":
    '''
    ファイル間共通変数 delaysの設定
    バルブ命令の遅れ時間を設定
    [0][0]:バルブ0の開放(電源OFF)
    [3][1]: バルブ3の閉鎖(電源ON)
    '''
    delays = [[0.0 for _ in range(2)] for _ in range(4)]
    status = False # 操作停止: False, 操作中: True
    main()
    GPIO.cleanup()
    print("main program is over.")
