from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
    QComboBox,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from src.patientEngine import Patient
from src.pulseOximeter import PulseOximeter
from src.alarm import Alarm
from ui.waveformWidget import WaveformWidget
from src.tcpServer import TCPServer
from src.hardware import HardwareInterface


# Alarm colour coding
ALARM_COLOURS = {
    "NORMAL":          ("#7dffc2", "#0f1914"),   # green text, dark bg
    "MOTION DETECTED": ("#ffd700", "#1a1500"),   # yellow  – advisory
    "CHECK SENSOR":    ("#ff9900", "#1a0d00"),   # orange  – warning
    "FINGER REMOVED":  ("#ff9900", "#1a0d00"),
    "HIGH TEMP":       ("#ff6b35", "#1a0900"),   # orange-red – fever
    "LOW TEMP":        ("#66cfff", "#000d1a"),   # blue – hypothermia
    "HIGH PULSE":      ("#ff4d4d", "#1a0000"),   # red – critical
    "LOW PULSE":       ("#ff4d4d", "#1a0000"),
    "LOW SPO2":        ("#ff1a1a", "#1a0000"),   # bright red – critical
    "SHOCK":           ("#ff0000", "#1a0000"),   # intense red – critical
}


def _alarm_colour(alarms):
    """Return (text_colour, bg_colour) for highest-severity active alarm."""
    priority = [
        "SHOCK", "LOW SPO2", "HIGH PULSE", "LOW PULSE",
        "HIGH TEMP", "LOW TEMP", "CHECK SENSOR", "FINGER REMOVED",
        "MOTION DETECTED",
    ]
    for name in priority:
        if name in alarms:
            return ALARM_COLOURS[name]
    return ALARM_COLOURS["NORMAL"]


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.patient = Patient()
        self.device = PulseOximeter(self.patient)
        self.alarm = Alarm()

        # TCP Server on port 5000
        self.tcp = TCPServer(
            host="0.0.0.0",
            port=5000
        )
        self.hardware = HardwareInterface(
            mode="Ethernet UDP",
            serial_port="/tmp/ttyV4",  # Unique virtual cable for the Oximeter
            ip="127.0.0.1",
            net_port=8000              # Pointing to the Linux Master Aggregator
        )

        self._muted = False          # audio mute flag passed to Alarm
        self._blink_state = False    # for alarm label blinking

        self.setWindowTitle("HELIOS Pulse Oximeter")
        self.resize(1200, 780)
        self.setStyleSheet("""
            QMainWindow { background: #060b08; color: #e9fff4; }
            QWidget { color: #e9fff4; }
            QLabel { color: #e9fff4; }
            QPushButton {
                background: #14231c;
                color: #7dffc2;
                border: 1px solid #2f5c45;
                border-radius: 10px;
                padding: 10px 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #1f3a2d;
                border-color: #57f0a4;
            }
            QPushButton#muteBtn {
                background: #1a0d00;
                color: #ff9900;
                border: 1px solid #cc6600;
            }
            QPushButton#muteBtn:checked {
                background: #330000;
                color: #ff4444;
                border: 1px solid #ff0000;
            }
            QComboBox {
                background: #14231c;
                color: #7dffc2;
                border: 1px solid #2f5c45;
                border-radius: 8px;
                padding: 6px 10px;
                font-weight: 600;
            }
            #screenPanel { background: #0d1712; border: 1px solid #27463a; border-radius: 18px; }
            #card { background: #0f1914; border: 1px solid #2b4d3a; border-radius: 14px; }
            #titleLabel { color: #76ffb8; font-size: 24px; letter-spacing: 4px; font-weight: 700; }
            #subtitleLabel { color: #8fe1b8; font-size: 10px; letter-spacing: 2px; }
            #metricValue { color: #7dffc2; font-size: 30px; font-weight: 700; }
            #sectionLabel { color: #8fe1b8; font-size: 11px; letter-spacing: 2px; }
            #alarmLabel { color: #ff7a7a; font-size: 17px; font-weight: 700; }
            #tcpLabel { color: #56d4a0; font-size: 10px; }
        """)

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        mainLayout = QVBoxLayout(central)
        mainLayout.setContentsMargins(24, 24, 24, 24)
        mainLayout.setSpacing(16)

        screen_panel = QFrame()
        screen_panel.setObjectName("screenPanel")
        panel_layout = QVBoxLayout(screen_panel)
        panel_layout.setContentsMargins(22, 22, 22, 22)
        panel_layout.setSpacing(16)

        # ── Title row ──────────────────────────────────────────────────
        titleRow = QHBoxLayout()
        title = QLabel("HELIOS PULSE OXIMETER")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Consolas")
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)

        self.tcpLabel = QLabel("TCP :5000 ●")
        self.tcpLabel.setObjectName("tcpLabel")
        self.tcpLabel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        titleRow.addWidget(title)
        titleRow.addStretch()
        self.hardwareMode = QComboBox()
        self.hardwareMode.addItems(["RS232", "Ethernet UDP", "Ethernet TCP"])
        self.hardwareMode.setCurrentText("Ethernet UDP")
        self.hardwareMode.currentTextChanged.connect(self._set_hardware_mode)
        titleRow.addWidget(self.hardwareMode)
        titleRow.addWidget(self.tcpLabel)
        panel_layout.addLayout(titleRow)

        subtitle = QLabel("Retro telemetry • patient vital monitor")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(subtitle)

        # ── Vital cards ────────────────────────────────────────────────
        vitalLayout = QGridLayout()
        vitalLayout.setSpacing(12)

        self.spo2 = QLabel("--")
        self.pulse = QLabel("--")
        self.temp = QLabel("--")

        self.spo2.setObjectName("metricValue")
        self.pulse.setObjectName("metricValue")
        self.temp.setObjectName("metricValue")

        for label in [self.spo2, self.pulse, self.temp]:
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        vitalLayout.addWidget(self._make_card("SpO₂", self.spo2), 0, 0)
        vitalLayout.addWidget(self._make_card("Pulse", self.pulse), 0, 1)
        vitalLayout.addWidget(self._make_card("Temperature", self.temp), 0, 2)
        panel_layout.addLayout(vitalLayout)

        # ── Waveform ───────────────────────────────────────────────────
        self.wave = WaveformWidget()
        self.wave.setMinimumHeight(220)
        panel_layout.addWidget(self.wave)

        # ── Status cards ───────────────────────────────────────────────
        statusLayout = QGridLayout()
        statusLayout.setSpacing(12)

        self.battery = QLabel("--")
        self.signal = QLabel("--")
        self.sensor = QLabel("--")
        self.alarmLabel = QLabel("NORMAL")

        self.battery.setObjectName("metricValue")
        self.signal.setObjectName("metricValue")
        self.sensor.setObjectName("metricValue")
        self.alarmLabel.setObjectName("alarmLabel")

        for label in [self.battery, self.signal, self.sensor]:
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.alarmLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.alarmCard = self._make_card("Alarm", self.alarmLabel)

        statusLayout.addWidget(self._make_card("Battery", self.battery), 0, 0)
        statusLayout.addWidget(self._make_card("Signal", self.signal), 0, 1)
        statusLayout.addWidget(self._make_card("Sensor", self.sensor), 0, 2)
        statusLayout.addWidget(self.alarmCard, 0, 3)
        panel_layout.addLayout(statusLayout)

        # ── Scenario buttons ───────────────────────────────────────────
        scenarioLayout = QHBoxLayout()
        scenarioLayout.setSpacing(10)

        healthy = QPushButton("Healthy")
        fever = QPushButton("🌡 Fever")
        hypoxia = QPushButton("💧 Hypoxia")
        shock = QPushButton("⚡ Shock")

        healthy.clicked.connect(self.patient.healthy)
        fever.clicked.connect(self.patient.fever)
        hypoxia.clicked.connect(self.patient.hypoxia)
        shock.clicked.connect(self.patient.shock)

        for btn in [healthy, fever, hypoxia, shock]:
            scenarioLayout.addWidget(btn)
        panel_layout.addLayout(scenarioLayout)

        # ── Device control + Mute button ───────────────────────────────
        controlLayout = QHBoxLayout()
        controlLayout.setSpacing(10)

        sensorBtn = QPushButton("Sensor")
        fingerBtn = QPushButton("Finger")
        motionBtn = QPushButton("Motion")

        sensorBtn.clicked.connect(self.patient.toggle_sensor)
        fingerBtn.clicked.connect(self.patient.toggle_finger)
        motionBtn.clicked.connect(self.patient.toggle_motion)

        self.muteBtn = QPushButton("🔇 Mute Alarm")
        self.muteBtn.setObjectName("muteBtn")
        self.muteBtn.setCheckable(True)
        self.muteBtn.clicked.connect(self._toggle_mute)

        for btn in [sensorBtn, fingerBtn, motionBtn]:
            controlLayout.addWidget(btn)
        controlLayout.addStretch()
        controlLayout.addWidget(self.muteBtn)
        panel_layout.addLayout(controlLayout)

        mainLayout.addWidget(screen_panel)

        # ── Timers ─────────────────────────────────────────────────────
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateMonitor)
        self.timer.start(1000)

        # Blink timer for active alarms (500 ms toggle)
        self.blinkTimer = QTimer()
        self.blinkTimer.timeout.connect(self._blink_alarm)
        self.blinkTimer.start(500)

        self._active_alarms = []

    # ──────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────

    def _make_card(self, title_text, value_label):
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(8)

        title = QLabel(title_text)
        title.setObjectName("sectionLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)
        card_layout.addWidget(value_label)
        return card

    def _toggle_mute(self, checked):
        self._muted = checked
        self.alarm.muted = checked
        self.muteBtn.setText("🔇 Muted" if checked else "🔇 Mute Alarm")

    def _set_hardware_mode(self, mode):
        self.hardware.configure(mode=mode)

    def _blink_alarm(self):
        """Toggle alarm label visibility when alarms are active."""
        if not self._active_alarms:
            return
        self._blink_state = not self._blink_state
        self.alarmLabel.setVisible(self._blink_state)

    def _update_alarm_style(self, alarms):
        """Colour the alarm card based on highest severity."""
        if not alarms:
            self.alarmLabel.setVisible(True)
            self.alarmCard.setStyleSheet("")
            return

        txt_col, bg_col = _alarm_colour(alarms)
        self.alarmCard.setStyleSheet(
            f"QFrame#card {{ background: {bg_col}; border: 2px solid {txt_col}; border-radius: 14px; }}"
        )
        self.alarmLabel.setStyleSheet(f"color: {txt_col}; font-size: 15px; font-weight: 800;")

    # ──────────────────────────────────────────────────────────────────
    # Main update loop
    # ──────────────────────────────────────────────────────────────────

    def updateMonitor(self):
        data = self.device.read()

        data["device_id"] = "SPO2-PULMO-01"

        self.tcp.send(data)
        self.hardware.send_data(data)

        self.wave.set_heart_rate(data["heart_rate"])
        self.wave.set_sensor(data["sensor_connected"])
        self.wave.set_motion(data["motion"])
        self.wave.set_signal(data["signal_quality"])

        self.spo2.setText(f"{data['spo2']}%")
        self.pulse.setText(f"{data['heart_rate']} BPM")
        self.temp.setText(f"{data['temperature']}°C")

        self.battery.setText(f"{data['battery']}%")

        self.sensor.setText(
            "CONNECTED" if data["sensor_connected"] else "OFF"
        )

        if data["signal_quality"] > 80:
            self.signal.setText("GOOD")
        elif data["signal_quality"] > 50:
            self.signal.setText("FAIR")
        else:
            self.signal.setText("POOR")

        # Alarm processing (beeps happen inside alarm.check)
        alarms = self.alarm.check(data, muted=self._muted)
        self._active_alarms = alarms

        if alarms:
            self.alarmLabel.setText(", ".join(alarms))
        else:
            self.alarmLabel.setText("NORMAL")
            self.alarmLabel.setVisible(True)

        self._update_alarm_style(alarms)

        # TCP indicator: green if client connected, grey if not
        if self.tcp.client is not None:
            self.tcpLabel.setText("TCP :5000 ●")
            self.tcpLabel.setStyleSheet("color: #56d4a0; font-size: 10px;")
        else:
            self.tcpLabel.setText("TCP :5000 ○")
            self.tcpLabel.setStyleSheet("color: #556655; font-size: 10px;")

    def closeEvent(self, event):
        self.hardware.close()
        super().closeEvent(event)
