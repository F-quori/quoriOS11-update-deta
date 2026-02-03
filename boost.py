import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import os
import sys
import json
import importlib
import importlib.util
import subprocess
import time
import datetime
import ctypes
import threading
import webbrowser
import platform
import logging

# 起動メッセージ
print("Quori OS Launching...\nLoading Kernel Components...")

# =============================================================================
# [1] SYSTEM PATHS & CONSTANTS
# =============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

APP_DIR = os.path.join(BASE_DIR, "app")
ICON_DIR = os.path.join(APP_DIR, "__appdeta__")
CONFIG_PATH = os.path.join(BASE_DIR, "system.qcfg")
LOG_PATH = os.path.join(BASE_DIR, "system.log")

LOGO_NORMAL = os.path.join(BASE_DIR, "logo.png")
LOGO_PRO = os.path.join(BASE_DIR, "pro_logo.png")
LOGIN_BG = os.path.join(BASE_DIR, "login_bg.png")

logging.basicConfig(
    filename=LOG_PATH, level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# =============================================================================
# [2] MASTER KERNEL ENGINE
# =============================================================================
class QuoriOSCore:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.kernel_version = "11.5.0.PRO-ULTIMATE"
        self.session_id = f"Q11P-{int(time.time())}"
        self.boot_time = datetime.datetime.now()
        
        self.current_user = None
        self.system_mode = "normal" 
        self.taskbar_images = {} 
        
        self.config = {"password": "", "accent_color": "#00d9ff", "user_name": "ADMIN"}
        self.user_db = {}
        
        self.initialize_filesystem()
        self.load_v11_config_persistence()
        
        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()
        
        logging.info(f"Kernel {self.kernel_version} initialized.")
        self.initiate_boot_sequence()

    def initialize_filesystem(self):
        for d in [APP_DIR, ICON_DIR]:
            if not os.path.exists(d):
                os.makedirs(d)

    def load_v11_config_persistence(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.user_db = data.get("users", {})
                    sys_info = data.get("system_info", {})
                    self.system_mode = sys_info.get("mode", "normal")
            except Exception as e:
                logging.error(f"Config Load Error: {e}")
        
        if not self.user_db:
            self.user_db = {"test01-q": {"name": "ADMIN", "role": "ADMIN", "color": "#00d9ff"}}
            self.save_system_state_to_disk()

    def save_system_state_to_disk(self):
        try:
            disk_data = {"users": self.user_db, "system_info": {"mode": self.system_mode}}
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(disk_data, f, indent=4, ensure_ascii=False)
            return True
        except: return False

    def get_icon(self, name, size=(45, 45)):
        icon_path = os.path.join(ICON_DIR, f"{name}_logo.png")
        if not os.path.exists(icon_path):
            icon_path = LOGO_PRO if self.system_mode == "pro" else LOGO_NORMAL
        try:
            img = Image.open(icon_path)
            return ImageTk.PhotoImage(img.resize(size, Image.Resampling.LANCZOS))
        except: return None

    def invoke_app(self, name, **kwargs):
        targets = [name, f"app.{name}"]
        if "setting" in name: targets.extend(["setting", "app.setting"])
        mod = None
        for t in targets:
            try:
                if t in sys.modules: mod = importlib.reload(sys.modules[t])
                else: mod = importlib.import_module(t)
                break
            except: continue
        if mod:
            if hasattr(mod, "run"): mod.run(self.root, self, **kwargs)
            elif hasattr(mod, "SettingApp"): mod.SettingApp(self.root, self)
        else:
            messagebox.showerror("Error", f"Module {name} not found.")

    def initiate_boot_sequence(self):
        self.boot_win = tk.Toplevel(self.root)
        self.boot_win.attributes("-fullscreen", True, "-topmost", True)
        self.boot_win.configure(bg="black")
        self.load_v11_config_persistence()
        
        if self.system_mode == "pro":
            target_logo, acc_color = LOGO_PRO, "#ff9d00"
        else:
            target_logo, acc_color = LOGO_NORMAL, "#00d9ff"
            
        logo_sz = int(min(self.sw, self.sh) * 0.55)
        try:
            if os.path.exists(target_logo):
                raw = Image.open(target_logo)
                self.boot_logo_tk = ImageTk.PhotoImage(raw.resize((logo_sz, logo_sz), Image.Resampling.LANCZOS))
                tk.Label(self.boot_win, image=self.boot_logo_tk, bg="black").place(relx=0.5, rely=0.5, anchor="center")
            else: raise FileNotFoundError
        except:
            tk.Label(self.boot_win, text="QUORI OS 11", fg=acc_color, bg="black", font=("Consolas", 60, "bold")).place(relx=0.5, rely=0.5, anchor="center")

        self.boot_win.attributes("-alpha", 0.0)
        self.animate_fade(self.boot_win, 0.0, 1.0, 2500, 
                          lambda: self.root.after(3000, 
                          lambda: self.animate_fade(self.boot_win, 1.0, 0.0, 1500, self.draw_login_gate)))

    def animate_fade(self, target, start, end, duration, callback):
        steps = 60
        delta = (end - start) / steps
        def step(curr):
            if not target.winfo_exists(): return
            target.attributes("-alpha", max(0.0, min(1.0, curr)))
            if (delta > 0 and curr < end) or (delta < 0 and curr > end):
                self.root.after(duration // steps, lambda: step(curr + delta))
            elif callback: callback()
        step(start)

    def draw_login_gate(self):
        if hasattr(self, 'boot_win'): self.boot_win.destroy()
        self.login_win = tk.Toplevel(self.root)
        self.login_win.attributes("-fullscreen", True)
        self.login_win.configure(bg="#050505")
        acc = "#ff9d00" if self.system_mode == "pro" else "#00d9ff"
        p = tk.Frame(self.login_win, bg="#000", highlightthickness=2, highlightbackground=acc)
        p.place(relx=0.5, rely=0.6, anchor="center")
        tk.Label(p, text="QuoriOS login window", fg=acc, bg="#000", font=("Consolas", 16, "bold")).pack(pady=20, padx=50)
        self.pw_input = tk.Entry(p, show="*", bg="#111", fg="white", font=("Consolas", 32), justify="center", relief="flat", width=20)
        self.pw_input.pack(pady=10, padx=40, ipady=12)
        self.pw_input.focus_set()
        self.pw_input.bind("<Return>", lambda e: self.process_login())
        tk.Button(p, text="ACCESS", command=self.process_login, bg=acc, fg="black", font=("Consolas", 12, "bold"), padx=60, pady=18).pack(pady=25)

    def process_login(self):
        pw = self.pw_input.get()
        if pw in self.user_db:
            self.current_user = self.user_db[pw]
            self.login_win.destroy()
            self.build_desktop_env()
        else: self.pw_input.delete(0, tk.END)

    def build_desktop_env(self):
        self.root.deiconify()
        self.root.attributes("-fullscreen", True); self.root.configure(bg="black")
        acc = "#ff9d00" if self.system_mode == "pro" else self.current_user.get("color", "#00d9ff")
        
        tk.Label(self.root, text=f"SESSION: {self.current_user['name'].upper()}", 
                 fg=acc, bg="black", font=("Consolas", 52, "bold")).place(relx=0.5, rely=0.5, anchor="center")
        
        self.bar = tk.Frame(self.root, bg="#050505", height=90)
        self.bar.pack(side="bottom", fill="x")

        # [PWR]ボタンを先にパッキング（右端を死守）
        tk.Button(self.bar, text=" [PWR] ", fg="white", bg="#aa0000", relief="flat", 
                  font=("Consolas", 12, "bold"), padx=25, command=self.show_power_menu).pack(side="right", padx=30, pady=10)

        # 固定アイコン（設定・時計）
        self.taskbar_images["setting"] = self.get_icon("setting")
        tk.Button(self.bar, image=self.taskbar_images["setting"], bg="#050505", bd=0, 
                  command=lambda: self.invoke_app("setting")).pack(side="left", padx=10, pady=5)

        self.taskbar_images["clock"] = self.get_icon("clock")
        tk.Button(self.bar, image=self.taskbar_images["clock"], bg="#050505", bd=0, 
                  command=lambda: self.invoke_app("clock")).pack(side="left", padx=5, pady=5)

        # 動的アプリエリア
        self.app_strip = tk.Frame(self.bar, bg="#050505")
        self.app_strip.pack(side="left", fill="both", expand=True, padx=10)
        
        self.sync_taskbar_with_orange_logic()

    def sync_taskbar_with_orange_logic(self):
        """はみ出し防止：パディングを詰め、スリムなフォントで配置"""
        for w in self.app_strip.winfo_children(): w.destroy()
        acc = "#ff9d00" if self.system_mode == "pro" else self.current_user.get("color", "#00d9ff")
        if os.path.exists(APP_DIR):
            for f in sorted(os.listdir(APP_DIR)):
                if f.endswith(".py") and f != "__init__.py" and "setting" not in f and "clock" not in f:
                    name = f.replace(".py", "")
                    tk.Button(self.app_strip, text=f"[{name.upper()}]", 
                              fg=acc, bg="#050505", relief="flat", 
                              font=("Consolas", 11, "bold"), # スリム化
                              padx=4, # 詰め
                              command=lambda n=name: self.invoke_app(n)).pack(side="left", padx=3)

    # --- [POWER MANAGEMENT MENU] ---
    def show_power_menu(self):
        self.pwr_win = tk.Toplevel(self.root)
        self.pwr_win.attributes("-fullscreen", True, "-topmost", True)
        self.pwr_win.configure(bg="black")
        self.pwr_win.attributes("-alpha", 0.95)
        
        f = tk.Frame(self.pwr_win, bg="#000", highlightthickness=1, highlightbackground="#444")
        f.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(f, text="SYSTEM POWER MENU", fg="#aa0000", bg="#000", font=("Consolas", 18, "bold")).pack(pady=20, padx=60)

        pwr_options = [
            ("SHUTDOWN", "Terminate all processes", self.pwr_shutdown),
            ("REBOOT (PC)", "Full system hardware restart", self.pwr_reboot_pc),
            ("REBOOT (quoriOS)", "Restart OS Kernel", self.pwr_reboot_os),
            ("SLEEP", "Lock session and sleep", self.pwr_sleep),
            ("CLOSE", "Return to desktop", self.pwr_win.destroy)
        ]

        for txt, desc, cmd in pwr_options:
            frame = tk.Frame(f, bg="#000")
            frame.pack(fill="x", padx=20, pady=5)
            tk.Button(frame, text=txt, command=cmd, bg="#111", fg="white", font=("Consolas", 12, "bold"), width=18, relief="flat").pack(side="left")
            tk.Label(frame, text=f"| {desc}", fg="#666", bg="#000", font=("Consolas", 9)).pack(side="left", padx=10)

    def pwr_shutdown(self):
        if messagebox.askyesno("Power", "Shutdown QuoriOS?"): self.root.quit()

    def pwr_reboot_pc(self):
        if messagebox.askyesno("Power", "Simulate PC Reboot?"):
            os.execl(sys.executable, sys.executable, *sys.argv)

    def pwr_reboot_os(self):
        self.pwr_win.destroy(); self.root.withdraw(); self.initiate_boot_sequence()

    def pwr_sleep(self):
        self.pwr_win.destroy(); self.root.withdraw(); self.draw_login_gate()

if __name__ == "__main__":
    kernel = QuoriOSCore()
    tk.mainloop()
