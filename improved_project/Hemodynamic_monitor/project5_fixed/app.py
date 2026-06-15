import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from src.patientEngine import PatientEngine
from src.hemodynamicMonitor import HemodynamicMonitor
from src.waveform import ArterialWaveform
from src.tcpServer import TCPServer
from src.therapyEngine import TherapyEngine
from src.dataLogger import DataLogger

from ui.mainWindow import MainWindow


class HemodynamicSimulator:

    def __init__(self):

        # -----------------
        # Backend
        # -----------------

        self.patient    = PatientEngine()
        self.therapy    = TherapyEngine()
        self.dataLogger = DataLogger()
        self.monitor    = HemodynamicMonitor(self.patient)
        self.waveform   = ArterialWaveform()

        self.tcp = TCPServer()
        self.tcp.start()

        # -----------------
        # GUI
        # -----------------

        self.window = MainWindow()

        self.window.connectScenarioButtons(
            lambda: self.patient.setScenario("Healthy"),
            lambda: self.patient.setScenario("Hemorrhage"),
            lambda: self.patient.setScenario("Sepsis"),
            lambda: self.patient.setScenario("Heart Failure"),
            lambda: self.patient.setScenario("Arrest"),
        )

        self.window.connectTherapyButtons(
            fluid      = lambda: self.therapy.give_fluid(),
            blood      = lambda: self.therapy.give_blood(),
            norad      = lambda: self.therapy.start_norad(),
            cpr_toggle = lambda checked: (
                self.therapy.start_cpr() if checked else self.therapy.stop_cpr()
            ),
        )

        # -----------------
        # Timer — 50 ms tick
        # -----------------

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def update(self):

        # 1. Apply therapy effects first
        self.therapy.apply(self.patient)

        # 2. Advance physiology
        self.patient.update()

        # 3. Read vitals
        data = self.monitor.read()

        # 4. Log
        self.dataLogger.log(data)

        # 5. Update GUI
        self.window.update_display(
            data,
            tcp_connected   = self.tcp.is_connected(),
            therapy_status  = self.therapy.status(),
        )

        # 6. Waveform
        self.window.wave.add_point(
            self.waveform.next_point(data["HR"])
        )

        # 7. Trend
        if hasattr(self.window, "trend"):
            self.window.trend.add_value(data["MAP"])

        # 8. TCP packet
        packet = (
            f"{data['HR']},"
            f"{data['SBP']},"
            f"{data['DBP']},"
            f"{data['MAP']},"
            f"{data['CO']},"
            f"{data['CVP']},"
            f"{data['RR']},"
            f"{data['SpO2']},"
            f"{data['Scenario']},"
            f"{data['Alarm']}"
        )
        self.tcp.send(packet)

    def show(self):
        self.window.show()


def main():

    app = QApplication(sys.argv)

    simulator = HemodynamicSimulator()
    simulator.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
