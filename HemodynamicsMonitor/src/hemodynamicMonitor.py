class HemodynamicMonitor:

    def __init__(self, patient):

        self.patient = patient

    def read(self):

        return self.patient.get_vitals()