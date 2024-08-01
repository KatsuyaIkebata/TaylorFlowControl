import tkinter as tk
from tkinter import ttk
from widgets import create_widgets
from config import operation

def main():
    root = tk.Tk()
    root.title("Taylor Flow Controller")

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

    # Create widgets
    create_widgets(scrollable_frame)

    # Start the Tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    main()
