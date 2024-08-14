import tkinter as tk
# from operation_manager import Operation

class Interface:
    def __init__(self, master):
        self.master = master
        # self.operation = Operation()  # Operation クラスのインスタンス化
        self.create_widgets()

    def create_widgets(self):
        self.delay_entry = tk.Entry(self.master)
        self.delay_entry.pack()
        self.update_button = tk.Button(self.master, text="Update Delay", command=self.update_delay)
        self.update_button.pack()
        self.run_button = tk.Button(self.master, text="Run Operation", command=self.run_operation)
        self.run_button.pack()

    def update_delay(self):
        new_delay = float(self.delay_entry.get())
        # self.operation.set_delay(new_delay)

    def run_operation(self):
        print("Run")
        # self.operation.run_process()


root = tk.Tk()
app = Interface(root)
root.mainloop()
