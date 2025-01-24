from tkinter import messagebox
import sys


def show_error(message, quit=False):
    messagebox.showerror("Error", message)
    if quit:
        sys.exit()

def show_info(message, quit=False):
    messagebox.showinfo("Info", message)
    if quit:
        sys.exit()