from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from src.patientEngine import Patient
from src.pulseOximeter import PulseOximeter
from src.alarm import Alarm


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.patient = Patient()
        self.device = PulseOximeter(self.patient)
        self.alarm = Alarm()

        self.setWindowTitle("HELIOS Pulse Oximeter")
        self.resize(950, 650)
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
            #screenPanel { background: #0d1712; border: 1px solid #27463a; border-radius: 16px; }
            #card { background: #0f1914; border: 1px solid #2b4d3a; border-radius: 14px; }
            #titleLabel { color: #76ffb8; font-size: 24px; letter-spacing: 4px; font-weight: 700; }
            #subtitleLabel { color: #8fe1b8; font-size: 10px; letter-spacing: 2px; text-transform: uppercase; }
            #metricValue { color: #7dffc2; font-size: 28px; font-weight: 700; }
            #sectionLabel { color: #8fe1b8; font-size: 11px; letter-spacing: 2px; text-transform: uppercase; }
            #alarmLabel { color: #ff7a7a; font-size: 18px; font-weight: 700; }
        """)

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        screen_panel = QFrame()
        screen_panel.setObjectName("screenPanel")
        screen_panel_layout = QVBoxLayout(screen_panel)
        screen_panel_layout.setContentsMargins(22, 22, 22, 22)
        screen_panel_layout.setSpacing(16)

        title = QLabel("HELIOS PULSE OXIMETER")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Consolas")
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)

        subtitle = QLabel("Retro telemetry • live patient monitor")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        screen_panel_layout.addWidget(title)
        screen_panel_layout.addWidget(subtitle)

        vitals_grid = QGridLayout()
        vitals_grid.setSpacing(12)

        self.spo2 = QLabel("--")
        self.pulse = QLabel("--")
        self.temp = QLabel("--")
        self.battery = QLabel("--")
        self.signal = QLabel("--")
        self.sensor = QLabel("--")

        self.spo2.setObjectName("metricValue")
        self.pulse.setObjectName("metricValue")
        self.temp.setObjectName("metricValue")
        self.battery.setObjectName("metricValue")
        self.signal.setObjectName("metricValue")
        self.sensor.setObjectName("metricValue")

        for label in [self.spo2, self.pulse, self.temp]:
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        vitals_grid.addWidget(self._make_card("SpO₂", self.spo2), 0, 0)
        vitals_grid.addWidget(self._make_card("Pulse", self.pulse), 0, 1)
        vitals_grid.addWidget(self._make_card("Temperature", self.temp), 0, 2)

        screen_panel_layout.addLayout(vitals_grid)

        self.alarm_label = QLabel("ALARM : NONE")
        self.alarm_label.setObjectName("alarmLabel")
        self.alarm_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        screen_panel_layout.addWidget(self.alarm_label)

        self.status = QLabel("SYSTEM READY")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setObjectName("sectionLabel")
        screen_panel_layout.addWidget(self.status)

        scenarios = QHBoxLayout()
        scenarios.setSpacing(10)

        healthy = QPushButton("Healthy")
        fever = QPushButton("Fever")
        hypoxia = QPushButton("Hypoxia")
        shock = QPushButton("Shock")

        healthy.clicked.connect(self.patient.healthy)
        fever.clicked.connect(self.patient.fever)
        hypoxia.clicked.connect(self.patient.hypoxia)
        shock.clicked.connect(self.patient.shock)

        for button in [healthy, fever, hypoxia, shock]:
            scenarios.addWidget(button)

        screen_panel_layout.addLayout(scenarios)

        controls = QHBoxLayout()
        controls.setSpacing(10)

        sensor_btn = QPushButton("Sensor")
        finger_btn = QPushButton("Finger")
        motion_btn = QPushButton("Motion")

        sensor_btn.clicked.connect(self.patient.toggle_sensor)
        finger_btn.clicked.connect(self.patient.toggle_finger)
        motion_btn.clicked.connect(self.patient.toggle_motion)

        for button in [sensor_btn, finger_btn, motion_btn]:
            controls.addWidget(button)

        screen_panel_layout.addLayout(controls)

        layout.addWidget(screen_panel)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_monitor)
        self.timer.start(1000)

    def _make_card(self, title_text, value_label):
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 14, 14, 14)
        card_layout.setSpacing(8)

        title = QLabel(title_text)
        title.setObjectName("sectionLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)
        card_layout.addWidget(value_label)
        return card

    def update_monitor(self):
        data = self.device.read()

        self.spo2.setText(str(data["spo2"]) + " %")
        self.pulse.setText(str(data["heart_rate"]) + " BPM")
        self.temp.setText(str(data["temperature"]) + " C")

        self.battery.setText(str(data["battery"]) + " %")

        if data["sensor_connected"]:
            self.sensor.setText("CONNECTED")
        else:
            self.sensor.setText("DISCONNECTED")

        if data["signal_quality"] > 80:
            self.signal.setText("GOOD")
        elif data["signal_quality"] > 50:
            self.signal.setText("FAIR")
        else:
            self.signal.setText("POOR")

        alarms = self.alarm.check(data)

        if alarms:
            self.alarm_label.setText("ALARM : " + ", ".join(alarms))
        else:
            self.alarm_label.setText("ALARM : NONE")