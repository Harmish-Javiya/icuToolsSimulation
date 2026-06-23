from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout


class Dashboard(QWidget):

    def __init__(self):
        super().__init__()

        layout = QGridLayout()

        self.state_label = QLabel("Idle")
        self.flow_label = QLabel("0 mL/hr")
        self.vtbi_label = QLabel("0 mL")
        self.infused_label = QLabel("0 mL")
        self.remaining_label = QLabel("0 mL")

        layout.addWidget(QLabel("State:"), 0, 0)
        layout.addWidget(self.state_label, 0, 1)

        layout.addWidget(QLabel("Flow Rate:"), 1, 0)
        layout.addWidget(self.flow_label, 1, 1)

        layout.addWidget(QLabel("VTBI:"), 2, 0)
        layout.addWidget(self.vtbi_label, 2, 1)

        layout.addWidget(QLabel("Infused:"), 3, 0)
        layout.addWidget(self.infused_label, 3, 1)

        layout.addWidget(QLabel("Remaining:"), 4, 0)
        layout.addWidget(self.remaining_label, 4, 1)

        self.setLayout(layout)