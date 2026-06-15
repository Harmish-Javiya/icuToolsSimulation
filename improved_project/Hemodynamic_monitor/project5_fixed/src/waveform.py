import math


class ArterialWaveform:

    def __init__(self):
        self.phase = 0.0

    def next_point(self, hr):

        if hr <= 0:
            return 0

        frequency = hr / 60.0

        self.phase += 0.04 * frequency

        if self.phase >= 1:
            self.phase -= 1

        x = self.phase

        if x < 0.15:
            y = x / 0.15

        elif x < 0.35:
            y = 1 - (x - 0.15) * 2

        elif x < 0.45:
            y = 0.5 - (x - 0.35)

        elif x < 0.60:
            y = 0.4 + (x - 0.45)

        else:
            y = 0.55 * math.exp(-(x - 0.60) * 5)

        return y