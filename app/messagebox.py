import tkinter as tk
from tkinter import messagebox

class MessageBoxShow(tk.Tk):
    def __init__(self, title, message, icon):
        super().__init__()
        self.withdraw()
        self.attributes('-topmost', True)
        messagebox.showinfo(title, message, parent=self, icon=icon)
        self.destroy()

class MessageBoxAsk(tk.Tk):
    def __init__(self, title, message, icon):
        super().__init__()
        self.withdraw()
        self.attributes('-topmost', True)
        self.result = messagebox.askyesno(title, message, parent=self, icon=icon)
        self.destroy()

class MessageBoxAskCancel(tk.Tk):
    def __init__(self, title, message, icon):
        super().__init__()
        self.withdraw()
        self.attributes('-topmost', True)
        self.result = messagebox.askyesnocancel(title, message, parent=self, icon=icon)
        self.destroy()

def showinfo(title, message):
    MessageBoxShow(title, message, "info")

def showerror(title, message):
    MessageBoxShow(title, message, "error")

def showwarning(title, message):
    MessageBoxShow(title, message, "warning")

def askyesno(title, message):
    return MessageBoxAsk(title, message, "question").result

def askyesnocancel(title, message):
    return MessageBoxAskCancel(title, message, "question").result
