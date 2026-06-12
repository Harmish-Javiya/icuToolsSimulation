from __future__ import annotations

import time
import tkinter as tk
from tkinter import ttk

from .control_panel import ControlPanel
from .graph_panel import GraphPanel
from .waveform_panel import WaveformPanel

class MedicalDashboard(tk.Tk):

    def __init__(self, state_provider=None, on_control_change=None, on_replace_filter=None, on_start=None, on_close=None):

        super().__init__()
        self.state_provider = state_provider
        self.on_control_change = on_control_change
        self.on_replace_filter = on_replace_filter
        self.on_start = on_start
        self.on_close = on_close
        self._last_graph_step = None
        self._last_alarm_signature = None
        self._seen_event_count = 0
        self._refresh_job = None
        self.is_running = True

        self.bg = "#07111f"
        self.panel = "#0d1728"
        self.panel_soft = "#12203a"
        self.border = "#22324f"
        self.text = "#e8f0ff"
        self.muted = "#8ea2c6"
        self.accent = "#5dd6c6"
        self.accent_2 = "#7c9cff"
        self.warning = "#ffcc66"
        self.danger = "#ff6b7a"
        self.ok = "#7cf0a5"

        self.title("CRRT Simulator Dashboard")
        self.configure(bg=self.bg)
        self.geometry("100x1020")
        self.minsize(1380, 900)
        self.protocol("WM_DELETE_WINDOW", self._handle_close)

        self._setup_styles()
        self._build_layout()
        self._refresh_loop()

    def _setup_styles(self):

        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("Dashboard.TFrame", background=self.bg)
        style.configure("Panel.TFrame", background=self.panel)
        style.configure("PanelSoft.TFrame", background=self.panel_soft)
        style.configure("Dashboard.TLabel", background=self.bg, foreground=self.text, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=self.bg, foreground=self.text, font=("Segoe UI", 28, "bold"))
        style.configure("Subtitle.TLabel", background=self.bg, foreground=self.muted, font=("Segoe UI", 10))
        style.configure("PanelTitle.TLabel", background=self.panel, foreground=self.text, font=("Segoe UI", 12, "bold"))
        style.configure("Metric.TLabel", background=self.panel, foreground=self.text, font=("Segoe UI", 18, "bold"))
        style.configure("MetricSub.TLabel", background=self.panel, foreground=self.muted, font=("Segoe UI", 9))
        style.configure("Machine.TLabel", background=self.panel, foreground=self.ok, font=("Segoe UI", 11, "bold"))
        style.configure("Accent.TButton", padding=(14, 8), font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton", foreground=[("active", self.text), ("!disabled", self.text)])
        style.configure("Alarm.Treeview", background=self.panel_soft, fieldbackground=self.panel_soft, foreground=self.text, bordercolor=self.border, rowheight=26, font=("Segoe UI", 9))
        style.configure("Alarm.Treeview.Heading", background=self.panel, foreground=self.text, font=("Segoe UI", 9, "bold"))
        style.map("Alarm.Treeview", background=[("selected", self.accent_2)])
        style.configure("Dash.Horizontal.TProgressbar", troughcolor=self.panel_soft, background=self.accent, bordercolor=self.border, lightcolor=self.accent, darkcolor=self.accent)

    def _build_layout(self):

        shell = ttk.Frame(self, style="Dashboard.TFrame", padding=18)
        shell.pack(fill=tk.BOTH, expand=True)

        top = tk.Frame(shell, bg=self.bg)
        top.pack(fill=tk.X, pady=(0, 14))

        title_block = tk.Frame(top, bg=self.bg)
        title_block.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            title_block,
            text="CRRT SIMULATOR",
            bg=self.bg,
            fg=self.text,
            font=("Segoe UI", 28, "bold"),
        ).pack(anchor="w")
        tk.Label(
            title_block,
            text="Continuous Renal Replacement Therapy monitoring workstation",
            bg=self.bg,
            fg=self.muted,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 0))

        status_block = tk.Frame(top, bg=self.bg)
        status_block.pack(side=tk.RIGHT)

        self.clock_value = tk.Label(status_block, text="--:--:--", bg=self.bg, fg=self.text, font=("Segoe UI", 22, "bold"))
        self.clock_value.pack(anchor="e")

        self.machine_banner = tk.Label(
            status_block,
            text="Machine: Stopped",
            bg="#10243a",
            fg=self.ok,
            font=("Segoe UI", 11, "bold"),
            padx=16,
            pady=8,
        )
        self.machine_banner.pack(anchor="e", pady=(8, 0))

        self.therapy_banner = tk.Label(
            status_block,
            text="Therapy Mode: --",
            bg="#10243a",
            fg=self.text,
            font=("Segoe UI", 11, "bold"),
            padx=16,
            pady=8,
        )
        self.therapy_banner.pack(anchor="e", pady=(8, 0))

        action_block = tk.Frame(status_block, bg=self.bg)
        action_block.pack(anchor="e", pady=(10, 0))
        ttk.Button(
            action_block,
            text="Start Machine",
            style="Accent.TButton",
            command=self._handle_start,
        ).pack(anchor="e")

        body = tk.Frame(shell, bg=self.bg)
        body.pack(fill=tk.BOTH, expand=True)
        body.grid_columnconfigure(0, weight=1, minsize=360)
        body.grid_columnconfigure(1, weight=2, minsize=760)
        body.grid_columnconfigure(2, weight=1, minsize=360)
        body.grid_rowconfigure(0, weight=1)

        left = tk.Frame(body, bg=self.bg)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        center = tk.Frame(body, bg=self.bg)
        center.grid(row=0, column=1, sticky="nsew", padx=(0, 12))
        right = tk.Frame(body, bg=self.bg)
        right.grid(row=0, column=2, sticky="nsew")

        self.control_panel = ControlPanel(left, on_change=self.on_control_change, on_replace_filter=self.on_replace_filter)
        self.control_panel.pack(fill=tk.BOTH, expand=True)

        center_top = tk.Frame(center, bg=self.bg)
        center_top.pack(fill=tk.BOTH, expand=True)
        self.graph_panel = GraphPanel(center_top)
        self.graph_panel.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        self.waveform_panel = WaveformPanel(center_top)
        self.waveform_panel.pack(fill=tk.X, expand=False)

        self.right_stack = tk.Frame(right, bg=self.bg)
        self.right_stack.pack(fill=tk.BOTH, expand=True)

        self._build_filter_stats(self.right_stack)
        self._build_therapy_stats(self.right_stack)
        self._build_alarm_panel(self.right_stack)

        bottom = tk.Frame(shell, bg=self.bg)
        bottom.pack(fill=tk.BOTH, expand=False, pady=(14, 0))
        self._build_event_log(bottom)

    def _metric_card(self, parent, title, value="--", subtitle=""):

        card = tk.Frame(parent, bg=self.panel, highlightbackground=self.border, highlightthickness=1)
        tk.Label(card, text=title, bg=self.panel, fg=self.muted, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(10, 0))
        metric = tk.Label(card, text=value, bg=self.panel, fg=self.text, font=("Segoe UI", 18, "bold"))
        metric.pack(anchor="w", padx=12, pady=(4, 0))
        sub = tk.Label(card, text=subtitle, bg=self.panel, fg=self.muted, font=("Segoe UI", 9))
        sub.pack(anchor="w", padx=12, pady=(2, 10))
        return card, metric, sub

    def _build_filter_stats(self, parent):

        panel = tk.Frame(parent, bg=self.panel, highlightbackground=self.border, highlightthickness=1)
        panel.pack(fill=tk.X, pady=(0, 12))
        tk.Label(panel, text="Filter Health", bg=self.panel, fg=self.text, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(12, 8))

        inner = tk.Frame(panel, bg=self.panel)
        inner.pack(fill=tk.X, padx=14, pady=(0, 14))
        self.filter_status_label = tk.Label(inner, text="Healthy", bg=self.panel, fg=self.ok, font=("Segoe UI", 22, "bold"))
        self.filter_status_label.pack(anchor="w")
        self.filter_health_label = tk.Label(inner, text="100.0%", bg=self.panel, fg=self.text, font=("Segoe UI", 10))
        self.filter_health_label.pack(anchor="w", pady=(4, 10))
        self.filter_progress = ttk.Progressbar(inner, style="Dash.Horizontal.TProgressbar", orient="horizontal", mode="determinate", maximum=100, value=100)
        self.filter_progress.pack(fill=tk.X)

        self.filter_metrics = tk.Frame(panel, bg=self.panel)
        self.filter_metrics.pack(fill=tk.BOTH, padx=14, pady=(0, 14))
        self.tmp_metric_card, self.tmp_metric, self.tmp_sub = self._metric_card(self.filter_metrics, "TMP", "--", "Transmembrane pressure")
        self.clot_metric_card, self.clot_metric, self.clot_sub = self._metric_card(self.filter_metrics, "Clotting Risk", "--", "Estimated clotting tendency")
        self.tmp_metric_card.pack(fill=tk.X, pady=(0, 10))
        self.clot_metric_card.pack(fill=tk.X)

    def _build_therapy_stats(self, parent):

        panel = tk.Frame(parent, bg=self.panel, highlightbackground=self.border, highlightthickness=1)
        panel.pack(fill=tk.X, pady=(0, 12))
        tk.Label(panel, text="Therapy Statistics", bg=self.panel, fg=self.text, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(12, 8))

        self.therapy_stats = tk.Frame(panel, bg=self.panel)
        self.therapy_stats.pack(fill=tk.X, padx=14, pady=(0, 14))
        self.therapy_mode_label = tk.Label(self.therapy_stats, text="Mode: --", bg=self.panel, fg=self.text, font=("Segoe UI", 14, "bold"))
        self.therapy_mode_label.pack(anchor="w")
        self.flow_label = tk.Label(self.therapy_stats, text="Blood Flow: --", bg=self.panel, fg=self.muted, font=("Segoe UI", 10))
        self.flow_label.pack(anchor="w", pady=(4, 0))
        self.dialysate_label = tk.Label(self.therapy_stats, text="Dialysate: --", bg=self.panel, fg=self.muted, font=("Segoe UI", 10))
        self.dialysate_label.pack(anchor="w")
        self.uf_label = tk.Label(self.therapy_stats, text="Ultrafiltration: --", bg=self.panel, fg=self.muted, font=("Segoe UI", 10))
        self.uf_label.pack(anchor="w")

    def _build_alarm_panel(self, parent):

        panel = tk.Frame(parent, bg=self.panel, highlightbackground=self.border, highlightthickness=1)
        panel.pack(fill=tk.BOTH, expand=True)
        tk.Label(panel, text="Alarm Feed", bg=self.panel, fg=self.text, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(12, 8))

        header = tk.Frame(panel, bg=self.panel)
        header.pack(fill=tk.X, padx=14)
        self.alarm_counter = tk.Label(header, text="0 Active", bg=self.panel, fg=self.warning, font=("Segoe UI", 10, "bold"))
        self.alarm_counter.pack(anchor="w")

        columns = ("time", "priority", "alarm")
        self.alarm_tree = ttk.Treeview(panel, columns=columns, show="headings", style="Alarm.Treeview", height=10)
        self.alarm_tree.heading("time", text="Time")
        self.alarm_tree.heading("priority", text="Priority")
        self.alarm_tree.heading("alarm", text="Alarm")
        self.alarm_tree.column("time", width=78, anchor="center")
        self.alarm_tree.column("priority", width=76, anchor="center")
        self.alarm_tree.column("alarm", width=260, anchor="w")
        self.alarm_tree.pack(fill=tk.BOTH, expand=True, padx=14, pady=(8, 14))

    def _build_event_log(self, parent):

        panel = tk.Frame(parent, bg=self.panel, highlightbackground=self.border, highlightthickness=1)
        panel.pack(fill=tk.BOTH, expand=True)
        tk.Label(panel, text="System Messages", bg=self.panel, fg=self.text, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(12, 8))

        self.event_text = tk.Text(
            panel,
            height=6,
            bg=self.panel_soft,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            wrap="word",
            font=("Segoe UI", 9),
        )
        self.event_text.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 14))
        self.event_text.insert("end", "Waiting for simulation updates...\n")
        self.event_text.configure(state="disabled")

    def _append_event_line(self, line):

        self.event_text.configure(state="normal")
        self.event_text.insert("end", line + "\n")
        self.event_text.see("end")
        self.event_text.configure(state="disabled")

    def _handle_start(self):

        if callable(self.on_start):
            self.on_start()

    def _refresh_loop(self):

        if not self.is_running:
            return

        snapshot = self.state_provider() if callable(self.state_provider) else None
        if snapshot:
            self._render_snapshot(snapshot)

        self._refresh_job = self.after(33, self._refresh_loop)

    def _render_snapshot(self, snapshot):

        self.clock_value.configure(text=snapshot.get("updated_at", "--:--:--"))
        machine_status = snapshot.get("machine_status", "Stopped")
        therapy_mode = snapshot.get("therapy_mode", "--")
        self.machine_banner.configure(
            text=f"Machine: {machine_status}",
            fg=self.ok if machine_status == "Running" else self.warning,
        )
        self.therapy_banner.configure(text=f"Therapy Mode: {therapy_mode}")
        self.therapy_mode_label.configure(text=f"Mode: {therapy_mode}")
        self.flow_label.configure(text=f"Blood Flow: {snapshot.get('blood_flow_rate', '--')} mL/min")
        self.dialysate_label.configure(text=f"Dialysate: {snapshot.get('dialysate_flow_rate', '--')} mL/hr")
        self.uf_label.configure(text=f"Ultrafiltration: {snapshot.get('ultrafiltration_rate', '--')} mL/hr")

        self.control_panel.sync_from_snapshot(snapshot)

        filter_state = snapshot.get("filter", {}) or {}
        filter_health = float(filter_state.get("health", 0))
        filter_status = filter_state.get("status", "Unknown")
        filter_tmp = snapshot.get("pressure", {}).get("tmp", 0)
        clotting_risk = filter_state.get("clotting_risk", snapshot.get("pressure", {}).get("clotting_risk", 0))

        self.filter_status_label.configure(text=filter_status)
        self.filter_status_label.configure(fg=self.ok if filter_health >= 75 else self.warning if filter_health >= 45 else self.danger)
        self.filter_health_label.configure(text=f"{filter_health:.1f}%")
        self.filter_progress.configure(value=max(0, min(100, filter_health)))
        self.tmp_metric.configure(text=f"{filter_tmp:.0f} mmHg")
        self.clot_metric.configure(text=f"{float(clotting_risk):.1f}%")

        self.alarm_counter.configure(text=f"{len(snapshot.get('alarms', []))} Active")
        self._render_alarms(snapshot.get("alarms", []))

        current_step = snapshot.get("simulation_step")
        if current_step != self._last_graph_step:
            self.graph_panel.update_from_snapshot(snapshot)
            self._last_graph_step = current_step

        self.waveform_panel.update_from_snapshot(snapshot)
        self._render_events(snapshot)

    def _render_alarms(self, alarms):

        signature = tuple((alarm.get("timestamp"), alarm.get("priority"), alarm.get("message")) for alarm in alarms)
        if signature == self._last_alarm_signature:
            return

        self._last_alarm_signature = signature
        for item in self.alarm_tree.get_children():
            self.alarm_tree.delete(item)

        if not alarms:
            self.alarm_tree.insert("", "end", values=("--", "OK", "No active alarms"))
            return

        for alarm in alarms:
            self.alarm_tree.insert(
                "",
                "end",
                values=(alarm.get("timestamp", "--"), alarm.get("priority", "--"), alarm.get("message", "")),
            )

    def _render_events(self, snapshot):

        events = snapshot.get("events", []) or []
        if len(events) <= self._seen_event_count:
            return

        for event in events[self._seen_event_count:]:
            self._append_event_line(f"[{event.get('timestamp', '--:--:--')}] {event.get('level', 'INFO')}: {event.get('message', '')}")

        self._seen_event_count = len(events)

    def _handle_close(self):

        self.is_running = False
        if self._refresh_job is not None:
            try:
                self.after_cancel(self._refresh_job)
            except tk.TclError:
                pass
            self._refresh_job = None

        if hasattr(self, "graph_panel") and hasattr(self.graph_panel, "close"):
            self.graph_panel.close()
        if hasattr(self, "waveform_panel") and hasattr(self.waveform_panel, "close"):
            self.waveform_panel.close()

        if callable(self.on_close):
            self.on_close()

        try:
            self.update_idletasks()
            self.update()
        except tk.TclError:
            pass

        self.destroy()

    def run(self):

        self.deiconify()
        self.lift()
        self.focus_force()

        while self.is_running and self.winfo_exists():
            try:
                self.update_idletasks()
                self.update()
                time.sleep(0.01)
            except tk.TclError:
                break
