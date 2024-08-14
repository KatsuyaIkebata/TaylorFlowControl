import tkinter as tk
from operation_manager import OperationManager

class Interface:
    def __init__(self, master, Opeartion):
        self.master = master
        self.button = tk.Button(master, text="Start Operation", command=self.start_operation)
        self.button.pack()

    def start_operation(self):
        om = OperationManager()
        om.start_operation()

    def
