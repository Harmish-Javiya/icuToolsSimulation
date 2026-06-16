from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QProgressBar
)

from PyQt6.QtCore import Qt, QTimer

from ui.waveformWidget import WaveformWidget
from ui.trendWidget import TrendWidget


class MainWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Hemodynamic Monitor")
        self.resize(1200, 750)

        self.setStyleSheet("""
            QWidget {
                background-color: black;
                color: lime;
                font-size: 16px;
            }
            QPushButton {
                background-color: #202020;
                color: white;
                padding: 8px;
                border: 1px solid #444;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #303030;
            }
            QPushButton[active="true"] {
                background-color: #004400;
                color: lime;
                border: 2px solid lime;
            }
            QProgressBar {
                border: 1px solid #444;
                border-radius: 3px;
                background: #111;
                text-align: center;
                color: white;
                font-size: 11px;
                max-height: 14px;
            }
            QProgressBar::chunk {
                background-color: #00aa00;
            }
        """)

        # Beep alarm system
        self._last_alarm = "NORMAL"
        self._beep_timer = QTimer(self)
        self._beep_timer.timeout.connect(self._do_beep)

        mainLayout = QVBoxLayout()
        mainLayout.setSpacing(6)

        # ── Vitals grid ──────────────────────────────────────────────
        vitals = QGridLayout()
        vitals.setSpacing(6)

        self.hr   = QLabel("HR\n75")
        self.bp   = QLabel("BP\n120/80")
        self.map  = QLabel("MAP\n93")
        self.co   = QLabel("CO\n5.2")
        self.cvp  = QLabel("CVP\n8")
        self.rr   = QLabel("RR\n16")
        self.spo2 = QLabel("SpO₂\n98")

        vital_style = """
            border: 2px solid green;
            padding: 10px;
            font-size: 22px;
        """
        for i, lbl in enumerate(
            [self.hr, self.bp, self.map, self.co, self.cvp, self.rr, self.spo2]
        ):
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(vital_style)
            vitals.addWidget(lbl, 0, i)

        mainLayout.addLayout(vitals)

        # ── Waveform ─────────────────────────────────────────────────
        self.wave = WaveformWidget()
        mainLayout.addWidget(self.wave)

        # ── Trend ────────────────────────────────────────────────────
        self.trend = TrendWidget()
        mainLayout.addWidget(self.trend)

        # ── Scenario buttons ─────────────────────────────────────────
        scenarioLayout = QHBoxLayout()
        self.healthyBtn = QPushButton("🟢 Healthy")
        self.hemBtn     = QPushButton("🔴 Hemorrhage")
        self.sepsisBtn  = QPushButton("🟠 Sepsis")
        self.hfBtn      = QPushButton("🔵 Heart Failure")
        self.arrestBtn  = QPushButton("💀 Arrest")

        for btn in [self.healthyBtn, self.hemBtn, self.sepsisBtn,
                    self.hfBtn, self.arrestBtn]:
            scenarioLayout.addWidget(btn)

        mainLayout.addLayout(scenarioLayout)

        # ── Therapy buttons + dose bars ──────────────────────────────
        therapyLayout = QGridLayout()
        therapyLayout.setSpacing(6)

        # Fluid Bolus
        self.fluidBtn = QPushButton("💧 Fluid Bolus")
        self.fluidBtn.setToolTip("Raises BP and CVP — use in Hemorrhage / Sepsis")
        self.fluidBar = QProgressBar()
        self.fluidBar.setRange(0, 100)
        self.fluidBar.setValue(0)
        self.fluidBar.setFormat("Fluid: %v%")
        therapyLayout.addWidget(self.fluidBtn, 0, 0)
        therapyLayout.addWidget(self.fluidBar, 1, 0)

        # Blood Transfusion
        self.bloodBtn = QPushButton("🩸 Blood Transfusion")
        self.bloodBtn.setToolTip("Raises BP and Stroke Volume — use in Hemorrhage")
        self.bloodBar = QProgressBar()
        self.bloodBar.setRange(0, 100)
        self.bloodBar.setValue(0)
        self.bloodBar.setFormat("Blood: %v%")
        therapyLayout.addWidget(self.bloodBtn, 0, 1)
        therapyLayout.addWidget(self.bloodBar, 1, 1)

        # Noradrenaline
        self.noradBtn = QPushButton("💉 Noradrenaline")
        self.noradBtn.setToolTip("Strong vasopressor — raises BP rapidly. Use in Sepsis")
        self.noradBar = QProgressBar()
        self.noradBar.setRange(0, 100)
        self.noradBar.setValue(0)
        self.noradBar.setFormat("Norad: %v%")
        self.noradBar.setStyleSheet(
            "QProgressBar::chunk { background-color: #cc8800; }"
        )
        therapyLayout.addWidget(self.noradBtn, 0, 2)
        therapyLayout.addWidget(self.noradBar, 1, 2)

        # CPR
        self.cprBtn = QPushButton("❤️ Start CPR")
        self.cprBtn.setToolTip("Only effective during Cardiac Arrest")
        self.cprBtn.setCheckable(True)
        self.cprActive = QLabel("CPR: OFF")
        self.cprActive.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cprActive.setStyleSheet("color: gray; font-size: 13px;")
        therapyLayout.addWidget(self.cprBtn, 0, 3)
        therapyLayout.addWidget(self.cprActive, 1, 3)

        mainLayout.addLayout(therapyLayout)

        # ── Status bar ───────────────────────────────────────────────
        status = QHBoxLayout()

        self.scenario = QLabel("Scenario: Healthy")
        self.alarm    = QLabel("Alarm: NORMAL")
        self.tcp      = QLabel("TCP: Waiting...")

        for lbl in [self.scenario, self.alarm, self.tcp]:
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status.addWidget(lbl)

        mainLayout.addLayout(status)

        self.setLayout(mainLayout)

    # ── Beep ─────────────────────────────────────────────────────────

    def _do_beep(self):
        print("\a", end="", flush=True)

    def _start_beep(self, fast=False):
        interval = 300 if fast else 800
        self._beep_timer.start(interval)

    def _stop_beep(self):
        self._beep_timer.stop()

    # ── Main update ──────────────────────────────────────────────────

    def update_display(self, data, tcp_connected=False, therapy_status=None):

        # Vitals
        self.hr.setText(f"HR\n{data['HR']}")
        self.bp.setText(f"BP\n{data['SBP']}/{data['DBP']}")
        self.map.setText(f"MAP\n{data['MAP']}")
        self.co.setText(f"CO\n{data['CO']}")
        self.cvp.setText(f"CVP\n{data['CVP']}")
        self.rr.setText(f"RR\n{data['RR']}")
        self.spo2.setText(f"SpO₂\n{data['SpO2']}")

        self.scenario.setText(f"Scenario: {data['Scenario']}")

        # Alarm
        alarm = data['Alarm']
        self.alarm.setText(f"Alarm: {alarm}")

        if alarm == "NORMAL":
            self.alarm.setStyleSheet("color: lime;")
            self._stop_beep()
        elif alarm == "CARDIAC ARREST":
            self.alarm.setStyleSheet(
                "color: red; font-weight: bold; font-size: 18px;"
            )
            self._start_beep(fast=True)
        else:
            self.alarm.setStyleSheet("color: orange; font-weight: bold;")
            self._start_beep(fast=False)

        self._last_alarm = alarm

        # TCP
        if tcp_connected:
            self.tcp.setText("TCP: Online")
            self.tcp.setStyleSheet("color: lime;")
        else:
            self.tcp.setText("TCP: Offline")
            self.tcp.setStyleSheet("color: gray;")

        # Therapy dose bars
        if therapy_status:
            fluid_pct = min(100, int(therapy_status["fluid"] * 100))
            blood_pct = min(100, int(therapy_status["blood"] * 100))
            norad_pct = min(100, int(therapy_status["norad"] * 100))

            self.fluidBar.setValue(fluid_pct)
            self.bloodBar.setValue(blood_pct)
            self.noradBar.setValue(norad_pct)

            # Highlight buttons while dose is active
            self._set_active(self.fluidBtn, fluid_pct > 0)
            self._set_active(self.bloodBtn, blood_pct > 0)
            self._set_active(self.noradBtn, norad_pct > 0)

            # CPR indicator
            cpr_on = therapy_status["cpr"]
            if cpr_on:
                self.cprActive.setText("CPR: ACTIVE")
                self.cprActive.setStyleSheet(
                    "color: red; font-weight: bold; font-size: 13px;"
                )
            else:
                self.cprActive.setText("CPR: OFF")
                self.cprActive.setStyleSheet("color: gray; font-size: 13px;")

    def _set_active(self, btn, active):
        btn.setProperty("active", "true" if active else "false")
        btn.style().unpolish(btn)
        btn.style().polish(btn)

    # ── Button wiring ────────────────────────────────────────────────

    def connectScenarioButtons(
        self, healthy, hemorrhage, sepsis, heart_failure, arrest
    ):
        self.healthyBtn.clicked.connect(healthy)
        self.hemBtn.clicked.connect(hemorrhage)
        self.sepsisBtn.clicked.connect(sepsis)
        self.hfBtn.clicked.connect(heart_failure)
        self.arrestBtn.clicked.connect(arrest)

    def connectTherapyButtons(self, fluid, blood, norad, cpr_toggle):
        self.fluidBtn.clicked.connect(fluid)
        self.bloodBtn.clicked.connect(blood)
        self.noradBtn.clicked.connect(norad)
        # CPR is a toggle — pass current checked state to handler
        self.cprBtn.toggled.connect(cpr_toggle)
