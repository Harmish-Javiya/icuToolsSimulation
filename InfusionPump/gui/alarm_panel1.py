from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt


class AlarmPanel(QLabel):

    def __init__(self):
        super().__init__()

        self.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.setText(
            "No Active Alarm"
        )

        self.setStyleSheet("""
            background-color: green;
            color: white;
            font-size: 16px;
            padding: 8px;
        """)