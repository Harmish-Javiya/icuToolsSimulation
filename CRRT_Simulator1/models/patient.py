import random


class Patient:

    def __init__(self):

        # Basic Vital Signs
        self.hr = 80                    # Heart Rate (bpm)
        self.bp_sys = 120               # Systolic BP
        self.bp_dia = 80                # Diastolic BP
        self.spo2 = 98                  # Oxygen Saturation (%)
        self.temperature = 37.0         # Celsius
        self.respiratory_rate = 16      # Breaths/min

        # Renal Parameters
        self.bun = 80.0                 # Blood Urea Nitrogen
        self.creatinine = 6.0           # mg/dL
        self.potassium = 6.2            # mmol/L
        self.sodium = 140.0             # mmol/L
        self.hemoglobin = 11.0          # g/dL

        # Fluid Status
        self.fluid_overload = 5.0       # Liters

    def update_vitals(self):
        """
        Simulates natural changes in patient vitals.
        """

        self.hr += random.randint(-2, 2)

        self.bp_sys += random.randint(-3, 3)

        self.bp_dia += random.randint(-2, 2)

        self.spo2 += random.randint(-1, 1)

        self.temperature += random.uniform(-0.1, 0.1)
        self.respiratory_rate += random.uniform(-1, 1)

        # Safety Limits

        self.hr = max(40, min(180, self.hr))

        self.bp_sys = max(60, min(220, self.bp_sys))

        self.bp_dia = max(40, min(140, self.bp_dia))

        self.spo2 = max(80, min(100, self.spo2))

        self.temperature = round(
            max(34, min(42, self.temperature)),
            1
        )

        self.respiratory_rate = max(4, min(50, round(self.respiratory_rate, 1)))

    def get_patient_data(self):

        return {
            "Heart Rate": self.hr,
            "Blood Pressure":
                f"{self.bp_sys}/{self.bp_dia}",
            "SpO2": self.spo2,
            "Temperature": self.temperature,
            "Respiratory Rate": self.respiratory_rate,
            "BUN": round(self.bun, 2),
            "Creatinine": round(self.creatinine, 2),
            "Potassium": round(self.potassium, 2),
            "Sodium": round(self.sodium, 2),
            "Hemoglobin": round(self.hemoglobin, 2),
            "Fluid Overload":
                round(self.fluid_overload, 2)
        }