from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen
from PySide6.QtCore import Qt


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
        # STRING SHIELD: Protect the graph from crashing if it receives "--" text
        if not isinstance(value, (int, float)):
            value = 0.0

        self.points.pop(0)
        self.points.append(value)

        # Triggers the paintEvent to redraw the screen
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
        # Draw waveform (Arterial Line)
        # -------------------
        # Using a red pen for arterial blood pressure
        wave_pen = QPen(Qt.GlobalColor.red)
        wave_pen.setWidth(2)
        painter.setPen(wave_pen)

        step_x = width / len(self.points)

        # === THE FIX: TRUE BLOOD PRESSURE SCALING ===
        # Map values from 0 to 220 mmHg to fit inside the widget height
        max_pressure = 220.0
        scale = height / max_pressure

        for i in range(len(self.points) - 1):

            x1 = int(i * step_x)
            x2 = int((i + 1) * step_x)

            # Qt draws from the top down. We subtract from the bottom (height)
            # so that 0 pressure is at the bottom and 120 pressure goes up.
            y1 = int(height - (self.points[i] * scale))
            y2 = int(height - (self.points[i + 1] * scale))

            # Clamp limits just in case physics go wild so it doesn't bleed out of the box
            y1 = max(0, min(height, y1))
            y2 = max(0, min(height, y2))

            painter.drawLine(x1, y1, x2, y2)