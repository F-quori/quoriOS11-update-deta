import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import time
import os

# tkcalendar は標準ライブラリではないため、インストールされていない場合を考慮
try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = None

def run(master, os_core):
    """Quori OSからの起動エントリーポイント"""
    win = tk.Toplevel(master)
    win.title("clock.qoa - Quori Multi-Clock")
    win.geometry("650x550")
    win.configure(bg="black")
    
    # 既存のOSインスタンスから設定を継承
    app = QuoriClockApp(win, os_core)

class QuoriClockApp:
    def __init__(self, root, os_core):
        self.root = root
        self.os_core = os_core
        self.acc = os_core.config.get("accent_color", "#00d9ff")
        
        # 保存ファイルのパス (appフォルダ内に作成)
        self.schedule_file = os.path.join(os.path.dirname(__file__), "clock_data.qtf")
        
        # 内部変数
        self.alarm_time = None
        self.timer_running = False
        self.timer_seconds = 0.0
        self.stopwatch_running = False
        self.stopwatch_time = 0.0

        self.setup_styles()
        self.create_widgets()
        self.update_time_loop()
        self.load_schedules()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background="black", borderwidth=0)
        style.configure("TNotebook.Tab", background="#111", foreground=self.acc, borderwidth=0, padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "black")], foreground=[("selected", self.acc)])
        style.configure("TFrame", background="black")

    def create_widgets(self):
        self.tabs = ttk.Notebook(self.root)
        
        # 各タブの生成
        self.tab_clock = ttk.Frame(self.tabs)
        self.tab_alarm = ttk.Frame(self.tabs)
        self.tab_timer = ttk.Frame(self.tabs)
        self.tab_stopwatch = ttk.Frame(self.tabs)
        self.tab_schedule = ttk.Frame(self.tabs)

        self.tabs.add(self.tab_clock, text=' CLOCK ')
        self.tabs.add(self.tab_alarm, text=' ALARM ')
        self.tabs.add(self.tab_timer, text=' TIMER ')
        self.tabs.add(self.tab_stopwatch, text=' WATCH ')
        self.tabs.add(self.tab_schedule, text=' PLAN ')
        self.tabs.pack(expand=1, fill="both")

        # --- 1. 現在時刻 UI ---
        self.lbl_big_time = tk.Label(self.tab_clock, text="00:00:00", font=("Consolas", 65, "bold"), fg=self.acc, bg="black")
        self.lbl_big_time.pack(expand=True)
        self.lbl_date = tk.Label(self.tab_clock, text="", font=("Consolas", 18), fg="#666", bg="black")
        self.lbl_date.pack(pady=20)

        # --- 2. アラーム UI ---
        tk.Label(self.tab_alarm, text="TARGET TIME (HH:MM:SS)", fg=self.acc, bg="black", font=("Consolas", 12)).pack(pady=30)
        self.ent_alarm = tk.Entry(self.tab_alarm, bg="#0a0a0a", fg=self.acc, insertbackground=self.acc, font=("Consolas", 25), justify="center", relief="flat", highlightthickness=1, highlightbackground="#333")
        self.ent_alarm.pack(pady=10, padx=50, fill="x")
        self.ent_alarm.insert(0, time.strftime("%H:%M:00"))
        tk.Button(self.tab_alarm, text="SET ALARM", command=self.set_alarm, bg=self.acc, fg="black", font=("Consolas", 12, "bold"), relief="flat").pack(pady=20)

        # --- 3. タイマー UI ---
        self.lbl_timer_disp = tk.Label(self.tab_timer, text="0.00", font=("Consolas", 50), fg=self.acc, bg="black")
        self.lbl_timer_disp.pack(pady=30)
        tk.Label(self.tab_timer, text="SECONDS:", fg="#666", bg="black").pack()
        self.ent_timer_input = tk.Entry(self.tab_timer, bg="#0a0a0a", fg=self.acc, justify="center", relief="flat", font=("Consolas", 15))
        self.ent_timer_input.pack(pady=10)
        tk.Button(self.tab_timer, text="START TIMER", command=self.start_timer, bg=self.acc, fg="black", relief="flat").pack(pady=10)

        # --- 4. ストップウォッチ UI ---
        self.lbl_sw_disp = tk.Label(self.tab_stopwatch, text="0.00s", font=("Consolas", 50), fg=self.acc, bg="black")
        self.lbl_sw_disp.pack(pady=40)
        sw_btn_frame = tk.Frame(self.tab_stopwatch, bg="black")
        sw_btn_frame.pack()
        tk.Button(sw_btn_frame, text="START", command=self.start_sw, bg=self.acc, fg="black", width=10).pack(side="left", padx=5)
        tk.Button(sw_btn_frame, text="STOP", command=self.stop_sw, bg="#ff0055", fg="white", width=10).pack(side="left", padx=5)
        tk.Button(sw_btn_frame, text="RESET", command=self.reset_sw, bg="#333", fg="white", width=10).pack(side="left", padx=5)

        # --- 5. スケジュール UI ---
        sch_frame = tk.Frame(self.tab_schedule, bg="black")
        sch_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        if DateEntry:
            self.cal = DateEntry(sch_frame, background=self.acc, foreground='black', borderwidth=0)
            self.cal.pack(fill="x", pady=5)
        else:
            tk.Label(sch_frame, text="(DateEntry not installed)", fg="red", bg="black").pack()

        self.ent_sch_event = tk.Entry(sch_frame, bg="#0a0a0a", fg="white", insertbackground=self.acc, font=("Consolas", 12))
        self.ent_sch_event.pack(fill="x", pady=5)
        self.ent_sch_event.insert(0, "Event description...")

        tk.Button(sch_frame, text="REGISTER PLAN", command=self.save_schedule, bg=self.acc, fg="black", relief="flat").pack(fill="x", pady=5)
        self.list_sch = tk.Listbox(sch_frame, bg="#050505", fg=self.acc, borderwidth=0, highlightthickness=1, highlightbackground="#222", font=("Consolas", 10))
        self.list_sch.pack(fill="both", expand=True, pady=10)
        tk.Button(sch_frame, text="DELETE SELECTED", command=self.delete_schedule, bg="#333", fg="white", relief="flat").pack(fill="x")

    # --- ロジック部 ---
    def update_time_loop(self):
        now = datetime.datetime.now()
        cur_t = now.strftime("%H:%M:%S")
        self.lbl_big_time.config(text=cur_t)
        self.lbl_date.config(text=now.strftime("%Y / %m / %d (%a)"))
        
        if self.alarm_time == cur_t:
            self.trigger_alarm()
            
        if self.root.winfo_exists():
            self.root.after(1000, self.update_time_loop)

    def set_alarm(self):
        self.alarm_time = self.ent_alarm.get()
        messagebox.showinfo("Quori OS", f"Alarm enabled: {self.alarm_time}")

    def trigger_alarm(self):
        messagebox.showwarning("SECURITY ALERT", "ALARM: REACHED DESIGNATED TIME")
        self.alarm_time = None

    def start_timer(self):
        try:
            self.timer_seconds = float(self.ent_timer_input.get())
            self.timer_running = True
            self.run_timer_tick()
        except ValueError:
            messagebox.showerror("Error", "Invalid time input")

    def run_timer_tick(self):
        if self.timer_running and self.timer_seconds > 0:
            self.timer_seconds -= 0.1
            self.lbl_timer_disp.config(text=f"{max(0, self.timer_seconds):.1f}")
            self.root.after(100, self.run_timer_tick)
        elif self.timer_seconds <= 0 and self.timer_running:
            self.timer_running = False
            messagebox.showinfo("Timer", "Countdown finished")

    def start_sw(self):
        if not self.stopwatch_running:
            self.stopwatch_running = True
            self.update_sw_tick()

    def stop_sw(self): self.stopwatch_running = False

    def reset_sw(self):
        self.stopwatch_running = False
        self.stopwatch_time = 0.0
        self.lbl_sw_disp.config(text="0.00s")

    def update_sw_tick(self):
        if self.stopwatch_running:
            self.stopwatch_time += 0.05
            self.lbl_sw_disp.config(text=f"{self.stopwatch_time:.2f}s")
            self.root.after(50, self.update_sw_tick)

    def save_schedule(self):
        date = self.cal.get() if DateEntry else "Unknown"
        event = self.ent_sch_event.get()
        if event:
            with open(self.schedule_file, "a", encoding="utf-8") as f:
                f.write(f"[{date}] {event}\n")
            self.ent_sch_event.delete(0, tk.END)
            self.load_schedules()

    def load_schedules(self):
        self.list_sch.delete(0, tk.END)
        if os.path.exists(self.schedule_file):
            with open(self.schedule_file, "r", encoding="utf-8") as f:
                for line in f:
                    self.list_sch.insert(tk.END, line.strip())

    def delete_schedule(self):
        sel = self.list_sch.curselection()
        if sel:
            idx = sel[0]
            lines = []
            if os.path.exists(self.schedule_file):
                with open(self.schedule_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                del lines[idx]
                with open(self.schedule_file, "w", encoding="utf-8") as f:
                    f.writelines(lines)
            self.load_schedules()