class OcclusionDetector:

    def __init__(self):
        self.threshold = 300

    def check(self, pressure):

        return pressure > self.threshold