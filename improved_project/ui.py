import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font as tkfont
from datetime import datetime

from simulator import Simulator
from src.device import Mode
from src.patient import Rhythm
from server import SimulatorHTTPServer

# ── colour palette ────────────────────────────────────────────────────────────
BG          = "#070b10"
PANEL       = "#0d1520"
CARD        = "#111e2d"
BORDER      = "#1a2d42"
TEXT        = "#c8d8e8"
DIM         = "#5a7080"
ACCENT      = "#00bfff"       # cyan-blue – primary interactive
GREEN       = "#00e676"       # normal / ok
YELLOW      = "#ffb300"       # warning
RED         = "#ff1744"       # critical
WHITE       = "#ffffff"

# ── alarm visual config ───────────────────────────────────────────────────────
ALARM_CFG = {
    "NORMAL":   dict(bg="#0b1c10", border="#00e676", icon="●", icon_fg=GREEN,  title_fg=GREEN,  label="ALL CLEAR"),
    "WARNING":  dict(bg="#1c1500", border="#ffb300", icon="▲", icon_fg=YELLOW, title_fg=YELLOW, label="WARNING"),
    "CRITICAL": dict(bg="#1c0005", border="#ff1744", icon="✦", icon_fg=RED,    title_fg=RED,    label="CRITICAL ALERT"),
}

RHYTHM_LABELS = {
    "Normal Sinus":              ("NS",  GREEN),
    "Ventricular Fibrillation":  ("VF",  RED),
    "Ventricular Tachycardia":   ("VT",  RED),
    "SVT":                       ("SVT", YELLOW),
    "Bradycardia":               ("BRD", YELLOW),
    "Tachycardia":               ("TCH", YELLOW),
    "PEA":                       ("PEA", RED),
    "Asystole":                  ("ASY", RED),
}

ENERGY_LEVELS = [50, 100, 150, 200, 300, 360]


class DefibrillatorApp:
    def __init__(self, root, port=None):
        self.root = root
        self.root.title("MED-CRT  ·  DEFIBRILLATOR SIMULATOR")
        self.root.geometry("1420x920")
        self.root.minsize(1200, 800)
        self.root.configure(bg=BG)

        self.simulator = Simulator()
        self.server = None
        self.port = port or int(os.getenv("SIM_PORT", "8000"))
        self.last_alert_level = None
        self.waveform_samples = []
        self._pulse_state = False
        self._pulse_job = None

        self.virtual_host_var = tk.StringVar(value="0.0.0.0")
        self.virtual_port_var = tk.StringVar(value="9000")
        self.virtual_interval_var = tk.StringVar(value="1.0")
        self.virtual_status_var = tk.StringVar(value="Disconnected")
        self.virtual_tx_var = tk.StringVar(value="● Idle")
        self.virtual_bytes_var = tk.StringVar(value="Bytes sent: 0")
        self.virtual_spo2_var = tk.StringVar(value="98")
        self.virtual_pulse_var = tk.StringVar(value="72")
        self.virtual_perf_var = tk.StringVar(value="1.8")
        self.virtual_signal_var = tk.StringVar(value="95")
        self.virtual_alarm_var = tk.StringVar(value="OK")

        self.rhythm_values = [r.value for r in Rhythm]
        self.mode_values = [m.value for m in Mode]
        self.rhythm_map = {r.value: r for r in Rhythm}
        self.mode_map = {m.value: m for m in Mode}

        self._setup_styles()
        self._build_ui()
        self._start_api_server()
        self._refresh_display()
        self._tick()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── fonts ─────────────────────────────────────────────────────────────────
    def _f(self, size, weight="normal"):
        for fam in ("Consolas", "Courier New", "Courier", "TkFixedFont"):
            try:
                return tkfont.Font(family=fam, size=size, weight=weight)
            except tk.TclError:
                pass
        return tkfont.Font(size=size, weight=weight)

    # ── ttk styles ────────────────────────────────────────────────────────────
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
                        fieldbackground=CARD, background=CARD,
                        foreground=TEXT, selectbackground=BORDER,
                        selectforeground=WHITE, bordercolor=BORDER,
                        lightcolor=BORDER, darkcolor=BORDER,
                        arrowcolor=ACCENT, relief="flat")
        style.map("TCombobox",
                  fieldbackground=[("readonly", CARD)],
                  foreground=[("readonly", TEXT)])
        style.configure("Accent.TButton",
                        background=ACCENT, foreground=BG,
                        relief="flat", borderwidth=0, padding=(10, 6))
        style.map("Accent.TButton",
                  background=[("active", "#0099cc")])
        style.configure("TProgressbar",
                        troughcolor=PANEL, background=ACCENT,
                        bordercolor=BORDER, relief="flat")

    # ─────────────────────────────────────────────────────────────────────────
    #  BUILD UI
    # ─────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = self.root

        # ── top bar ────────────────────────────────────────────────────────
        topbar = tk.Frame(root, bg=PANEL, height=56)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        tk.Label(topbar, text="MED-CRT", fg=ACCENT, bg=PANEL,
                 font=self._f(16, "bold")).pack(side="left", padx=(18, 6), pady=10)
        tk.Label(topbar, text="DEFIBRILLATOR SIMULATOR", fg=TEXT, bg=PANEL,
                 font=self._f(10)).pack(side="left", pady=10)

        # right-side status pills
        pills = tk.Frame(topbar, bg=PANEL)
        pills.pack(side="right", padx=18)
        self.device_status_var  = tk.StringVar(value="ONLINE")
        self.device_mode_var    = tk.StringVar(value="MANUAL")
        self.connection_var     = tk.StringVar(value="TCP: CONNECTED")
        self._pill(pills, "STATUS", self.device_status_var,  GREEN).pack(side="left", padx=4)
        self._pill(pills, "MODE",   self.device_mode_var,    ACCENT).pack(side="left", padx=4)
        self._pill(pills, "",       self.connection_var,     YELLOW).pack(side="left", padx=4)

        # ── ALARM BANNER ───────────────────────────────────────────────────
        self.alarm_frame = tk.Frame(root, bg=PANEL, height=66)
        self.alarm_frame.pack(fill="x")
        self.alarm_frame.pack_propagate(False)
        self.alarm_frame.configure(highlightbackground=BORDER, highlightthickness=1)

        self.alarm_icon_lbl  = tk.Label(self.alarm_frame, text="●", fg=GREEN, bg=PANEL,
                                        font=self._f(22, "bold"))
        self.alarm_icon_lbl.pack(side="left", padx=(18, 8))

        alarm_text = tk.Frame(self.alarm_frame, bg=PANEL)
        alarm_text.pack(side="left", fill="y", pady=8)
        self.alarm_title_lbl = tk.Label(alarm_text, text="ALL CLEAR", fg=GREEN, bg=PANEL,
                                        font=self._f(13, "bold"))
        self.alarm_title_lbl.pack(anchor="w")
        self.alarm_msg_lbl   = tk.Label(alarm_text, text="System ready for monitoring",
                                        fg=DIM, bg=PANEL, font=self._f(9))
        self.alarm_msg_lbl.pack(anchor="w")

        # right side of banner – rhythm badge + mode tag
        right_meta = tk.Frame(self.alarm_frame, bg=PANEL)
        right_meta.pack(side="right", padx=18)
        self.alarm_rhythm_badge = tk.Label(right_meta, text="NS", fg=BG, bg=GREEN,
                                           font=self._f(13, "bold"), width=4,
                                           relief="flat", padx=6, pady=2)
        self.alarm_rhythm_badge.pack(side="right", padx=(8, 0))
        tk.Label(right_meta, text="RHYTHM", fg=DIM, bg=PANEL,
                 font=self._f(8)).pack(side="right")
        self.alarm_mode_lbl = tk.Label(self.alarm_frame, text="Mode: Manual",
                                       fg=ACCENT, bg=PANEL, font=self._f(9, "bold"))
        self.alarm_mode_lbl.pack(side="right", padx=10)

        # ── main body (left waveform+vitals | right controls) ─────────────
        body = tk.Frame(root, bg=BG)
        body.pack(fill="both", expand=True, padx=12, pady=8)

        left = tk.Frame(body, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        right = tk.Frame(body, bg=BG, width=310)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        # ── ECG panel ──────────────────────────────────────────────────────
        ecg_panel = self._panel(left, "ECG WAVEFORM")
        ecg_panel.pack(fill="x", pady=(0, 8))

        ecg_top = tk.Frame(ecg_panel, bg=CARD)
        ecg_top.pack(fill="x", padx=10, pady=(8, 4))
        tk.Label(ecg_top, text="HEART RATE", fg=DIM, bg=CARD,
                 font=self._f(8)).pack(side="left")
        self.rate_value = tk.Label(ecg_top, text="--", fg=GREEN, bg=CARD,
                                   font=self._f(24, "bold"))
        self.rate_value.pack(side="left", padx=(6, 4))
        tk.Label(ecg_top, text="bpm", fg=DIM, bg=CARD,
                 font=self._f(9)).pack(side="left", pady=6)

        self.waveform_canvas = tk.Canvas(ecg_panel, height=180, bg="#000d1a",
                                         highlightbackground=BORDER,
                                         highlightthickness=1)
        self.waveform_canvas.pack(fill="x", padx=10, pady=(0, 10))

        # ── vital cards ────────────────────────────────────────────────────
        cards_row = tk.Frame(left, bg=BG)
        cards_row.pack(fill="x", pady=(0, 8))
        self.vital_cards = {}
        for col, (label, key, unit) in enumerate([
            ("HR",       "heart_rate", "bpm"),
            ("SpO₂",     "spo2",       "%"),
            ("BP",       "bp",         "mmHg"),
            ("BATTERY",  "battery",    "%"),
        ]):
            self._vital_card(cards_row, label, key, unit, col)
            cards_row.grid_columnconfigure(col, weight=1)

        # ── lower left: device info + event log ───────────────────────────
        lower_left = tk.Frame(left, bg=BG)
        lower_left.pack(fill="both", expand=True)

        dev_panel = self._panel(lower_left, "DEVICE STATUS")
        dev_panel.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self.device_info = scrolledtext.ScrolledText(
            dev_panel, height=10, bg=CARD, fg=TEXT,
            bd=0, font=self._f(9), insertbackground=TEXT)
        self.device_info.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.device_info.configure(state="disabled")

        evt_panel = self._panel(lower_left, "EVENT LOG")
        evt_panel.pack(side="left", fill="both", expand=True)
        self.event_box = scrolledtext.ScrolledText(
            evt_panel, wrap=tk.WORD, height=10, bg=CARD, fg=TEXT,
            bd=0, font=self._f(9), insertbackground=TEXT)
        self.event_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # ── RIGHT COLUMN ───────────────────────────────────────────────────
        self._build_right_column(right)

        # ── footer ─────────────────────────────────────────────────────────
        footer = tk.Frame(root, bg=PANEL)
        footer.pack(fill="x", side="bottom")
        self.api_status_var = tk.StringVar(value="API ready")
        tk.Label(footer, textvariable=self.api_status_var,
                 fg=ACCENT, bg=PANEL, font=self._f(8)).pack(side="left", padx=12, pady=4)
        tk.Label(footer,
                 text="Charge → select energy → Shock when READY  |  Choose rhythm & mode in the right panel",
                 fg=DIM, bg=PANEL, font=self._f(8)).pack(side="right", padx=12)

    # ── right column panels ───────────────────────────────────────────────────
    def _build_right_column(self, right):
        # ── CONTROLS ────────────────────────────────────────────────────────
        ctrl = self._panel(right, "CONTROLS")
        ctrl.pack(fill="x", pady=(0, 8))
        btn_grid = tk.Frame(ctrl, bg=CARD)
        btn_grid.pack(fill="x", padx=10, pady=(0, 10))

        self.charge_btn = self._btn(btn_grid, "⚡  CHARGE",  self.charge_device,   ACCENT)
        self.shock_btn  = self._btn(btn_grid, "⚡  SHOCK",   self.deliver_shock,   RED)
        self.stop_btn   = self._btn(btn_grid, "■  DISARM",   self.disarm_device,   YELLOW)
        self.reset_btn  = self._btn(btn_grid, "↺  RESET BAT",self.recharge_device, DIM)
        self.ecg_btn    = self._btn(btn_grid, "♥  ECG",      self.show_ecg,        ACCENT)
        self.tele_btn   = self._btn(btn_grid, "📡  TELEMETRY",self.send_telemetry,  ACCENT)

        for i, btn in enumerate([self.charge_btn, self.shock_btn,
                                  self.stop_btn,  self.reset_btn,
                                  self.ecg_btn,   self.tele_btn]):
            btn.grid(row=i // 2, column=i % 2, padx=4, pady=4, sticky="ew")
        btn_grid.grid_columnconfigure(0, weight=1)
        btn_grid.grid_columnconfigure(1, weight=1)

        # ── ENERGY SELECTOR ─────────────────────────────────────────────────
        e_panel = self._panel(right, "ENERGY  (Joules)")
        e_panel.pack(fill="x", pady=(0, 8))

        e_inner = tk.Frame(e_panel, bg=CARD)
        e_inner.pack(fill="x", padx=10, pady=(0, 8))

        # Quick-select joule buttons
        quick = tk.Frame(e_inner, bg=CARD)
        quick.pack(fill="x", pady=(0, 6))
        tk.Label(quick, text="Quick select:", fg=DIM, bg=CARD,
                 font=self._f(8)).pack(anchor="w", pady=(0, 4))
        btn_row = tk.Frame(quick, bg=CARD)
        btn_row.pack(fill="x")
        self._energy_btns = {}
        for j in ENERGY_LEVELS:
            b = tk.Button(btn_row, text=str(j), bg=PANEL, fg=TEXT,
                          activebackground=ACCENT, activeforeground=BG,
                          bd=0, relief="flat", padx=0, pady=5,
                          font=self._f(9, "bold"), width=4,
                          command=lambda v=j: self._quick_energy(v))
            b.pack(side="left", padx=2)
            self._energy_btns[j] = b

        # Dropdown + apply
        dd_row = tk.Frame(e_inner, bg=CARD)
        dd_row.pack(fill="x", pady=(0, 4))
        tk.Label(dd_row, text="Or select:", fg=DIM, bg=CARD,
                 font=self._f(8)).pack(side="left", padx=(0, 6))
        self.energy_var = tk.StringVar(value="200")
        energy_combo = ttk.Combobox(dd_row, textvariable=self.energy_var,
                                    values=[str(v) for v in ENERGY_LEVELS],
                                    state="readonly", width=6,
                                    font=self._f(10))
        energy_combo.pack(side="left", padx=(0, 8))
        energy_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_energy())

        self.energy_indicator = tk.Label(e_inner, text="Selected: 200 J",
                                         fg=ACCENT, bg=CARD, font=self._f(10, "bold"))
        self.energy_indicator.pack(anchor="w", pady=(2, 0))

        # Battery bar
        batt_row = tk.Frame(e_inner, bg=CARD)
        batt_row.pack(fill="x", pady=(8, 0))
        tk.Label(batt_row, text="BATTERY", fg=DIM, bg=CARD,
                 font=self._f(8)).pack(anchor="w")
        self.battery_bar = ttk.Progressbar(batt_row, orient="horizontal",
                                            mode="determinate")
        self.battery_bar.pack(fill="x", pady=(2, 0))
        self.battery_lbl = tk.Label(batt_row, text="100 %", fg=GREEN, bg=CARD,
                                    font=self._f(9, "bold"))
        self.battery_lbl.pack(anchor="e")

        # ── RHYTHM SELECTOR ─────────────────────────────────────────────────
        r_panel = self._panel(right, "RHYTHM SELECTOR")
        r_panel.pack(fill="x", pady=(0, 8))
        r_inner = tk.Frame(r_panel, bg=CARD)
        r_inner.pack(fill="x", padx=10, pady=(0, 8))

        tk.Label(r_inner, text="Select rhythm:", fg=DIM, bg=CARD,
                 font=self._f(8)).pack(anchor="w", pady=(0, 4))

        self.rhythm_var = tk.StringVar(value=self.simulator.patient.rhythm.value)
        self.rhythm_combo = ttk.Combobox(r_inner, textvariable=self.rhythm_var,
                                         values=self.rhythm_values,
                                         state="readonly", width=26,
                                         font=self._f(10))
        self.rhythm_combo.pack(fill="x", pady=(0, 6))
        self.rhythm_combo.bind("<<ComboboxSelected>>", lambda e: self.on_rhythm_selected())

        # Quick-rhythm shortcut buttons
        qr = tk.Frame(r_inner, bg=CARD)
        qr.pack(fill="x", pady=(0, 6))
        for abbr, rhythm in (("NS", Rhythm.NORMAL), ("VF", Rhythm.VF),
                              ("VT", Rhythm.VT),    ("ASY", Rhythm.ASYSTOLE)):
            _, col = RHYTHM_LABELS.get(rhythm.value, ("?", ACCENT))
            b = tk.Button(qr, text=abbr, bg=PANEL, fg=col,
                          activebackground=col, activeforeground=BG,
                          bd=0, relief="flat", padx=0, pady=5,
                          font=self._f(9, "bold"), width=5,
                          command=lambda r=rhythm: self.set_rhythm(r))
            b.pack(side="left", padx=2)

        apply_r = tk.Button(r_inner, text="▶  APPLY RHYTHM",
                            bg=ACCENT, fg=BG, activebackground="#0099cc",
                            activeforeground=BG, bd=0, relief="flat",
                            padx=10, pady=7, font=self._f(9, "bold"),
                            command=self.apply_rhythm)
        apply_r.pack(fill="x")

        # ── MODE + CONFIG ────────────────────────────────────────────────────
        m_panel = self._panel(right, "DEVICE MODE")
        m_panel.pack(fill="x", pady=(0, 8))
        m_inner = tk.Frame(m_panel, bg=CARD)
        m_inner.pack(fill="x", padx=10, pady=(0, 8))

        tk.Label(m_inner, text="Operating mode:", fg=DIM, bg=CARD,
                 font=self._f(8)).pack(anchor="w", pady=(0, 4))
        self.mode_var = tk.StringVar(value=self.simulator.device.mode.value)
        self.mode_combo = ttk.Combobox(m_inner, textvariable=self.mode_var,
                                       values=self.mode_values,
                                       state="readonly", width=26,
                                       font=self._f(10))
        self.mode_combo.pack(fill="x", pady=(0, 6))

        tgl_row = tk.Frame(m_inner, bg=CARD)
        tgl_row.pack(fill="x", pady=(0, 6))
        self.sync_var   = tk.BooleanVar(value=False)
        self.pacing_var = tk.BooleanVar(value=False)
        tk.Checkbutton(tgl_row, text="Sync enabled", variable=self.sync_var,
                       bg=CARD, fg=TEXT, selectcolor=PANEL,
                       activebackground=CARD, activeforeground=ACCENT,
                       command=self.toggle_sync).pack(side="left", padx=(0, 12))
        tk.Checkbutton(tgl_row, text="Pacing", variable=self.pacing_var,
                       bg=CARD, fg=TEXT, selectcolor=PANEL,
                       activebackground=CARD, activeforeground=ACCENT,
                       command=self.toggle_pacing).pack(side="left")

        btns = tk.Frame(m_inner, bg=CARD)
        btns.pack(fill="x")
        tk.Button(btns, text="▶  APPLY MODE",
                  bg=ACCENT, fg=BG, activebackground="#0099cc",
                  activeforeground=BG, bd=0, relief="flat",
                  padx=10, pady=7, font=self._f(9, "bold"),
                  command=self.apply_mode).pack(side="left", fill="x", expand=True, padx=(0, 4))
        tk.Button(btns, text="🔔  ALARM TEST",
                  bg=RED, fg=WHITE, activebackground="#cc0030",
                  activeforeground=WHITE, bd=0, relief="flat",
                  padx=10, pady=7, font=self._f(9, "bold"),
                  command=self.trigger_alarm_test).pack(side="left", fill="x", expand=True)

        # ── VIRTUAL OUTPUT PORT ───────────────────────────────────────────
        v_panel = self._panel(right, "VIRTUAL OUTPUT PORT")
        v_panel.pack(fill="x", pady=(0, 8))
        v_inner = tk.Frame(v_panel, bg=CARD)
        v_inner.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(v_inner, textvariable=self.virtual_status_var, fg=ACCENT, bg=CARD,
                 font=self._f(9, "bold")).pack(anchor="w")
        tk.Label(v_inner, textvariable=self.virtual_tx_var, fg=GREEN, bg=CARD,
                 font=self._f(9)).pack(anchor="w", pady=(2, 4))
        tk.Label(v_inner, textvariable=self.virtual_bytes_var, fg=DIM, bg=CARD,
                 font=self._f(9)).pack(anchor="w")

        host_row = tk.Frame(v_inner, bg=CARD)
        host_row.pack(fill="x", pady=(6, 2))
        tk.Label(host_row, text="Host", fg=DIM, bg=CARD, font=self._f(8)).pack(side="left")
        tk.Entry(host_row, textvariable=self.virtual_host_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, width=14).pack(side="left", padx=6)
        tk.Label(host_row, text="Port", fg=DIM, bg=CARD, font=self._f(8)).pack(side="left")
        tk.Entry(host_row, textvariable=self.virtual_port_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT, width=6).pack(side="left", padx=6)

        tk.Label(v_inner, text="Transmit every (s)", fg=DIM, bg=CARD,
                 font=self._f(8)).pack(anchor="w", pady=(6, 2))
        tk.Entry(v_inner, textvariable=self.virtual_interval_var, bg=PANEL, fg=TEXT,
                 insertbackground=TEXT).pack(fill="x")

        tk.Label(v_inner, text="Monitor values", fg=DIM, bg=CARD,
                 font=self._f(8)).pack(anchor="w", pady=(8, 2))
        vals = [
            ("SpO₂ (%)", self.virtual_spo2_var),
            ("Pulse (BPM)", self.virtual_pulse_var),
            ("Perfusion", self.virtual_perf_var),
            ("Signal", self.virtual_signal_var),
            ("Alarm", self.virtual_alarm_var),
        ]
        for label, var in vals:
            row = tk.Frame(v_inner, bg=CARD)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, fg=DIM, bg=CARD, font=self._f(8)).pack(side="left")
            tk.Entry(row, textvariable=var, bg=PANEL, fg=TEXT, insertbackground=TEXT, width=10).pack(side="right")

        btn_row = tk.Frame(v_inner, bg=CARD)
        btn_row.pack(fill="x", pady=(8, 0))
        tk.Button(btn_row, text="CONNECT", bg=GREEN, fg=BG,
                  activebackground="#00b35a", activeforeground=BG, bd=0, relief="flat",
                  padx=8, pady=6, font=self._f(9, "bold"), command=self.connect_virtual_output).pack(side="left", fill="x", expand=True, padx=(0, 4))
        tk.Button(btn_row, text="APPLY", bg=ACCENT, fg=BG,
                  activebackground="#0099cc", activeforeground=BG, bd=0, relief="flat",
                  padx=8, pady=6, font=self._f(9, "bold"), command=self.apply_virtual_output).pack(side="left", fill="x", expand=True, padx=(0, 4))
        tk.Button(btn_row, text="DISCONNECT", bg=YELLOW, fg=BG,
                  activebackground="#cc8800", activeforeground=BG, bd=0, relief="flat",
                  padx=8, pady=6, font=self._f(9, "bold"), command=self.disconnect_virtual_output).pack(side="left", fill="x", expand=True)

        # ── NETWORK ──────────────────────────────────────────────────────────
        net_panel = self._panel(right, "NETWORK")
        net_panel.pack(fill="x")
        n_inner = tk.Frame(net_panel, bg=CARD)
        n_inner.pack(fill="x", padx=10, pady=(0, 10))
        self.host_var        = tk.StringVar(value="Host: 0.0.0.0")
        self.port_var        = tk.StringVar(value=f"Port: {self.port}")
        self.network_state_var = tk.StringVar(value="State: ONLINE")
        for var, fg in ((self.host_var, DIM), (self.port_var, DIM),
                        (self.network_state_var, GREEN)):
            tk.Label(n_inner, textvariable=var, fg=fg, bg=CARD,
                     font=self._f(9)).pack(anchor="w")
        self.connection_btn = tk.Button(n_inner, text="DISCONNECT",
                                        bg=YELLOW, fg=BG,
                                        activebackground="#cc8800", activeforeground=BG,
                                        bd=0, relief="flat", padx=10, pady=7,
                                        font=self._f(9, "bold"),
                                        command=self.toggle_server)
        self.connection_btn.pack(fill="x", pady=(8, 0))

    # ── widget helpers ────────────────────────────────────────────────────────
    def _panel(self, parent, title):
        frame = tk.Frame(parent, bg=CARD,
                         highlightbackground=BORDER, highlightthickness=1)
        tk.Label(frame, text=f"  {title}  ", fg=ACCENT, bg=CARD,
                 font=self._f(8, "bold")).pack(anchor="w", padx=10, pady=(8, 4))
        return frame

    def _pill(self, parent, label, var, fg):
        f = tk.Frame(parent, bg=BORDER)
        if label:
            tk.Label(f, text=label, fg=DIM, bg=BORDER,
                     font=self._f(7)).pack(side="left", padx=(6, 2), pady=3)
        tk.Label(f, textvariable=var, fg=fg, bg=BORDER,
                 font=self._f(8, "bold")).pack(side="left", padx=(0, 8), pady=3)
        return f

    def _btn(self, parent, text, command, color):
        b = tk.Button(parent, text=text, bg=color, fg=BG if color != DIM else TEXT,
                      activebackground=BORDER, activeforeground=WHITE,
                      bd=0, relief="flat", padx=8, pady=8,
                      font=self._f(9, "bold"), command=command)
        b.bind("<Enter>", lambda e, b=b: b.config(bg=BORDER))
        b.bind("<Leave>", lambda e, b=b, c=color: b.config(bg=c))
        return b

    def _vital_card(self, parent, label, key, unit, col):
        frame = tk.Frame(parent, bg=CARD,
                         highlightbackground=BORDER, highlightthickness=1)
        frame.grid(row=0, column=col, padx=4, sticky="nsew")
        tk.Label(frame, text=label, fg=ACCENT, bg=CARD,
                 font=self._f(8, "bold")).pack(anchor="w", padx=10, pady=(8, 0))
        value_var = tk.StringVar(value="--")
        tk.Label(frame, textvariable=value_var, fg=WHITE, bg=CARD,
                 font=self._f(20, "bold")).pack(anchor="w", padx=10)
        tk.Label(frame, text=unit, fg=DIM, bg=CARD,
                 font=self._f(8)).pack(anchor="w", padx=10, pady=(0, 8))
        self.vital_cards[key] = {"value": value_var}

    # ── energy quick-select ───────────────────────────────────────────────────
    def _quick_energy(self, value):
        self.energy_var.set(str(value))
        self.apply_energy()

    def apply_energy(self):
        try:
            energy = int(self.energy_var.get())
            self.simulator.device.set_energy(energy)
            self.simulator.add_event(f"Energy set to {energy} J")
            self.energy_indicator.config(text=f"Selected: {energy} J")
            # highlight active quick-btn
            for j, b in self._energy_btns.items():
                b.config(bg=ACCENT if j == energy else PANEL,
                         fg=BG    if j == energy else TEXT)
            self._refresh_display()
        except ValueError:
            messagebox.showwarning("Invalid Energy", "Choose a valid energy level.")

    # ── rhythm helpers ────────────────────────────────────────────────────────
    def set_rhythm(self, rhythm):
        self.simulator.patient.set_rhythm(rhythm)
        self.rhythm_var.set(rhythm.value)
        self.simulator.add_event(f"Rhythm → {rhythm.value}")
        self._refresh_display()

    def on_rhythm_selected(self, *_):
        sel = self.rhythm_var.get()
        if sel in self.rhythm_map:
            self.set_rhythm(self.rhythm_map[sel])

    def apply_rhythm(self):
        sel = self.rhythm_var.get()
        if sel in self.rhythm_map:
            self.set_rhythm(self.rhythm_map[sel])

    def trigger_alarm_test(self):
        self._set_alarm_banner("CRITICAL", "TEST ALERT: Monitor response required",
                               self.simulator.device.mode.value,
                               self.simulator.patient.rhythm.value)
        self._play_alert_sound()
        self.simulator.add_event("Alarm test triggered")
        self.last_alert_level = "CRITICAL"

    # ── toggle / mode ─────────────────────────────────────────────────────────
    def toggle_sync(self):
        self.simulator.device.toggle_sync()
        self.simulator.add_event("Sync toggled")
        self._refresh_display()

    def toggle_pacing(self):
        self.simulator.device.toggle_pacing()
        self.simulator.add_event("Pacing toggled")
        self._refresh_display()

    def select_mode(self, mode):
        self.simulator.device.set_mode(mode)
        self.simulator.update()
        self.simulator.add_event(f"Mode → {mode.value}")
        self._refresh_display()

    def apply_mode(self):
        sel = self.mode_var.get()
        if sel in self.mode_map:
            self.select_mode(self.mode_map[sel])
            messagebox.showinfo("Mode", f"Mode set to {sel}.")

    # ── device actions ────────────────────────────────────────────────────────
    def charge_device(self):
        self.simulator.charge()
        self.simulator.add_event("Charge command issued")
        self._refresh_display()
        messagebox.showinfo("Charge", "Charging sequence started.")

    def deliver_shock(self):
        success = self.simulator.shock()
        self._refresh_display()
        if success:
            self.simulator.add_event("Shock delivered")
            self._refresh_display()
            messagebox.showinfo("Shock", "Shock delivered successfully.")
        else:
            messagebox.showwarning("Shock unavailable",
                                   "Device must be in Ready state before delivering a shock.")

    def disarm_device(self):
        self.simulator.disarm()
        self.simulator.add_event("Device disarmed")
        self._refresh_display()
        messagebox.showinfo("Disarm", "Device has been disarmed.")

    def recharge_device(self):
        self.simulator.recharge()
        self.simulator.add_event("Battery recharged to 100%")
        self._refresh_display()
        messagebox.showinfo("Recharge", "Battery recharged to 100%.")

    def show_ecg(self):
        sample = self.simulator.ecg_sample()
        messagebox.showinfo("ECG Sample", f"Current sample: {sample:.3f}")
        self._refresh_display()

    def send_telemetry(self):
        self.simulator.telemetry()
        self.simulator.add_event("Telemetry packet sent")
        self._refresh_display()
        messagebox.showinfo("Telemetry", "Hardware telemetry packet sent.")

    def connect_virtual_output(self):
        try:
            host = self.virtual_host_var.get()
            port = int(self.virtual_port_var.get())
            interval = float(self.virtual_interval_var.get())
            ok = self.simulator.connect_virtual_output(host=host, port=port, transmit_interval=interval)
            if ok:
                self.virtual_status_var.set("Connected")
                self.virtual_tx_var.set("● Streaming")
                self.simulator.add_event(f"Virtual output listening on {host}:{port}")
            else:
                self.virtual_status_var.set("Connection failed")
                self.virtual_tx_var.set("● Error")
                messagebox.showwarning("Virtual Output", "Unable to open the virtual output port.")
        except ValueError:
            messagebox.showwarning("Virtual Output", "Port and interval must be valid numbers.")
        self._refresh_display()

    def disconnect_virtual_output(self):
        self.simulator.disconnect_virtual_output()
        self.virtual_status_var.set("Disconnected")
        self.virtual_tx_var.set("● Idle")
        self._refresh_display()

    def apply_virtual_output(self):
        try:
            self.simulator.set_monitor_values(
                spo2=self.virtual_spo2_var.get(),
                pulse_rate=self.virtual_pulse_var.get(),
                perfusion_index=self.virtual_perf_var.get(),
                signal_strength=self.virtual_signal_var.get(),
                alarm_status=self.virtual_alarm_var.get(),
            )
            self.simulator.transmit_virtual_output()
            self._refresh_display()
            messagebox.showinfo("Virtual Output", "Monitor values applied and transmitted.")
        except ValueError:
            messagebox.showwarning("Virtual Output", "Please enter numeric values for the monitor fields.")

    # ── alarm banner ──────────────────────────────────────────────────────────
    def _set_alarm_banner(self, level, message, mode_name, rhythm_value):
        cfg = ALARM_CFG.get(level, ALARM_CFG["NORMAL"])
        bg  = cfg["bg"]

        self.alarm_frame.configure(bg=bg, highlightbackground=cfg["border"])
        self.alarm_icon_lbl.configure(text=cfg["icon"], fg=cfg["icon_fg"], bg=bg)
        self.alarm_title_lbl.configure(text=cfg["label"], fg=cfg["title_fg"], bg=bg)
        self.alarm_msg_lbl.configure(text=message, bg=bg)
        self.alarm_mode_lbl.configure(text=f"Mode: {mode_name}", bg=bg)

        abbr, badge_col = RHYTHM_LABELS.get(rhythm_value, ("?", DIM))
        self.alarm_rhythm_badge.configure(text=abbr, fg=BG, bg=badge_col)

        # find the right-meta frame and update its bg
        for w in self.alarm_frame.winfo_children():
            try:
                w.configure(bg=bg)
            except tk.TclError:
                pass
        # pulsing for critical
        if self._pulse_job:
            self.root.after_cancel(self._pulse_job)
            self._pulse_job = None
        if level == "CRITICAL":
            self._pulse_banner(cfg)

    def _pulse_banner(self, cfg):
        self._pulse_state = not self._pulse_state
        c = "#200008" if self._pulse_state else cfg["bg"]
        self.alarm_frame.configure(bg=c)
        self._pulse_job = self.root.after(280, lambda: self._pulse_banner(cfg))

    def _play_alert_sound(self):
        try:
            import winsound
            winsound.Beep(1200, 300)
            return
        except Exception:
            pass
        for cmd in (["paplay", "/usr/share/sounds/alsa/Front_Center.wav"],
                    ["aplay",  "/usr/share/sounds/alsa/Front_Center.wav"]):
            try:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
                return
            except OSError:
                continue

    # ── main display refresh ──────────────────────────────────────────────────
    def _refresh_display(self):
        status  = self.simulator.status()
        device  = status["device"]
        patient = status["patient"]
        alarm   = status["alarm"]

        self.device_status_var.set(device["state"].upper())
        self.device_mode_var.set(device["mode"].upper())

        bat = device["battery"]
        self.battery_bar["value"] = bat
        bat_col = GREEN if bat > 30 else (YELLOW if bat > 10 else RED)
        self.battery_lbl.configure(text=f"{bat} %", fg=bat_col)

        self.rate_value.configure(text=str(patient["heart_rate"]))
        self.vital_cards["heart_rate"]["value"].set(str(patient["heart_rate"]))
        self.vital_cards["spo2"]["value"].set(str(patient["spo2"]))
        self.vital_cards["bp"]["value"].set(patient["bp"])
        self.vital_cards["battery"]["value"].set(str(bat))

        self._set_alarm_banner(alarm["level"], alarm["alarm"],
                                device["mode"], patient["rhythm"])
        self._update_button_states(device)
        self._refresh_events(status["events"])
        self._update_device_info(device, patient, alarm)

        virtual_status = status.get("virtual_output", {})
        self.virtual_status_var.set(virtual_status.get("connection_state", "DISCONNECTED").title())
        self.virtual_tx_var.set("● Streaming" if virtual_status.get("connected") else "● Idle")
        self.virtual_bytes_var.set(f"Bytes sent: {virtual_status.get('bytes_sent', 0)}")

        if self.last_alert_level != alarm["level"] and alarm["level"] in {"WARNING", "CRITICAL"}:
            self._play_alert_sound()
        self.last_alert_level = alarm["level"]

    def _update_button_states(self, device):
        ok   = "normal"
        self.shock_btn.config(state=ok if device["state"] == "Ready" else "disabled")

    def _update_device_info(self, device, patient, alarm):
        self.device_info.configure(state="normal")
        self.device_info.delete("1.0", tk.END)
        lines = [
            ("Mode",    device["mode"]),
            ("State",   device["state"]),
            ("Energy",  f"{device['energy']} J"),
            ("Battery", f"{device['battery']} %"),
            ("Shocks",  str(device.get("shocks", "--"))),
            ("Rhythm",  patient["rhythm"]),
            ("HR",      f"{patient['heart_rate']} bpm"),
            ("SpO₂",    f"{patient['spo2']} %"),
            ("BP",      patient["bp"]),
            ("Alarm",   alarm["alarm"]),
        ]
        for k, v in lines:
            self.device_info.insert(tk.END, f"  {k:<10}{v}\n")
        self.device_info.configure(state="disabled")

    def _refresh_events(self, events):
        self.event_box.configure(state="normal")
        self.event_box.delete("1.0", tk.END)
        if not events:
            self.event_box.insert(tk.END, "  No events yet.\n")
        else:
            for ev in reversed(events):
                ts = datetime.now().strftime("%H:%M:%S")
                self.event_box.insert(tk.END, f"  {ts}  {ev}\n")
        self.event_box.configure(state="disabled")

    # ── waveform ──────────────────────────────────────────────────────────────
    def _render_waveform(self):
        c = self.waveform_canvas
        c.delete("all")
        w = c.winfo_width() or 900
        h = 180
        mid = h / 2
        c.create_line(0, mid, w, mid, fill=BORDER, width=1)

        alarm_level = self.last_alert_level or "NORMAL"
        wave_col = {
            "CRITICAL": RED,
            "WARNING":  YELLOW,
        }.get(alarm_level, GREEN)

        if len(self.waveform_samples) < 2:
            return
        step = w / max(1, len(self.waveform_samples) - 1)
        pts  = [(i * step, mid - (v * 28)) for i, v in enumerate(self.waveform_samples)]
        c.create_line(pts, fill=wave_col, width=2, smooth=True)

    # ── tick (animation loop) ─────────────────────────────────────────────────
    def _tick(self):
        sample = self.simulator.ecg_sample()
        self.waveform_samples.append(sample)
        if len(self.waveform_samples) > 260:
            self.waveform_samples.pop(0)
        self._render_waveform()
        self._refresh_display()
        self.root.after(500, self._tick)

    # ── server ────────────────────────────────────────────────────────────────
    def _start_api_server(self):
        try:
            self.server = SimulatorHTTPServer(self.simulator, host="0.0.0.0", port=self.port)
            self.server.start()
            self.api_status_var.set(f"API: http://127.0.0.1:{self.port}")
            self.connection_var.set("TCP: CONNECTED")
            self.network_state_var.set("State: ONLINE")
        except RuntimeError as exc:
            self.api_status_var.set(f"API unavailable: {exc}")
            self.connection_var.set("TCP: DISCONNECTED")
            self.network_state_var.set("State: OFFLINE")

    def toggle_server(self):
        if self.server is None:
            self._start_api_server()
            self.connection_btn.configure(text="DISCONNECT", bg=YELLOW)
        else:
            self.server.stop()
            self.server = None
            self.connection_var.set("TCP: DISCONNECTED")
            self.network_state_var.set("State: OFFLINE")
            self.api_status_var.set("API stopped")
            self.connection_btn.configure(text="CONNECT", bg=GREEN)

    def _on_close(self):
        if self._pulse_job:
            self.root.after_cancel(self._pulse_job)
        if self.server:
            self.server.stop()
        self.root.destroy()


def run_app(port=None):
    root = tk.Tk()
    app = DefibrillatorApp(root, port=port)
    root.mainloop()


if __name__ == "__main__":
    run_app()
