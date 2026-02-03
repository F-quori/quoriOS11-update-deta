import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, ttk
from PIL import Image, ImageDraw
import os
import json

# =============================================================================
# [1] PATH & DATA ARCHITECTURE
# =============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "app", "deta")
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

def run(root, os_core):
    QPaintApp(root, os_core)

class QPaintApp:
    def __init__(self, master, os_core):
        self.os_core = os_core
        self.win = tk.Toplevel(master)
        self.win.title("Q-PAINT v1.0 - Cyberpunk Edition")
        self.win.geometry("1100x750")
        self.win.configure(bg="#0a0a0a")
        self.win.attributes("-topmost", True)

        # --- DRAWING STATES ---
        self.color = "#00d9ff"
        self.thickness = 5
        self.zoom = 1.0
        self.objects = [] # SVG用: [{"type":"line", "coords":(x1,y1,x2,y2), "color":"#", "width":w}, ...]
        self.last_x, self.last_y = None, None

        self._setup_ui()

    def _setup_ui(self):
        # ツールバー (左サイド)
        self.sidebar = tk.Frame(self.win, bg="#111", width=220)
        self.sidebar.pack(side="left", fill="y", padx=5, pady=5)

        tk.Label(self.sidebar, text="Q-PAINT PRO", fg="#00d9ff", bg="#111", font=("Consolas", 14, "bold")).pack(pady=20)

        # RGB カラーピッカー
        tk.Button(self.sidebar, text="🎨 PICK RGB COLOR", command=self._pick_color, bg="#222", fg="white", relief="flat").pack(fill="x", padx=20, pady=5)
        self.color_preview = tk.Frame(self.sidebar, bg=self.color, height=30)
        self.color_preview.pack(fill="x", padx=20, pady=5)

        # 太さ 50段階スライダー
        tk.Label(self.sidebar, text="BRUSH THICKNESS (1-50)", fg="white", bg="#111", font=("Consolas", 9)).pack(pady=10)
        self.thick_scale = ttk.Scale(self.sidebar, from_=1, to=50, orient="horizontal", command=self._update_thick)
        self.thick_scale.set(self.thickness)
        self.thick_scale.pack(fill="x", padx=20)
        self.thick_label = tk.Label(self.sidebar, text=f"{self.thickness} px", fg="#888", bg="#111")
        self.thick_label.pack()

        # ズーム 10%-500%
        tk.Label(self.sidebar, text="ZOOM (10%-500%)", fg="white", bg="#111", font=("Consolas", 9)).pack(pady=10)
        self.zoom_scale = ttk.Scale(self.sidebar, from_=0.1, to=5.0, orient="horizontal", command=self._update_zoom)
        self.zoom_scale.set(1.0)
        self.zoom_scale.pack(fill="x", padx=20)

        # 保存セクション
        tk.Frame(self.sidebar, bg="#333", height=1).pack(fill="x", pady=20)
        tk.Button(self.sidebar, text="💾 SAVE AS SVG (VECTOR)", command=self.save_svg, bg="#005577", fg="white", relief="flat").pack(fill="x", padx=20, pady=5)
        tk.Button(self.sidebar, text="📷 EXPORT AS PNG", command=self.export_png, bg="#007744", fg="white", relief="flat").pack(fill="x", padx=20, pady=5)
        tk.Button(self.sidebar, text="🗑️ CLEAR ALL", command=self.clear_canvas, bg="#770022", fg="white", relief="flat").pack(fill="x", padx=20, pady=5)

        # キャンバスエリア
        self.canvas_frame = tk.Frame(self.win, bg="#1a1a1a", bd=2, relief="sunken")
        self.canvas_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", width=800, height=600, cursor="cross")
        self.canvas.pack(expand=True)

        # マウスイベントのバインド (Scratchの「マウスが押された」＆「動いた」に相当)
        self.canvas.bind("<Button-1>", self._start_draw)
        self.canvas.bind("<B1-Motion>", self._draw)
        self.canvas.bind("<ButtonRelease-1>", self._stop_draw)

    # --- LOGIC ---

    def _pick_color(self):
        color = colorchooser.askcolor(title="Select RGB Color")[1]
        if color:
            self.color = color
            self.color_preview.config(bg=self.color)

    def _update_thick(self, e):
        self.thickness = int(float(e))
        self.thick_label.config(text=f"{self.thickness} px")

    def _update_zoom(self, e):
        self.zoom = float(e)
        # 簡易ズーム: キャンバスのスケールを変更
        self.canvas.config(width=800*self.zoom, height=600*self.zoom)

    def _start_draw(self, e):
        self.last_x, self.last_y = e.x, e.y

    def _draw(self, e):
        if self.last_x and self.last_y:
            # 描画 (Canvas上)
            self.canvas.create_line(self.last_x, self.last_y, e.x, e.y, 
                                     fill=self.color, width=self.thickness * self.zoom, 
                                     capstyle=tk.ROUND, smooth=True)
            
            # データ保存 (SVG用) - Scratchの「リストに座標を入れる」と同じ！
            self.objects.append({
                "type": "line",
                "coords": (self.last_x/self.zoom, self.last_y/self.zoom, e.x/self.zoom, e.y/self.zoom),
                "color": self.color,
                "width": self.thickness
            })
            self.last_x, self.last_y = e.x, e.y

    def _stop_draw(self, e):
        self.last_x, self.last_y = None, None

    def clear_canvas(self):
        if messagebox.askyesno("Confirm", "Clear everything?"):
            self.canvas.delete("all")
            self.objects = []

    # --- SAVE ENGINE ---

    def save_svg(self):
        """ベクター形式(SVG)で保存。XML構造を生成します。"""
        path = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("SVG files", "*.svg")])
        if not path: return
        
        with open(path, "w") as f:
            f.write(f'<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">\n')
            f.write(f'  <rect width="100%" height="100%" fill="white"/>\n')
            for obj in self.objects:
                x1, y1, x2, y2 = obj["coords"]
                f.write(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                        f'stroke="{obj["color"]}" stroke-width="{obj["width"]}" stroke-linecap="round" />\n')
            f.write('</svg>')
        messagebox.showinfo("Success", "SVG Project Saved.")

    def export_png(self):
        """PILを使用してラスタライズ(PNG)保存。"""
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if not path: return
        
        # 新しい白い画像を作成
        img = Image.new("RGB", (800, 600), "white")
        draw = ImageDraw.Draw(img)
        
        for obj in self.objects:
            draw.line(obj["coords"], fill=obj["color"], width=obj["width"])
        
        img.save(path)
        messagebox.showinfo("Success", "PNG Exported.")
