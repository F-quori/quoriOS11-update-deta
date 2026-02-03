import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import os
import datetime

def run(master, os_core):
    """Quori OS エントリーポイント"""
    win = tk.Toplevel(master)
    win.title("explorer.qoa")
    win.geometry("900x600")
    win.configure(bg="black")
    
    acc = os_core.config.get("accent_color", "#00d9ff")
    target_dir = os.path.join(os.path.dirname(__file__), "deta")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # --- UIデザイン ---
    header = tk.Frame(win, bg="#050505", height=45)
    header.pack(fill="x")
    
    tk.Label(header, text=f" SOURCE: {target_dir}", fg=acc, bg="#050505", font=("Consolas", 9)).pack(side="left", padx=10)

    # --- Treeview (ファイルリスト) ---
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background="black", foreground=acc, fieldbackground="black", rowheight=30, borderwidth=0, font=("Consolas", 11))
    style.configure("Treeview.Heading", background="#111", foreground=acc, borderwidth=0)
    style.map("Treeview", background=[('selected', acc)], foreground=[('selected', 'black')])

    tree = ttk.Treeview(win, columns=("Size", "Date"), selectmode="browse")
    tree.heading("#0", text=" FILE NAME", anchor="w")
    tree.heading("Size", text=" SIZE", anchor="w")
    tree.heading("Date", text=" MODIFIED", anchor="w")
    tree.pack(expand=True, fill="both", padx=20, pady=10)

    status_var = tk.StringVar(value="SYSTEM READY")
    footer = tk.Frame(win, bg="#050505", height=30)
    footer.pack(fill="x", side="bottom")
    tk.Label(footer, textvariable=status_var, fg="#555", bg="#050505", font=("Consolas", 9)).pack(side="right", padx=10)

    # --- ロジック ---
    def refresh():
        for i in tree.get_children(): tree.delete(i)
        try:
            for f in os.listdir(target_dir):
                f_path = os.path.join(target_dir, f)
                f_size = f"{os.path.getsize(f_path) / 1024:.1f} KB"
                f_mtime = datetime.datetime.fromtimestamp(os.path.getmtime(f_path)).strftime('%Y-%m-%d %H:%M')
                
                if f.endswith(".qs"): prefix = "⚡ "
                elif os.path.isfile(f_path): prefix = "📄 "
                else: prefix = "📁 "
                tree.insert("", "end", text=f"{prefix}{f}", values=(f_size, f_mtime))
        except Exception as e:
            status_var.set(f"ERROR: {str(e)}")

    def create_new_file():
        """新規ファイル作成ダイアログ"""
        filename = simpledialog.askstring("QUORI OS", "Enter Filename (e.g. note.qtf / app.qs):", parent=win)
        if filename:
            path = os.path.join(target_dir, filename)
            if os.path.exists(path):
                messagebox.showwarning("Warning", "File already exists.")
                return
            try:
                # 空のファイルを作成
                with open(path, "w", encoding="utf-8") as f:
                    f.write("")
                status_var.set(f"CREATED: {filename}")
                refresh()
                # 作成後、即座にエディタで開く
                if not filename.endswith(".qs"):
                    os_core.launch_app("texteditor", target_file=filename)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create file: {e}")

    def on_double_click(event):
        selected = tree.selection()
        if not selected: return
        raw_name = tree.item(selected[0])['text']
        clean_name = raw_name[2:].strip()
        path = os.path.join(target_dir, clean_name)

        if os.path.isfile(path):
            if clean_name.endswith(".qs"):
                with open(path, "r", encoding="utf-8") as f:
                    app_to_launch = f.read().strip()
                os_core.launch_app(app_to_launch)
            else:
                os_core.launch_app("texteditor", target_file=clean_name)

    # --- 操作ボタン群 ---
    btn_style = {"bg": acc, "fg": "black", "relief": "flat", "font": ("Consolas", 9, "bold"), "padx": 10}
    
    tk.Button(header, text=" + NEW FILE ", command=create_new_file, **btn_style).pack(side="left", padx=5, pady=5)
    tk.Button(header, text=" RE-SCAN ", command=refresh, bg="#333", fg="white", relief="flat", font=("Consolas", 8), padx=10).pack(side="right", padx=10, pady=5)

    tree.bind("<Double-1>", on_double_click)
    refresh()