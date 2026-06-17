from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class ControlPanel(ttk.Frame):

    def __init__(self, master, on_change=None, on_replace_filter=None, **kwargs):

        super().__init__(master, **kwargs)
        self.on_change = on_change
        self.on_replace_filter = on_replace_filter
        self._syncing = False
        self._fields = {}

        self.configure(style="Dashboard.TFrame")
        self._build_layout()

    def _build_layout(self):

        container = tk.Frame(self, bg=self.master.bg if hasattr(self.master, "bg") else "#07111f")
        container.pack(fill=tk.BOTH, expand=True)

        header = tk.Frame(container, bg=self.master.panel if hasattr(self.master, "panel") else "#0d1728")
        header.pack(fill=tk.X, padx=0, pady=(0, 12))

        tk.Label(
            header,
            text="Patient Control Panel",
            bg=header["bg"],
            fg=self.master.text if hasattr(self.master, "text") else "#e8f0ff",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", padx=14, pady=(12, 2))

        tk.Label(
            header,
            text="Adjust vitals, laboratory values, and therapy-related fluid settings live.",
            bg=header["bg"],
            fg=self.master.muted if hasattr(self.master, "muted") else "#8ea2c6",
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=14, pady=(0, 12))

        canvas = tk.Canvas(container, highlightthickness=0, bg=container["bg"])
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.inner = tk.Frame(canvas, bg=container["bg"])
        self.inner.bind(
            "<Configure>",
            lambda _event: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self.inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._add_section("Vitals", [
            ("hr", "Heart Rate", 30, 220, 80),
            ("bp_sys", "Systolic BP", 40, 240, 120),
            ("bp_dia", "Diastolic BP", 20, 160, 80),
            ("spo2", "SpO2", 50, 100, 98),
            ("temperature", "Temperature", 33.0, 42.5, 37.0),
            ("respiratory_rate", "Respiratory Rate", 4, 50, 16),
        ])

        self._add_section("Laboratory Values", [
            ("bun", "BUN", 0, 220, 80),
            ("creatinine", "Creatinine", 0, 20, 6.0),
            ("potassium", "Potassium", 2.0, 8.5, 6.2),
            ("sodium", "Sodium", 120, 165, 140),
            ("hemoglobin", "Hemoglobin", 4.0, 20.0, 11.0),
        ])

        self._add_section("Fluid Parameters", [
            ("fluid_intake", "Fluid Intake", 0, 5000, 0),
            ("fluid_output", "Fluid Output", 0, 5000, 0),
            ("ultrafiltration_rate", "Ultrafiltration Rate", 0, 500, 100),
        ])

        action_box = tk.Frame(self.inner, bg=self.inner["bg"])
        action_box.pack(fill=tk.X, padx=12, pady=(2, 18))

        ttk.Button(
            action_box,
            text="Replace Filter",
            command=self._replace_filter,
        ).pack(side=tk.LEFT)

    def _add_section(self, title, fields):

        panel = tk.Frame(self.inner, bg=self.master.panel if hasattr(self.master, "panel") else "#0d1728", bd=0)
        panel.pack(fill=tk.X, padx=12, pady=(0, 14))

        tk.Label(
            panel,
            text=title,
            bg=panel["bg"],
            fg=self.master.text if hasattr(self.master, "text") else "#e8f0ff",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", padx=14, pady=(12, 8))

        for name, label, minimum, maximum, initial in fields:
            self._fields[name] = self._create_field(panel, name, label, minimum, maximum, initial)

    def _create_field(self, parent, name, label_text, minimum, maximum, initial):

        row = tk.Frame(parent, bg=parent["bg"])
        row.pack(fill=tk.X, padx=14, pady=6)

        tk.Label(
            row,
            text=label_text,
            width=18,
            anchor="w",
            bg=row["bg"],
            fg=self.master.muted if hasattr(self.master, "muted") else "#8ea2c6",
            font=("Segoe UI", 9, "bold"),
        ).grid(row=0, column=0, sticky="w")

        value_var = tk.DoubleVar(value=initial)
        value_display = tk.StringVar(value=f"{initial:g}")

        def clamp_value(raw):
            try:
                numeric = float(raw)
            except (TypeError, ValueError):
                numeric = initial
            return max(minimum, min(maximum, numeric))

        def push_change(*_args):
            if self._syncing:
                return
            value = clamp_value(value_var.get())
            self._syncing = True
            value_var.set(value)
            value_display.set(f"{value:.1f}" if isinstance(minimum, float) or isinstance(maximum, float) else f"{int(round(value))}")
            self._syncing = False
            if callable(self.on_change):
                self.on_change(name, value)

        value_var.trace_add("write", push_change)

        slider = ttk.Scale(row, from_=minimum, to=maximum, orient="horizontal", variable=value_var)
        slider.grid(row=0, column=1, sticky="ew", padx=(12, 10))

        spin = tk.Spinbox(
            row,
            from_=minimum,
            to=maximum,
            increment=0.1 if isinstance(minimum, float) or isinstance(maximum, float) else 1,
            textvariable=value_display,
            width=10,
            justify="right",
            command=lambda: value_var.set(clamp_value(value_display.get())),
        )
        spin.grid(row=0, column=2, sticky="e")

        def commit_spin(_event=None):
            value = clamp_value(value_display.get())
            self._syncing = True
            value_var.set(value)
            value_display.set(f"{value:.1f}" if isinstance(minimum, float) or isinstance(maximum, float) else f"{int(round(value))}")
            self._syncing = False
            if callable(self.on_change):
                self.on_change(name, value)

        spin.bind("<Return>", commit_spin)
        spin.bind("<FocusOut>", commit_spin)

        row.grid_columnconfigure(1, weight=1)

        return {
            "var": value_var,
            "display": value_display,
            "minimum": minimum,
            "maximum": maximum,
        }

    def _replace_filter(self):

        if callable(self.on_replace_filter):
            self.on_replace_filter()

    def sync_from_snapshot(self, snapshot):

        if not snapshot:
            return

        values = {
            "hr": snapshot.get("heart_rate"),
            "bp_sys": snapshot.get("blood_pressure", "0/0").split("/")[0],
            "bp_dia": snapshot.get("blood_pressure", "0/0").split("/")[1],
            "spo2": snapshot.get("spo2"),
            "temperature": snapshot.get("temperature"),
            "respiratory_rate": snapshot.get("respiratory_rate"),
            "bun": snapshot.get("bun"),
            "creatinine": snapshot.get("creatinine"),
            "potassium": snapshot.get("potassium"),
            "sodium": snapshot.get("sodium"),
            "hemoglobin": snapshot.get("hemoglobin"),
            "fluid_intake": snapshot.get("fluid_intake"),
            "fluid_output": snapshot.get("fluid_output"),
            "ultrafiltration_rate": snapshot.get("ultrafiltration_rate"),
        }

        self._syncing = True
        try:
            for name, raw_value in values.items():
                field = self._fields.get(name)
                if field is None or raw_value is None:
                    continue
                minimum = field["minimum"]
                maximum = field["maximum"]
                try:
                    numeric = float(raw_value)
                except (TypeError, ValueError):
                    continue
                numeric = max(minimum, min(maximum, numeric))
                field["var"].set(numeric)
                field["display"].set(f"{numeric:.1f}" if isinstance(minimum, float) or isinstance(maximum, float) else f"{int(round(numeric))}")
        finally:
            self._syncing = False
