import tkinter as tk
from tkinter import messagebox
import os
import urllib.request
import ssl

def run(main_root, os_core):
    """Kernelから呼び出されるエントリーポイント"""
    AppStore(main_root, os_core)

class AppStore:
    def __init__(self, master, os_core):
        self.os_core = os_core
        self.win = tk.Toplevel(master)
        self.win.title("QUORI GLOBAL APP STORE")
        self.win.geometry("750x650")
        self.win.configure(bg="#050505")
        self.win.attributes("-topmost", True)
        
        self.acc = self.os_core.config.get("accent_color", "#00d9ff")
        
        # --- ダウンロード先の絶対パスを確定 ---
        # あなたの環境に合わせて C:\project-quoriOS\app を確実にターゲットにします
        self.target_dir = os.path.dirname(os.path.abspath(__file__))
        
        # UI構築
        header = tk.Frame(self.win, bg="#111", height=100)
        header.pack(fill="x")
        tk.Label(header, text="CLOUD INHALE SYSTEM", fg=self.acc, bg="#111", font=("Consolas", 18, "bold")).pack(pady=(20, 0))
        tk.Label(header, text=f"DESTINATION: {self.target_dir}", fg="#444", bg="#111", font=("Consolas", 8)).pack()

        inhale_container = tk.Frame(self.win, bg="#0a0a0a", pady=25)
        inhale_container.pack(fill="x", padx=40, pady=20)
        
        tk.Label(inhale_container, text="GITHUB RAW URL:", fg=self.acc, bg="#0a0a0a", font=("Consolas", 10, "bold")).pack(anchor="w", padx=15)
        self.url_field = tk.Entry(inhale_container, bg="#111", fg="white", insertbackground=self.acc, relief="flat", font=("Consolas", 11))
        self.url_field.pack(fill="x", padx=15, pady=10, ipady=7)
        
        tk.Button(inhale_container, text=" EXECUTE INHALE ", bg=self.acc, fg="black", font=("Consolas", 10, "bold"), 
                  relief="flat", pady=10, command=self.process_remote_download).pack(fill="x", padx=15, pady=5)

    def process_remote_download(self):
        """リモートURLからソースを吸引し、appフォルダへ直接保存する"""
        target_url = self.url_field.get().strip()
        if not target_url:
            messagebox.showwarning("WARNING", "URL field is empty.")
            return

        # ファイル名のクリーンアップ
        filename = target_url.split("/")[-1].split("?")[0]
        if not filename.endswith(".py"):
            filename += ".py"
            
        # 保存先のフルパスを作成
        save_path = os.path.join(self.target_dir, filename)

        try:
            # ネットワーク接続
            ssl_ctx = ssl._create_unverified_context()
            with urllib.request.urlopen(target_url, context=ssl_ctx, timeout=10) as response:
                if response.status != 200:
                    raise Exception(f"HTTP Error: {response.status}")
                code_content = response.read().decode('utf-8')

            # 物理ファイル書き込み
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(code_content)
            
            # Kernelのタスクバー更新メソッドを叩く
            if hasattr(self.os_core, 'refresh_taskbar_apps'):
                self.os_core.refresh_taskbar_apps()
                messagebox.showinfo("SUCCESS", f"Inhaled: {filename}\nPath: {save_path}")
            else:
                messagebox.showwarning("SYNC ERROR", "File saved but Kernel refresh failed.")
                
            self.url_field.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("INHALE FAILED", f"Error details:\n{str(e)}")

# --- カタログ部分は省略（GitHubからのダウンロードを優先） ---