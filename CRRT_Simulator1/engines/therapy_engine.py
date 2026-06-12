class TherapyEngine:

    def __init__(self):

        self.active = False

        self.mode = "CVVHDF"

        self.ur_rate = 100

    def start_therapy(self):

        self.active = True

        print(
            f"Therapy Started ({self.mode})"
        )

    def stop_therapy(self):

        self.active = False

        print("Therapy Stopped")

    def set_mode(self, mode):

        self.mode = mode



    def update(self, patient, fluid):

        if not self.active:
            return

        if patient.potassium > 4.0:
            patient.potassium -= 0.02

        if patient.creatinine > 1.0:
            patient.creatinine -= 0.03

        if patient.bun > 20:
            patient.bun -= 0.20
            

        # Ultrafiltration
        fluid.output += 10