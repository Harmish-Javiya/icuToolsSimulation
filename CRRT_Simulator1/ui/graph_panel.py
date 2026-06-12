from __future__ import annotations

from collections import deque

import numpy as np
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class GraphPanel(ttk.Frame):

    def __init__(self, master, **kwargs):

        super().__init__(master, **kwargs)
        self.history = {
            "step": deque(maxlen=300),
            "heart_rate": deque(maxlen=300),
            "spo2": deque(maxlen=300),
            "temperature": deque(maxlen=300),
            "respiratory_rate": deque(maxlen=300),
            "access_pressure": deque(maxlen=300),
            "return_pressure": deque(maxlen=300),
            "filter_pressure": deque(maxlen=300),
            "tmp": deque(maxlen=300),
            "bun": deque(maxlen=300),
            "creatinine": deque(maxlen=300),
            "potassium": deque(maxlen=300),
            "fluid_intake": deque(maxlen=300),
            "fluid_output": deque(maxlen=300),
            "fluid_balance": deque(maxlen=300),
            "filter_health": deque(maxlen=300),
            "pressure_drop": deque(maxlen=300),
            "clotting_risk": deque(maxlen=300),
        }
        self._tooltip = None

        self._build_layout()

    def _build_layout(self):

        container = tk.Frame(self, bg=self.master.panel if hasattr(self.master, "panel") else "#0d1728")
        container.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(container, bg=container["bg"])
        header.pack(fill=tk.X, padx=14, pady=(12, 8))

        tk.Label(
            header,
            text="Live Graph Dashboard",
            bg=header["bg"],
            fg=self.master.text if hasattr(self.master, "text") else "#e8f0ff",
            font=("Segoe UI", 13, "bold"),
        ).pack(side=tk.LEFT)

        tk.Label(
            header,
            text="History window: 300 samples",
            bg=header["bg"],
            fg=self.master.muted if hasattr(self.master, "muted") else "#8ea2c6",
            font=("Segoe UI", 9),
        ).pack(side=tk.RIGHT)

        self.figure = Figure(figsize=(9.8, 7.4), dpi=100, facecolor=container["bg"])
        self.axes = [
            self.figure.add_subplot(3, 2, 1),
            self.figure.add_subplot(3, 2, 2),
            self.figure.add_subplot(3, 2, 3),
            self.figure.add_subplot(3, 2, 4),
            self.figure.add_subplot(3, 2, 5),
            self.figure.add_subplot(3, 2, 6),
        ]

        for axis in self.axes:
            axis.set_facecolor(self.master.panel_soft if hasattr(self.master, "panel_soft") else "#12203a")
            axis.grid(True, alpha=0.25, linewidth=0.8)
            axis.tick_params(colors=self.master.muted if hasattr(self.master, "muted") else "#8ea2c6", labelsize=8)
            for spine in axis.spines.values():
                spine.set_color(self.master.border if hasattr(self.master, "border") else "#22324f")

        titles = [
            "Patient Vitals",
            "Pressure Monitoring",
            "Kidney Function",
            "Fluid Balance",
            "Filter Performance",
        ]
        for axis, title in zip(self.axes, titles):
            axis.set_title(title, color=self.master.text if hasattr(self.master, "text") else "#e8f0ff", fontsize=9)

        self.axes[5].set_visible(False)

        self.figure.tight_layout(pad=1.4)
        self.canvas = FigureCanvasTkAgg(self.figure, master=container)
        self.canvas.draw()
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 12))
        self.canvas.mpl_connect("motion_notify_event", self._on_motion)
        self.canvas.mpl_connect("figure_leave_event", self._hide_tooltip)

    def update_from_snapshot(self, snapshot):

        if not snapshot:
            return

        step = snapshot.get("simulation_step", 0)
        pressure = snapshot.get("pressure", {}) or {}
        filter_state = snapshot.get("filter", {}) or {}

        self.history["step"].append(step)
        self.history["heart_rate"].append(snapshot.get("heart_rate", 0))
        self.history["spo2"].append(snapshot.get("spo2", 0))
        self.history["temperature"].append(snapshot.get("temperature", 0))
        self.history["respiratory_rate"].append(snapshot.get("respiratory_rate", 0))
        self.history["access_pressure"].append(pressure.get("access", 0))
        self.history["return_pressure"].append(pressure.get("return", 0))
        self.history["filter_pressure"].append(pressure.get("filter", 0))
        self.history["tmp"].append(pressure.get("tmp", 0))
        self.history["bun"].append(snapshot.get("bun", 0))
        self.history["creatinine"].append(snapshot.get("creatinine", 0))
        self.history["potassium"].append(snapshot.get("potassium", 0))
        self.history["fluid_intake"].append(snapshot.get("fluid_intake", 0))
        self.history["fluid_output"].append(snapshot.get("fluid_output", 0))
        self.history["fluid_balance"].append(snapshot.get("fluid_balance", 0))
        self.history["filter_health"].append(filter_state.get("health", 0))
        self.history["pressure_drop"].append(filter_state.get("pressure_drop", 0))
        self.history["clotting_risk"].append(filter_state.get("clotting_risk", 0))

        self._redraw()

    def _redraw(self):

        if not self.history["step"]:
            return

        step_values = np.asarray(self.history["step"], dtype=float)
        series = [
            (self.axes[0], [
                (self.history["heart_rate"], "Heart Rate", "#5dd6c6", "bpm"),
                (self.history["spo2"], "SpO2", "#7c9cff", "%"),
                (self.history["temperature"], "Temperature", "#ffcc66", "C"),
                (self.history["respiratory_rate"], "Resp Rate", "#ff6b7a", "rpm"),
            ]),
            (self.axes[1], [
                (self.history["access_pressure"], "Access", "#5dd6c6", "mmHg"),
                (self.history["return_pressure"], "Return", "#7c9cff", "mmHg"),
                (self.history["filter_pressure"], "Filter", "#ffcc66", "mmHg"),
                (self.history["tmp"], "TMP", "#ff6b7a", "mmHg"),
            ]),
            (self.axes[2], [
                (self.history["bun"], "BUN", "#5dd6c6", "mg/dL"),
                (self.history["creatinine"], "Creatinine", "#7c9cff", "mg/dL"),
                (self.history["potassium"], "Potassium", "#ffcc66", "mmol/L"),
            ]),
            (self.axes[3], [
                (self.history["fluid_intake"], "Intake", "#5dd6c6", "mL"),
                (self.history["fluid_output"], "Output", "#7c9cff", "mL"),
                (self.history["fluid_balance"], "Net", "#ff6b7a", "mL"),
            ]),
            (self.axes[4], [
                (self.history["filter_health"], "Health", "#5dd6c6", "%"),
                (self.history["pressure_drop"], "Pressure Drop", "#7c9cff", "mmHg"),
                (self.history["clotting_risk"], "Clotting Risk", "#ff6b7a", "%"),
            ]),
        ]

        for axis, chart_defs in series:
            axis.clear()
            axis.set_facecolor(self.master.panel_soft if hasattr(self.master, "panel_soft") else "#12203a")
            axis.grid(True, alpha=0.25, linewidth=0.8)
            axis.tick_params(colors=self.master.muted if hasattr(self.master, "muted") else "#8ea2c6", labelsize=8)
            for spine in axis.spines.values():
                spine.set_color(self.master.border if hasattr(self.master, "border") else "#22324f")

            for values, label, color, unit in chart_defs:
                y_values = np.asarray(values, dtype=float)
                axis.plot(step_values, y_values, color=color, linewidth=1.8, label=f"{label} ({unit})")
                axis.fill_between(step_values, y_values, color=color, alpha=0.08)

            axis.legend(loc="upper left", fontsize=7, frameon=False, labelcolor=self.master.text if hasattr(self.master, "text") else "#e8f0ff")
            self._autoscale(axis, chart_defs)

        self.axes[0].set_title("Patient Vitals", color=self.master.text if hasattr(self.master, "text") else "#e8f0ff", fontsize=9)
        self.axes[1].set_title("Pressure Monitoring", color=self.master.text if hasattr(self.master, "text") else "#e8f0ff", fontsize=9)
        self.axes[2].set_title("Kidney Function", color=self.master.text if hasattr(self.master, "text") else "#e8f0ff", fontsize=9)
        self.axes[3].set_title("Fluid Balance", color=self.master.text if hasattr(self.master, "text") else "#e8f0ff", fontsize=9)
        self.axes[4].set_title("Filter Performance", color=self.master.text if hasattr(self.master, "text") else "#e8f0ff", fontsize=9)

        self.canvas.draw_idle()

    def _autoscale(self, axis, chart_defs):

        series_values = []
        for values, *_rest in chart_defs:
            series_values.extend(list(values))

        if not series_values:
            return

        low = min(series_values)
        high = max(series_values)
        if low == high:
            margin = max(abs(low) * 0.1, 1.0)
        else:
            margin = (high - low) * 0.15
        axis.set_ylim(low - margin, high + margin)
        axis.set_xlim(self.history["step"][0], self.history["step"][-1] + 1)

    def _on_motion(self, event):

        if event.inaxes not in self.axes[:5] or not self.history["step"]:
            self._hide_tooltip(event)
            return

        x_value = event.xdata
        if x_value is None:
            self._hide_tooltip(event)
            return

        index = int(np.clip(round(x_value), 0, len(self.history["step"]) - 1))
        axis = event.inaxes
        axis_title = axis.get_title()
        values = [line.get_ydata() for line in axis.lines]
        labels = [line.get_label() for line in axis.lines]
        if not values:
            return

        lines = []
        for label, series in zip(labels, values):
            if len(series) <= index:
                continue
            lines.append(f"{label}: {series[index]:.2f}")

        if not lines:
            return

        text = f"Step {self.history['step'][index]}\n" + "\n".join(lines)
        if self._tooltip is None:
            self._tooltip = axis.annotate(
                text,
                xy=(event.xdata, event.ydata),
                xytext=(12, 12),
                textcoords="offset points",
                bbox={"boxstyle": "round,pad=0.4", "fc": "#0d1728", "ec": "#5dd6c6", "alpha": 0.95},
                color="#e8f0ff",
                fontsize=8,
            )
        else:
            self._tooltip.set_text(text)
            self._tooltip.xy = (event.xdata, event.ydata)
            self._tooltip.set_visible(True)
        self.canvas.draw_idle()

    def _hide_tooltip(self, _event=None):

        if self._tooltip is not None:
            self._tooltip.set_visible(False)
            self.canvas.draw_idle()

    def close(self):

        try:
            self.canvas.mpl_disconnect(self.canvas.callbacks.callbacks.get("motion_notify_event", []))
        except Exception:
            pass

        try:
            self.canvas.get_tk_widget().destroy()
        except tk.TclError:
            pass

        try:
            import matplotlib.pyplot as plt
            plt.close(self.figure)
        except Exception:
            pass
