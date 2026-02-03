from tkinter import colorchooser
import tkinter as tk
from tkinter import messagebox
import os
import json

def run(root, os_core):
    """OSコアから呼び出されるエントリポイント"""
    SettingApp(root, os_core)

class SettingApp:
    def __init__(self, master, os_core):
        self.os_core = os_core
        self.master = master
        
        # 物理パス解決
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.base_dir, "system.qcfg")
        self.app_dir = os.path.join(self.base_dir, "app")
        
        # ウィンドウ初期化
        self.win = tk.Toplevel(master)
        self.win.title("QUORI SYSTEM CONTROL CENTER")
        self.win.geometry("700x850")
        self.win.configure(bg="#050505")
        self.win.attributes("-topmost", True)
        
        self.update_accent_color()
        
        # メインコンテナ（この中身を入れ替える）
        self.main_container = None
        self.refresh_container()
        
        self.show_main_menu()

    def update_accent_color(self):
        """Proモード同期"""
        self.acc = "#ff9d00" if self.os_core.system_mode == "pro" else "#00d9ff"

    def refresh_container(self):
        """Bad window pathエラーを防ぐための重厚なコンテナ再生成ロジック"""
        if self.main_container and self.main_container.winfo_exists():
            self.main_container.destroy()
        
        self.main_container = tk.Frame(self.win, bg="#050505")
        self.main_container.pack(fill="both", expand=True, padx=50, pady=50)

    # --- [PAGE 1] MAIN MENU ---
    def show_main_menu(self):
        self.refresh_container()
        self.update_accent_color()
        
        tk.Label(self.main_container, text="CORE CONTROL PANEL", fg=self.acc, bg="#050505", 
                 font=("Consolas", 28, "bold")).pack(pady=(0, 50))
        
        btn_s = {"bg": "#111", "fg": "white", "relief": "flat", "font": ("Consolas", 14), "pady": 20, "cursor": "hand2"}
        
        tk.Button(self.main_container, text="👤 PERSONALIZATION", command=self.show_personal_settings, **btn_s).pack(fill="x", pady=10)
        tk.Button(self.main_container, text="⚙️ SYSTEM MANAGEMENT", command=self.show_system_settings, **btn_s).pack(fill="x", pady=10)
        
        # セパレーター
        tk.Frame(self.main_container, bg=self.acc, height=1).pack(fill="x", pady=30)
        
        # AppStoreボタン
        tk.Button(self.main_container, text="🚀 OPEN APPSTORE", 
                  command=lambda: self.os_core.invoke_app("appstore"),
                  bg="#1a1a1a", fg=self.acc, font=("Consolas", 12, "bold"), pady=15, relief="flat").pack(fill="x")

        tk.Button(self.main_container, text="EXIT", command=self.win.destroy, 
                  bg="#222", fg="#666", relief="flat", font=("Consolas", 10)).pack(side="bottom", pady=20)

    # --- [PAGE 2] PERSONALIZATION ---
    def show_personal_settings(self):
        self.refresh_container()
        tk.Label(self.main_container, text="PERSONALIZATION", fg=self.acc, bg="#050505", font=("Consolas", 20, "bold")).pack(pady=(0, 30))
        
        # ユーザー名
        tk.Label(self.main_container, text="DISPLAY NAME", fg="#888", bg="#050505", font=("Consolas", 10)).pack(anchor="w")
        self.user_entry = tk.Entry(self.main_container, bg="#111", fg="white", relief="flat", font=("Consolas", 14))
        self.user_entry.insert(0, self.os_core.config.get("user_name", "ADMIN"))
        self.user_entry.pack(fill="x", pady=(5, 15), ipady=8)

        # パスワード
        tk.Label(self.main_container, text="ACCESS PASSWORD", fg="#888", bg="#050505", font=("Consolas", 10)).pack(anchor="w")
        self.pw_entry = tk.Entry(self.main_container, bg="#111", fg="white", relief="flat", font=("Consolas", 14))
        self.pw_entry.insert(0, self.os_core.config.get("password", ""))
        self.pw_entry.pack(fill="x", pady=(5, 15), ipady=8)

        # テーマカラー
        tk.Label(self.main_container, text="THEME ACCENT COLOR", fg="#888", bg="#050505", font=("Consolas", 10)).pack(anchor="w")
        self.target_color = self.os_core.config.get("accent_color", "#00d9ff")
        self.color_preview = tk.Frame(self.main_container, bg=self.target_color, height=40)
        self.color_preview.pack(fill="x", pady=5)
        
        tk.Button(self.main_container, text="PICK NEW COLOR", command=self.pick_color, bg="#222", fg="white", relief="flat").pack(fill="x", pady=(0, 15))

        self.add_navigation_buttons(self.save_personal)

    def pick_color(self):
        color = colorchooser.askcolor(initialcolor=self.target_color)[1]
        if color:
            self.target_color = color
            self.color_preview.config(bg=color)

    # --- [PAGE 3] SYSTEM MANAGEMENT ---
    def show_system_settings(self):
        self.refresh_container()
        tk.Label(self.main_container, text="SYSTEM ARCHITECTURE", fg=self.acc, bg="#050505", font=("Consolas", 20, "bold")).pack(pady=(0, 30))

        # 容量計算
        try:
            app_count = len([f for f in os.listdir(self.app_dir) if f.endswith(".py")])
            app_size = sum(os.path.getsize(os.path.join(self.app_dir, f)) for f in os.listdir(self.app_dir)) / 1024
        except:
            app_count, app_size = 0, 0
        
        stat_frame = tk.Frame(self.main_container, bg="#111", padx=15, pady=15)
        stat_frame.pack(fill="x", pady=10)
        tk.Label(stat_frame, text=f"INSTALLED APPS: {app_count}", fg="white", bg="#111", font=("Consolas", 11)).pack(anchor="w")
        tk.Label(stat_frame, text=f"APP DIRECTORY SIZE: {app_size:.2f} KB", fg="white", bg="#111", font=("Consolas", 11)).pack(anchor="w")

        # Pro切替
        tk.Label(self.main_container, text="KERNEL OPERATION MODE", fg="#888", bg="#050505", font=("Consolas", 10)).pack(anchor="w", pady=(20, 0))
        mode_text = f"SWITCH TO { 'NORMAL' if self.os_core.system_mode == 'pro' else 'PRO' } MODE"
        tk.Button(self.main_container, text=mode_text, command=self.toggle_mode_ui, 
                  bg=self.acc, fg="black", font=("Consolas", 12, "bold"), pady=10).pack(fill="x", pady=5)

        # ユーザー追加
        tk.Label(self.main_container, text="SECURITY ACCESS", fg="#888", bg="#050505", font=("Consolas", 10)).pack(anchor="w", pady=(20, 0))
        tk.Button(self.main_container, text="[+] ADD NEW SYSTEM USER", command=lambda: messagebox.showinfo("USER MGMT", "Initiating creation protocol..."), 
                  bg="#222", fg="white", font=("Consolas", 12), pady=10).pack(fill="x", pady=5)

        self.add_navigation_buttons(self.save_system)

    def toggle_mode_ui(self):
        self.os_core.system_mode = "pro" if self.os_core.system_mode == "normal" else "normal"
        self.update_accent_color()
        self.show_system_settings()

    def add_navigation_buttons(self, save_func):
        btn_f = tk.Frame(self.main_container, bg="#050505")
        btn_f.pack(side="bottom", fill="x", pady=20)
        tk.Button(btn_f, text="APPLY", command=save_func, bg=self.acc, fg="black", width=15, height=2, font=("Consolas", 10, "bold")).pack(side="right")
        tk.Button(btn_f, text="BACK", command=self.show_main_menu, bg="#333", fg="white", width=15, height=2).pack(side="right", padx=10)

    # --- [PERSISTENCE] ---
    def save_personal(self):
        self.finalize_save(new_user=self.user_entry.get(), new_pw=self.pw_entry.get(), new_color=self.target_color)

    def save_system(self):
        self.finalize_save(new_mode=self.os_core.system_mode)

    def finalize_save(self, new_user=None, new_pw=None, new_color=None, new_mode=None):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {"users": {}, "system_info": {}}

            if new_pw:
                old_pw = self.os_core.config.get("password")
                user_info = data.get("users", {}).get(old_pw, {"role": "ADMIN", "color": "#00d9ff", "name": "ADMIN"})
                if old_pw in data["users"]: data["users"].pop(old_pw)
                if new_user: user_info["name"] = new_user
                if new_color: user_info["color"] = new_color
                data["users"][new_pw] = user_info
                self.os_core.config.update({"password": new_pw, "user_name": new_user, "accent_color": new_color})

            if new_mode:
                if "system_info" not in data: data["system_info"] = {}
                data["system_info"]["mode"] = new_mode

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("SYNC", "System state updated.")
            self.show_main_menu()
        except Exception as e:
            messagebox.showerror("ERROR", f"Save failed: {e}")