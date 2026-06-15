class PulseOximeter:

    def __init__(self, patient):
        self.patient = patient

    def read(self):
        return self.patient.update()