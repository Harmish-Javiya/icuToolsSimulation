import pyqtgraph as pg
import numpy as np

from PySide6.QtCore import QTimer


class WaveformWidget(pg.PlotWidget):

    def __init__(self):
        super().__init__()

        self.setBackground("#050806")
        self.setTitle("")
        self.showGrid(x=False, y=True)
        self.setYRange(-1.5, 1.5)
        self.setXRange(0, 200)

        self.getAxis("left").setPen(pg.mkPen("#3bd48b", width=1))
        self.getAxis("bottom").setPen(pg.mkPen("#3bd48b", width=1))
        self.getAxis("left").setTextPen("#d9f5e8")
        self.getAxis("bottom").setTextPen("#d9f5e8")

        self.hideAxis("left")
        self.hideAxis("bottom")

        self.x = np.arange(200)
        self.phase = 0
        self.y = np.zeros(200)

        self.heart_rate = 72
        self.sensor_connected = True
        self.motion = False
        self.signal_quality = 100

        self.curve = self.plot(
            self.x,
            self.y,
            pen=pg.mkPen(color="#6effb7", width=3)
        )

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_wave)
        self.timer.start(40)

    def set_heart_rate(self, heart_rate):
        self.heart_rate = heart_rate

    def set_sensor(self, connected):
        self.sensor_connected = connected

    def set_motion(self, motion):
        self.motion = motion

    def set_signal(self, signal_quality):
        self.signal_quality = signal_quality

    def update_wave(self):
        self.phase += max(0.12, self.heart_rate / 600.0)

        if not self.sensor_connected:
            new_point = 0.0
        else:
            new_point = (
                np.sin(self.phase) ** 5
                + 0.08 * np.sin(4 * self.phase)
            )

            if self.motion:
                new_point += 0.18 * np.sin(12 * self.phase)

            if self.signal_quality < 60:
                new_point *= 0.75

        self.y = np.roll(self.y, -1)
        self.y[-1] = new_point

        self.curve.setData(self.x, self.y)