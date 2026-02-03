import tkinter as tk
from tkinter import messagebox, filedialog, font
from PIL import Image, ImageTk
import os
import sys
import json
import importlib
import importlib.util
import winreg
import subprocess
import time
import datetime
import ctypes
import threading

# =============================================================================
# [QCP-PRO] ADVANCED TERMINAL SUBSYSTEM - VERSION 3.0.5
# =============================================================================

def run(root, os_core):
    """
    KERNEL ENTRY POINT:
    boost.py の invoke_app から呼び出される際、この関数が実行されます。
    """
    try:
        # 既存のQCPが多重起動しないようチェック（任意）
        terminal_app = QuoriCommandPrompt(root, os_core)
    except Exception as e:
        error_msg = f"QCP_BOOT_ERR: {str(e)}"
        if hasattr(os_core, "write_log"):
            os_core.write_log(error_msg)
        print(error_msg)

class QuoriCommandPrompt:
    """
    Quori Command Prompt (QCP)
    Kernelとの通信を最適化し、ホストOSブリッジ機能を有するプロフェッショナル・ターミナル。
    """
    def __init__(self, master, os_core):
        # ---------------------------------------------------------------------
        # 1. CORE LINKING
        # ---------------------------------------------------------------------
        self.os_core = os_core
        self.win = tk.Toplevel(master)
        
        # Kernelのプロパティを安全に取得
        self.config = getattr(self.os_core, "config", {})
        self.version = self.config.get("version", "2.9.Quori10")
        self.acc_color = self.config.get("accent_color", "#00d9ff")
        self.user_name = self.config.get("user_name", "QUORI-ADMIN")
        
        # 内部変数
        self.current_dir = os.getcwd()
        self.command_history = []
        self.start_timestamp = time.time()
        
        # ---------------------------------------------------------------------
        # 2. WINDOW ARCHITECTURE (デザイン維持)
        # ---------------------------------------------------------------------
        self.win.title(f"Quori Terminal Professional - {self.version}")
        self.win.geometry("1100x750")
        self.win.configure(bg="#020202")
        self.win.attributes("-topmost", True)
        
        # UIセットアップ
        self.setup_ui_components()
        
        # ---------------------------------------------------------------------
        # 3. KERNEL SYNC & DIAGNOSTICS
        # ---------------------------------------------------------------------
        self.execute_boot_diagnostics()

    def setup_ui_components(self):
        """スキャナブルで高密度なUI構築"""
        try:
            self.main_font = font.Font(family="Consolas", size=12)
            self.bold_font = font.Font(family="Consolas", size=12, weight="bold")
        except:
            self.main_font = ("monospace", 12)
            self.bold_font = ("monospace", 12, "bold")

        self.main_frame = tk.Frame(self.win, bg="#020202")
        self.main_frame.pack(fill="both", expand=True)

        # テキストエリア
        self.text_area = tk.Text(
            self.main_frame, 
            bg="#020202", 
            fg="#e0e0e0", 
            insertbackground=self.acc_color,
            font=self.main_font,
            relief="flat",
            padx=25,
            pady=25,
            undo=True
        )
        self.text_area.pack(side="left", fill="both", expand=True)

        self.scroll_bar = tk.Scrollbar(self.main_frame, bg="#111")
        self.scroll_bar.pack(side="right", fill="y")
        self.text_area.config(yscrollcommand=self.scroll_bar.set)
        self.scroll_bar.config(command=self.text_area.yview)

        # イベントバインド
        self.text_area.bind("<Return>", self.handle_input_event)
        self.text_area.bind("<BackSpace>", self.enforce_prompt_protection)
        self.text_area.focus_set()

    def write_out(self, text, color="#dcdcdc", is_bold=False):
        """ターミナルへの標準出力"""
        tag_key = f"color_{color}_bold_{is_bold}"
        if is_bold:
            self.text_area.tag_configure(tag_key, foreground=color, font=self.bold_font)
        else:
            self.text_area.tag_configure(tag_key, foreground=color, font=self.main_font)
            
        self.text_area.insert(tk.END, text, tag_key)
        self.text_area.see(tk.END)

    def execute_boot_diagnostics(self):
        """起動時のシステムスキャン演出 (WinReg, CTypes活用)"""
        boot_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.write_out(">> QUORI TERMINAL SUBSYSTEM INITIALIZING...\n", self.acc_color, True)
        self.write_out(f"[*] Boot Time: {boot_time}\n")
        self.write_out(f"[*] Connected to Kernel: {self.version}\n")
        
        # ホストOS特定 (winreg)
        try:
            h_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
            prod_name = winreg.QueryValueEx(h_key, "ProductName")[0]
            winreg.CloseKey(h_key)
            self.write_out(f"[*] Host OS: {prod_name}\n")
        except: pass

        # メモリ負荷取得 (ctypes)
        try:
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), 
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("sullAvailExtendedVirtual", ctypes.c_ulonglong)]
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(stat)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            self.write_out(f"[*] System Memory Load: {stat.dwMemoryLoad}%\n")
        except: pass

        self.write_out("-" * 60 + "\n")
        self.write_out("Ready for commands. Type 'help' for assistance.\n\n")
        self.refresh_prompt_display()

    def refresh_prompt_display(self):
        prompt = f"Q:{self.current_dir}> "
        self.write_out(prompt, self.acc_color, True)
        self.text_area.mark_set("input_start", "insert")

    def enforce_prompt_protection(self, event):
        if self.text_area.index("insert") == self.text_area.index("input_start"):
            return "break"

    def handle_input_event(self, event):
        raw_input = self.text_area.get("input_start", "insert").strip()
        self.write_out("\n")
        
        if raw_input:
            self.command_history.append(raw_input)
            self.route_command(raw_input)
        else:
            self.refresh_prompt_display()
        return "break"

    def route_command(self, cmd_line):
        """コマンド解析とKernelへのリレー"""
        cmd_lower = cmd_line.lower()

        # 1. Windows Bridge
        if cmd_line.upper().startswith("WIN:"):
            target = cmd_line[4:].strip()
            threading.Thread(target=self.execute_host_shell, args=(target,), daemon=True).start()
            return

        # 2. Kernel App Launch (qoa !m)
        elif cmd_lower.startswith("qoa "):
            self.handle_qoa_logic(cmd_line)

        # 3. File System
        elif cmd_lower in ["ls", "dir"]:
            self.list_directory()
        elif cmd_lower.startswith("cd "):
            self.change_directory(cmd_line[3:].strip())

        # 4. Utilities
        elif cmd_lower == "help":
            self.display_help()
        elif cmd_lower in ["cls", "clear"]:
            self.text_area.delete("1.0", tk.END)
            self.refresh_prompt_display()
            return
        elif cmd_lower == "exit":
            self.win.destroy()
            return
        else:
            self.write_out(f"Command '{cmd_line}' not found.\n", "red")

        self.refresh_prompt_display()

    def execute_host_shell(self, shell_cmd):
        """[Threading/Subprocess] Windowsコマンド実行"""
        try:
            res = subprocess.run(shell_cmd, shell=True, capture_output=True, text=True, cwd=self.current_dir)
            if res.stdout: self.win.after(0, lambda: self.write_out(res.stdout))
            if res.stderr: self.win.after(0, lambda: self.write_out(res.stderr, "red"))
        except Exception as e:
            self.win.after(0, lambda: self.write_out(f"Shell Error: {e}\n", "red"))
        self.win.after(0, self.refresh_prompt_display)

    def handle_qoa_logic(self, raw_input):
        """Kernelの invoke_app を呼び出す"""
        tokens = raw_input.split()
        if len(tokens) >= 3 and tokens[1] == "!m":
            module_name = tokens[2]
            # Kernel側のメソッド存在確認
            if hasattr(self.os_core, "invoke_app"):
                self.os_core.invoke_app(module_name)
                self.write_out(f"Relaying launch request for {module_name} to Kernel...\n")
            else:
                self.write_out("Kernel Error: invoke_app method not found.\n", "red")
        else:
            self.write_out("Usage: qoa !m <app_name>\n", "orange")

    def list_directory(self):
        try:
            files = os.listdir(self.current_dir)
            self.write_out(f"\n Index of {self.current_dir}:\n", self.acc_color)
            for f in files:
                prefix = "<DIR>" if os.path.isdir(os.path.join(self.current_dir, f)) else "     "
                self.write_out(f" {prefix}  {f}\n")
            self.write_out("\n")
        except Exception as e:
            self.write_out(f"Access Denied: {e}\n", "red")

    def change_directory(self, path):
        try:
            new_path = os.path.abspath(os.path.join(self.current_dir, path))
            if os.path.isdir(new_path):
                self.current_dir = new_path
                os.chdir(new_path)
            else: self.write_out("Path not found.\n", "red")
        except Exception as e: self.write_out(f"CD Error: {e}\n", "red")

    def display_help(self):
        help_text = """
--- Quori Command Prompt Help ---
 qoa !m <app>   : Launch system module
 ls / dir       : List directory contents
 cd <path>      : Change working directory
 cls / clear    : Clear screen
 WIN:<cmd>      : Direct Windows shell access
 exit           : Close terminal
"""
        self.write_out(help_text, "#ffffff")

# --- END OF QCP SOURCE ---