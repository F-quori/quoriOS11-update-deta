import tkinter as tk
from tkinter import messagebox
import os

def run(master, os_core, target_file=None):
    """
    Quori OS エントリーポイント
    target_file: explorer等から渡されるファイル名
    """
    win = tk.Toplevel(master)
    win.title("texteditor.qoa")
    win.geometry("800x600")
    win.configure(bg="black")
    
    # OS側からアクセントカラーを取得
    acc = os_core.config.get("accent_color", "#00d9ff")
    app = QuoriTextEditor(win, os_core, acc, target_file)

class QuoriTextEditor:
    def __init__(self, root, os_core, acc, target_file):
        self.root = root
        self.os_core = os_core
        self.acc = acc
        self.current_file = None
        
        # app/deta をデフォルト保存先に
        self.target_dir = os.path.join(os.path.dirname(__file__), "deta")
        
        self.create_widgets()
        
        if target_file:
            self.load_file(target_file)

    def create_widgets(self):
        # ツールバー
        self.toolbar = tk.Frame(self.root, bg="#0a0a0a", height=35)
        self.toolbar.pack(fill="x", side="top")

        # ファイル名表示
        self.file_label = tk.Label(self.toolbar, text="NEW_FILE.qtf", fg=self.acc, bg="#0a0a0a", font=("Consolas", 10))
        self.file_label.pack(side="left", padx=15)

        # テキストエリア
        self.text_area = tk.Text(self.root, bg="black", fg="white", insertbackground=self.acc,
                                 font=("Consolas", 13), relief="flat", padx=15, pady=15,
                                 undo=True)
        self.text_area.pack(expand=True, fill="both")

        # ステータスバー兼ボタンエリア
        self.footer = tk.Frame(self.root, bg="#050505", height=30)
        self.footer.pack(fill="x", side="bottom")

        # 操作ボタン
        btn_style = {"bg": "black", "fg": self.acc, "relief": "flat", "font": ("Consolas", 9), "padx": 10}
        
        tk.Button(self.footer, text="[ SAVE ]", command=self.save_file, **btn_style).pack(side="left")
        tk.Button(self.footer, text="[ CLEAR ]", command=lambda: self.text_area.delete(1.0, tk.END), **btn_style).pack(side="left")
        tk.Button(self.footer, text="[ EXIT ]", command=self.root.destroy, **btn_style).pack(side="right")

    def load_file(self, filename):
        # アイコン記号などを除去して純粋なファイルパスを作成
        clean_name = filename.replace("📄 ", "").replace("📁 ", "").strip()
        path = os.path.join(self.target_dir, clean_name)
        
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, content)
                self.current_file = clean_name
                self.file_label.config(text=clean_name)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def save_file(self):
        if not self.current_file:
            # 新規ファイルの場合の簡易的な名前入力
            from tkinter import simpledialog
            name = simpledialog.askstring("Quori OS", "Enter filename (e.g. note.qtf):")
            if not name: return
            self.current_file = name if name.endswith(".qtf") else name + ".qtf"

        path = os.path.join(self.target_dir, self.current_file)
        try:
            content = self.text_area.get(1.0, tk.END)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content.strip())
            self.file_label.config(text=self.current_file)
            messagebox.showinfo("Success", f"File saved: {self.current_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")
