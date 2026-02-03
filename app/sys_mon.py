import tkinter as tk
import platform
def run(root, os_core):
    w = tk.Toplevel(root)
    w.title('MONITOR')
    w.geometry('300x200')
    info = f'ARCH: {platform.machine()}'
    tk.Label(w, text=info, font=('Consolas', 12)).pack(pady=50)
