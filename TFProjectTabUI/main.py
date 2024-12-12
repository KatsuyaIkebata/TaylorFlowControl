import tkinter as tk
from tkinter import ttk
from interface import Interface

def main():
    def create_app():
        root = tk.Tk()
        root.title("Taylor Flow Controller")
        root.geometry("800x400")

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
        canvas.configure(yscrollcommand=v_scrollbar.set)
        h_scrollbar.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        frame.pack(fill="both", expand=True)

        return root, scrollable_frame

    root, scrollable_frame = create_app()
    Interface(master=scrollable_frame)
    root.mainloop()

if __name__ == "__main__":
    main()
    print("main program is over.")
