import tkinter as tk
from tkinter import ttk
from widgets import create_widgets
from config import operation
import global_value as g

def main():
    root = tk.Tk()
    root.title("Taylor Flow Controller")

    # Frame to hold canvas and scrollbars
    frame = ttk.Frame(root)

    # Canvas and scrollbar
    canvas = tk.Canvas(root)
    v_scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    h_scrollbar = ttk.Scrollbar(root, orient="horizontal", command=canvas.xview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)


    # Pack canvas and scrollbar
    v_scrollbar.pack(side="right", fill="y")
    h_scrollbar.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)
    frame.pack(fill="both", expand=True)

    # Create widgets
    create_widgets(scrollable_frame)

    # Start the Tkinter main loop
    root.mainloop()

    # 終了メッセージ表示
    end_label = tk.Label(scrollable_frame, text="Operation Finished", font=("Helvetica", 16), fg="red")
    end_label.pack(pady=20)

if __name__ == "__main__":
    main()

