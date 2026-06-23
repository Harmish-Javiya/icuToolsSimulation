from PyQt6.QtCore import QTimer


class TimerManager:

    def __init__(self, callback):

        self.timer = QTimer()
        self.timer.timeout.connect(callback)

    def start(self, interval=1000):
        self.timer.start(interval)

    def stop(self):
        self.timer.stop()