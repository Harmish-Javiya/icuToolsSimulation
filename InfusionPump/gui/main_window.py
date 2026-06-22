from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QGroupBox
)
from PyQt6.QtCore import QTimer
from gui.graph_widget import GraphWidget
from gui.dashboard import Dashboard
from gui.event_log import EventLog
from core.pump_controller import PumpController
from core.infusion_engine import InfusionEngine

# ---> IMPORT THE CENTRAL SERVER CLIENT <---
from core.central_patient_engine import CentralPatientEngine


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Infusion Pump Simulator")
        self.resize(800, 600)

        self.controller = PumpController()
        self.engine = InfusionEngine(self.controller)

        # ---> INITIALIZE NETWORK ENGINE <---
        self.net_engine = CentralPatientEngine()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)

        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        self.event_log = EventLog()
        self.graph_widget = GraphWidget()
        main_layout = QVBoxLayout()

        # Dashboard
        self.dashboard = Dashboard()
        main_layout.addWidget(self.dashboard)
        main_layout.addWidget(self.event_log)
        main_layout.addWidget(self.graph_widget)

        # Input section
        input_box = QGroupBox("Pump Settings")
        input_layout = QHBoxLayout()

        self.flow_input = QLineEdit("100")
        self.vtbi_input = QLineEdit("50")

        input_layout.addWidget(QLabel("Flow Rate (mL/hr):"))
        input_layout.addWidget(self.flow_input)
        input_layout.addWidget(QLabel("VTBI (mL):"))
        input_layout.addWidget(self.vtbi_input)

        input_box.setLayout(input_layout)
        main_layout.addWidget(input_box)

        # Buttons
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.pause_btn = QPushButton("Pause")
        self.stop_btn = QPushButton("Stop")
        self.reset_btn = QPushButton("Reset")

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.pause_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.reset_btn)

        main_layout.addLayout(button_layout)
        central.setLayout(main_layout)

        # Connect buttons
        self.start_btn.clicked.connect(self.start_pump)
        self.pause_btn.clicked.connect(self.pause_pump)
        self.stop_btn.clicked.connect(self.stop_pump)
        self.reset_btn.clicked.connect(self.reset_pump)

    def start_pump(self):
        flow = float(self.flow_input.text())
        vtbi = float(self.vtbi_input.text())
        self.controller.set_parameters(flow, vtbi)
        self.controller.start()
        self.timer.start(1000)

    def pause_pump(self):
        self.controller.pause()

    def stop_pump(self):
        self.controller.stop()

    def reset_pump(self):
        self.timer.stop()
        self.controller.reset()
        self.update_dashboard()
        self.graph_widget.update_graph(0, 0, 0)

    def update_simulation(self):
        # ---> PULL ALL GLOBAL VITALS <---
        sys_bp = self.net_engine.get("bp_sys")
        dia_bp = self.net_engine.get("bp_dia")
        hr = self.net_engine.get("hr")
        spo2 = self.net_engine.get("spo2")

        global_map = 90.0
        if sys_bp is not None and dia_bp is not None:
            global_map = (float(sys_bp) + 2.0 * float(dia_bp)) / 3.0

        # Pass global patient state into the physics engine
        self.engine.update(global_map=global_map)

        # Pull actual calculated pressure for the graph
        pressure = self.controller.pressure_monitor.pressure

        self.graph_widget.update_graph(
            self.controller.flow_rate,
            self.controller.infused,
            pressure
        )

        # Pass the newly pulled network vitals directly to the dashboard updater
        self.update_dashboard(sys_bp, dia_bp, hr, spo2)

    def update_dashboard(self, sys_bp=None, dia_bp=None, hr=None, spo2=None):
        # 1. Update Pump Specifics
        self.dashboard.state_label.setText(str(self.controller.get_state().value))
        self.dashboard.flow_label.setText(f"{self.controller.flow_rate:.1f} mL/hr")
        self.dashboard.vtbi_label.setText(f"{self.controller.vtbi:.1f} mL")
        self.dashboard.infused_label.setText(f"{self.controller.infused:.3f} mL")
        self.dashboard.remaining_label.setText(f"{self.controller.remaining:.3f} mL")

        # 2. Update Global Vitals if connected to the Master Server
        if sys_bp is not None and dia_bp is not None:
            self.dashboard.bp_label.setText(f"{float(sys_bp):.0f} / {float(dia_bp):.0f} mmHg")
        if hr is not None:
            self.dashboard.hr_label.setText(f"{float(hr):.0f} bpm")
        if spo2 is not None:
            self.dashboard.spo2_label.setText(f"{float(spo2):.1f} %")

        # 3. Update Event Log
        self.event_log.clear()
        for log in self.controller.logger.get_logs():
            self.event_log.add_log(log)

    def closeEvent(self, event):
        """Ensures the hardware socket is released when the UI closes."""
        self.timer.stop()
        if hasattr(self.controller, 'hardware'):
            self.controller.hardware.close()
        event.accept()