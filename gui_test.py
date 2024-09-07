import tkinter as tk
from tkinter import ttk

class SimpleGUI:
    def __init__(self, master):
        self.master = master
        master.title("Simple GUI Example")

        # Text
        self.label = tk.Label(master, text="Welcome to the SOS Game Setup")
        self.label.pack()

        # Line
        self.canvas = tk.Canvas(master, width=200, height=2)
        self.canvas.create_line(0, 1, 200, 1)
        self.canvas.pack()

        # Checkbox
        self.check_var = tk.IntVar()
        self.checkbox = tk.Checkbutton(master, text="Enable AI opponent", variable=self.check_var)
        self.checkbox.pack()

        # Radio buttons
        self.radio_var = tk.StringVar()
        self.radio_var.set("3x3")
        self.radio_label = tk.Label(master, text="Select board size:")
        self.radio_label.pack()
        sizes = [("3x3", "3x3"), ("4x4", "4x4"), ("5x5", "5x5")]
        for text, value in sizes:
            tk.Radiobutton(master, text=text, variable=self.radio_var, value=value).pack()

        # Submit button
        self.submit_button = tk.Button(master, text="Start Game", command=self.submit)
        self.submit_button.pack()

    def submit(self):
        print(f"AI opponent: {'Yes' if self.check_var.get() else 'No'}")
        print(f"Board size: {self.radio_var.get()}")

root = tk.Tk()
gui = SimpleGUI(root)
root.mainloop()