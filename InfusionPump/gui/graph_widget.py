import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout


class GraphWidget(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.plot = pg.PlotWidget()

        self.plot.setTitle("Infusion Parameters")
        self.plot.showGrid(x=True, y=True)
        self.plot.addLegend()

        self.flow_curve = self.plot.plot(
            name="Flow Rate"
        )

        self.infused_curve = self.plot.plot(
            name="Infused Volume"
        )

        self.pressure_curve = self.plot.plot(name="Pressure")

        layout.addWidget(self.plot)

        self.setLayout(layout)

        self.flow_data = []
        self.infused_data = []
        self.pressure_data = []
    def update_graph(
        self,
        flow_rate,
        infused,
        pressure
    ):

        self.flow_data.append(flow_rate)
        self.infused_data.append(infused)
        self.pressure_data.append(pressure)

        # Keep last 300 samples
        if len(self.flow_data) > 300:
            self.flow_data.pop(0)

        if len(self.infused_data) > 300:
            self.infused_data.pop(0)

        if len(self.pressure_data) > 300:
            self.pressure_data.pop(0)

        self.flow_curve.setData(
            self.flow_data
        )

        self.infused_curve.setData(
            self.infused_data
        )

        self.pressure_curve.setData(
            self.pressure_data
        )

        self.flow_curve = self.plot.plot(
            name="Flow Rate",
            pen=pg.mkPen((0, 255, 0), width=2)  # Green
)

        self.infused_curve = self.plot.plot(
            name="Infused Volume",
            pen=pg.mkPen((0, 128, 255), width=2)  # Blue
)

        self.pressure_curve = self.plot.plot(
            name="Pressure",
            pen=pg.mkPen((255, 0, 0), width=2)  # Red
)