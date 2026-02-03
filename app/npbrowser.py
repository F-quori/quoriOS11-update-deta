import tkinter as tk
import subprocess
import time
import ctypes
from ctypes import wintypes

# Windows APIの定義
user32 = ctypes.windll.user32
SetParent = user32.SetParent
SetWindowPos = user32.SetWindowPos
FindWindowW = user32.FindWindowW
GetWindowThreadProcessId = user32.GetWindowThreadProcessId

def run(master, os_core):
    win = tk.Toplevel(master)
    win.title("peroppa_browser.qoa - neepars Hijack v9.0")
    win.geometry("1100x800")
    win.configure(bg="black")
    
    acc = os_core.config.get("accent_color", "#00d9ff")
    NPBrowser(win, acc)

class NPBrowser:
    def __init__(self, root, acc):
        self.root = root
        self.acc = acc
        self.browser_process = None
        self.child_hwnd = None
        self.create_widgets()

    def create_widgets(self):
        # Header
        header = tk.Frame(self.root, bg="#0a0a0a", height=40)
        header.pack(fill="x")
        tk.Label(header, text=" [P] HIJACK MODE ", fg="white", bg="#ff0044", font=("Consolas", 10, "bold")).pack(side="left", padx=10)
        
        # キャンバス（ここをブラウザの「受け皿」にする）
        self.container = tk.Frame(self.root, bg="black", highlightthickness=0)
        self.container.pack(expand=True, fill="both", padx=5, pady=5)
        
        # 起動ボタン
        self.launch_btn = tk.Button(self.container, text=" CLICK TO INHALE EDGE ", 
                                    command=self.start_hijack, bg="#222", fg=self.acc, 
                                    relief="flat", font=("Consolas", 12))
        self.launch_btn.place(relx=0.5, rely=0.5, anchor="center")

    def start_hijack(self):
        self.launch_btn.config(text="INHALING... PLEASE WAIT", state="disabled")
        self.root.update()

        # 1. Edgeを「アプリモード」で起動（余計なバーを消して吸引しやすくする）
        # ※ 起動直後はウィンドウハンドルが取れないので少し待つ
        cmd = 'start msedge --app=https://www.google.com'
        subprocess.Popen(cmd, shell=True)
        
        time.sleep(3) # 起動待ち（PCの速度に合わせて調整）

        # 2. ウィンドウを探す (Edgeのクラス名を利用)
        # 本来はプロセスIDから探すのが正確ですが、邪道なのでクラス名で狙い撃ち
        self.child_hwnd = FindWindowW("Chrome_WidgetWin_1", None)

        if self.child_hwnd:
            # 3. 自分のTkinterウィンドウのIDを取得
            parent_hwnd = self.root.winfo_id()
            
            # 4. 運命の SetParent
            SetParent(self.child_hwnd, parent_hwnd)
            
            # 5. 位置調整（Tkinterの枠にフィットさせる）
            self.root.after(100, self.resize_browser)
            self.launch_btn.destroy()
        else:
            self.launch_btn.config(text="INHALE FAILED. RETRY?", state="normal")

    def resize_browser(self):
        if self.child_hwnd:
            # 枠に合わせてリサイズ (x=0, y=40, width, height)
            w = self.root.winfo_width()
            h = self.root.winfo_height() - 40
            SetWindowPos(self.child_hwnd, 0, 0, 40, w, h, 0x0040)
