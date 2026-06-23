class BatteryMonitor:

    def __init__(self):
        self.level = 100.0

    def update(self):

        self.level = max(
            0,
            self.level - 0.01
        )

        return self.level