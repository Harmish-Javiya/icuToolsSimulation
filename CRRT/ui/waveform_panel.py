from __future__ import annotations

from collections import deque
import math

import numpy as np
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class WaveformPanel(ttk.Frame):

    def __init__(self, master, **kwargs):

        super().__init__(master, **kwargs)
        self.buffer_size = 300
        self.ecg = deque([0.0] * self.buffer_size, maxlen=self.buffer_size)
        self.pleth = deque([0.0] * self.buffer_size, maxlen=self.buffer_size)
        self.resp = deque([0.0] * self.buffer_size, maxlen=self.buffer_size)
        self.phase = {
            "ecg": 0.0,
            "pleth": 0.0,
            "resp": 0.0,
        }
        self._last_snapshot = {}

        self._build_layout()

    def _build_layout(self):

        container = tk.Frame(self, bg=self.master.panel if hasattr(self.master, "panel") else "#0d1728")
        container.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(container, bg=container["bg"])
        header.pack(fill=tk.X, padx=14, pady=(10, 4))

        tk.Label(
            header,
            text="Waveform Monitors",
            bg=header["bg"],
            fg=self.master.text if hasattr(self.master, "text") else "#e8f0ff",
            font=("Segoe UI", 12, "bold"),
        ).pack(side=tk.LEFT)

        tk.Label(
            header,
            text="ECG | SpO2 Pleth | Respiratory",
            bg=header["bg"],
            fg=self.master.muted if hasattr(self.master, "muted") else "#8ea2c6",
            font=("Segoe UI", 9),
        ).pack(side=tk.RIGHT)

        self.figure = Figure(figsize=(9.8, 3.1), dpi=100, facecolor=container["bg"])
        self.axes = [
            self.figure.add_subplot(3, 1, 1),
            self.figure.add_subplot(3, 1, 2),
            self.figure.add_subplot(3, 1, 3),
        ]

        for axis in self.axes:
            axis.set_facecolor(self.master.panel_soft if hasattr(self.master, "panel_soft") else "#12203a")
            axis.grid(True, alpha=0.18, linewidth=0.6)
            axis.tick_params(colors=self.master.muted if hasattr(self.master, "muted") else "#8ea2c6", labelsize=7)
            axis.set_xlim(0, self.buffer_size - 1)
            axis.set_ylim(-2.2, 2.2)
            for spine in axis.spines.values():
                spine.set_color(self.master.border if hasattr(self.master, "border") else "#22324f")

        self.axes[0].set_title("ECG Waveform", color=self.master.text if hasattr(self.master, "text") else "#e8f0ff", fontsize=9)
        self.axes[1].set_title("SpO2 Pleth", color=self.master.text if hasattr(self.master, "text") else "#e8f0ff", fontsize=9)
        self.axes[2].set_title("Respiratory Waveform", color=self.master.text if hasattr(self.master, "text") else "#e8f0ff", fontsize=9)

        self.ecg_line, = self.axes[0].plot([], [], color="#5dd6c6", linewidth=1.8)
        self.pleth_line, = self.axes[1].plot([], [], color="#7c9cff", linewidth=1.8)
        self.resp_line, = self.axes[2].plot([], [], color="#ffcc66", linewidth=1.8)

        self.figure.tight_layout(pad=1.1)
        self.canvas = FigureCanvasTkAgg(self.figure, master=container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def update_from_snapshot(self, snapshot):

        if snapshot:
            self._last_snapshot = snapshot

        self._advance_waveforms()
        self._draw()

    def _advance_waveforms(self):

        snapshot = self._last_snapshot or {}
        heart_rate = float(snapshot.get("heart_rate", 80))
        spo2 = float(snapshot.get("spo2", 98))
        respiratory_rate = float(snapshot.get("respiratory_rate", 16))

        ecg_rate = max(40.0, min(160.0, heart_rate)) / 60.0
        resp_rate = max(6.0, min(40.0, respiratory_rate)) / 60.0
        pleth_strength = max(0.35, min(1.3, spo2 / 100.0))

        self.phase["ecg"] += ecg_rate * 0.35
        self.phase["pleth"] += ecg_rate * 0.22
        self.phase["resp"] += resp_rate * 0.14

        ecg_value = self._ecg_wave(self.phase["ecg"])
        pleth_value = self._pleth_wave(self.phase["pleth"], pleth_strength)
        resp_value = self._resp_wave(self.phase["resp"])

        self.ecg.append(ecg_value)
        self.pleth.append(pleth_value)
        self.resp.append(resp_value)

    def _ecg_wave(self, phase):

        cycle = phase % 1.0
        qrs = math.exp(-((cycle - 0.18) ** 2) / 0.0008) * 2.0
        p_wave = math.exp(-((cycle - 0.08) ** 2) / 0.0015) * 0.28
        t_wave = math.exp(-((cycle - 0.38) ** 2) / 0.01) * 0.55
        baseline = math.sin(phase * 2 * math.pi) * 0.04
        return baseline + p_wave + qrs - 0.25 + t_wave

    def _pleth_wave(self, phase, strength):

        cycle = phase % 1.0
        upstroke = 1.6 / (1 + math.exp(-28 * (cycle - 0.1)))
        decay = math.exp(-3.6 * max(0.0, cycle - 0.28))
        ripple = math.sin(phase * 6 * math.pi) * 0.06
        return (upstroke * decay * strength) - 1.0 + ripple

    def _resp_wave(self, phase):

        return math.sin(phase * 2 * math.pi) * 0.85 + math.sin(phase * 4 * math.pi) * 0.12

    def _draw(self):

        x_values = np.arange(self.buffer_size)
        self.ecg_line.set_data(x_values, np.asarray(self.ecg))
        self.pleth_line.set_data(x_values, np.asarray(self.pleth))
        self.resp_line.set_data(x_values, np.asarray(self.resp))

        for axis in self.axes:
            axis.set_xlim(0, self.buffer_size - 1)

        self.canvas.draw_idle()

    def close(self):

        try:
            self.canvas.get_tk_widget().destroy()
        except tk.TclError:
            pass

        try:
            import matplotlib.pyplot as plt
            plt.close(self.figure)
        except Exception:
            pass
