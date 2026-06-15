from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtCore import Qt


class WaveformWidget(QWidget):

    def __init__(self):
        super().__init__()

        # Number of displayed samples
        self.max_points = 500

        # Waveform buffer
        self.points = [0.0] * self.max_points

        # Minimum display size
        self.setMinimumHeight(300)
        self.setMinimumWidth(800)

    def add_point(self, value):
        """
        Add a new waveform sample.
        """

        self.points.pop(0)
        self.points.append(value)

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        width = self.width()
        height = self.height()

        # Black background
        painter.fillRect(self.rect(), Qt.GlobalColor.black)

        # -------------------
        # Draw grid
        # -------------------

        grid_pen = QPen(Qt.GlobalColor.darkGreen)
        grid_pen.setWidth(1)

        painter.setPen(grid_pen)

        grid_size = 40

        for x in range(0, width, grid_size):
            painter.drawLine(x, 0, x, height)

        for y in range(0, height, grid_size):
            painter.drawLine(0, y, width, y)

        # -------------------
        # Draw waveform
        # -------------------

        wave_pen = QPen(Qt.GlobalColor.green)
        wave_pen.setWidth(2)

        painter.setPen(wave_pen)

        step_x = width / len(self.points)

        baseline = height * 0.75

        scale = height * 0.5

        for i in range(len(self.points) - 1):

            x1 = int(i * step_x)
            x2 = int((i + 1) * step_x)

            y1 = int(baseline - self.points[i] * scale)
            y2 = int(baseline - self.points[i + 1] * scale)

            painter.drawLine(
                x1,
                y1,
                x2,
                y2
            )