import math
import random

class ECG:
    def __init__(self):
        self.t = 0
        self.base_step = 0.1

    # === THE FIX: Accept 'hr' parameter to scale the speed ===
    def next_sample(self, rhythm, hr=75.0):
        # Scale speed so 60bpm = normal speed, 120bpm = double speed
        hr_multiplier = max(0.1, hr / 60.0) if hr > 0 else 1.0
        self.t += (self.base_step * hr_multiplier)

        r = rhythm.value
        if r == "Normal Sinus":
            return math.sin(self.t * 2) + 0.2 * math.sin(self.t * 8)
        elif r == "Ventricular Fibrillation":
            return random.uniform(-2, 2)
        elif r == "Ventricular Tachycardia":
            return math.sin(self.t * 8)
        elif r == "SVT":
            return 0.8 * math.sin(self.t * 6)
        elif r == "Bradycardia":
            return math.sin(self.t)
        elif r == "Tachycardia":
            return math.sin(self.t * 4)
        elif r == "PEA":
            return 0.3 * math.sin(self.t * 2)
        elif r == "Asystole":
            return random.uniform(-0.02, 0.02)
        return 0

    def get_samples(self, rhythm, count=20):
        data = []
        for _ in range(count):
            data.append(round(self.next_sample(rhythm), 3))
        return data