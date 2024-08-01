import tkinter as tk
from config import operation

def create_widgets(parent):
    # Example of adding widgets in a grid (2 columns)
    for i in range(10):  # Adjust the range as needed
        label = tk.Label(parent, text=f"Valve {i+1} Delay:")
        entry = tk.Entry(parent)
        label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
        entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")

    # Additional example to show the next set of widgets in the second column
    for i in range(10, 20):  # Adjust the range as needed
        label = tk.Label(parent, text=f"Valve {i+1} Delay:")
        entry = tk.Entry(parent)
        label.grid(row=i-10, column=2, padx=10, pady=5, sticky="w")
        entry.grid(row=i-10, column=3, padx=10, pady=5, sticky="w")

    # Example button to start the operation
    start_button = tk.Button(parent, text="Start Operation", command=operation)
    start_button.grid(row=21, column=0, columnspan=4, pady=10)
