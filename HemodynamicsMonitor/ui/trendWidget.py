from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen
from PySide6.QtCore import Qt


class TrendWidget(QWidget):

    def __init__(self):

        super().__init__()

        self.max_points = 300
        self.data = [0] * self.max_points

        self.setMinimumHeight(150)

    def add_value(self, value):

        self.data.pop(0)
        self.data.append(value)

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        w = self.width()
        h = self.height()

        painter.fillRect(
            self.rect(),
            Qt.GlobalColor.black
        )

        grid = QPen(Qt.GlobalColor.darkGreen)
        painter.setPen(grid)

        for x in range(0, w, 40):
            painter.drawLine(x, 0, x, h)

        for y in range(0, h, 20):
            painter.drawLine(0, y, w, y)

        pen = QPen(Qt.GlobalColor.cyan)
        pen.setWidth(2)

        painter.setPen(pen)

        step = w / len(self.data)

        for i in range(len(self.data)-1):

            x1 = int(i * step)
            x2 = int((i+1) * step)

            y1 = h - int(self.data[i] * h / 150)
            y2 = h - int(self.data[i+1] * h / 150)

            painter.drawLine(
                x1,
                y1,
                x2,
                y2
            )