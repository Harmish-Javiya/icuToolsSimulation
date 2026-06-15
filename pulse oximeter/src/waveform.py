import math

class Waveform:

    def generate(self, t, hr):

        frequency = hr / 60

        return math.sin(2 * math.pi * frequency * t)